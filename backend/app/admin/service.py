"""
Admin service layer
"""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.admin.repository import (
    AdminCategoriaRepository,
    AdminIngredienteRepository,
    AdminMetricsRepository,
    AdminOrderRepository,
    AdminProductoRepository,
    AdminUserRepository,
)
from app.admin.schemas import (
    AdminCategoriaListItem,
    AdminCategoriaListResponse,
    AdminChangeStateRequest,
    AdminIngredienteListItem,
    AdminIngredienteListResponse,
    AdminOrderListResponse,
    AdminProductoListItem,
    AdminProductoListResponse,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    MetricsPedidosEstadoItem,
    MetricsPedidosEstadoResponse,
    MetricsProductoTopItem,
    MetricsProductoTopResponse,
    MetricsResumenResponse,
    MetricsVentasItem,
    MetricsVentasResponse,
)
from app.auth.repository import RefreshTokenRepository, UserRepository
from app.auth.schemas import UserResponse
from app.core.exceptions import (
    ForbiddenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models import User
from app.models.producto import Producto
from app.pedidos.repository import PedidoRepository
from app.pedidos.schemas import PedidoRead
from app.pedidos.service import TERMINAL_STATES, TRANSITIONS


class AdminService:
    """Service for admin operations"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.metrics_repo = AdminMetricsRepository(db)

    def assign_roles_to_user(self, user_id: UUID, roles: list[str]) -> UserResponse:
        """Assign roles to a user"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # Check if trying to remove ADMIN from last ADMIN
        admin_count = self.user_repo.count_admin_users()
        if admin_count == 1 and "ADMIN" not in roles:
            current_admin = self.user_repo.get_user_with_roles(user_id)
            has_admin = any(role.role == "ADMIN" for role in current_admin.roles)
            if has_admin:
                raise ForbiddenException(
                    "No puedes quitarle el rol ADMIN al único administrador del sistema"
                )

        # Remove existing roles and assign new ones
        for role in user.roles:
            self.user_repo.remove_role(user_id, role.role)

        for role in roles:
            self.user_repo.assign_role(user_id, role)

        # Refresh user to get updated roles
        self.db.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=[role.role for role in user.roles],
        )

    def remove_role_from_user(self, user_id: UUID, role: str) -> UserResponse:
        """Remove a specific role from a user"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # Check if trying to remove ADMIN from last ADMIN
        if role == "ADMIN":
            admin_count = self.user_repo.count_admin_users()
            if admin_count == 1:
                current_admin = self.user_repo.get_user_with_roles(user_id)
                has_admin = any(r.role == "ADMIN" for r in current_admin.roles)
                if has_admin:
                    raise ForbiddenException(
                        "No puedes quitarle el rol ADMIN al único administrador del sistema"
                    )

        self.user_repo.remove_role(user_id, role)

        # Refresh user to get updated roles
        self.db.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=[role.role for role in user.roles],
        )

    def list_users(
        self,
        page: int = 1,
        size: int = 20,
        rol: str | None = None,
        search: str | None = None,
        estado: str = "activo",
    ) -> AdminUserListResponse:
        """List users with pagination and filters"""
        if estado not in ("activo", "inactivo", "todos"):
            estado = "activo"

        repo = AdminUserRepository(self.db)
        users, total = repo.list_users(page, size, rol, search, estado)
        items = [self._user_to_response(u) for u in users]
        pages = max(1, (total + size - 1) // size)
        return AdminUserListResponse(items=items, total=total, page=page, size=size, pages=pages)

    def get_user_detail(self, user_id: UUID) -> AdminUserResponse:
        """Get user detail by ID (including soft-deleted)"""
        repo = AdminUserRepository(self.db)
        user = repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()
        return self._user_to_response(user)

    def update_user(self, user_id: UUID, data: AdminUserUpdateRequest) -> AdminUserResponse:
        """Update user fields and/or roles"""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        roles_changed = False

        # Update email with uniqueness check
        if data.email is not None and data.email != user.email:
            existing = self.user_repo.get_user_by_email(data.email)
            if existing:
                raise UserAlreadyExistsException()
            user.email = data.email

        # Update scalar fields
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.telefono is not None:
            user.telefono = data.telefono

        # Update roles if provided
        if data.roles is not None:
            current_roles = {role.role for role in user.roles}
            new_roles = set(data.roles)

            if current_roles != new_roles:
                # Check last ADMIN protection
                if "ADMIN" in current_roles and "ADMIN" not in new_roles:
                    admin_count = self.user_repo.count_admin_users()
                    if admin_count == 1:
                        raise ForbiddenException(
                            "No puedes quitarle el rol ADMIN al único administrador del sistema"
                        )

                # Replace roles
                for role in user.roles:
                    self.user_repo.remove_role(user_id, role.role)
                for role in data.roles:
                    self.user_repo.assign_role(user_id, role)

                roles_changed = True

        self.db.commit()

        if roles_changed:
            refresh_token_repo = RefreshTokenRepository(self.db)
            refresh_token_repo.revoke_all_user_tokens(user_id)

        self.db.refresh(user)
        return self._user_to_response(user)

    def deactivate_user(self, user_id: UUID) -> dict:
        """Soft delete user. Protect last ADMIN."""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        if user.soft_deleted_at is not None:
            raise UserNotFoundException()

        # Check last ADMIN protection
        has_admin = any(role.role == "ADMIN" for role in user.roles)
        if has_admin:
            admin_count = self.user_repo.count_admin_users()
            if admin_count == 1:
                raise ForbiddenException("No puedes desactivar al único administrador del sistema")

        admin_repo.soft_delete_user(user_id)

        # Revoke all tokens
        refresh_token_repo = RefreshTokenRepository(self.db)
        refresh_token_repo.revoke_all_user_tokens(user_id)

        return {"message": "Usuario desactivado correctamente"}

    def reactivate_user(self, user_id: UUID) -> AdminUserResponse:
        """Restore soft-deleted user."""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        if user.soft_deleted_at is None:
            raise UserNotFoundException()

        admin_repo.reactivate_user(user_id)
        self.db.refresh(user)
        return self._user_to_response(user)

    def _user_to_response(self, user: User) -> AdminUserResponse:
        """Convert User model to AdminUserResponse"""
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            telefono=user.telefono,
            roles=[role.role for role in user.roles],
            activo=user.soft_deleted_at is None,
            created_at=user.created_at,
            soft_deleted_at=user.soft_deleted_at,
        )

    # ─── Order Management Methods ─────────────────────────────────────────

    def list_orders_admin(
        self,
        page: int = 1,
        size: int = 20,
        estado_codigo: str | None = None,
        fecha_inicio: datetime | None = None,
        fecha_fin: datetime | None = None,
        usuario_id: UUID | None = None,
        monto_min: float | None = None,
        monto_max: float | None = None,
    ) -> AdminOrderListResponse:
        """List orders for admin with pagination and filters"""
        repo = AdminOrderRepository(self.db)
        orders, total = repo.list_orders_admin(
            page=page,
            size=size,
            estado_codigo=estado_codigo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            usuario_id=usuario_id,
            monto_min=monto_min,
            monto_max=monto_max,
        )

        # Convert orders to AdminOrderListItem format
        from app.admin.schemas import AdminOrderListItem

        items = [
            AdminOrderListItem(
                id=order["id"],
                cliente_nombre=order["cliente_nombre"],
                usuario_id=order["usuario_id"],
                estado_codigo=order["estado_codigo"],
                total=float(order["total"]),
                created_at=order["created_at"],
                direccion_calle=order["direccion_calle"],
            )
            for order in orders
        ]

        pages = max(1, (total + size - 1) // size)
        return AdminOrderListResponse(items=items, total=total, page=page, size=size, pages=pages)

    def change_order_state_admin(
        self,
        order_id: UUID,
        request: AdminChangeStateRequest,
        current_user: User,
    ) -> PedidoRead:
        """
        Change order state in admin panel.
        Validates FSM transitions, creates audit entries, handles stock restoration.
        """
        repo = PedidoRepository(self.db)
        pedido = repo.get_by_id(order_id)

        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        # Check if order is in terminal state
        if pedido.estado_codigo in TERMINAL_STATES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El pedido está en un estado terminal ({pedido.estado_codigo}). "
                "No se puede cambiar.",
            )

        # Check if transition is valid
        transitions_from_state = TRANSITIONS.get(pedido.estado_codigo, {})
        if request.nuevo_estado not in transitions_from_state:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transición inválida: {pedido.estado_codigo} → {request.nuevo_estado}",
            )

        # Check role authorization
        transition_info = transitions_from_state[request.nuevo_estado]
        allowed_roles = transition_info["roles"]
        user_roles = [r.role for r in current_user.roles]

        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta transición",
            )

        try:
            # Update order state
            estado_anterior = pedido.estado_codigo
            pedido.estado_codigo = request.nuevo_estado

            # Handle stock restoration if needed
            if transition_info.get("stock_action") == "restore":
                for detalle in pedido.detalles or []:
                    producto = (
                        self.db.query(Producto)
                        .filter(
                            Producto.id == detalle.producto_id,
                            Producto.soft_deleted_at.is_(None),
                        )
                        .with_for_update()
                        .first()
                    )
                    if producto:
                        producto.stock_cantidad += detalle.cantidad

            # Create audit entry
            repo.create_historial(
                pedido_id=pedido.id,
                estado_desde=estado_anterior,
                estado_nuevo=request.nuevo_estado,
                actor_id=current_user.id,
                motivo=request.motivo,
            )

            # Commit transaction
            repo.commit()
            repo.refresh(pedido)

            return PedidoRead(
                id=pedido.id,
                estado_codigo=pedido.estado_codigo,
                subtotal=pedido.subtotal,
                costo_envio=pedido.costo_envio,
                total=pedido.total,
                created_at=pedido.created_at,
            )
        except HTTPException:
            repo.rollback()
            raise
        except Exception as e:
            repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar estado del pedido: {str(e)}",
            )

    # ─── Catalog Management Methods ──────────────────────────────────────

    def list_productos_admin(
        self,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        disponible: bool | None = None,
        eliminado: bool | None = None,
        categoria_id: UUID | None = None,
    ) -> AdminProductoListResponse:
        """List all productos for admin (including soft-deleted)"""
        repo = AdminProductoRepository(self.db)
        skip = (page - 1) * size
        items, total = repo.list_all_admin(
            skip=skip,
            limit=size,
            search=search,
            disponible=disponible,
            eliminado=eliminado,
            categoria_id=categoria_id,
        )
        pages = max(1, (total + size - 1) // size) if size > 0 else 1

        result_items = []
        for p in items:
            categoria_names = [c.nombre for c in p.categorias or []]
            result_items.append(
                AdminProductoListItem(
                    id=p.id,
                    nombre=p.nombre,
                    precio_base=float(p.precio_base),
                    stock_cantidad=p.stock_cantidad,
                    disponible=p.disponible,
                    eliminado=p.soft_deleted_at is not None,
                    soft_deleted_at=p.soft_deleted_at,
                    created_at=p.created_at,
                    categorias=categoria_names,
                )
            )

        return AdminProductoListResponse(
            items=result_items, total=total, page=page, size=size, pages=pages
        )

    def list_categorias_admin(self, eliminado: bool | None = None) -> AdminCategoriaListResponse:
        """List all categorias for admin (including soft-deleted)"""
        repo = AdminCategoriaRepository(self.db)
        items, total = repo.list_all_admin(eliminado=eliminado)

        result_items = [
            AdminCategoriaListItem(
                id=c.id,
                nombre=c.nombre,
                parent_id=c.parent_id,
                eliminado=c.soft_deleted_at is not None,
                soft_deleted_at=c.soft_deleted_at,
                created_at=c.created_at,
            )
            for c in items
        ]

        return AdminCategoriaListResponse(items=result_items, total=total)

    def list_ingredientes_admin(
        self,
        page: int = 1,
        size: int = 20,
        es_alergeno: bool | None = None,
        eliminado: bool | None = None,
    ) -> AdminIngredienteListResponse:
        """List all ingredientes for admin (including soft-deleted)"""
        repo = AdminIngredienteRepository(self.db)
        skip = (page - 1) * size
        items, total = repo.list_all_admin(
            skip=skip, limit=size, es_alergeno=es_alergeno, eliminado=eliminado
        )
        pages = max(1, (total + size - 1) // size) if size > 0 else 1

        result_items = [
            AdminIngredienteListItem(
                id=i.id,
                nombre=i.nombre,
                es_alergeno=i.es_alergeno,
                eliminado=i.soft_deleted_at is not None,
                soft_deleted_at=i.soft_deleted_at,
                created_at=i.created_at,
            )
            for i in items
        ]

        return AdminIngredienteListResponse(
            items=result_items, total=total, page=page, size=size, pages=pages
        )

    # ─── Metrics Methods ─────────────────────────────────────────────────

    def get_metrics_resumen(self) -> MetricsResumenResponse:
        """Return KPIs summary for admin dashboard."""
        data = self.metrics_repo.get_resumen()
        return MetricsResumenResponse(
            total_ventas=data["total_ventas"],
            cantidad_pedidos=data["cantidad_pedidos"],
            pedidos_por_estado=data["pedidos_por_estado"],
            usuarios_registrados=data["usuarios_registrados"],
        )

    def get_metrics_ventas(
        self, fecha_inicio, fecha_fin, granularidad: str
    ) -> MetricsVentasResponse:
        """Return ventas time series with configurable granularity."""
        from datetime import date

        if fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="fecha_inicio debe ser anterior a fecha_fin",
            )

        if (fecha_fin - fecha_inicio).days > 365:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El rango de fechas no puede exceder 365 días",
            )

        if granularidad not in ("day", "week", "month"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="granularidad debe ser day, week o month",
            )

        daily_data = self.metrics_repo.get_ventas_por_periodo(fecha_inicio, fecha_fin)

        if granularidad == "day":
            items = [
                MetricsVentasItem(
                    fecha=d["fecha"],
                    monto_total=d["monto_total"],
                    cantidad_pedidos=d["cantidad_pedidos"],
                )
                for d in daily_data
            ]
            return MetricsVentasResponse(items=items)

        if granularidad == "week":
            from collections import defaultdict

            buckets: dict[str, dict] = defaultdict(
                lambda: {"monto_total": 0.0, "cantidad_pedidos": 0}
            )
            for d in daily_data:
                parsed = date.fromisoformat(d["fecha"])
                iso_year, iso_week, _ = parsed.isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
                buckets[key]["monto_total"] += d["monto_total"]
                buckets[key]["cantidad_pedidos"] += d["cantidad_pedidos"]

            items = [
                MetricsVentasItem(
                    fecha=key,
                    monto_total=round(val["monto_total"], 2),
                    cantidad_pedidos=val["cantidad_pedidos"],
                )
                for key, val in sorted(buckets.items())
            ]
            return MetricsVentasResponse(items=items)

        if granularidad == "month":
            from collections import defaultdict

            buckets: dict[str, dict] = defaultdict(
                lambda: {"monto_total": 0.0, "cantidad_pedidos": 0}
            )
            for d in daily_data:
                parsed = date.fromisoformat(d["fecha"])
                key = parsed.strftime("%Y-%m")
                buckets[key]["monto_total"] += d["monto_total"]
                buckets[key]["cantidad_pedidos"] += d["cantidad_pedidos"]

            items = [
                MetricsVentasItem(
                    fecha=key,
                    monto_total=round(val["monto_total"], 2),
                    cantidad_pedidos=val["cantidad_pedidos"],
                )
                for key, val in sorted(buckets.items())
            ]
            return MetricsVentasResponse(items=items)

    def get_metrics_productos_top(self) -> MetricsProductoTopResponse:
        """Return top 10 products by quantity sold."""
        data = self.metrics_repo.get_productos_top()
        items = [
            MetricsProductoTopItem(
                producto_id=d["producto_id"],
                nombre=d["nombre"],
                cantidad_vendida=d["cantidad_vendida"],
                monto_total=d["monto_total"],
            )
            for d in data
        ]
        return MetricsProductoTopResponse(items=items)

    def get_metrics_pedidos_por_estado(self) -> MetricsPedidosEstadoResponse:
        """Return order distribution by estado with percentages."""
        data = self.metrics_repo.get_pedidos_por_estado()
        total = sum(d["cantidad"] for d in data)

        items = []
        for d in data:
            porcentaje = round((d["cantidad"] / total * 100), 2) if total > 0 else 0.0
            items.append(
                MetricsPedidosEstadoItem(
                    estado=d["estado"],
                    cantidad=d["cantidad"],
                    porcentaje=porcentaje,
                )
            )

        return MetricsPedidosEstadoResponse(items=items)
