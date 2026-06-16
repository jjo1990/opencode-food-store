"""
Admin routes for role-based access control and user management
"""

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.admin.schemas import (
    AdminCategoriaListResponse,
    AdminChangeStateRequest,
    AdminIngredienteListResponse,
    AdminOrderListResponse,
    AdminProductoListResponse,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    MetricsPedidosEstadoResponse,
    MetricsProductoTopResponse,
    MetricsResumenResponse,
    MetricsVentasResponse,
)
from app.admin.service import AdminService
from app.auth.schemas import UpdateRolesRequest, UserResponse
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.exceptions import ForbiddenException, UserNotFoundException
from app.models import User
from app.pedidos.schemas import PedidoDetail, PedidoRead

router = APIRouter(prefix="/admin", tags=["admin"])


# ─── Existing endpoints (role management) ────────────────────────────────────


@router.put("/users/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: UUID,
    request: UpdateRolesRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update user roles (ADMIN only)"""
    service = AdminService(db)

    try:
        return service.assign_roles_to_user(user_id, request.roles)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador",
        )


@router.delete("/users/{user_id}/roles/{role}", status_code=status.HTTP_200_OK)
async def remove_user_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Remove a role from a user (ADMIN only)"""
    service = AdminService(db)

    try:
        return service.remove_role_from_user(user_id, role)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador",
        )


# ─── New endpoints (user management) ─────────────────────────────────────────


@router.get("/usuarios", response_model=AdminUserListResponse)
async def list_usuarios(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    rol: str | None = Query(None, description="Filtrar por rol (ADMIN, CLIENT, STOCK, PEDIDOS)"),
    search: str | None = Query(None, description="Buscar por email o nombre"),
    estado: str = Query("activo", description="Filtrar por estado: activo, inactivo, todos"),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserListResponse:
    """Listar usuarios con paginación y filtros"""
    service = AdminService(db)
    return service.list_users(page, size, rol, search, estado)


@router.get("/usuarios/{user_id}", response_model=AdminUserResponse)
async def get_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Obtener detalle de un usuario"""
    service = AdminService(db)
    try:
        return service.get_user_detail(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )


@router.put("/usuarios/{user_id}", response_model=AdminUserResponse)
async def update_usuario(
    user_id: UUID,
    request: AdminUserUpdateRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Actualizar datos y/o roles de un usuario"""
    service = AdminService(db)
    try:
        return service.update_user(user_id, request)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )


@router.delete("/usuarios/{user_id}", response_model=dict)
async def deactivate_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> dict:
    """Desactivar un usuario (soft delete)"""
    service = AdminService(db)
    try:
        return service.deactivate_user(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )


@router.patch("/usuarios/{user_id}/reactivar", response_model=AdminUserResponse)
async def reactivate_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Reactivar un usuario desactivado"""
    service = AdminService(db)
    try:
        return service.reactivate_user(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )


# ─── Order Management Endpoints ────────────────────────────────────────────

"""
Admin Order Management Endpoints

These endpoints provide comprehensive order management for admins:

1. GET /admin/pedidos — List orders with pagination and filtering
   - Filters: estado_codigo, fecha_inicio, fecha_fin, usuario_id, monto_min, monto_max
   - Pagination: page, size (default 20, max 100)
   - Required roles: ADMIN or PEDIDOS
   - Joined with User and DireccionEntrega for client names and addresses

2. PATCH /admin/pedidos/{id}/estado — Change order state
   - Validates FSM transitions from pedidos.service.TRANSITIONS
   - Prevents transitions from terminal states (ENTREGADO, CANCELADO)
   - Restores stock when transition has stock_action: "restore"
   - Creates HistorialEstadoPedido audit entry with motivo
   - Required roles: ADMIN or PEDIDOS

3. GET /admin/pedidos/{id} — Get order details
   - Returns PedidoDetail with items, historial, and joined actor names
   - Requires ADMIN or PEDIDOS role
