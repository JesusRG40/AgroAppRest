from fastapi import APIRouter, Request
from typing import Any

from dao.riegosDao import RiegosDAO
from models.riegosModels import RiegoInsert, RiegoUpdate, RiegosSalida, RiegoDetalleSalida, Salida

router = APIRouter(prefix="/riegos", tags=["Riegos"])

@router.post("/", response_model=Salida, summary="Registrar un nuevo riego")
async def registrar_riego(riego: RiegoInsert, request: Request) -> Salida:
    """
    - Registra un nuevo riego con los datos proporcionados.
    - Se espera una fecha, cantidad de agua, método, duración e ID de usuario.
    """
    riegos_dao = RiegosDAO(request.app.db)
    return riegos_dao.registrar(riego)

@router.put("/{idRiego}", response_model=Salida, summary="Actualizar un riego existente")
async def actualizar_riego(idRiego: str, datos: RiegoUpdate, request: Request) -> Salida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Actualiza únicamente los campos enviados del riego.
    """
    riegos_dao = RiegosDAO(request.app.db)
    return riegos_dao.editar(idRiego, datos)

@router.delete("/{idRiego}", response_model=Salida, summary="Eliminar un riego por su ID")
async def eliminar_riego(idRiego: str, request: Request) -> Salida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Elimina el riego si existe en la base de datos.
    """
    riegos_dao = RiegosDAO(request.app.db)
    return riegos_dao.borrar(idRiego)

@router.get("/", response_model=RiegosSalida, summary="Consultar lista de riegos")
async def listar_riegos(request: Request) -> RiegosSalida:
    """
    - Recupera la lista de todos los registros de riegos.
    - Incluye: fecha, cantidad, método, duración y usuario asociado.
    """
    riegos_dao = RiegosDAO(request.app.db)
    return riegos_dao.consultar_lista()

@router.get("/{idRiego}", response_model=RiegoDetalleSalida, summary="Consultar un riego por ID")
async def obtener_riego(idRiego: str, request: Request) -> RiegoDetalleSalida:
    """
    - Recupera los detalles de un riego específico usando su ID.
    """
    riegos_dao = RiegosDAO(request.app.db)
    return riegos_dao.consultar(idRiego)
