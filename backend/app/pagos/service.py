import uuid

import mercadopago
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import MP_ACCESS_TOKEN
from app.models import User
from app.models.pago import Pago
from app.pagos.schemas import CrearPagoRequest, PagoResponse
from app.pedidos.repository import PedidoRepository


class PagoService:
    def __init__(self, db: Session):
        self.db = db
        self.pedido_repo = PedidoRepository(db)

        if not MP_ACCESS_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MercadoPago no está configurado. Contacte al administrador.",
            )
        self.sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

    def crear_pago(self, user: User, data: CrearPagoRequest) -> PagoResponse:
        # 1. Validar pedido
        pedido = self.pedido_repo.get_by_id(data.pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # 2. Ownership check
        user_roles = [r.role for r in user.roles]
        is_admin = "ADMIN" in user_roles
        if not is_admin and pedido.usuario_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # 3. Validar estado PENDIENTE
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El pedido debe estar en estado PENDIENTE (actual: {pedido.estado_codigo})",
            )

        # 4. Generar idempotency_key
        idempotency_key = str(uuid.uuid4())
        external_reference = str(pedido.id)

        # 5. Check idempotencia
        existing = self.db.query(Pago).filter(Pago.idempotency_key == idempotency_key).first()
        if existing:
            return PagoResponse(
                mp_payment_id=existing.mp_payment_id,
                status=existing.mp_status,
                status_detail=existing.status_detail,
            )

        # 6. Preparar payload para MercadoPago
        items = []
        for detalle in pedido.detalles or []:
            items.append(
                {
                    "title": detalle.nombre_snapshot,
                    "quantity": detalle.cantidad,
                    "unit_price": float(detalle.precio_snapshot),
                }
            )

        payment_data = {
            "token": data.card_token,
            "installments": 1,
            "transaction_amount": float(pedido.total),
            "description": f"Pedido Food Store #{str(pedido.id)[:8]}",
            "external_reference": external_reference,
            "idempotency_key": idempotency_key,
            "payment_method_id": "visa",
        }

        # 7. Llamar a MercadoPago SDK
        try:
            result = self.sdk.payment().create(payment_data)

            if result.get("status") in (200, 201):
                response = result.get("response", {})
                mp_status = response.get("status", "rejected")
                mp_payment_id = str(response.get("id", ""))
                status_detail = response.get("status_detail", "")
            else:
                mp_status = "rejected"
                mp_payment_id = ""
                cause = result.get("cause", [{}])
                status_detail = (
                    cause[0].get("description", "") if cause else str(result.get("error", ""))
                )
        except Exception as e:
            mp_status = "rejected"
            mp_payment_id = ""
            status_detail = str(e)

        # 8. Registrar en BD
        pago = Pago(
            pedido_id=pedido.id,
            mp_payment_id=mp_payment_id or None,
            mp_status=mp_status,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            status_detail=status_detail or None,
        )
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)

        return PagoResponse(
            mp_payment_id=pago.mp_payment_id,
            status=pago.mp_status,
            status_detail=pago.status_detail,
        )
