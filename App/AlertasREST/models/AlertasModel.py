from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class AlertaBase(BaseModel):
    tipoAlerta: str = Field(..., example="Alerta de riego")
    descripcion: str = Field(..., example="Falta riego en cultivo X")
    fechaGenerada: date = Field(..., example="2025-06-01")
    estadoAlerta: str = Field(..., example="Pendiente")  # Puedes limitar estados con Enum si quieres

class AlertaInsert(AlertaBase):
    pass  # Igual que base para crear

class AlertaUpdate(BaseModel):
    tipoAlerta: Optional[str]
    descripcion: Optional[str]
    fechaGenerada: Optional[date]
    estadoAlerta: Optional[str]

class AlertaSalida(AlertaBase):
    idAlerta: str  # ID generado en BD

class Salida(BaseModel):
    estatus: str
    mensaje: str
