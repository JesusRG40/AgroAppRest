from fastapi import APIRouter, Request
from models.cultivosModel import CultivoInsert, Salida, CultivoUpdate, CultivoSalidaIndividual, CultivosListSalida, \
    UbicacionInsert, UbicacionUpdate, UbicacionSalidaIndividual, SeguimientoInsert, SeguimientoUpdate, \
    SeguimientoSalidaIndividual, SeguimientoListSalida
from dao.cultivosDAO import CultivoDAO


router = APIRouter(prefix="/cultivos")

# Endpoint para registrar un nuevo cultivo
@router.post("/agregar", response_model=Salida, tags=["Cultivos"])
async def registrar_cultivo(cultivo_data: CultivoInsert, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.agregarCultivo(cultivo_data)
    return resultado


# Endpoint para editar un cultivo existente
@router.put("/editar/{id_cultivo}", response_model=Salida, tags=["Cultivos"])
async def editar_cultivo(id_cultivo: str, cultivo_update_data: CultivoUpdate, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.actualizarCultivo(id_cultivo, cultivo_update_data)
    return resultado


# Endpoint para eliminar un cultivo
@router.delete("/eliminar/{id_cultivo}", response_model=Salida, tags=["Cultivos"])
async def eliminar_cultivo(id_cultivo: str, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.borrarCultivo(id_cultivo)
    return resultado


# Endpoint para consultar un cultivo por su ID
@router.get("/consultar/{id_cultivo}", response_model=CultivoSalidaIndividual, tags=["Cultivos"])
async def consultar_cultivo(id_cultivo: str, request: Request) -> CultivoSalidaIndividual:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarCultivoPorId(id_cultivo)
    return resultado


# Endpoint para consultar la lista de todos los cultivos
@router.get("/", response_model=CultivosListSalida, tags=["Cultivos"])
async def consultar_lista_cultivos(request: Request) -> CultivosListSalida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarListaDeCultivos()
    return resultado


@router.post("/{id_cultivo}/ubicacion/agregar", response_model=Salida, tags=["Ubicacion Cultivos"])
async def registrar_ubicacion_cultivo(id_cultivo: str, ubicacion_data: UbicacionInsert, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.registrarNuevaUbicacion(id_cultivo, ubicacion_data)
    return resultado


@router.put("/{id_cultivo}/ubicacion/editar", response_model=Salida, tags=["Ubicacion Cultivos"])
async def editar_ubicacion_cultivo(id_cultivo: str, ubicacion_data: UbicacionUpdate, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.actualizarUbicacionCultivo(id_cultivo, ubicacion_data)
    return resultado



@router.get("/{id_cultivo}/ubicacion/consultar", response_model=UbicacionSalidaIndividual, tags=["Ubicacion Cultivos"])
async def consultar_ubicacion_cultivo(id_cultivo: str, request: Request) -> UbicacionSalidaIndividual:
    from dao.cultivosDAO import CultivoDAO
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarUbicacionDeCultivo(id_cultivo)
    return resultado


# Endpoint para registrar un nuevo seguimiento a un cultivo
@router.post("/{id_cultivo}/seguimientos/agregar", response_model=Salida, tags=["Seguimientos-Cultivo"])
async def registrar_seguimiento_cultivo(id_cultivo: str, seguimiento_data: SeguimientoInsert, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.agregar_seguimiento(id_cultivo, seguimiento_data)
    return resultado


# Endpoint para editar un seguimiento existente de un cultivo
@router.put("/{id_cultivo}/seguimientos/editar/{id_seguimiento}", response_model=Salida, tags=["Seguimientos-Cultivo"])
async def editar_seguimiento_cultivo(id_cultivo: str, id_seguimiento: str, seguimiento_data: SeguimientoUpdate, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.editar_seguimiento(id_cultivo, id_seguimiento, seguimiento_data)
    return resultado


# Endpoint para eliminar un seguimiento existente de un cultivo
@router.delete("/{id_cultivo}/seguimientos/eliminar/{id_seguimiento}", response_model=Salida, tags=["Seguimientos-Cultivo"])
async def eliminar_seguimiento_cultivo(id_cultivo: str, id_seguimiento: str, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.eliminar_seguimiento(id_cultivo, id_seguimiento)
    return resultado


# Endpoint para consultar un seguimiento específico de un cultivo
@router.get("/{id_cultivo}/seguimientos/consultar/{id_seguimiento}", response_model=SeguimientoSalidaIndividual,tags=["Seguimientos-Cultivo"])
async def consultar_seguimiento_especifico_cultivo(id_cultivo: str, id_seguimiento: str, request: Request) -> SeguimientoSalidaIndividual:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultar_seguimiento_por_id(id_cultivo, id_seguimiento)
    return resultado


# Endpoint para consultar la lista de seguimientos de un cultivo
@router.get("/{id_cultivo}/seguimientos/consultar", response_model=SeguimientoListSalida, tags=["Seguimientos-Cultivo"])
async def consultar_lista_seguimiento(id_cultivo: str, request: Request) -> SeguimientoListSalida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarListaSeguimiento(id_cultivo)
    return resultado
