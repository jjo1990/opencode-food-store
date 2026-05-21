from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.direccion_entrega import DireccionEntrega


class DireccionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> DireccionEntrega:
        direccion = DireccionEntrega(**data)
        self.db.add(direccion)
        self.db.commit()
        self.db.refresh(direccion)
        return direccion

    def get_by_id(self, id: UUID) -> DireccionEntrega | None:
        return (
            self.db.query(DireccionEntrega)
            .filter(DireccionEntrega.id == id, DireccionEntrega.soft_deleted_at.is_(None))
            .first()
        )

    def get_by_user(self, user_id: UUID) -> list[DireccionEntrega]:
        return (
            self.db.query(DireccionEntrega)
            .filter(
                DireccionEntrega.usuario_id == user_id, DireccionEntrega.soft_deleted_at.is_(None)
            )
            .order_by(DireccionEntrega.es_principal.desc(), DireccionEntrega.created_at.desc())
            .all()
        )

    def get_principal(self, user_id: UUID) -> DireccionEntrega | None:
        return (
            self.db.query(DireccionEntrega)
            .filter(
                DireccionEntrega.usuario_id == user_id,
                DireccionEntrega.es_principal.is_(True),
                DireccionEntrega.soft_deleted_at.is_(None),
            )
            .first()
        )

    def count_active_by_user(self, user_id: UUID) -> int:
        return (
            self.db.query(DireccionEntrega)
            .filter(
                DireccionEntrega.usuario_id == user_id, DireccionEntrega.soft_deleted_at.is_(None)
            )
            .count()
        )

    def update(self, direccion: DireccionEntrega, data: dict) -> DireccionEntrega:
        for key, value in data.items():
            setattr(direccion, key, value)
        self.db.commit()
        self.db.refresh(direccion)
        return direccion

    def soft_delete(self, direccion: DireccionEntrega) -> None:
        direccion.soft_deleted_at = datetime.utcnow()
        self.db.commit()