"""


@router.get("/pedidos", response_model=AdminOrderListResponse)
async def list_pedidos_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    estado_codigo: str | None = Query(None, description="Filtrar por estado del pedido"),
    fecha_inicio: datetime | None = Query(None, description="Filtrar desde fecha"),
    fecha_fin: datetime | None = Query(None, description="Filtrar hasta fecha"),
    usuario_id: UUID | None = Query(None, description="Filtrar por usuario"),
    monto_min: float | None = Query(None, description="Monto mínimo del pedido"),
    monto_max: float | None = Query(None, description="Monto máximo del pedido"),
    current_user: User = Depends(require_role("ADMIN", "PEDIDOS")),
    db: Session = Depends(get_db),
) -> AdminOrderListResponse:
    """
    Listar pedidos para admin con paginación y filtros.

    Retorna una lista paginada de pedidos con datos del cliente y dirección.
    Los filtros se aplican con lógica AND.

    Query Parameters:
    - page: Número de página (default: 1)
    - size: Items por página (default: 20, max: 100)
    - estado_codigo: Filtrar por estado (ej: PENDIENTE, CONFIRMADO, ENTREGADO)
    - fecha_inicio: Filtrar desde fecha ISO (ej: 2026-06-01)
    - fecha_fin: Filtrar hasta fecha ISO
    - usuario_id: UUID del usuario cliente
    - monto_min: Monto mínimo del pedido
    - monto_max: Monto máximo del pedido

    Returns: AdminOrderListResponse con items, total, page, size, pages
    """
    service = AdminService(db)
    return service.list_orders_admin(
        page=page,
        size=size,
        estado_codigo=estado_codigo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        usuario_id=usuario_id,
        monto_min=monto_min,
        monto_max=monto_max,
    )


@router.patch("/pedidos/{pedido_id}/estado", response_model=PedidoRead)
async def change_pedido_state(
    pedido_id: UUID,
    request: AdminChangeStateRequest,
    current_user: User = Depends(require_role("ADMIN", "PEDIDOS")),
    db: Session = Depends(get_db),
) -> PedidoRead:
    """
    Cambiar estado de un pedido (admin panel).

    Valida la transición de estado usando la FSM definida en pedidos.service:
    - TRANSITIONS: mapa de transiciones válidas con roles requeridos
    - TERMINAL_STATES: estados desde los que no se puede transicionar

    Si la transición tiene stock_action="restore", incrementa el stock de los productos.

    Crea una entrada de auditoría en HistorialEstadoPedido con:
    - estado_desde: estado anterior
    - estado_nuevo: nuevo estado
    - actor_id: ID del admin que realizó el cambio
    - motivo: razón del cambio (opcional, max 500 caracteres)

    Request Body:
    - nuevo_estado: Nuevo estado (1-20 caracteres, debe ser válido en la transición)
    - motivo: Razón del cambio (opcional, max 500 caracteres)

    Returns: PedidoRead con el pedido actualizado

    Errors:
    - 404: Pedido no encontrado
    - 403: Usuario sin permisos para esta transición
    - 422: Transición inválida o pedido en estado terminal
    """
    service = AdminService(db)
    return service.change_order_state_admin(pedido_id, request, current_user)


@router.get("/pedidos/{pedido_id}", response_model=PedidoDetail)
async def get_pedido_detail(
    pedido_id: UUID,
    current_user: User = Depends(require_role("ADMIN", "PEDIDOS")),
    db: Session = Depends(get_db),
) -> PedidoDetail:
    """
    Obtener detalle completo de un pedido (admin panel).

    Retorna PedidoDetail con:
    - Datos del pedido (id, estado, monto, fechas)
    - items: Lista de DetallePedido con productos, cantidades, precios
    - historial: Audit trail con todas las transiciones de estado
      (incluye actor_nombre joinado desde User)

    Path Parameter:
    - pedido_id: UUID del pedido

    Returns: PedidoDetail

    Errors:
    - 404: Pedido no encontrado (o usuario sin permisos de lectura)
    - 403: Usuario sin rol ADMIN o PEDIDOS
    """
    from app.pedidos.service import PedidoService

    service = PedidoService(db)
    return service.obtener_pedido(current_user, pedido_id)


# ─── Catalog Management Endpoints ──────────────────────────────────────────


@router.get("/productos", response_model=AdminProductoListResponse)
async def list_productos_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Buscar por nombre"),
    disponible: bool | None = Query(None, description="Filtrar por disponibilidad"),
    eliminado: bool | None = Query(None, description="Filtrar por estado de eliminación"),
    categoria_id: UUID | None = Query(None, description="Filtrar por categoría"),
    current_user: User = Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> AdminProductoListResponse:
    """Listar todos los productos (incluyendo soft-deleted) con filtros y paginación"""
    service = AdminService(db)
    return service.list_productos_admin(
        page=page,
        size=size,
        search=search,
        disponible=disponible,
        eliminado=eliminado,
        categoria_id=categoria_id,
    )


@router.get("/categorias", response_model=AdminCategoriaListResponse)
async def list_categorias_admin(
    eliminado: bool | None = Query(None, description="Filtrar por estado de eliminación"),
    current_user: User = Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> AdminCategoriaListResponse:
    """Listar todas las categorías (incluyendo soft-deleted)"""
    service = AdminService(db)
    return service.list_categorias_admin(eliminado=eliminado)


@router.get("/ingredientes", response_model=AdminIngredienteListResponse)
async def list_ingredientes_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    es_alergeno: bool | None = Query(None, description="Filtrar por alérgeno"),
    eliminado: bool | None = Query(None, description="Filtrar por estado de eliminación"),
    current_user: User = Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> AdminIngredienteListResponse:
    """Listar todos los ingredientes (incluyendo soft-deleted) con filtros y paginación"""
    service = AdminService(db)
    return service.list_ingredientes_admin(
        page=page, size=size, es_alergeno=es_alergeno, eliminado=eliminado
    )


# ─── Metrics Endpoints ─────────────────────────────────────────────────────


@router.get("/metricas/resumen", response_model=MetricsResumenResponse)
async def get_metrics_resumen(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> MetricsResumenResponse:
    """Obtener KPIs generales del negocio (ADMIN only)."""
    service = AdminService(db)
    return service.get_metrics_resumen()


@router.get("/metricas/ventas", response_model=MetricsVentasResponse)
async def get_metrics_ventas(
    fecha_inicio: date = Query(..., description="Fecha de inicio del rango (inclusive)"),
    fecha_fin: date = Query(..., description="Fecha de fin del rango (inclusive)"),
    granularidad: str = Query("day", description="Granularidad: day, week, month"),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> MetricsVentasResponse:
    """Obtener ventas agregadas por período (ADMIN only)."""
    service = AdminService(db)
    return service.get_metrics_ventas(fecha_inicio, fecha_fin, granularidad)


@router.get("/metricas/productos-top", response_model=MetricsProductoTopResponse)
async def get_metrics_productos_top(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> MetricsProductoTopResponse:
    """Obtener top 10 productos más vendidos (ADMIN only)."""
    service = AdminService(db)
    return service.get_metrics_productos_top()


@router.get("/metricas/pedidos-por-estado", response_model=MetricsPedidosEstadoResponse)
async def get_metrics_pedidos_por_estado(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> MetricsPedidosEstadoResponse:
    """Obtener distribución de pedidos por estado con porcentajes (ADMIN only)."""
    service = AdminService(db)
    return service.get_metrics_pedidos_por_estado()
