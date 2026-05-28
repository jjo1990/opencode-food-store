from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import User
from app.pedidos.schemas import (
    AvanzarEstadoRequest,
    CrearPedidoRequest,
    HistorialResponse,
    PedidoDetail,
    PedidoRead,
)
from app.pedidos.service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    data: CrearPedidoRequest,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> PedidoRead:
    service = PedidoService(db)
    return service.crear_pedido(current_user, data)


@router.get("", response_model=dict)
def listar_pedidos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    estado_codigo: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return PedidoService(db).listar_pedidos(
        current_user, skip=skip, limit=limit, estado_codigo=estado_codigo
    )


@router.get("/{pedido_id}", response_model=PedidoDetail)
def obtener_pedido(
    pedido_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PedidoDetail:
    return PedidoService(db).obtener_pedido(current_user, pedido_id)


@router.patch("/{pedido_id}/avanzar", response_model=PedidoRead)
def avanzar_estado(
    pedido_id: UUID,
    data: AvanzarEstadoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PedidoRead:
    service = PedidoService(db)
    return service.avanzar_estado(current_user, pedido_id, data.nuevo_estado, data.motivo)


@router.get("/{pedido_id}/historial", response_model=list[HistorialResponse])
def obtener_historial(
    pedido_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[HistorialResponse]:
    service = PedidoService(db)
    return service.obtener_historial(current_user, pedido_id)
