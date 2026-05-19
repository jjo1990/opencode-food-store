"""
Service layer for ingredientes
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ingredientes.repository import IngredienteRepository
from app.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteResponse,
    IngredienteUpdate,
    PaginatedIngredientes,
)


class IngredienteNotFoundException(HTTPException):
    """Raised when ingrediente is not found"""

    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")


class IngredienteDuplicateException(HTTPException):
    """Raised when ingrediente nombre already exists"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail="Ya existe un ingrediente con ese nombre"
        )


class IngredienteService:
    """Service for ingrediente operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = IngredienteRepository(db)

    def _to_response(self, ing) -> IngredienteResponse:
        return IngredienteResponse(
            id=ing.id,
            nombre=ing.nombre,
            es_alergeno=ing.es_alergeno,
            created_at=ing.created_at,
        )

    def create_ingrediente(self, data: IngredienteCreate) -> IngredienteResponse:
        """Create a new ingrediente"""
        if self.repo.exists_by_nombre(data.nombre):
            raise IngredienteDuplicateException()

        ing = self.repo.create(nombre=data.nombre, es_alergeno=data.es_alergeno)
        return self._to_response(ing)

    def list_ingredientes(
        self,
        skip: int = 0,
        limit: int = 20,
        es_alergeno: bool | None = None,
    ) -> PaginatedIngredientes:
        """List ingredientes with pagination and optional allergen filter"""
        items = self.repo.get_all_active(skip=skip, limit=limit, es_alergeno=es_alergeno)
        total = self.repo.count(es_alergeno=es_alergeno)

        return PaginatedIngredientes(
            items=[self._to_response(i) for i in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    def get_ingrediente(self, id: UUID) -> IngredienteResponse:
        """Get a single ingrediente by ID"""
        ing = self.repo.get_by_id(id)
        if not ing:
            raise IngredienteNotFoundException()
        return self._to_response(ing)

    def update_ingrediente(self, id: UUID, data: IngredienteUpdate) -> IngredienteResponse:
        """Update an ingrediente"""
        ing = self.repo.get_by_id(id)
        if not ing:
            raise IngredienteNotFoundException()

        if data.nombre is not None and data.nombre != ing.nombre:
            if self.repo.exists_by_nombre(data.nombre):
                raise IngredienteDuplicateException()

        ing = self.repo.update(
            id=id,
            nombre=data.nombre,
            es_alergeno=data.es_alergeno,
        )
        return self._to_response(ing)

    def delete_ingrediente(self, id: UUID) -> None:
        """Soft delete an ingrediente"""
        ing = self.repo.get_by_id(id)
        if not ing:
            raise IngredienteNotFoundException()

        self.repo.soft_delete(id)
