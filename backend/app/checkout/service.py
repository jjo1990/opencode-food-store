"""
Service layer for checkout validation
"""

from collections import OrderedDict

from sqlalchemy.orm import Session

from app.checkout.schemas import ItemValidado, ValidarRequest, ValidarResponse
from app.productos.repository import ProductoRepository


class CheckoutService:
    """Service for checkout pre-purchase validation"""

    def __init__(self, db: Session):
        self.db = db
        self.producto_repo = ProductoRepository(db)

    def validar(self, request: ValidarRequest) -> ValidarResponse:
        grupos = OrderedDict()
        for item in request.items:
            key = (item.producto_id, frozenset(item.personalizacion))
            if key in grupos:
                grupos[key]["cantidad"] += item.cantidad
            else:
                grupos[key] = {
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad,
                    "precio_snapshot": item.precio_snapshot,
                    "personalizacion": item.personalizacion,
                }

        errores_globales = []
        advertencias_globales = []
        detalles = []

        for grupo in grupos.values():
            producto_id = grupo["producto_id"]
            cantidad = grupo["cantidad"]
            precio_snapshot = grupo["precio_snapshot"]
            personalizacion = grupo["personalizacion"]

            item_errores = []
            item_advertencias = []
            item_nombre = None

            producto = self.producto_repo.get_by_id(producto_id)
            if not producto:
                item_errores.append(f"Producto {producto_id} no encontrado")
                item_valido = ItemValidado(
                    producto_id=producto_id,
                    nombre="",
                    valido=False,
                    errores=item_errores,
                    advertencias=[],
                )
                detalles.append(item_valido)
                errores_globales.extend(item_errores)
                continue

            item_nombre = producto.nombre

            if not producto.disponible:
                item_errores.append(f"{producto.nombre} no está disponible actualmente")

            if producto.stock_cantidad < cantidad:
                item_errores.append(
                    f"{producto.nombre} tiene stock insuficiente "
                    f"(disponible: {producto.stock_cantidad}, solicitado: {cantidad})"
                )

            ingredientes_ids = {i.id for i in (producto.ingredientes or [])}

            for ing_id in personalizacion:
                if ing_id not in ingredientes_ids:
                    item_errores.append(f"Ingrediente {ing_id} no válido para {producto.nombre}")

            if personalizacion:
                junction_rows = self.producto_repo.get_ingredientes(producto_id)
                removible_map = {jr.ingrediente_id: jr.es_removible for jr in junction_rows}
                ingrediente_nombre_map = {i.id: i.nombre for i in (producto.ingredientes or [])}

                for ing_id in personalizacion:
                    if ing_id in removible_map and not removible_map[ing_id]:
                        ing_nombre = ingrediente_nombre_map.get(ing_id, str(ing_id))
                        item_errores.append(
                            f"El ingrediente {ing_nombre} no se puede remover de {producto.nombre}"
                        )

            if precio_snapshot != producto.precio_base:
                item_advertencias.append(
                    f"El precio de {producto.nombre} cambió de ${precio_snapshot:.2f} a ${producto.precio_base:.2f}"
                )

            item_valido = ItemValidado(
                producto_id=producto_id,
                nombre=item_nombre,
                valido=len(item_errores) == 0,
                errores=item_errores,
                advertencias=item_advertencias,
            )
            detalles.append(item_valido)
            errores_globales.extend(item_errores)
            advertencias_globales.extend(item_advertencias)

        return ValidarResponse(
            valido=len(errores_globales) == 0,
            errores=errores_globales,
            advertencias=advertencias_globales,
            detalles=detalles,
        )
