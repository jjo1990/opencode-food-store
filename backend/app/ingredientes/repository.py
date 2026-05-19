"""
Repository layer for ingredientes
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ingrediente import Ingrediente


class IngredienteRepository:
    """Repository for ingrediente operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nombre: str, es_alergeno: bool = False) -> Ingrediente:
        """Create a new ingrediente"""
        ingrediente = Ingrediente(
            nombre=nombre,
            es_alergeno=es_alergeno,
        )
        self.db.add(ingrediente)
        self.db.commit()
        self.db.refresh(ingrediente)
        return ingrediente

    def get_by_id(self, id: UUID) -> Ingrediente | None:
        """Get ingrediente by ID (excludes soft_deleted)"""
        return (
            self.db.query(Ingrediente)
            .filter(
                Ingrediente.id == id,
                Ingrediente.soft_deleted_at.is_(None),
            )
            .first()
        )

    def get_all_active(
        self,
        skip: int = 0,
        limit: int = 20,
        es_alergeno: bool | None = None,
    ) -> list[Ingrediente]:
        """Get active ingredientes with optional allergen filter, ordered by nombre"""
        query = self.db.query(Ingrediente).filter(
            Ingrediente.soft_deleted_at.is_(None),
        )
        if es_alergeno is not None:
            query = query.filter(Ingrediente.es_alergeno == es_alergeno)
        return query.order_by(Ingrediente.nombre).offset(skip).limit(limit).all()

    def count(self, es_alergeno: bool | None = None) -> int:
        """Count active ingredientes with optional allergen filter"""
        query = self.db.query(Ingrediente).filter(
            Ingrediente.soft_deleted_at.is_(None),
        )
        if es_alergeno is not None:
            query = query.filter(Ingrediente.es_alergeno == es_alergeno)
        return query.count()

    def exists_by_nombre(self, nombre: str) -> bool:
        """Check if an ingrediente with the same nombre exists (excludes soft_deleted)"""
        return (
            self.db.query(Ingrediente)
            .filter(
                Ingrediente.nombre == nombre,
                Ingrediente.soft_deleted_at.is_(None),
            )
            .first()
            is not None
        )

    def update(
        self,
        id: UUID,
        nombre: str | None = None,
        es_alergeno: bool | None = None,
    ) -> Ingrediente | None:
        """Update an ingrediente"""
        ingrediente = self.get_by_id(id)
        if not ingrediente:
            return None

        if nombre is not None:
            ingrediente.nombre = nombre
        if es_alergeno is not None:
            ingrediente.es_alergeno = es_alergeno

        ingrediente.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ingrediente)
        return ingrediente

    def soft_delete(self, id: UUID) -> None:
        """Soft delete an ingrediente"""
        ingrediente = self.db.query(Ingrediente).filter(Ingrediente.id == id).first()
        if ingrediente:
            ingrediente.soft_deleted_at = datetime.utcnow()
            self.db.commit()
