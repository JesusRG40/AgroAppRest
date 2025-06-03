from fastapi import APIRouter, Request, Depends, HTTPException
from bson import ObjectId
from models.cultivosModel import (CultivoInsert, Salida, CultivoUpdate, CultivoSalidaIndividual, CultivosListSalida,
    UbicacionInsert, UbicacionUpdate, UbicacionSalidaIndividual,
    SeguimientoInsert, SeguimientoUpdate, SeguimientoSalidaIndividual, SeguimientoListSalida)
from dao.cultivosDAO import CultivoDAO

# Importaciones para la seguridad
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.usuariosModel import UsuarioDetalleSalida
from dao.usuariosDAO import UsuarioDAO as UsuarioAuthDAO

security = HTTPBasic()

async def validarUsuario(request: Request,
                         credenciales: HTTPBasicCredentials = Depends(security)) -> UsuarioDetalleSalida:
    usuario_dao = UsuarioAuthDAO(request.app.db)
    resultado_login = usuario_dao.iniciar_sesion(credenciales.username, credenciales.password)
    if resultado_login.estatus != "OK" or not resultado_login.usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas o usuario no encontrado",
            headers={"WWW-Authenticate": "Basic"},)
    return resultado_login


# --- Fin de la sección de Seguridad ---

router = APIRouter(prefix="/cultivos")



# --- Endpoints para Cultivos ---

@router.post("/agregar", response_model=Salida, summary="Registrar un nuevo cultivo", tags=["Cultivos"])
async def registrar_cultivo(
        cultivo_data: CultivoInsert,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.agregarCultivo(cultivo_data)
    return resultado


@router.put("/editar/{id_cultivo}", response_model=Salida, summary="Editar un cultivo existente", tags=["Cultivos"])
async def editar_cultivo(
        id_cultivo: str,
        cultivo_update_data: CultivoUpdate,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para editar este cultivo.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.actualizarCultivo(id_cultivo, cultivo_update_data)
    return resultado


@router.delete("/eliminar/{id_cultivo}", response_model=Salida, summary="Eliminar un cultivo", tags=["Cultivos"])
async def eliminar_cultivo(
        id_cultivo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    if usuario_actual.usuario['rol'] != "Administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar cultivos.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.borrarCultivo(id_cultivo)
    return resultado


@router.get("/consultar/{id_cultivo}", response_model=CultivoSalidaIndividual, summary="Consultar un cultivo por ID", tags=["Cultivos"])
async def consultar_cultivo(
        id_cultivo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> CultivoSalidaIndividual:
    # Todos los roles permitidos, no se necesita chequeo específico de rol.
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarCultivoPorId(id_cultivo)
    return resultado


@router.get("/", response_model=CultivosListSalida, summary="Consultar lista de todos los cultivos", tags=["Cultivos"])
async def consultar_lista_cultivos(
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> CultivosListSalida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver la lista de todos los cultivos.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarListaDeCultivos()
    return resultado


# --- Endpoints para Ubicación de Cultivos ---

@router.post("/{id_cultivo}/ubicacion/agregar", response_model=Salida, tags=["Ubicacion Cultivos"],
             summary="Registrar ubicación para un cultivo")
async def registrar_ubicacion_cultivo(
        id_cultivo: str,
        ubicacion_data: UbicacionInsert,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para editar la ubicación del cultivo.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.registrarNuevaUbicacion(id_cultivo, ubicacion_data)
    return resultado


@router.put("/{id_cultivo}/ubicacion/editar", response_model=Salida, tags=["Ubicacion Cultivos"],
            summary="Editar ubicación de un cultivo")
async def editar_ubicacion_cultivo(
        id_cultivo: str,
        ubicacion_data: UbicacionUpdate,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para editar la ubicación del cultivo.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.actualizarUbicacionCultivo(id_cultivo, ubicacion_data)
    return resultado


@router.get("/{id_cultivo}/ubicacion/consultar", response_model=UbicacionSalidaIndividual, tags=["Ubicacion Cultivos"],
            summary="Consultar ubicación de un cultivo")
async def consultar_ubicacion_cultivo(
        id_cultivo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> UbicacionSalidaIndividual:
    # Todos los roles permitidos.
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarUbicacionDeCultivo(id_cultivo)
    return resultado


# --- Endpoints para Seguimientos de Cultivo ---

@router.post("/{id_cultivo}/seguimientos/agregar", response_model=Salida, tags=["Seguimientos-Cultivo"],
             summary="Registrar seguimiento para un cultivo")
async def registrar_seguimiento_cultivo(
        id_cultivo: str,
        seguimiento_data: SeguimientoInsert,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.agregar_seguimiento(id_cultivo, seguimiento_data)
    return resultado


@router.put("/{id_cultivo}/seguimientos/editar/{id_seguimiento}", response_model=Salida, tags=["Seguimientos-Cultivo"],
            summary="Editar seguimiento de un cultivo")
async def editar_seguimiento_cultivo(
        id_cultivo: str,
        id_seguimiento: str,
        seguimiento_data: SeguimientoUpdate,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.editar_seguimiento(id_cultivo, id_seguimiento, seguimiento_data)
    return resultado


@router.delete("/{id_cultivo}/seguimientos/eliminar/{id_seguimiento}", response_model=Salida,
               tags=["Seguimientos-Cultivo"], summary="Eliminar seguimiento de un cultivo")
async def eliminar_seguimiento_cultivo(
        id_cultivo: str,
        id_seguimiento: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar este seguimiento.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.eliminar_seguimiento(id_cultivo, id_seguimiento)
    return resultado


@router.get("/{id_cultivo}/seguimientos/consultar/{id_seguimiento}", response_model=SeguimientoSalidaIndividual,
            tags=["Seguimientos-Cultivo"], summary="Consultar un seguimiento específico")
async def consultar_seguimiento_especifico_cultivo(
        id_cultivo: str,
        id_seguimiento: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> SeguimientoSalidaIndividual:
    # Todos los roles permitidos.
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultar_seguimiento_por_id(id_cultivo, id_seguimiento)
    return resultado


@router.get("/{id_cultivo}/seguimientos/consultar", response_model=SeguimientoListSalida, tags=["Seguimientos-Cultivo"],
            summary="Consultar lista de seguimientos de un cultivo")
async def consultar_lista_seguimiento(
        id_cultivo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> SeguimientoListSalida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver esta lista de seguimientos.")
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarListaSeguimiento(id_cultivo)
    return resultado
