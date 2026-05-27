"""
Data models for Food Store API
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.categoria import Categoria  # noqa: E402, F401
from app.models.detalle_pedido import DetallePedido  # noqa: E402, F401
from app.models.direccion_entrega import DireccionEntrega  # noqa: E402, F401
from app.models.estado_pedido import EstadoPedido  # noqa: E402, F401
from app.models.forma_pago import FormaPago  # noqa: E402, F401
from app.models.historial_estado_pedido import HistorialEstadoPedido  # noqa: E402, F401
from app.models.ingrediente import Ingrediente  # noqa: E402, F401
from app.models.pago import Pago  # noqa: E402, F401
from app.models.pedido import Pedido  # noqa: E402, F401
from app.models.producto import Producto  # noqa: E402, F401
from app.models.producto_categoria import ProductoCategoria  # noqa: E402, F401
from app.models.producto_ingrediente import ProductoIngrediente  # noqa: E402, F401
from app.models.refresh_token import RefreshToken  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.user_role import UserRole  # noqa: E402, F401

__all__ = [
    "Base",
    "User",
    "UserRole",
    "RefreshToken",
    "Categoria",
    "Ingrediente",
    "Producto",
    "ProductoCategoria",
    "ProductoIngrediente",
    "DireccionEntrega",
    "EstadoPedido",
    "FormaPago",
    "Pedido",
    "DetallePedido",
    "HistorialEstadoPedido",
    "Pago",
]
