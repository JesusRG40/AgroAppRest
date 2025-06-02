from pydantic import BaseModel
from datetime import date
from typing import List, Optional, Literal

class Salida(BaseModel):
    estatus: str
    mensaje: str    

# Modelo para insertar un riego
class RiegoInsert(BaseModel):
    fechaEsperada: date                    # fecha esperada para el riego
    fechaAplicada: Optional[date] = None  # fecha cuando se aplicó el riego, opcional
    cantAgua: float
    metodoRiego: str
    duracionRiego: float
    idUsuario: str
    status: Literal["Pendiente", "Aplicado", "Cancelado"] = "Pendiente"  # Nuevo campo status

# Modelo para actualización parcial
class RiegoParcialUpdate(BaseModel):
    fechaEsperada: Optional[date] = None
    fechaAplicada: Optional[date] = None
    cantAgua: Optional[float] = None
    metodoRiego: Optional[str] = None
    duracionRiego: Optional[float] = None
    idUsuario: Optional[str] = None
    status: Optional[Literal["Pendiente", "Aplicado", "Cancelado"]] = None

class RiegoConsulta(RiegoInsert):
    idRiego: str

class RiegoConsultaIndividual(Salida):
    riego: Optional[RiegoConsulta] = None

class RiegosSalida(BaseModel):
    estatus: str
    mensaje: str
    riegos: List[RiegoConsulta]
