"""
Database seed: carga datos iniciales para que el sistema funcione.
- 6 estados de pedido
- 3 formas de pago
"""

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago

logger = logging.getLogger(__name__)


def seed():
    estados = [
        {
            "codigo": "PENDIENTE",
            "descripcion": "Pedido creado, pago pendiente",
            "orden": 1,
            "es_terminal": False,
        },
        {
            "codigo": "CONFIRMADO",
            "descripcion": "Pago procesado y confirmado",
            "orden": 2,
            "es_terminal": False,
        },
        {
            "codigo": "EN_PREPARACION",
            "descripcion": "Pedido en preparaci\u00f3n",
            "orden": 3,
            "es_terminal": False,
        },
        {
            "codigo": "EN_CAMINO",
            "descripcion": "Pedido en camino",
            "orden": 4,
            "es_terminal": False,
        },
        {"codigo": "ENTREGADO", "descripcion": "Pedido entregado", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
    ]
    formas_pago = [
        {
            "codigo": "MERCADOPAGO",
            "descripcion": "MercadoPago (tarjeta, Rapipago, Pago F\u00e1cil)",
            "habilitado": True,
        },
        {"codigo": "EFECTIVO", "descripcion": "Efectivo al recibir", "habilitado": True},
        {"codigo": "TRANSFERENCIA", "descripcion": "Transferencia bancaria", "habilitado": True},
    ]
    db = SessionLocal()
    try:
        for e in estados:
            exists = db.query(EstadoPedido).filter(EstadoPedido.codigo == e["codigo"]).first()
            if not exists:
                db.add(EstadoPedido(**e))
        for f in formas_pago:
            exists = db.query(FormaPago).filter(FormaPago.codigo == f["codigo"]).first()
            if not exists:
                db.add(FormaPago(**f))
        db.commit()
        logger.info("Seed completado exitosamente.")
    except Exception as e:
        db.rollback()
        logger.error("Error en seed", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    seed()
