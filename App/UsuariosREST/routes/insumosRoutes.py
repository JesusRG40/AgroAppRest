from fastapi import APIRouter, Request, Depends, HTTPException

from dao.insumosDAO import InsumoDAO
from models.InsumosModel import InsumoInsert, Salida, InsumoUpdate, InsumoDetalleSalida, InsumosSalida
from models.UsuariosModel import UsuarioDetalleSalida
from routes.usuariosRoutes import validarUsuario

router = APIRouter(prefix="/insumos", tags=["Insumos"])

@router.post("/", response_model=Salida, summary="Registrar un nuevo insumo")
async def registrar_insumo(insumo: InsumoInsert, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Registra un nuevo insumo en el sistema.
    - Verifica que los campos obligatorios estén presentes y sean válidos.
    - Verifica que 'cantDisponible' sea un valor numérico >= 0.
    - Verifica que 'tipoInsumo' pertenezca a la lista de tipos válidos.
    - Comprueba la unicidad de 'nombreInsumo'.
    - Solo usuarios con rol 'Administrador' pueden registrar insumos.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] == "Administrador":
        insumo_dao = InsumoDAO(request.app.db)
        return insumo_dao.registrar(insumo)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.put("/{id_insumo}", response_model=Salida, summary="Editar un insumo existente")
async def actualizar_insumo(id_insumo: str, insumo_update: InsumoUpdate, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Actualiza un insumo existente.
    - Verifica que el insumo con el ID proporcionado exista.
    - Valida que los campos modificados cumplan con las reglas de negocio:
        - nombre no vacío
        - cantidad mayor o igual a cero
        - tipo válido
        - unicidad de nombre si se cambia
    - Solo usuarios con rol 'Administrador' pueden editar insumos.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] == "Administrador":
        insumo_dao = InsumoDAO(request.app.db)
        return insumo_dao.actualizar(id_insumo, insumo_update)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.delete("/{id_insumo}", response_model=Salida, summary="Eliminar lógicamente un insumo")
async def eliminar_insumo(id_insumo: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> Salida:
    """
    Elimina lógicamente un insumo existente (cambia su estatus a 'Inactivo').
    - Verifica que el insumo con el ID proporcionado exista.
    - Verifica que el insumo no esté ya inactivo.
    - Solo usuarios con rol 'Administrador' pueden eliminar insumos.
    """
    usuar = respuesta.usuario
    if respuesta.estatus == "OK" and usuar["rol"] == "Administrador":
        insumo_dao = InsumoDAO(request.app.db)
        return insumo_dao.eliminar(id_insumo)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.get("/{id_insumo}", response_model=InsumoDetalleSalida, summary="Obtener detalles de un insumo")
async def obtener_insumo(id_insumo: str, request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> InsumoDetalleSalida:
    """
    Consulta los detalles de un insumo específico por su ID.
    - Verifica que el ID proporcionado sea válido.
    - Devuelve la información del insumo si existe y está activo.
    - Usuarios con cualquier rol autenticado pueden consultar insumos.
    """
    if respuesta.estatus == "OK":
        insumo_dao = InsumoDAO(request.app.db)
        return insumo_dao.obtener_por_id(id_insumo)
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")

@router.get("/", response_model=InsumosSalida, summary="Consultar listado general de insumos")
async def obtener_lista_insumos(request: Request, respuesta: UsuarioDetalleSalida = Depends(validarUsuario)) -> InsumosSalida:
    """
    Consulta general de todos los insumos activos.
    - Usuarios con cualquier rol autenticado pueden consultar insumos.
    """
    if respuesta.estatus == "OK":
        insumo_dao = InsumoDAO(request.app.db)
        return insumo_dao.consultaGeneral()
    else:
        raise HTTPException(status_code=403, detail="Sin autorización")