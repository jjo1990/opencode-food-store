"""
Repository layer for categorias
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.categoria import Categoria


class CategoriaRepository:
    """Repository for categoria operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nombre: str, parent_id: UUID | None = None) -> Categoria:
        """Create a new categoria"""
        categoria = Categoria(
            nombre=nombre,
            parent_id=parent_id,
        )
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def get_by_id(self, id: UUID) -> Categoria | None:
        """Get categoria by ID (excludes soft_deleted)"""
        return (
            self.db.query(Categoria)
            .filter(
                Categoria.id == id,
                Categoria.soft_deleted_at.is_(None),
            )
            .first()
        )

    def get_all_active(self) -> list[Categoria]:
        """Get all active categorias ordered by nombre"""
        return (
            self.db.query(Categoria)
            .filter(
                Categoria.soft_deleted_at.is_(None),
            )
            .order_by(Categoria.nombre)
            .all()
        )

    def get_immediate_children(self, parent_id: UUID) -> list[Categoria]:
        """Get active children of a categoria"""
        return (
            self.db.query(Categoria)
            .filter(
                Categoria.parent_id == parent_id,
                Categoria.soft_deleted_at.is_(None),
            )
            .order_by(Categoria.nombre)
            .all()
        )

    def exists_by_name_at_level(self, nombre: str, parent_id: UUID | None) -> bool:
        """Check if a categoria with same nombre exists at same level"""
        return (
            self.db.query(Categoria)
            .filter(
                Categoria.nombre == nombre,
                Categoria.parent_id == parent_id,
                Categoria.soft_deleted_at.is_(None),
            )
            .first()
            is not None
        )

    def has_active_children(self, id: UUID) -> bool:
        """Check if categoria has active children"""
        return (
            self.db.query(Categoria)
            .filter(
                Categoria.parent_id == id,
                Categoria.soft_deleted_at.is_(None),
            )
            .first()
            is not None
        )

    def update(
        self,
        id: UUID,
        nombre: str | None = None,
        parent_id: UUID | None = None,
    ) -> Categoria:
        """Update a categoria"""
        categoria = self.get_by_id(id)
        if not categoria:
            return None

        if nombre is not None:
            categoria.nombre = nombre
        if parent_id is not None:
            categoria.parent_id = parent_id

        categoria.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def soft_delete(self, id: UUID) -> None:
        """Soft delete a categoria"""
        categoria = self.db.query(Categoria).filter(Categoria.id == id).first()
        if categoria:
            categoria.soft_deleted_at = datetime.utcnow()
            self.db.commit()

    def get_tree(self) -> list[dict]:
        """Build the full category tree using adjacency list approach

        Gets all active categories, builds a parent→children map,
        then recurses from root (parent_id IS NULL) to build the tree.
        """
        all_categories = self.get_all_active()

        # Build adjacency list: parent_id → [children]
        children_map: dict[UUID | None, list[Categoria]] = {}
        for cat in all_categories:
            parent_key = cat.parent_id
            if parent_key not in children_map:
                children_map[parent_key] = []
            children_map[parent_key].append(cat)

        def _build_node(cat: Categoria) -> dict:
            node = {
                "id": cat.id,
                "nombre": cat.nombre,
                "parent_id": cat.parent_id,
                "children": [],
            }
            child_cats = children_map.get(cat.id, [])
            if child_cats:
                node["children"] = [_build_node(c) for c in child_cats]
            return node

        # Root nodes are those with parent_id IS NULL
        root_cats = children_map.get(None, [])
        return [_build_node(cat) for cat in root_cats]
