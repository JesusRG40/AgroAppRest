from fastapi import APIRouter, Request
from models.aplicacionesInsumoModel import AplicacionInsumoInsert, AplicacionInsumoUpdate, \
    AplicacionInsumoSalidaIndividual, AplicacionInsumoListSalida
from models.cultivosModel import Salida
from dao.aplicacionesInsumoDAO import AplicacionesInsumoDAO

router = APIRouter(prefix="/aplicacionInsumos")

# Endpoint para registrar la aplicación de un insumo en un cultivo
@router.post("/{id_cultivo}/insumos/registrar", response_model=Salida, tags=["Aplicaciones de Insumo"])
async def registrar_aplicacion_insumo(id_cultivo: str, insumo_data: AplicacionInsumoInsert, request: Request) -> Salida:
    aplicacion_insumo = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo.registrarAplicacionInsumo(id_cultivo, insumo_data)
    return resultado


# Endpoint para editar una aplicación de insumo específica
@router.put("/{id_cultivo}/insumos/editar/{id_aplicacionInsumo}", response_model=Salida, tags=["Aplicaciones de Insumo"])
async def editar_aplicacion_insumo(id_cultivo: str, id_aplicacion_insumo: str, insumo_data: AplicacionInsumoUpdate, request: Request) -> Salida:
    aplicacion_insumo = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo.editarAplicacionInsumo(id_cultivo, id_aplicacion_insumo, insumo_data)
    return resultado


# Endpoint para eliminar una aplicación de insumo específica
@router.delete("/{id_cultivo}/insumos/eliminar/{id_aplicacionInsumo}", response_model=Salida, tags=["Aplicaciones de Insumo"])
async def eliminar_aplicacion_insumo(id_cultivo: str, id_aplicacionInsumo: str, request: Request) -> Salida:
    aplicacion_insumo = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo.eliminarAplicacionInsumo(id_cultivo, id_aplicacionInsumo)
    return resultado


# Endpoint para consultar una aplicación de insumo específica por su ID
@router.get("/{id_cultivo}/insumos/consultar/{id_aplicacionInsumo}", response_model=AplicacionInsumoSalidaIndividual, tags=["Aplicaciones de Insumo"])
async def consultar_aplicacion_insumo(id_cultivo: str, id_aplicacionInsumo: str, request: Request) -> AplicacionInsumoSalidaIndividual:
    aplicacion_insumo = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo.consultarAplicacionInsumo(id_cultivo, id_aplicacionInsumo)
    return resultado


@router.get("/{id_cultivo}/aplicacionInsumos", response_model=AplicacionInsumoListSalida, tags=["Aplicaciones de Insumo"], summary="Consultar lista de aplicaciones de insumo para un cultivo")
async def get_lista_aplicacion_insumo_cultivo(id_cultivo: str, request: Request) -> AplicacionInsumoListSalida:
    aplicacion_insumo = AplicacionesInsumoDAO(request.app.db)
    resultado = aplicacion_insumo.consultarListaAplicacionInsumo(id_cultivo)
    return resultado