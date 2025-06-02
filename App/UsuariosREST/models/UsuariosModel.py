from typing import Optional

from pydantic import BaseModel, Field

class Domicilio(BaseModel):
    calle: str
    numero: str
    colonia: str
    ciudad: str
    estado: str
    codigoPostal: str

class UsuarioInsert(BaseModel):
    nombre: str
    telefono: str
    estatus: bool
    domicilio: Domicilio | None = None
    email: str
    password: str
    rol: str

class Salida(BaseModel):
    estatus: str
    mensaje: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    estatus: Optional[bool] = None
    domicilio: Optional[Domicilio] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None

class UsuarioListado(BaseModel):
    idUsuario: str
    nombre: str
    estatus: bool
    email: str

class UsuariosSalida(Salida):
    usuarios: list[UsuarioListado]

class UsuarioDetalle(BaseModel):
    idUsuario: str
    nombre: str
    telefono: str
    estatus: bool
    domicilio: Optional[Domicilio] = None
    email: str
    password: str
    rol: str

class UsuarioDetalleSalida(Salida):
    usuario: Optional[UsuarioDetalle] = None