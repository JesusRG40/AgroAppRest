from bson import ObjectId
from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Any

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dao.usuariosDAO import UsuarioDAO
from models.UsuariosModel import UsuarioInsert, Salida, UsuarioUpdate, UsuariosSalida, UsuarioDetalleSalida

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

security = HTTPBasic()

async def validarUsuario(request: Request, credenciales: HTTPBasicCredentials=Depends(security)) -> UsuarioDetalleSalida:
    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.iniciar_sesion(credenciales.username, credenciales.password)

@router.post("/", response_model=Salida, summary="Registrar un nuevo usuario")
async def registrar_usuario(usuario: UsuarioInsert, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Registra un nuevo usuario en el sistema.
    - Verifica que el email no exista.
    - Valida seguridad de contraseña.
    - Comprueba que el rol sea válido.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == 'OK' and usuar['rol'] == 'Administrador':
        usuario_dao = UsuarioDAO(request.app.db)
        return usuario_dao.registrar(usuario)
    else:
        raise HTTPException(status_code=404, detail="Sin autorizacion")

@router.put("/{idUsuario}", response_model=Salida, summary="Actualizar un usuario existente")
async def actualizar_usuario(idUsuario: str, datos: UsuarioUpdate, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    - Verifica que el usuario con el id especificado exista.
    - Valida que el email no esté en uso por otro usuario si se modifica.
    - Si se cambia la contraseña, comprueba que cumple con la política de seguridad.
    - Actualiza únicamente los campos enviados.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == 'OK' and usuar['rol'] == 'Administrador':
        usuario_dao = UsuarioDAO(request.app.db)
        print(usuar)
        return usuario_dao.actualizar(idUsuario, datos)
    else:
        if respuesta.estatus == 'OK' and usuar['_id'] == ObjectId(idUsuario):
            usuario_dao = UsuarioDAO(request.app.db)
            return usuario_dao.actualizar(idUsuario, datos)
        else:
            raise HTTPException(status_code=404, detail="Sin autorizacion")

@router.delete("/{idUsuario}", response_model=Salida, summary="Desactivar un usuario por su ID")
async def eliminar_usuario(idUsuario: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Comprueba que el usuario exista.
    - Desactiva el usuario de la base de datos.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == 'OK' and usuar['rol'] == 'Administrador':
        usuario_dao = UsuarioDAO(request.app.db)
        return usuario_dao.eliminar(idUsuario)
    else:
        raise HTTPException(status_code=404, detail="Sin autorizacion")

@router.get("/", response_model=UsuariosSalida, summary="Consultar lista de usuarios")
async def consultaUsuarios(request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Any:
    """
    - Recupera la lista de usuarios con campos: idUsuario, nombre, estatus y email.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == 'OK' and usuar['rol'] == 'Administrador':
        usuario_DAO = UsuarioDAO(request.app.db)
        return usuario_DAO.consultaGeneral()
    else:
        raise HTTPException(status_code=404, detail="Sin autorizacion")

@router.get("/{idUsuario}", response_model=UsuarioDetalleSalida, summary="Obtener un usuario por ID")
async def obtener_usuario(idUsuario: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> UsuarioDetalleSalida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Comprueba que el usuario exista en la base de datos.
    - Devuelve los detalles completos del usuario.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == 'OK' and usuar['rol'] == 'Administrador':
        usuario_dao = UsuarioDAO(request.app.db)
        return usuario_dao.consultar(idUsuario)
    else:
        if respuesta.estatus == 'OK' and usuar['_id'] == ObjectId(idUsuario):
            usuario_dao = UsuarioDAO(request.app.db)
            return usuario_dao.consultar(idUsuario)
        else:
            raise HTTPException(status_code=404, detail="Sin autorizacion")

@router.post("/login", response_model=Salida, summary="Iniciar sesión de un usuario")
async def iniciar_sesion(correo: str, contrasena: str, request: Request) -> Salida:
    """
    - Verifica que el correo exista en la base de datos.
    - Compara la contraseña ingresada con la almacenada.
    - Comprueba que el usuario esté activo (estatus=True).
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.iniciar_sesion(email=correo, password=contrasena)

@router.post("/recuperar-password", response_model=Salida, summary="Recuperar contraseña por email")
async def recuperar_password(email: str, request: Request) -> Salida:
    """
    - Verifica que el correo proporcionado exista en el sistema.
    - Devuelve la contraseña si el email está registrado.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.recuperar_password(email)