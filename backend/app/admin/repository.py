"""
Repository layer for admin user management and metrics
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.models.categoria import Categoria
from app.models.detalle_pedido import DetallePedido
from app.models.ingrediente import Ingrediente
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria


class AdminUserRepository:
    """Repository for admin user operations"""

    def __init__(self, db: Session):
        self.db = db

    def list_users(
        self,
        page: int = 1,
        size: int = 20,
        rol: str | None = None,
        search: str | None = None,
        estado: str = "activo",
    ) -> tuple[list[User], int]:
        """List users with pagination and filters"""
        query = self.db.query(User)

        if estado == "activo":
            query = query.filter(User.soft_deleted_at.is_(None))
        elif estado == "inactivo":
            query = query.filter(User.soft_deleted_at.isnot(None))

        if rol:
            query = query.join(UserRole).filter(UserRole.role == rol)

        if search:
            pattern = f"%{search}%"
            query = query.filter(User.email.ilike(pattern) | User.full_name.ilike(pattern))

        if rol:
            query = query.distinct()

        total = query.count()

        users = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()

        return users, total

    def get_user_by_id_including_deleted(self, user_id: UUID) -> User | None:
        """Get user by ID including soft-deleted"""
        return self.db.query(User).filter(User.id == user_id).first()

    def soft_delete_user(self, user_id: UUID) -> bool:
        """Mark user as soft-deleted. Returns True if affected."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.soft_deleted_at is not None:
            return False
        user.soft_deleted_at = datetime.utcnow()
        self.db.commit()
        return True

    def reactivate_user(self, user_id: UUID) -> bool:
        """Restore soft-deleted user. Returns True if affected."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.soft_deleted_at is None:
            return False
        user.soft_deleted_at = None
        self.db.commit()
        return True


class AdminOrderRepository:
    """Repository for admin order operations"""

    def __init__(self, db: Session):
        self.db = db

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
    ) -> tuple[list[dict], int]:
        """
        List orders for admin with pagination and filters.
        Joins User table for client names and DireccionEntrega for address.
        Returns tuple of (list of order dicts with cliente_nombre and direccion_calle, total_count)
        """
        from app.models.direccion_entrega import DireccionEntrega

        query = (
            self.db.query(
                Pedido.id,
                Pedido.usuario_id,
                Pedido.estado_codigo,
                Pedido.total,
                Pedido.created_at,
                User.full_name.label("cliente_nombre"),
                DireccionEntrega.calle.label("direccion_calle"),
            )
            .join(User, Pedido.usuario_id == User.id)
            .outerjoin(DireccionEntrega, Pedido.direccion_id == DireccionEntrega.id)
            .filter(Pedido.soft_deleted_at.is_(None))
        )

        # Apply filters
        if estado_codigo:
            query = query.filter(Pedido.estado_codigo == estado_codigo)

        if fecha_inicio:
            query = query.filter(Pedido.created_at >= fecha_inicio)

        if fecha_fin:
            query = query.filter(Pedido.created_at <= fecha_fin)

        if usuario_id:
            query = query.filter(Pedido.usuario_id == usuario_id)

        if monto_min is not None:
            query = query.filter(Pedido.total >= monto_min)

        if monto_max is not None:
            query = query.filter(Pedido.total <= monto_max)

        # Get total count before pagination
        total = query.count()

        # Apply ordering and pagination
        results = (
            query.order_by(Pedido.created_at.desc()).offset((page - 1) * size).limit(size).all()
        )

        # Convert to dict for flexible response building
        orders = []
        for row in results:
            orders.append(
                {
                    "id": row.id,
                    "usuario_id": row.usuario_id,
                    "cliente_nombre": row.cliente_nombre,
                    "estado_codigo": row.estado_codigo,
                    "total": row.total,
                    "created_at": row.created_at,
                    "direccion_calle": row.direccion_calle,
                }
            )

        return orders, total


class AdminProductoRepository:
    """Repository for admin producto operations — no soft_delete filter"""

    def __init__(self, db: Session):
        self.db = db

    def list_all_admin(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        disponible: bool | None = None,
        eliminado: bool | None = None,
        categoria_id: UUID | None = None,
    ) -> tuple[list[Producto], int]:
        """List ALL productos (including soft-deleted) with filters and pagination"""
        query = self.db.query(Producto)

        if eliminado is True:
            query = query.filter(Producto.soft_deleted_at.isnot(None))
        elif eliminado is False:
            query = query.filter(Producto.soft_deleted_at.is_(None))

        if disponible is not None:
            query = query.filter(Producto.disponible == disponible)

        if search:
            query = query.filter(Producto.nombre.ilike(f"%{search}%"))

        if categoria_id is not None:
            query = query.join(ProductoCategoria).filter(
                ProductoCategoria.categoria_id == categoria_id
            )

        total = query.count()
        items = query.order_by(Producto.nombre).offset(skip).limit(limit).all()
        return items, total


class AdminCategoriaRepository:
    """Repository for admin categoria operations — no soft_delete filter"""

    def __init__(self, db: Session):
        self.db = db

    def list_all_admin(self, eliminado: bool | None = None) -> tuple[list[Categoria], int]:
        """List ALL categorias (including soft-deleted) with optional filter"""
        query = self.db.query(Categoria)

        if eliminado is True:
            query = query.filter(Categoria.soft_deleted_at.isnot(None))
        elif eliminado is False:
            query = query.filter(Categoria.soft_deleted_at.is_(None))

        total = query.count()
        items = query.order_by(Categoria.nombre).all()
        return items, total


class AdminIngredienteRepository:
    """Repository for admin ingrediente operations — no soft_delete filter"""

    def __init__(self, db: Session):
        self.db = db

    def list_all_admin(
        self,
        skip: int = 0,
        limit: int = 20,
        es_alergeno: bool | None = None,
        eliminado: bool | None = None,
    ) -> tuple[list[Ingrediente], int]:
        """List ALL ingredientes (including soft-deleted) with filters and pagination"""
        query = self.db.query(Ingrediente)

        if eliminado is True:
            query = query.filter(Ingrediente.soft_deleted_at.isnot(None))
        elif eliminado is False:
            query = query.filter(Ingrediente.soft_deleted_at.is_(None))

        if es_alergeno is not None:
            query = query.filter(Ingrediente.es_alergeno == es_alergeno)

        total = query.count()
        items = query.order_by(Ingrediente.nombre).offset(skip).limit(limit).all()
        return items, total


class AdminMetricsRepository:
    """Repository for admin dashboard metrics — aggregation queries"""

    def __init__(self, db: Session):
        self.db = db

    def get_resumen(self) -> dict:
        """Return dict with 4 KPIs: total_ventas, cantidad_pedidos, pedidos_por_estado, usuarios_registrados."""
        total_ventas = (
            self.db.query(func.coalesce(func.sum(Pedido.total), 0))
            .filter(Pedido.soft_deleted_at.is_(None))
            .scalar()
        )

        cantidad_pedidos = (
            self.db.query(func.count(Pedido.id)).filter(Pedido.soft_deleted_at.is_(None)).scalar()
        )

        pedidos_por_estado_rows = (
            self.db.query(Pedido.estado_codigo, func.count(Pedido.id))
            .filter(Pedido.soft_deleted_at.is_(None))
            .group_by(Pedido.estado_codigo)
            .all()
        )
        pedidos_por_estado = {row[0]: row[1] for row in pedidos_por_estado_rows}

        usuarios_registrados = (
            self.db.query(func.count(User.id)).filter(User.soft_deleted_at.is_(None)).scalar()
        )

        return {
            "total_ventas": float(total_ventas or 0),
            "cantidad_pedidos": cantidad_pedidos or 0,
            "pedidos_por_estado": pedidos_por_estado,
            "usuarios_registrados": usuarios_registrados or 0,
        }

    def get_ventas_por_periodo(self, fecha_inicio, fecha_fin) -> list[dict]:
        """Return list of dicts with daily ventas aggregation in [fecha_inicio, fecha_fin]."""
        rows = (
            self.db.query(
                func.date(Pedido.created_at).label("fecha"),
                func.sum(Pedido.total).label("monto_total"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .filter(
                Pedido.soft_deleted_at.is_(None),
                func.date(Pedido.created_at) >= fecha_inicio,
                func.date(Pedido.created_at) <= fecha_fin,
            )
            .group_by(func.date(Pedido.created_at))
            .order_by(func.date(Pedido.created_at))
            .all()
        )

        return [
            {
                "fecha": str(row.fecha),
                "monto_total": float(row.monto_total or 0),
                "cantidad_pedidos": row.cantidad_pedidos or 0,
            }
            for row in rows
        ]

    def get_productos_top(self, limit: int = 10) -> list[dict]:
        """Return top N products by quantity sold, joined with Pedido for soft-delete filter."""
        rows = (
            self.db.query(
                DetallePedido.producto_id,
                DetallePedido.nombre_snapshot.label("nombre"),
                func.sum(DetallePedido.cantidad).label("cantidad_vendida"),
                func.sum(DetallePedido.subtotal).label("monto_total"),
            )
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .filter(Pedido.soft_deleted_at.is_(None))
            .group_by(DetallePedido.producto_id, DetallePedido.nombre_snapshot)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "producto_id": row.producto_id,
                "nombre": row.nombre,
                "cantidad_vendida": row.cantidad_vendida or 0,
                "monto_total": float(row.monto_total or 0),
            }
            for row in rows
        ]

    def get_pedidos_por_estado(self) -> list[dict]:
        """Return list of dicts with order count grouped by estado_codigo."""
        rows = (
            self.db.query(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad"),
            )
            .filter(Pedido.soft_deleted_at.is_(None))
            .group_by(Pedido.estado_codigo)
            .all()
        )

        return [{"estado": row[0], "cantidad": row[1]} for row in rows]


class AdminConfigRepository:
    """Repository for system configuration key-value store"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        from app.models.system_config import SystemConfig
        from app.models.user import User

        return (
            self.db.query(SystemConfig, User.full_name.label("updated_by_name"))
            .outerjoin(User, SystemConfig.updated_by == User.id)
            .all()
        )

    def get_by_key(self, clave: str):
        from app.models.system_config import SystemConfig

        return self.db.query(SystemConfig).filter(SystemConfig.clave == clave).first()

    def upsert(self, clave: str, valor: str, updated_by: UUID | None = None):
        from app.models.system_config import SystemConfig

        existing = self.get_by_key(clave)
        if existing:
            existing.valor = valor
            existing.updated_by = updated_by
            existing.updated_at = datetime.utcnow()
        else:
            new_row = SystemConfig(
                clave=clave, valor=valor, updated_by=updated_by, updated_at=datetime.utcnow()
            )
            self.db.add(new_row)
        self.db.commit()
        return self.get_by_key(clave)
