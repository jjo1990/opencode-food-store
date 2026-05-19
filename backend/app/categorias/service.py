"""
Service layer for categorias
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.categorias.repository import CategoriaRepository
from app.categorias.schemas import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaTreeNode,
    CategoriaUpdate,
)


class CategoriaNotFoundException(HTTPException):
    """Raised when categoria is not found"""

    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")


class CategoriaDuplicateException(HTTPException):
    """Raised when categoria nombre already exists at same level"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría con ese nombre en el mismo nivel",
        )


class CategoriaCycleException(HTTPException):
    """Raised when moving categoria would create a cycle"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede mover: crearía un ciclo en la jerarquía",
        )


class CategoriaSelfParentException(HTTPException):
    """Raised when categoria is set as its own parent"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Una categoría no puede ser su propio padre",
        )


class CategoriaHasChildrenException(HTTPException):
    """Raised when deleting categoria that has active children"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la categoría tiene subcategorías activas",
        )


class CategoriaService:
    """Service for categoria operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoriaRepository(db)

    def _to_response(self, cat) -> CategoriaResponse:
        return CategoriaResponse(
            id=cat.id,
            nombre=cat.nombre,
            parent_id=cat.parent_id,
            created_at=cat.created_at,
        )

    def create_categoria(self, data: CategoriaCreate) -> CategoriaResponse:
        """Create a new categoria"""
        # Validate no duplicate at same level
        if self.repo.exists_by_name_at_level(data.nombre, data.parent_id):
            raise CategoriaDuplicateException()

        # If parent_id given, verify parent exists and is active
        if data.parent_id is not None:
            parent = self.repo.get_by_id(data.parent_id)
            if not parent:
                raise CategoriaNotFoundException()

        cat = self.repo.create(nombre=data.nombre, parent_id=data.parent_id)
        return self._to_response(cat)

    def get_tree(self) -> list[CategoriaTreeNode]:
        """Get full hierarchical tree"""
        tree_data = self.repo.get_tree()

        def _build_node(node_data: dict) -> CategoriaTreeNode:
            return CategoriaTreeNode(
                id=node_data["id"],
                nombre=node_data["nombre"],
                parent_id=node_data["parent_id"],
                children=[_build_node(c) for c in node_data.get("children", [])],
            )

        return [_build_node(n) for n in tree_data]

    def get_categoria(self, id: UUID) -> CategoriaResponse:
        """Get a single categoria by ID"""
        cat = self.repo.get_by_id(id)
        if not cat:
            raise CategoriaNotFoundException()
        return self._to_response(cat)

    def update_categoria(self, id: UUID, data: CategoriaUpdate) -> CategoriaResponse:
        """Update a categoria"""
        cat = self.repo.get_by_id(id)
        if not cat:
            raise CategoriaNotFoundException()

        # If changing parent_id, validate
        if data.parent_id is not None and data.parent_id != cat.parent_id:
            # Self-reference check
            if data.parent_id == id:
                raise CategoriaSelfParentException()

            # Cycle check: walk up from new parent to ensure we don't reach current node
            current = self.repo.get_by_id(data.parent_id)
            if not current:
                raise CategoriaNotFoundException()
            visited = {id}
            while current is not None:
                if current.id in visited:
                    raise CategoriaCycleException()
                visited.add(current.id)
                if current.parent_id is None:
                    break
                current = self.repo.get_by_id(current.parent_id)

        # If changing nombre, validate no duplicate at same level
        new_parent_id = data.parent_id if data.parent_id is not None else cat.parent_id
        if data.nombre is not None and data.nombre != cat.nombre:
            if self.repo.exists_by_name_at_level(data.nombre, new_parent_id):
                raise CategoriaDuplicateException()

        cat = self.repo.update(
            id=id,
            nombre=data.nombre,
            parent_id=data.parent_id,
        )
        return self._to_response(cat)

    def delete_categoria(self, id: UUID) -> None:
        """Soft delete a categoria"""
        cat = self.repo.get_by_id(id)
        if not cat:
            raise CategoriaNotFoundException()

        if self.repo.has_active_children(id):
            raise CategoriaHasChildrenException()

        self.repo.soft_delete(id)
