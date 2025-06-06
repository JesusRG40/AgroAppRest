from fastapi import APIRouter, HTTPException, Body, Request
from dao.riegosDAO import RiegosDAO
from models.riegosModel import (
    RiegoConsulta,
    RiegoConsultaIndividual,
    RiegoInsert,
    RiegoParcialUpdate,
    RiegosSalida,
    Salida
)

router = APIRouter(prefix="/riegos", tags=["Riegos"])

@router.post("/registrar/{id_cultivo}", response_model=Salida)
def registrar_riego(
    request: Request,
    id_cultivo: str,
    riego: RiegoInsert = Body(...)
):
    dao = RiegosDAO(request.app.db)
    salida = dao.registrarNuevoRiego(id_cultivo, riego)
    if salida.estatus == "ERROR":
        raise HTTPException(status_code=400, detail=salida.mensaje)
    return salida


@router.put("/actualizar/{id_cultivo}/{id_riego}", response_model=Salida)
def actualizar_riego(
    request: Request,
    id_cultivo: str,
    id_riego: str,
    riego_data: RiegoParcialUpdate = Body(...)
):
    dao = RiegosDAO(request.app.db)
    salida = dao.actualizarRiegoDeCultivo(id_cultivo, id_riego, riego_data)
    if salida.estatus == "ERROR":
        raise HTTPException(status_code=400, detail=salida.mensaje)
    return salida


# Cambié el endpoint a DELETE y llamo a eliminación física
@router.delete("/eliminar/{id_cultivo}/{id_riego}", response_model=Salida)
def eliminar_riego(
    request: Request,
    id_cultivo: str,
    id_riego: str
):
    dao = RiegosDAO(request.app.db)
    salida = dao.eliminarRiegoDeCultivo(id_cultivo, id_riego)
    if salida.estatus == "ERROR":
        raise HTTPException(status_code=400, detail=salida.mensaje)
    return salida


@router.get("/detalle/{id_cultivo}/{id_riego}", response_model=RiegoConsultaIndividual)
def obtener_riego_por_id(
    request: Request,
    id_cultivo: str,
    id_riego: str
):
    dao = RiegosDAO(request.app.db)
    salida = dao.consultarRiegoDeCultivoPorId(id_cultivo, id_riego)
    if salida.estatus == "ERROR":
        raise HTTPException(status_code=404, detail=salida.mensaje)
    return salida


@router.get("/listar/{id_cultivo}", response_model=RiegosSalida)
def obtener_riegos_activos(
    request: Request,
    id_cultivo: str
):
    dao = RiegosDAO(request.app.db)
    salida = dao.consultarRiegosDeCultivo(id_cultivo)
    return salida
