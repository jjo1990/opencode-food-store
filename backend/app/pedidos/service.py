import json
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.direcciones.repository import DireccionRepository
from app.models import User
from app.models.forma_pago import FormaPago
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.producto import Producto
from app.pedidos.repository import PedidoRepository
from app.pedidos.schemas import (
    CrearPedidoRequest,
    DetallePedidoRead,
    HistorialRead,
    HistorialResponse,
    PedidoDetail,
    PedidoRead,
)
from app.productos.repository import ProductoRepository

TRANSITIONS = {
    "PENDIENTE": {
        "CANCELADO": {"roles": ["CLIENT", "ADMIN", "PEDIDOS"], "stock_action": None},
    },
    "CONFIRMADO": {
        "EN_PREPARACION": {"roles": ["ADMIN", "PEDIDOS"], "stock_action": None},
        "CANCELADO": {"roles": ["CLIENT", "ADMIN", "PEDIDOS"], "stock_action": "restore"},
    },
    "EN_PREPARACION": {
        "EN_CAMINO": {"roles": ["ADMIN", "PEDIDOS"], "stock_action": None},
        "CANCELADO": {"roles": ["ADMIN"], "stock_action": "restore"},
    },
    "EN_CAMINO": {
        "ENTREGADO": {"roles": ["ADMIN", "PEDIDOS"], "stock_action": None},
    },
    "ENTREGADO": {},
    "CANCELADO": {},
}

TERMINAL_STATES = {"ENTREGADO", "CANCELADO"}


class PedidoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PedidoRepository(db)
        self.producto_repo = ProductoRepository(db)
        self.direccion_repo = DireccionRepository(db)

    def crear_pedido(self, user: User, data: CrearPedidoRequest) -> PedidoRead:
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El pedido debe contener al menos un item",
            )

        costo_envio = Decimal("50.00")
        subtotal = Decimal("0")
        detalles_data = []

        for item in data.items:
            producto = (
                self.db.query(Producto)
                .filter(Producto.id == item.producto_id, Producto.soft_deleted_at.is_(None))
                .with_for_update()
                .first()
            )
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Producto {item.producto_id} no encontrado",
                )

            if not producto.disponible:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"El producto {producto.nombre} no está disponible actualmente",
                )

            if producto.stock_cantidad < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Stock insuficiente para {producto.nombre} "
                    f"(disponible: {producto.stock_cantidad}, solicitado: {item.cantidad})",
                )

            ingredientes_ids = {i.id for i in (producto.ingredientes or [])}
            for ing_id in item.personalizacion:
                if ing_id not in ingredientes_ids:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Ingrediente {ing_id} no válido para {producto.nombre}",
                    )

            junction_rows = self.producto_repo.get_ingredientes(producto.id)
            removible_map = {jr.ingrediente_id: jr.es_removible for jr in junction_rows}
            for ing_id in item.personalizacion:
                if ing_id in removible_map and not removible_map[ing_id]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"El ingrediente no se puede remover de {producto.nombre}",
                    )

            item_subtotal = producto.precio_base * item.cantidad
            subtotal += item_subtotal

            detalles_data.append(
                {
                    "producto_id": producto.id,
                    "cantidad": item.cantidad,
                    "precio_snapshot": producto.precio_base,
                    "nombre_snapshot": producto.nombre,
                    "subtotal": item_subtotal,
                    "personalizacion": item.personalizacion if item.personalizacion else None,
                }
            )

        direccion = self.direccion_repo.get_by_id(data.direccion_id)
        if not direccion or direccion.usuario_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Dirección de entrega no encontrada",
            )

        forma_pago = (
            self.db.query(FormaPago).filter(FormaPago.codigo == data.forma_pago_codigo).first()
        )
        if not forma_pago or not forma_pago.habilitado:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Forma de pago no válida o no habilitada",
            )

        total = subtotal + costo_envio

        direccion_snapshot = json.dumps(
            {
                "calle": direccion.calle,
                "numero": direccion.numero,
                "piso": direccion.piso,
                "departamento": direccion.departamento,
                "ciudad": direccion.ciudad,
                "codigo_postal": direccion.codigo_postal,
                "referencia": direccion.referencia,
            },
            ensure_ascii=False,
        )

        try:
            pedido = self.repo.create_pedido(
                usuario_id=user.id,
                estado_codigo="PENDIENTE",
                direccion_id=direccion.id,
                forma_pago_codigo=data.forma_pago_codigo,
                direccion_snapshot=direccion_snapshot,
                subtotal=subtotal,
                costo_envio=costo_envio,
                total=total,
                notas=data.notas,
            )

            for dd in detalles_data:
                self.repo.create_detalle(
                    pedido_id=pedido.id,
                    **dd,
                )

            self.repo.create_historial(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_nuevo="PENDIENTE",
                actor_id=user.id,
                motivo=None,
            )

            self.repo.commit()
            self.repo.refresh(pedido)
        except Exception:
            self.repo.rollback()
            raise

        return PedidoRead(
            id=pedido.id,
            estado_codigo=pedido.estado_codigo,
            subtotal=pedido.subtotal,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            created_at=pedido.created_at,
        )

    def listar_pedidos(
        self, user: User, skip: int = 0, limit: int = 20, estado_codigo: str | None = None
    ) -> dict:
        user_roles = [r.role for r in user.roles]
        is_admin_or_pedidos = any(r in ("ADMIN", "PEDIDOS") for r in user_roles)

        if is_admin_or_pedidos:
            items = self.repo.get_all(skip=skip, limit=limit, estado_codigo=estado_codigo)
            total = self.repo.count_all(estado_codigo=estado_codigo)
        else:
            items = self.repo.get_by_user(
                user_id=user.id, skip=skip, limit=limit, estado_codigo=estado_codigo
            )
            total = self.repo.count_by_user(user_id=user.id, estado_codigo=estado_codigo)

        return {
            "items": [self._to_list_read(p) for p in items],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def _to_list_read(self, p) -> dict:
        from app.pedidos.schemas import PedidoListRead

        return PedidoListRead(
            id=p.id,
            estado_codigo=p.estado_codigo,
            subtotal=p.subtotal,
            costo_envio=p.costo_envio,
            total=p.total,
            created_at=p.created_at,
        ).model_dump()

    def obtener_pedido(self, user: User, pedido_id: UUID) -> PedidoDetail:
        pedido = self.repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        user_roles = [r.role for r in user.roles]
        is_admin_or_pedidos = any(r in ("ADMIN", "PEDIDOS") for r in user_roles)

        if not is_admin_or_pedidos and pedido.usuario_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        return PedidoDetail(
            id=pedido.id,
            estado_codigo=pedido.estado_codigo,
            subtotal=pedido.subtotal,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            created_at=pedido.created_at,
            items=[
                DetallePedidoRead(
                    id=d.id,
                    producto_id=d.producto_id,
                    nombre_snapshot=d.nombre_snapshot,
                    precio_snapshot=d.precio_snapshot,
                    cantidad=d.cantidad,
                    subtotal=d.subtotal,
                    personalizacion=d.personalizacion,
                )
                for d in (pedido.detalles or [])
            ],
            historial=[
                HistorialRead(
                    estado_desde=h.estado_desde,
                    estado_nuevo=h.estado_nuevo,
                    actor_id=h.actor_id,
                    motivo=h.motivo,
                    created_at=h.created_at,
                )
                for h in sorted((pedido.historial or []), key=lambda x: x.created_at)
            ],
        )

    def avanzar_estado(
        self, current_user: User, pedido_id: UUID, nuevo_estado: str, motivo: str | None = None
    ) -> PedidoRead:
        pedido = self.repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        estado_actual = pedido.estado_codigo

        if estado_actual in TERMINAL_STATES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El pedido está en un estado terminal ({estado_actual}). No se puede cambiar.",
            )

        estado_transitions = TRANSITIONS.get(estado_actual, {})
        if nuevo_estado not in estado_transitions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transición inválida: {estado_actual} → {nuevo_estado}",
            )

        transition_info = estado_transitions[nuevo_estado]
        user_roles = [r.role for r in current_user.roles]
        is_admin = "ADMIN" in user_roles

        if not is_admin and pedido.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        allowed_roles = transition_info["roles"]
        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta transición",
            )

        try:
            estado_anterior = estado_actual
            pedido.estado_codigo = nuevo_estado

            if transition_info.get("stock_action") == "restore":
                for detalle in pedido.detalles or []:
                    producto = (
                        self.db.query(Producto)
                        .filter(
                            Producto.id == detalle.producto_id, Producto.soft_deleted_at.is_(None)
                        )
                        .with_for_update()
                        .first()
                    )
                    if producto:
                        producto.stock_cantidad += detalle.cantidad

            self.repo.create_historial(
                pedido_id=pedido.id,
                estado_desde=estado_anterior,
                estado_nuevo=nuevo_estado,
                actor_id=current_user.id,
                motivo=motivo,
            )

            self.repo.commit()
            self.repo.refresh(pedido)

            return PedidoRead(
                id=pedido.id,
                estado_codigo=pedido.estado_codigo,
                subtotal=pedido.subtotal,
                costo_envio=pedido.costo_envio,
                total=pedido.total,
                created_at=pedido.created_at,
            )
        except HTTPException:
            self.repo.rollback()
            raise
        except Exception:
            self.repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al avanzar estado del pedido",
            )

    def obtener_historial(self, current_user: User, pedido_id: UUID) -> list[HistorialResponse]:
        from app.models.user import User as UserModel

        pedido = self.repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        user_roles = [r.role for r in current_user.roles]
        is_admin_or_pedidos = any(r in ("ADMIN", "PEDIDOS") for r in user_roles)
        if not is_admin_or_pedidos and pedido.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        results = (
            self.db.query(HistorialEstadoPedido, UserModel.full_name)
            .outerjoin(UserModel, HistorialEstadoPedido.actor_id == UserModel.id)
            .filter(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
            .all()
        )

        historial = []
        for entry, actor_name in results:
            historial.append(
                HistorialResponse(
                    estado_desde=entry.estado_desde,
                    estado_nuevo=entry.estado_nuevo,
                    actor_id=entry.actor_id,
                    actor_nombre=actor_name if actor_name else "SISTEMA",
                    motivo=entry.motivo,
                    created_at=entry.created_at,
                )
            )

        return historial
