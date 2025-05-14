from fastapi import APIRouter, Request
from typing import Any

from dao.usuariosDAO import UsuarioDAO
from models.UsuariosModel import UsuarioInsert, Salida, UsuarioUpdate, UsuariosSalida, UsuarioDetalleSalida

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=Salida, summary="Registrar un nuevo usuario")
async def registrar_usuario(usuario: UsuarioInsert, request: Request) -> Salida:
    """
    Registra un nuevo usuario en el sistema.
    - Verifica que el email no exista.
    - Valida seguridad de contraseña.
    - Comprueba que el rol sea válido.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.registrar(usuario)

@router.put("/{idUsuario}", response_model=Salida, summary="Actualizar un usuario existente")
async def actualizar_usuario(idUsuario: str, datos: UsuarioUpdate, request: Request) -> Salida:
    """
    - Verifica que el usuario con el id especificado exista.
    - Valida que el email no esté en uso por otro usuario si se modifica.
    - Si se cambia la contraseña, comprueba que cumple con la política de seguridad.
    - Actualiza únicamente los campos enviados.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.actualizar(idUsuario, datos)

@router.delete("/{idUsuario}", response_model=Salida, summary="Eliminar un usuario por su ID")
async def eliminar_usuario(idUsuario: str, request: Request) -> Salida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Comprueba que el usuario exista.
    - Elimina el usuario de la base de datos.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.eliminar(idUsuario)

@router.get("/", response_model=UsuariosSalida, summary="Consultar lista de usuarios")
async def consultaUsuarios(request: Request) -> Any:
    """
    - Recupera la lista de usuarios con campos: idUsuario, nombre, estatus y email.
    """
    usuario_DAO = UsuarioDAO(request.app.db)
    return usuario_DAO.consultaGeneral()

@router.get("/{idUsuario}", response_model=UsuarioDetalleSalida, summary="Obtener un usuario por ID")
async def obtener_usuario(idUsuario: str, request: Request) -> UsuarioDetalleSalida:
    """
    - Verifica que el ID proporcionado sea válido.
    - Comprueba que el usuario exista en la base de datos.
    - Devuelve los detalles completos del usuario.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.consultar(idUsuario)

@router.post("/login", response_model=Salida, summary="Iniciar sesión de un usuario")
async def iniciar_sesion(correo: str, contrasena: str, request: Request) -> Salida:
    """
    - Verifica que el correo exista en la base de datos.
    - Compara la contraseña ingresada con la almacenada.
    - Comprueba que el usuario esté activo (estatus=True).
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.iniciar_sesion(email=correo, password=contrasena)

@router.put("/{idUsuario}/rol", response_model=Salida, summary="Asignar o cambiar rol de un usuario")
async def asignar_rol_usuario(idUsuario: str, rol: str, request: Request) -> Salida:
    """
    - Verifica que el usuario con el id especificado exista.
    - Comprueba que el rol proporcionado sea válido.
    - Actualiza el rol del usuario.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.asignar_rol(idUsuario, rol)

@router.post("/recuperar-password", response_model=Salida, summary="Recuperar contraseña por email")
async def recuperar_password(email: str, request: Request) -> Salida:
    """
    - Verifica que el correo proporcionado exista en el sistema.
    - Devuelve la contraseña si el email está registrado.
    """
    usuario_dao = UsuarioDAO(request.app.db)
    return usuario_dao.recuperar_password(email)