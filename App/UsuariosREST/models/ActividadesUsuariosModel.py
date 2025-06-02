from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ActividadUsuarioInsert(BaseModel):
    actividad: str
    fechaActividad: datetime
    estatus: str
    idCultivo: str
    idUsuario: str


class ActividadUsuarioUpdate(BaseModel):
    actividad: Optional[str] = None
    fechaActividad: Optional[datetime] = None
    estatus: Optional[str] = None
    idCultivo: Optional[str] = None
    idUsuario: Optional[str] = None


class ActividadUsuarioListado(BaseModel):
    idActividad: str
    actividad: str
    fechaActividad: datetime
    estatus: str
    idCultivo: str
    idUsuario: str
    nombreCultivo: Optional[str] = None
    nombreUsuario: Optional[str] = None


class ActividadUsuarioDetalle(BaseModel):
    idActividad: str
    actividad: str
    fechaActividad: datetime
    estatus: str
    idCultivo: str
    idUsuario: str
    nombreCultivo: Optional[str] = None
    nombreUsuario: Optional[str] = None


class Salida(BaseModel):
    estatus: str
    mensaje: str


class ActividadesUsuariosSalida(Salida):
    actividades: List[ActividadUsuarioListado]


class ActividadUsuarioDetalleSalida(Salida):
    actividad: Optional[ActividadUsuarioDetalle] = None