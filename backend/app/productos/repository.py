"""
Repository layer for productos
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente


class ProductoRepository:
    """Repository for producto operations"""

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(Producto).filter(Producto.soft_deleted_at.is_(None))

    def create(
        self,
        nombre: str,
        descripcion: str | None,
        precio_base: float,
        stock_cantidad: int,
        disponible: bool,
        imagen_url: str | None,
        categoria_ids: list[UUID],
        ingrediente_ids: list[UUID],
    ) -> Producto:
        """Create a new producto with junction relations"""
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio_base=precio_base,
            stock_cantidad=stock_cantidad,
            disponible=disponible,
            imagen_url=imagen_url,
        )
        self.db.add(producto)
        self.db.flush()

        # Bulk insert junction rows
        for cat_id in categoria_ids:
            self.db.add(ProductoCategoria(producto_id=producto.id, categoria_id=cat_id))

        for ing_id in ingrediente_ids:
            self.db.add(
                ProductoIngrediente(
                    producto_id=producto.id, ingrediente_id=ing_id, es_removible=True
                )
            )

        self.db.commit()
        self.db.refresh(producto)
        return producto

    def get_by_id(self, id: UUID) -> Producto | None:
        """Get producto by ID with eager-loaded relations (excludes soft_deleted)"""
        return (
            self._base_query()
            .options(selectinload(Producto.categorias), selectinload(Producto.ingredientes))
            .filter(Producto.id == id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: UUID | None = None,
        nombre: str | None = None,
        disponible: bool | None = None,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
    ) -> list[Producto]:
        """Get active productos with optional filters, ordered by nombre"""
        query = self._base_query()

        if categoria_id is not None:
            query = query.join(Producto.categorias).filter(Categoria.id == categoria_id)

        if nombre is not None:
            query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))

        if disponible is not None:
            query = query.filter(Producto.disponible == disponible)

        if precio_min is not None:
            query = query.filter(Producto.precio_base >= precio_min)

        if precio_max is not None:
            query = query.filter(Producto.precio_base <= precio_max)

        return query.order_by(Producto.nombre).offset(skip).limit(limit).all()

    def count(
        self,
        categoria_id: UUID | None = None,
        nombre: str | None = None,
        disponible: bool | None = None,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
    ) -> int:
        """Count active productos with optional filters"""
        query = self._base_query()

        if categoria_id is not None:
            query = query.join(Producto.categorias).filter(Categoria.id == categoria_id)

        if nombre is not None:
            query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))

        if disponible is not None:
            query = query.filter(Producto.disponible == disponible)

        if precio_min is not None:
            query = query.filter(Producto.precio_base >= precio_min)

        if precio_max is not None:
            query = query.filter(Producto.precio_base <= precio_max)

        return query.count()

    def update(
        self,
        id: UUID,
        nombre: str | None = None,
        descripcion: str | None = None,
        precio_base: float | None = None,
        stock_cantidad: int | None = None,
        disponible: bool | None = None,
        imagen_url: str | None = None,
        categoria_ids: list[UUID] | None = None,
        ingrediente_ids: list[UUID] | None = None,
    ) -> Producto | None:
        """Update a producto, syncing junction tables if provided"""
        producto = self.get_by_id(id)
        if not producto:
            return None

        if nombre is not None:
            producto.nombre = nombre
        if descripcion is not None:
            producto.descripcion = descripcion
        if precio_base is not None:
            producto.precio_base = precio_base
        if stock_cantidad is not None:
            producto.stock_cantidad = stock_cantidad
        if disponible is not None:
            producto.disponible = disponible
        if imagen_url is not None:
            producto.imagen_url = imagen_url

        # Sync categoria junction
        if categoria_ids is not None:
            self.db.query(ProductoCategoria).filter(ProductoCategoria.producto_id == id).delete()
            for cat_id in categoria_ids:
                self.db.add(ProductoCategoria(producto_id=id, categoria_id=cat_id))

        # Sync ingrediente junction
        if ingrediente_ids is not None:
            self.db.query(ProductoIngrediente).filter(
                ProductoIngrediente.producto_id == id
            ).delete()
            for ing_id in ingrediente_ids:
                self.db.add(
                    ProductoIngrediente(producto_id=id, ingrediente_id=ing_id, es_removible=True)
                )

        producto.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def soft_delete(self, id: UUID) -> None:
        """Soft delete a producto"""
        producto = self.db.query(Producto).filter(Producto.id == id).first()
        if producto:
            producto.soft_deleted_at = datetime.utcnow()
            self.db.commit()

    def toggle_disponibilidad(self, id: UUID, disponible: bool) -> Producto | None:
        """Toggle only the disponible field"""
        producto = self.get_by_id(id)
        if not producto:
            return None

        producto.disponible = disponible
        producto.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def get_ingredientes(self, producto_id: UUID) -> list[ProductoIngrediente]:
        """Get ingredientes for a producto with junction data"""
        return (
            self.db.query(ProductoIngrediente)
            .filter(ProductoIngrediente.producto_id == producto_id)
            .all()
        )
