from bson import ObjectId
from fastapi import APIRouter, Request, Depends, HTTPException

from dao.usuariosDAO import UsuarioDAO
from dao.actividadesusuariosDAO import ActividadUsuarioDAO
from models.ActividadesUsuariosModel import ActividadUsuarioInsert, Salida, ActividadUsuarioUpdate, \
    ActividadUsuarioDetalleSalida, ActividadesUsuariosSalida
from models.UsuariosModel import UsuarioDetalleSalida
from routes.usuariosRoutes import validarUsuario

router = APIRouter(prefix="/actividades_usuarios", tags=["ActividadesUsuarios"])

@router.post("/", response_model=Salida, summary="Registrar una nueva actividad de usuario")
async def registrar_actividad(actividad: ActividadUsuarioInsert, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Registra una nueva actividad de usuario en el sistema.
    - Verifica que los campos requeridos estén presentes y sean válidos.
    - Verifica que el cultivo y el usuario referenciados existan.
    - Solo usuarios con rol 'Administrador' o 'Supervisor' pueden registrar actividades.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar['rol'] in {"Administrador", "Supervisor"}:
        actividad_dao = ActividadUsuarioDAO(request.app.db)
        return actividad_dao.registrar(actividad)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.put("/{id_actividad}", response_model=Salida, summary="Actualizar una actividad de usuario")
async def actualizar_actividad(id_actividad: str, datos: ActividadUsuarioUpdate, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Actualiza una actividad de usuario existente.
    - Verifica que el id_actividad exista en la base de datos.
    - Valida que los campos a modificar (actividad, fechaActividad, estatus) sean válidos.
    - Verifica que el cultivo y el usuario referenciados existan, si se modifican.
    - Solo usuarios con rol 'Administrador' o 'Supervisor' pueden actualizar actividades.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] in {"Administrador", "Supervisor"}:
        actividad_dao = ActividadUsuarioDAO(request.app.db)
        return actividad_dao.actualizar(id_actividad, datos)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.delete("/{id_actividad}", response_model=Salida, summary="Eliminar (lógicamente) una actividad de usuario")
async def eliminar_actividad(id_actividad: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Elimina lógicamente una actividad de usuario (cambiando estatus a 'Cancelada').
    - Verifica que el id_actividad exista en la base de datos.
    - Solo usuarios con rol 'Administrador' o 'Supervisor' pueden eliminar actividades.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] == "Administrador":
        actividad_dao = ActividadUsuarioDAO(request.app.db)
        return actividad_dao.eliminar(id_actividad)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.get("/{id_actividad}", response_model=ActividadUsuarioDetalleSalida, summary="Obtener detalle de una actividad de usuario")
async def consultar_actividad(id_actividad: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> ActividadUsuarioDetalleSalida:
    """
    Consulta una actividad de usuario por su ID.
    - Verifica que el id_actividad exista en la base de datos.
    - Retorna información de la actividad junto con nombre del cultivo y nombre del usuario asociados.
    - Solo usuarios con rol 'Administrador' o 'Supervisor' pueden consultar actividades.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] in {"Administrador", "Supervisor"}:
        actividad_dao = ActividadUsuarioDAO(request.app.db)
        return actividad_dao.consultar(id_actividad)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.get("/", response_model=ActividadesUsuariosSalida, summary="Obtener listado de todas las actividades de usuario")
async def listar_actividades(request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> ActividadesUsuariosSalida:
    """
    Retorna la lista de todas las actividades de usuario.
    - Solo usuarios con rol 'Administrador' o 'Supervisor' pueden listar actividades.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] in {"Administrador", "Supervisor"}:
        actividad_dao = ActividadUsuarioDAO(request.app.db)
        return actividad_dao.consultaGeneral()
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")