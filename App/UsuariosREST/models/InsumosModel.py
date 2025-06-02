from typing import Optional, List
from pydantic import BaseModel, Field


class InsumoInsert(BaseModel):
    nombreInsumo: str
    tipoInsumo: str
    cantDisponible: float
    unidadMedida: str


class InsumoUpdate(BaseModel):
    nombreInsumo: Optional[str] = None
    tipoInsumo: Optional[str] = None
    cantDisponible: Optional[float] = None
    unidadMedida: Optional[str] = None


class InsumoListado(BaseModel):
    idInsumo: str
    nombreInsumo: str
    tipoInsumo: str
    cantDisponible: float
    unidadMedida: str


class InsumoDetalle(BaseModel):
    idInsumo: str
    nombreInsumo: str
    tipoInsumo: str
    cantDisponible: float
    unidadMedida: str


class Salida(BaseModel):
    estatus: str
    mensaje: str


class InsumosSalida(Salida):
    insumos: List[InsumoListado]


class InsumoDetalleSalida(Salida):
    insumo: Optional[InsumoDetalle] = None