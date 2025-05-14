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
    tipoSuelo: str
    estadoActual: str
    idUsuario: str

#-------------------------------------------------
class CultivoUpdate(BaseModel):
    nomCultivo: str
    fechaSiembra: date
    fechaCosechaEst: date
    fechaCosechaReal: date | None = None
    areaCultivo: float
    tipoSuelo: str
    estadoActual: str
    idUsuario: str

#-------------------------------------------------
class CultivoSelect(BaseModel):
    _id: str
    nomCultivo: str
    fechaSiembra: date
    fechaCosechaEst: date
    fechaCosechaReal: date | None = None
    areaCultivo: float
    tipoSuelo: str
    estadoActual: str
    idUsuario: str

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

#----------------------------------------------
class UbicacionUpdate(BaseModel):
    nombreUbicacion: str
    coordenadas: Coordenadas
    superficie: float
    tipoSuelo: str
    accesoAgua: bool

#-----------------------------------------------
class UbicacionSubConsulta(UbicacionInsert):
    idUbicacion: str


class UbicacionSalidaIndividual(Salida):
    ubicacion: UbicacionSubConsulta | None = None