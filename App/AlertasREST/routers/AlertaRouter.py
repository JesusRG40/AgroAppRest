from fastapi import APIRouter, Request, HTTPException, Body
from typing import List
from models.AlertasModel import AlertaInsert, AlertaUpdate, AlertaSalida, Salida
from dao.AlertasDAO import AlertasDAO

alertaRouter = APIRouter(prefix="/alertas", tags=["Alertas"])

@alertaRouter.post("/registrar", response_model=Salida)
def registrar_alerta(request: Request, alerta: AlertaInsert = Body(...)):
    dao = AlertasDAO(request.app.db)
    return dao.registrarAlerta(alerta)

@alertaRouter.put("/actualizar/{id_alerta}", response_model=Salida)
def actualizar_alerta(
    request: Request,
    id_alerta: str,
    alerta_data: AlertaUpdate = Body(...)
):
    dao = AlertasDAO(request.app.db)
    salida = dao.actualizarAlerta(id_alerta, alerta_data)
    if salida.estatus == "ERROR":
        raise HTTPException(status_code=400, detail=salida.mensaje)
    return salida

@alertaRouter.delete("/eliminar/{id_alerta}", response_model=Salida)
def eliminar_alerta(request: Request, id_alerta: str):
    dao = AlertasDAO(request.app.db)
    return dao.eliminarAlerta(id_alerta)

@alertaRouter.get("/detalle/{id_alerta}", response_model=AlertaSalida)
def consultar_alerta_por_id(request: Request, id_alerta: str):
    dao = AlertasDAO(request.app.db)
    alerta = dao.consultarAlertaPorId(id_alerta)
    if alerta is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alerta

@alertaRouter.get("/listar", response_model=List[AlertaSalida])
def listar_alertas(request: Request):
    dao = AlertasDAO(request.app.db)
    return dao.listarAlertas()
