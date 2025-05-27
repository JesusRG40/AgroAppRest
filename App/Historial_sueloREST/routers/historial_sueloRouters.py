from fastapi import APIRouter, Request
from typing import Any

from dao.historial_sueloDao import HistorialSueloDAO
from models.historial_sueloModels import HistorialSueloInsert, HistorialSueloUpdate, HistorialSueloSalida, HistorialSueloDetalleSalida, Salida

router = APIRouter(prefix="/historial_suelo", tags=["Historial de Suelo"])

@router.post("/", response_model=Salida, summary="Registrar un nuevo historial de suelo")
async def registrar_historial_suelo(historial_suelo: HistorialSueloInsert, request: Request) -> Salida:
    """
    -Registra un nuevo historial de suelo con los datos proporcionados.
    -Se espera una fecha de medicion, pH, nutrientes, observaciones, ID de cultivo e ID de usuario.
    """
    historial_suelo_dao = HistorialSueloDAO(request.app.db)
    return historial_suelo_dao.registrar(historial_suelo)

@router.put("/{idHistorial}", response_model=Salida, summary="Actualizar un historial de suelo existente")
async def actualizar_historial_suelo(idHistorial: str, datos: HistorialSueloUpdate, request: Request) -> Salida:
    """
    -Verifica que el ID proporcionado sea válido.
    -Actualiza únicamente los campos enviados del historial de suelo.
    """
    historial_suelo_dao = HistorialSueloDAO(request.app.db)
    return historial_suelo_dao.editar(idHistorial, datos)

@router.delete("/{idHistorial}", response_model=Salida, summary="Eliminar un historial de suelo por su ID")
async def eliminar_historial_suelo(idHistorial: str, request: Request) -> Salida:
    """
    -Verifica que el ID proporcionado sea válido.
    -Elimina el historial de suelo si existe en la base de datos.
    """
    historial_suelo_dao = HistorialSueloDAO(request.app.db)
    return historial_suelo_dao.borrar(idHistorial)

@router.get("/", response_model=HistorialSueloSalida, summary="Consultar lista de historiales de suelo")
async def listar_historiales_suelo(request: Request) -> HistorialSueloSalida:
    """
    -Recupera la lista de todos los registros de historial de suelo.
    - Incluye: fecha de medición, pH, nutrientes, observaciones, ID de cultivo e ID de usuario.
    """
    historial_suelo_dao = HistorialSueloDAO(request.app.db)
    return historial_suelo_dao.consultar_lista()

@router.get("/{idHistorial}", response_model=HistorialSueloDetalleSalida, summary="Consultar un historial de suelo por ID")
async def obtener_historial_suelo(idHistorial: str, request: Request) -> HistorialSueloDetalleSalida:
    """
    - Recupera los detalles de un historial de suelo específico usando su ID.
    """
    historial_suelo_dao = HistorialSueloDAO(request.app.db)
    return historial_suelo_dao.consultar(idHistorial)
