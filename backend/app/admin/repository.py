"""
Repository layer for admin user management
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.models.pedido import Pedido


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
            query.order_by(Pedido.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
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
