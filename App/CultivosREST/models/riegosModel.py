from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Salida(BaseModel):
    estatus: str
    mensaje: str    

#Servicio Riegos: Juan Humberto Bañales
class RiegoInsert(BaseModel):
    fechaRiego: date
    cantAgua: float
    metodoRiego: str
    duracionRiego: float
    idUsuario: str
    eliminado: bool = False
    
class RiegoParcialUpdate(BaseModel):
    fechaRiego: Optional[date] = None
    cantAgua: Optional[float] = None
    metodoRiego: Optional[str] = None
    duracionRiego: Optional[float] = None
    idUsuario: Optional[str] = None
    eliminado: Optional[bool] = None

class RiegoConsulta(RiegoInsert):
    idRiego: str

class RiegoConsultaIndividual(Salida):
    riego: RiegoConsulta | None = None
    
class RiegosSalida(BaseModel):
    riegos: list[RiegoConsulta]
