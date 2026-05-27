from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.pedido import Pedido


class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_pedido(self, **data) -> Pedido:
        pedido = Pedido(**data)
        self.db.add(pedido)
        self.db.flush()
        return pedido

    def create_detalle(self, **data) -> DetallePedido:
        detalle = DetallePedido(**data)
        self.db.add(detalle)
        self.db.flush()
        return detalle

    def create_historial(self, **data) -> HistorialEstadoPedido:
        historial = HistorialEstadoPedido(**data)
        self.db.add(historial)
        self.db.flush()
        return historial

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)

    def get_by_id(self, id: UUID) -> Pedido | None:
        return (
            self.db.query(Pedido)
            .options(selectinload(Pedido.detalles), selectinload(Pedido.historial))
            .filter(Pedido.id == id, Pedido.soft_deleted_at.is_(None))
            .first()
        )

    def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20, estado_codigo: str | None = None
    ) -> list[Pedido]:
        query = self.db.query(Pedido).filter(
            Pedido.usuario_id == user_id, Pedido.soft_deleted_at.is_(None)
        )
        if estado_codigo:
            query = query.filter(Pedido.estado_codigo == estado_codigo)
        return query.order_by(Pedido.created_at.desc()).offset(skip).limit(limit).all()

    def get_all(
        self, skip: int = 0, limit: int = 20, estado_codigo: str | None = None
    ) -> list[Pedido]:
        query = self.db.query(Pedido).filter(Pedido.soft_deleted_at.is_(None))
        if estado_codigo:
            query = query.filter(Pedido.estado_codigo == estado_codigo)
        return query.order_by(Pedido.created_at.desc()).offset(skip).limit(limit).all()

    def count_by_user(self, user_id: UUID, estado_codigo: str | None = None) -> int:
        query = self.db.query(Pedido).filter(
            Pedido.usuario_id == user_id, Pedido.soft_deleted_at.is_(None)
        )
        if estado_codigo:
            query = query.filter(Pedido.estado_codigo == estado_codigo)
        return query.count()

    def count_all(self, estado_codigo: str | None = None) -> int:
        query = self.db.query(Pedido).filter(Pedido.soft_deleted_at.is_(None))
        if estado_codigo:
            query = query.filter(Pedido.estado_codigo == estado_codigo)
        return query.count()
