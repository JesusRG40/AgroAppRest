from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

# Modelo base para un riego
class RiegoBase(BaseModel):
    fechaRiego: date
    cantidadAgua: float
    metodoRiego: str
    duracionRiego: float
    idUsuario: str  # Referencia al usuario que realizó el riego

# Para registrar un nuevo riego
class RiegoInsert(RiegoBase):
    pass

# Para actualizar un riego existente
class RiegoUpdate(BaseModel):
    fechaRiego: Optional[date] = None
    cantidadAgua: Optional[float] = None
    metodoRiego: Optional[str] = None
    duracionRiego: Optional[float] = None
    idUsuario: Optional[str] = None

# Para respuestas generales
class Salida(BaseModel):
    mensaje: str
    success: bool
    estatus: int

# Para mostrar un riego individual
class RiegoDetalle(BaseModel):
    idRiego: str
    fechaRiego: datetime
    cantidadAgua: float
    metodoRiego: str
    duracionRiego: float
    idUsuario: str

# Para una lista resumida de riegos
class RiegoListado(BaseModel):
    idRiego: str
    fechaRiego: date
    metodoRiego: str
    cantidadAgua: float

# Salida con un solo riego
class RiegoDetalleSalida(Salida):
    riego: Optional[RiegoDetalle] = None

# Salida con lista de riegos
class RiegosSalida(BaseModel):
    riegos: List[RiegoDetalle]