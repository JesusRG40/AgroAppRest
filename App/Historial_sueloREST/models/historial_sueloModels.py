from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

# Modelo base para un historial de suelo
class HistorialSueloBase(BaseModel):
    fechaMedicion: date
    pH: float
    nutrientes: List[dict]
    observaciones: List[str]
    idCultivo: str
    idUsuario: str

# Para registrar un nuevo historial de suelo
class HistorialSueloInsert(HistorialSueloBase):
    pass

# Para actualizar un historial de suelo existente
class HistorialSueloUpdate(BaseModel):
    fechaMedicion: Optional[date] = None
    pH: Optional[float] = None
    nutrientes: Optional[List[dict]] = None
    observaciones: Optional[List[str]] = None
    idCultivo: Optional[str] = None
    idUsuario: Optional[str] = None

# Para respuestas generales
class Salida(BaseModel):
    mensaje: str
    success: bool
    estatus: int

# Para mostrar un historial individual
class HistorialSueloDetalle(BaseModel):
    idHistorial: str
    fechaMedicion: datetime
    pH: float
    nutrientes: List[dict]
    observaciones: List[str]
    idCultivo: str
    idUsuario: str

# Para una lista resumida de historiales
class HistorialSueloListado(BaseModel):
    idHistorial: str
    fechaMedicion: date
    pH: float

# Salida con un solo historial
class HistorialSueloDetalleSalida(Salida):
    historial: Optional[HistorialSueloDetalle] = None

# Salida con lista de historiales
class HistorialSueloSalida(BaseModel):
    historiales: List[HistorialSueloDetalle]

