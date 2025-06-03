from fastapi import APIRouter, Request, Depends, HTTPException
from bson import ObjectId
from models.aplicacionesInsumoModel import (
    AplicacionInsumoInsert, AplicacionInsumoUpdate,
    AplicacionInsumoSalidaIndividual, AplicacionInsumoListSalida)
from models.cultivosModel import Salida
from dao.aplicacionesInsumoDAO import AplicacionesInsumoDAO

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
    if not isinstance(resultado_login.usuario, dict):
        pass
    return resultado_login


# --- Fin de la sección de Seguridad ---

router = APIRouter(prefix="/aplicacionInsumos", tags=["Aplicaciones de Insumo"])

@router.post("/{id_cultivo}/insumos/registrar", response_model=Salida, summary="Registrar aplicación de insumo")
async def registrar_aplicacion_insumo(
        id_cultivo: str,
        insumo_data: AplicacionInsumoInsert,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para registrar esta aplicación de insumo.")
    aplicacion_insumo_dao = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo_dao.registrarAplicacionInsumo(id_cultivo, insumo_data)
    return resultado


@router.put("/{id_cultivo}/insumos/editar/{id_aplicacionInsumo}", response_model=Salida,
            summary="Editar aplicación de insumo")
async def editar_aplicacion_insumo(
        id_cultivo: str,
        id_aplicacionInsumo: str,
        insumo_data: AplicacionInsumoUpdate,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para editar esta aplicación de insumo.")
    aplicacion_insumo_dao = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo_dao.editarAplicacionInsumo(id_cultivo, id_aplicacionInsumo, insumo_data)
    return resultado


@router.delete("/{id_cultivo}/insumos/eliminar/{id_aplicacionInsumo}", response_model=Salida,
               summary="Eliminar aplicación de insumo")
async def eliminar_aplicacion_insumo(
        id_cultivo: str,
        id_aplicacionInsumo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario != "Administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar esta aplicación de insumo.")
    aplicacion_insumo_dao = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo_dao.eliminarAplicacionInsumo(id_cultivo, id_aplicacionInsumo)
    return resultado


@router.get("/{id_cultivo}/insumos/consultar/{id_aplicacionInsumo}", response_model=AplicacionInsumoSalidaIndividual,
            summary="Consultar una aplicación de insumo")
async def consultar_aplicacion_insumo(
        id_cultivo: str,
        id_aplicacionInsumo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> AplicacionInsumoSalidaIndividual:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Agricultor", "Agricultor"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para consultar esta aplicación de insumo.")
    aplicacion_insumo_dao = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo_dao.consultarAplicacionInsumo(id_cultivo, id_aplicacionInsumo)
    return resultado


@router.get("/{id_cultivo}/aplicacionInsumos", response_model=AplicacionInsumoListSalida,
            summary="Consultar lista de aplicaciones de insumo para un cultivo")
async def get_lista_aplicacion_insumo_cultivo(
        id_cultivo: str,
        request: Request,
        usuario_actual: UsuarioDetalleSalida = Depends(validarUsuario)) -> AplicacionInsumoListSalida:
    rol_usuario = usuario_actual.usuario['rol']
    if rol_usuario not in ["Administrador", "Agricultor", "Supervisor"]:
        raise HTTPException(status_code=403,
                            detail="No tiene permisos para consultar esta lista de aplicaciones de insumo.")
    aplicacion_insumo_dao = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo_dao.consultarListaAplicacionInsumo(id_cultivo)
    return resultado
