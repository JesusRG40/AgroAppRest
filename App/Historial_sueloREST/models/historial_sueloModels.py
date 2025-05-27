from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

class HistorialSueloBase(BaseModel):
    fechaMedicion: date
    pH: float
    nutrientes: List[dict]
    observaciones: List[str]
    idCultivo: str
    idUsuario: str
    eliminado: bool = False

class HistorialSueloInsert(HistorialSueloBase):
    pass

class HistorialSueloUpdate(BaseModel):
    fechaMedicion: Optional[date] = None
    pH: Optional[float] = None
    nutrientes: Optional[List[dict]] = None
    observaciones: Optional[List[str]] = None
    idCultivo: Optional[str] = None
    idUsuario: Optional[str] = None
    eliminado: Optional[bool] = None

class Salida(BaseModel):
    mensaje: str
    success: bool
    estatus: int

class HistorialSueloDetalle(BaseModel):
    idHistorial: str
    fechaMedicion: datetime
    pH: float
    nutrientes: List[dict]
    observaciones: List[str]
    idCultivo: str  # aquí se mostrará el nombre del cultivo
    idUsuario: str  # aquí se mostrará el nombre del usuario

class HistorialSueloDetalleSalida(Salida):
    historial: Optional[HistorialSueloDetalle] = None

class HistorialSueloSalida(BaseModel):
    historiales: List[HistorialSueloDetalle]
