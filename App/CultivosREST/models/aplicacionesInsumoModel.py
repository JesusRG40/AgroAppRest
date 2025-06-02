from pydantic import BaseModel
from datetime import date, datetime

class Salida(BaseModel):
    estatus: str
    mensaje: str

class AplicacionInsumoInsert(BaseModel):
    cantidadAplicada: float         # Ej: 20.5
    fechaAplicacion: date | None = None
    metodoAplicacion: str | None = None # Ej: "Foliar", "Al suelo", "Riego"
    observaciones: str | None = None
    idUsuario : str
    idInsumo: str

#--------------------------------------------------------
class AplicacionInsumoUpdate(BaseModel):
    cantidadAplicada: float | None = None
    fechaAplicacion: date | None = None
    metodoAplicacion: str | None = None
    observaciones: str | None = None
    idUsuario: str | None = None
    idInsumo: str | None = None

#---------------------------------------------------
class AplicacionInsumoSubConsulta(BaseModel):
    _id: str
    tipoInsumo: str
    nombreInsumo: str
    cantidadAplicada: float
    unidadMedida: str
    fechaAplicacion: date
    metodoAplicacion: str
    observaciones: str | None = None
    nombreUsuario: str

class AplicacionInsumoSalidaIndividual(Salida):
    insumo: AplicacionInsumoSubConsulta | None = None

#------------------------------------------------------
class AplicacionInsumoDetalle(BaseModel):
    _id: str
    fechaAplicacion: date
    cantAplicada: float
    nombreInsumo: str
    nombreUsuario: str

class AplicacionInsumoListSalida(Salida):
    aplicaciones: list[AplicacionInsumoDetalle] | None = None
