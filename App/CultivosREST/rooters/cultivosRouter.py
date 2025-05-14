from fastapi import APIRouter, Request
from models.cultivosModel import CultivoInsert, Salida, CultivoUpdate, CultivoSalidaIndividual, CultivosListSalida, \
    UbicacionInsert, UbicacionUpdate, UbicacionSalidaIndividual
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


@router.post("/{id_cultivo}/ubicaciones/agregar", response_model=Salida, tags=["Ubicacion Cultivos"])
async def registrar_ubicacion_cultivo(id_cultivo: str, ubicacion_data: UbicacionInsert, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.registrarNuevaUbicacion(id_cultivo, ubicacion_data)
    return resultado


@router.put("/{id_cultivo}/ubicaciones/editar/{id_ubicacion}", response_model=Salida, tags=["Ubicacion Cultivos"])
async def editar_ubicacion_cultivo(id_cultivo: str, id_ubicacion: str, ubicacion_data: UbicacionUpdate, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.actualizarUbicacionDeCultivo(id_cultivo, id_ubicacion, ubicacion_data)
    return resultado


@router.delete("/{id_cultivo}/ubicaciones/eliminar/{id_ubicacion}", response_model=Salida, tags=["Ubicacion Cultivos"])
async def eliminar_ubicacion_cultivo(id_cultivo: str, id_ubicacion: str, request: Request) -> Salida:
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.borrarUbicacionDeCultivo(id_cultivo, id_ubicacion)
    return resultado


@router.get("/{id_cultivo}/ubicaciones/consultar/{id_ubicacion}", response_model=UbicacionSalidaIndividual, tags=["Ubicacion Cultivos"])
async def consultar_ubicacion_cultivo(id_cultivo: str, id_ubicacion: str, request: Request) -> UbicacionSalidaIndividual:
    from dao.cultivosDAO import CultivoDAO
    cultivo_dao = CultivoDAO(request.app.db)
    resultado = cultivo_dao.consultarUbicacionDeCultivoPorId(id_cultivo, id_ubicacion)
    return resultado

