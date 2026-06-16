"""
Service layer for productos
"""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.categorias.repository import CategoriaRepository
from app.ingredientes.repository import IngredienteRepository
from app.productos.repository import ProductoRepository
from app.productos.schemas import (
    CategoriaEnProducto,
    IngredienteEnProducto,
    PaginatedProductos,
    ProductoCreate,
    ProductoDetail,
    ProductoDisponibilidadUpdate,
    ProductoResponse,
    ProductoUpdate,
    PublicPaginatedProductos,
    PublicProductoDetail,
    PublicProductoResponse,
)


class ProductoNotFoundException(HTTPException):
    """Raised when producto is not found"""

    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")


class ProductoValidationException(HTTPException):
    """Raised when producto data is invalid"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ProductoService:
    """Service for producto operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductoRepository(db)
        self.categoria_repo = CategoriaRepository(db)
        self.ingrediente_repo = IngredienteRepository(db)

    def _to_response(self, p) -> ProductoResponse:
        return ProductoResponse(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio_base=p.precio_base,
            stock_cantidad=p.stock_cantidad,
            disponible=p.disponible,
            imagen_url=p.imagen_url,
            created_at=p.created_at,
        )

    def _to_detail(self, p) -> ProductoDetail:
        return ProductoDetail(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio_base=p.precio_base,
            stock_cantidad=p.stock_cantidad,
            disponible=p.disponible,
            imagen_url=p.imagen_url,
            created_at=p.created_at,
            categorias=[CategoriaEnProducto(id=c.id, nombre=c.nombre) for c in p.categorias or []],
            ingredientes=[
                IngredienteEnProducto(
                    id=i.id,
                    nombre=i.nombre,
                    es_alergeno=i.es_alergeno,
                    es_removible=True,
                )
                for i in p.ingredientes or []
            ],
        )

    def _validate_categorias(self, categoria_ids: list[UUID]) -> None:
        """Validate that all categoria_ids exist"""
        for cat_id in categoria_ids:
            cat = self.categoria_repo.get_by_id(cat_id)
            if not cat:
                raise ProductoValidationException(f"Categoría con ID {cat_id} no encontrada")

    def _validate_ingredientes(self, ingrediente_ids: list[UUID]) -> None:
        """Validate that all ingrediente_ids exist"""
        for ing_id in ingrediente_ids:
            ing = self.ingrediente_repo.get_by_id(ing_id)
            if not ing:
                raise ProductoValidationException(f"Ingrediente con ID {ing_id} no encontrado")

    def create_producto(self, data: ProductoCreate) -> ProductoDetail:
        """Create a new producto"""
        if data.categoria_ids:
            self._validate_categorias(data.categoria_ids)

        if data.ingrediente_ids:
            self._validate_ingredientes(data.ingrediente_ids)

        p = self.repo.create(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio_base=data.precio_base,
            stock_cantidad=data.stock_cantidad,
            disponible=data.disponible,
            imagen_url=data.imagen_url,
            categoria_ids=data.categoria_ids,
            ingrediente_ids=data.ingrediente_ids,
        )
        return self._to_detail(p)

    def list_productos(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: UUID | None = None,
        nombre: str | None = None,
        disponible: bool | None = None,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
        is_public: bool = False,
        include_deleted: bool = False,
    ) -> PaginatedProductos | PublicPaginatedProductos:
        """List productos with pagination and optional filters"""
        if is_public:
            disponible = True

        items = self.repo.get_all(
            skip=skip,
            limit=limit,
            categoria_id=categoria_id,
            nombre=nombre,
            disponible=disponible,
            precio_min=precio_min,
            precio_max=precio_max,
            include_deleted=include_deleted,
        )
        total = self.repo.count(
            categoria_id=categoria_id,
            nombre=nombre,
            disponible=disponible,
            precio_min=precio_min,
            precio_max=precio_max,
            include_deleted=include_deleted,
        )

        if is_public:
            return PublicPaginatedProductos(
                items=[self._to_public_response(p) for p in items],
                total=total,
                skip=skip,
                limit=limit,
            )

        return PaginatedProductos(
            items=[self._to_response(p) for p in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    def get_producto(self, id: UUID) -> ProductoDetail:
        """Get a single producto by ID with relations"""
        p = self.repo.get_by_id(id)
        if not p:
            raise ProductoNotFoundException()

        return self._to_detail(p)

    def _to_public_response(self, p) -> PublicProductoResponse:
        return PublicProductoResponse(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio_base=p.precio_base,
            disponible=p.disponible,
            imagen_url=p.imagen_url,
            created_at=p.created_at,
        )

    def _to_public_detail(self, p) -> PublicProductoDetail:
        return PublicProductoDetail(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio_base=p.precio_base,
            disponible=p.disponible,
            imagen_url=p.imagen_url,
            created_at=p.created_at,
            categorias=[CategoriaEnProducto(id=c.id, nombre=c.nombre) for c in p.categorias or []],
            ingredientes=[
                IngredienteEnProducto(
                    id=i.id,
                    nombre=i.nombre,
                    es_alergeno=i.es_alergeno,
                    es_removible=True,
                )
                for i in p.ingredientes or []
            ],
        )

    def get_producto_public(self, id: UUID) -> PublicProductoDetail:
        """Get a single public producto by ID (only if disponible)"""
        p = self.repo.get_by_id(id)
        if not p or not p.disponible:
            raise ProductoNotFoundException()
        return self._to_public_detail(p)

    def update_producto(self, id: UUID, data: ProductoUpdate) -> ProductoDetail:
        """Update a producto"""
        p = self.repo.get_by_id(id)
        if not p:
            raise ProductoNotFoundException()

        if data.categoria_ids is not None:
            self._validate_categorias(data.categoria_ids)

        if data.ingrediente_ids is not None:
            self._validate_ingredientes(data.ingrediente_ids)

        p = self.repo.update(
            id=id,
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio_base=data.precio_base,
            stock_cantidad=data.stock_cantidad,
            disponible=data.disponible,
            imagen_url=data.imagen_url,
            categoria_ids=data.categoria_ids,
            ingrediente_ids=data.ingrediente_ids,
        )
        return self._to_detail(p)

    def toggle_disponibilidad(
        self, id: UUID, data: ProductoDisponibilidadUpdate
    ) -> ProductoResponse:
        """Toggle producto disponibilidad"""
        p = self.repo.get_by_id(id)
        if not p:
            raise ProductoNotFoundException()

        p = self.repo.toggle_disponibilidad(id=id, disponible=data.disponible)
        return self._to_response(p)

    def delete_producto(self, id: UUID) -> None:
        """Soft delete a producto"""
        p = self.repo.get_by_id(id)
        if not p:
            raise ProductoNotFoundException()

        self.repo.soft_delete(id)

    def get_ingredientes(self, producto_id: UUID) -> list[IngredienteEnProducto]:
        """Get ingredients for a producto with es_removible flag"""
        p = self.repo.get_by_id(producto_id)
        if not p:
            raise ProductoNotFoundException()

        junction_rows = self.repo.get_ingredientes(producto_id)
        removible_map = {jr.ingrediente_id: jr.es_removible for jr in junction_rows}

        result = []
        for ing in p.ingredientes or []:
            result.append(
                IngredienteEnProducto(
                    id=ing.id,
                    nombre=ing.nombre,
                    es_alergeno=ing.es_alergeno,
                    es_removible=removible_map.get(ing.id, True),
                )
            )
        return result
