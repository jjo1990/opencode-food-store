from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.direcciones.repository import DireccionRepository
from app.direcciones.schemas import DireccionCreate, DireccionResponse, DireccionUpdate
from app.models import User


class DireccionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DireccionRepository(db)

    def create(self, user: User, data: DireccionCreate) -> DireccionResponse:
        active_count = self.repo.count_active_by_user(user.id)

        if active_count == 0:
            data.es_principal = True

        if data.es_principal:
            current_principal = self.repo.get_principal(user.id)
            if current_principal:
                self.repo.update(current_principal, {"es_principal": False})

        direccion = self.repo.create(
            {
                "usuario_id": user.id,
                "alias": data.alias,
                "calle": data.calle,
                "numero": data.numero,
                "piso": data.piso,
                "departamento": data.departamento,
                "ciudad": data.ciudad,
                "codigo_postal": data.codigo_postal,
                "referencia": data.referencia,
                "es_principal": data.es_principal,
            }
        )

        return DireccionResponse(
            id=direccion.id,
            usuario_id=direccion.usuario_id,
            alias=direccion.alias,
            calle=direccion.calle,
            numero=direccion.numero,
            piso=direccion.piso,
            departamento=direccion.departamento,
            ciudad=direccion.ciudad,
            codigo_postal=direccion.codigo_postal,
            referencia=direccion.referencia,
            es_principal=direccion.es_principal,
            created_at=direccion.created_at,
            updated_at=direccion.updated_at,
        )

    def list_addresses(self, user: User) -> list[DireccionResponse]:
        direcciones = self.repo.get_by_user(user.id)

        return [
            DireccionResponse(
                id=d.id,
                usuario_id=d.usuario_id,
                alias=d.alias,
                calle=d.calle,
                numero=d.numero,
                piso=d.piso,
                departamento=d.departamento,
                ciudad=d.ciudad,
                codigo_postal=d.codigo_postal,
                referencia=d.referencia,
                es_principal=d.es_principal,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in direcciones
        ]

    def _get_owned_or_404(self, user: User, address_id: UUID):
        direccion = self.repo.get_by_id(address_id)
        if not direccion or direccion.usuario_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        return direccion

    def get_address(self, user: User, address_id: UUID) -> DireccionResponse:
        direccion = self._get_owned_or_404(user, address_id)

        return DireccionResponse(
            id=direccion.id,
            usuario_id=direccion.usuario_id,
            alias=direccion.alias,
            calle=direccion.calle,
            numero=direccion.numero,
            piso=direccion.piso,
            departamento=direccion.departamento,
            ciudad=direccion.ciudad,
            codigo_postal=direccion.codigo_postal,
            referencia=direccion.referencia,
            es_principal=direccion.es_principal,
            created_at=direccion.created_at,
            updated_at=direccion.updated_at,
        )

    def update(self, user: User, address_id: UUID, data: DireccionUpdate) -> DireccionResponse:
        direccion = self._get_owned_or_404(user, address_id)

        update_data = data.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar",
            )

        if update_data.get("es_principal") and not direccion.es_principal:
            current_principal = self.repo.get_principal(user.id)
            if current_principal and current_principal.id != direccion.id:
                self.repo.update(current_principal, {"es_principal": False})

        direccion = self.repo.update(direccion, update_data)

        return DireccionResponse(
            id=direccion.id,
            usuario_id=direccion.usuario_id,
            alias=direccion.alias,
            calle=direccion.calle,
            numero=direccion.numero,
            piso=direccion.piso,
            departamento=direccion.departamento,
            ciudad=direccion.ciudad,
            codigo_postal=direccion.codigo_postal,
            referencia=direccion.referencia,
            es_principal=direccion.es_principal,
            created_at=direccion.created_at,
            updated_at=direccion.updated_at,
        )

    def set_principal(self, user: User, address_id: UUID) -> DireccionResponse:
        direccion = self._get_owned_or_404(user, address_id)

        if direccion.es_principal:
            return DireccionResponse(
                id=direccion.id,
                usuario_id=direccion.usuario_id,
                alias=direccion.alias,
                calle=direccion.calle,
                numero=direccion.numero,
                piso=direccion.piso,
                departamento=direccion.departamento,
                ciudad=direccion.ciudad,
                codigo_postal=direccion.codigo_postal,
                referencia=direccion.referencia,
                es_principal=direccion.es_principal,
                created_at=direccion.created_at,
                updated_at=direccion.updated_at,
            )

        current_principal = self.repo.get_principal(user.id)
        if current_principal:
            self.repo.update(current_principal, {"es_principal": False})

        direccion = self.repo.update(direccion, {"es_principal": True})

        return DireccionResponse(
            id=direccion.id,
            usuario_id=direccion.usuario_id,
            alias=direccion.alias,
            calle=direccion.calle,
            numero=direccion.numero,
            piso=direccion.piso,
            departamento=direccion.departamento,
            ciudad=direccion.ciudad,
            codigo_postal=direccion.codigo_postal,
            referencia=direccion.referencia,
            es_principal=direccion.es_principal,
            created_at=direccion.created_at,
            updated_at=direccion.updated_at,
        )

    def delete(self, user: User, address_id: UUID) -> None:
        direccion = self._get_owned_or_404(user, address_id)

        active_count = self.repo.count_active_by_user(user.id)
        if active_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu única dirección de entrega",
            )

        self.repo.soft_delete(direccion)
