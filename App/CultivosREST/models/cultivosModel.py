from pydantic import BaseModel
from datetime import date, datetime

class Salida(BaseModel):
    estatus: str
    mensaje: str

class CultivoInsert(BaseModel):
    nomCultivo: str
    fechaSiembra: date
    fechaCosechaEst: date
    fechaCosechaReal: date | None = None
    areaCultivo: float
    idUsuario: str

#-------------------------------------------------
class CultivoUpdate(BaseModel):
    nomCultivo: str | None = None
    fechaSiembra: date | None = None
    fechaCosechaEst: date | None = None
    fechaCosechaReal: date | None = None
    areaCultivo: float | None = None
    estadoActual: str | None = None
    idUsuario: str | None = None

#-------------------------------------------------
class CultivoSelect(BaseModel):
    _id: str
    nomCultivo: str
    fechaSiembra: date
    fechaCosechaEst: date
    fechaCosechaReal: date | None = None
    areaCultivo: float
    estadoActual: str
    nombreUsuario: str | None = None

class CultivoSalidaIndividual(Salida):
    cultivo: CultivoSelect | None = None

#--------------------------------------------------
class CultivosListSalida(Salida):
    cultivos: list[CultivoSelect] = []

#--------------------------------------------------
class Coordenadas(BaseModel):
    latitud: float
    longitud: float

class UbicacionInsert(BaseModel):
    nombreUbicacion: str
    coordenadas: Coordenadas
    superficie: float
    tipoSuelo: str
    accesoAgua: bool
    estado: str
    municipio: str
    localidad: str
    cp: str
    detalles: str | None = None

#----------------------------------------------
class UbicacionUpdate(BaseModel):
    nombreUbicacion: str | None = None
    coordenadas: Coordenadas | None = None
    superficie: float | None = None
    tipoSuelo: str | None = None
    accesoAgua: bool | None = None
    estado: str | None = None
    municipio: str | None = None
    localidad: str | None = None
    cp: str | None = None
    detalles: str | None = None

#-----------------------------------------------
class UbicacionSubConsulta(UbicacionInsert):
    nombreCultivo: str


class UbicacionSalidaIndividual(Salida):
    ubicacion: UbicacionSubConsulta | None = None

#-------------------------------------------------
class SeguimientoInsert(BaseModel):
    fechaRevision: date
    estadoCultivo: str
    observaciones: list[str] | None = None
    recomendaciones: list[str] | None = None
    idUsuario: str

#---------------------------------------------------
class SeguimientoUpdate(BaseModel):
    fechaRevision: date | None = None
    estadoCultivo: str | None = None
    observaciones: list[str] | None = None
    recomendaciones: list[str] | None = None
    idUsuario: str | None = None

#-------------------------------------------------------------
class SeguimientoSelect(BaseModel):
    _id: str
    fechaRevision: date
    estadoCultivo: str
    observaciones: list[str]
    recomendaciones: list[str]
    idCultivo: str
    nombreUsuario: str

class SeguimientoSalidaIndividual(Salida):
    seguimiento: SeguimientoSelect | None = None

#------------------------------------------------
class SeguimientoSubConsulta(BaseModel):
    fecha: datetime
    etapaCultivo: str
    descripcion: str
    observacionesAdicionales: str | None = None

#-------------------------------------------------------

class SeguimientoListSalida(Salida):
    nombreCultivo: str | None = None
    seguimientos: list[SeguimientoSelect] | None = None
