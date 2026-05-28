import hashlib
import hmac
import json
import uuid
from uuid import UUID

import mercadopago
import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import MP_ACCESS_TOKEN, MP_WEBHOOK_SECRET
from app.models import User
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.pago import Pago
from app.models.producto import Producto
from app.pagos.schemas import (
    CrearPagoRequest,
    PagoHistoryItem,
    PagoHistoryResponse,
    PagoResponse,
    ReintentarPagoRequest,
    WebhookNotification,
)
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

    def _validar_firma(self, raw_body: bytes, x_signature: str, x_request_id: str) -> bool:
        """
        Valida la firma X-Signature de MercadoPago.

        Formato esperado: ts=<timestamp>,v1=<hmac_sha256>
        El template string sigue el formato de MP:
            "id:{data.id};request-id:{x-request-id};ts:{ts};"
        """
        if not x_signature or not MP_WEBHOOK_SECRET:
            return True  # Sin configuración, no validamos (modo degradado)

        try:
            parts = {}
            for pair in x_signature.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    parts[k.strip()] = v.strip()

            ts = parts.get("ts", "")
            received_hash = parts.get("v1", "")

            if not ts or not received_hash:
                return False

            # Reconstruir el template string de MP
            data_id = ""
            try:
                body_dict = json.loads(raw_body.decode("utf-8"))
                data_id = body_dict.get("data", {}).get("id", "")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            template_string = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

            expected_hash = hmac.new(
                MP_WEBHOOK_SECRET.encode("utf-8"),
                template_string.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected_hash, received_hash)
        except Exception:
            return False

    def procesar_webhook(
        self,
        data: WebhookNotification,
        x_signature: str = "",
        x_request_id: str = "",
        raw_body: bytes = b"",
    ) -> dict:
        # Validar firma
        if not self._validar_firma(raw_body, x_signature, x_request_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook inválida",
            )

        if data.type != "payment" or not data.data or not data.data.get("id"):
            return {"status": "ignored"}

        payment_id = str(data.data["id"])

        mp_url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
        headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        try:
            mp_response = requests.get(mp_url, headers=headers, timeout=10)
            mp_response.raise_for_status()
            payment_info = mp_response.json()
            real_status = payment_info.get("status", "rejected")
        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo verificar el pago con MercadoPago",
            )

        pago = self.db.query(Pago).filter(Pago.mp_payment_id == payment_id).first()
        if not pago:
            return {"status": "ignored", "reason": "payment_not_found"}

        if pago.mp_status in ("approved", "rejected") and pago.mp_status != "pending":
            return {"status": "duplicate", "mp_status": pago.mp_status}

        if real_status == "approved":
            return self._procesar_pago_aprobado(pago, payment_info)
        else:
            return self._procesar_pago_no_aprobado(pago, real_status, payment_info)

    def _procesar_pago_aprobado(self, pago: Pago, payment_info: dict) -> dict:
        pedido = self.pedido_repo.get_by_id(pago.pedido_id)
        if not pedido or pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pedido no encontrado o no está en estado PENDIENTE",
            )

        pago.mp_status = "approved"
        pago.status_detail = payment_info.get("status_detail")
        pedido.estado_codigo = "CONFIRMADO"

        try:
            for detalle in pedido.detalles:
                producto = (
                    self.db.query(Producto)
                    .filter(Producto.id == detalle.producto_id, Producto.soft_deleted_at.is_(None))
                    .with_for_update()
                    .first()
                )
                if not producto:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Producto {detalle.producto_id} no encontrado",
                    )
                if producto.stock_cantidad < detalle.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Stock insuficiente para {producto.nombre}: disponible {producto.stock_cantidad}, requerido {detalle.cantidad}",
                    )
                producto.stock_cantidad -= detalle.cantidad

            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde="PENDIENTE",
                estado_nuevo="CONFIRMADO",
                actor_id=None,
                motivo="Pago aprobado vía MercadoPago",
            )
            self.db.add(historial)
            self.db.commit()
            self.db.refresh(pago)
            return {"status": "approved", "mp_payment_id": pago.mp_payment_id}
        except HTTPException:
            self.db.rollback()
            raise

    def _procesar_pago_no_aprobado(self, pago: Pago, real_status: str, payment_info: dict) -> dict:
        pago.mp_status = real_status
        pago.status_detail = payment_info.get("status_detail")
        self.db.commit()
        return {"status": real_status}

    def consultar_pagos(self, pedido_id: UUID, current_user: User) -> PagoHistoryResponse:
        # 1. Buscar pedido
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        # 2. Ownership check
        user_roles = [r.role for r in current_user.roles]
        is_admin = "ADMIN" in user_roles
        if not is_admin and pedido.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        # 3. Buscar pagos asociados
        pagos = (
            self.db.query(Pago)
            .filter(Pago.pedido_id == pedido_id)
            .order_by(Pago.created_at.desc())
            .all()
        )

        # 4. Retornar
        return PagoHistoryResponse(pagos=[PagoHistoryItem.model_validate(p) for p in pagos])

    def reintentar_pago(self, current_user: User, data: ReintentarPagoRequest) -> PagoResponse:
        # 1. Validar pedido
        pedido = self.pedido_repo.get_by_id(data.pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        # 2. Ownership check
        user_roles = [r.role for r in current_user.roles]
        is_admin = "ADMIN" in user_roles
        if not is_admin and pedido.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        # 3. Validar estado PENDIENTE
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El pedido debe estar en estado PENDIENTE (actual: {pedido.estado_codigo})",
            )

        # 4. Validar último pago fue rechazado (no aprobado)
        ultimo_pago = (
            self.db.query(Pago)
            .filter(Pago.pedido_id == pedido.id)
            .order_by(Pago.created_at.desc())
            .first()
        )

        if ultimo_pago and ultimo_pago.mp_status == "approved":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El pago ya fue aprobado. No se puede reintentar.",
            )

        # 5. Generar nueva idempotency_key y external_reference
        idempotency_key = str(uuid.uuid4())
        external_reference = str(pedido.id)

        # 6. Check idempotencia
        existing = self.db.query(Pago).filter(Pago.idempotency_key == idempotency_key).first()
        if existing:
            return PagoResponse(
                mp_payment_id=existing.mp_payment_id,
                status=existing.mp_status,
                status_detail=existing.status_detail,
            )

        # 7. Preparar payload con los items del pedido (igual que crear_pago)
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

        # 8. Llamar a MercadoPago SDK
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

        # 9. Registrar nuevo Pago en BD (nuevo intento)
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
