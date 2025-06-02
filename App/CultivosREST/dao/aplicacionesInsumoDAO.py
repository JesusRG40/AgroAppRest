from datetime import datetime
from bson import ObjectId
from models.aplicacionesInsumoModel import AplicacionInsumoInsert, AplicacionInsumoUpdate, \
    AplicacionInsumoSalidaIndividual, AplicacionInsumoSubConsulta, AplicacionInsumoListSalida, AplicacionInsumoDetalle
from models.cultivosModel import Salida
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database

class AplicacionesInsumoDAO:
    def __init__(self, db):
        self.db = db

    def registrarAplicacionInsumo(self, id_cultivo: str, insumo_data: AplicacionInsumoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar datos de entrada (tus validaciones existentes)

            if not (isinstance(insumo_data.cantidadAplicada, (int, float)) and insumo_data.cantidadAplicada > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "La cantidad aplicada debe ser un número mayor a cero."
                return salida

            # 2. Validar ID del cultivo y su existencia
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            cultivo_existente = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True}, {"_id": 1}
            )
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            # 3. Validar idUsuario
            if not hasattr(insumo_data, 'idUsuario') or not insumo_data.idUsuario:
                salida.estatus = "ERROR"
                salida.mensaje = "El idUsuario es obligatorio para registrar la aplicación."
                return salida
            try:
                obj_id_usuario = ObjectId(insumo_data.idUsuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idUsuario proporcionado no es válido."
                return salida
            usuario_existente = self.db.usuarios.find_one({"_id": obj_id_usuario}, {"_id": 1})
            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"El usuario con ID '{insumo_data.idUsuario}' no existe."
                return salida

            # 4. Validar idInsumo (NUEVO)
            if not hasattr(insumo_data, 'idInsumo') or not insumo_data.idInsumo:
                salida.estatus = "ERROR"
                salida.mensaje = "El idInsumo es obligatorio para registrar la aplicación."
                return salida
            try:
                obj_id_insumo_ref = ObjectId(insumo_data.idInsumo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idInsumo proporcionado no es válido."
                return salida
            # Verificar que el insumo exista en la colección 'insumos'
            insumo_existente_ref = self.db.insumos.find_one({"_id": obj_id_insumo_ref}, {"_id": 1})
            if not insumo_existente_ref:
                salida.estatus = "ERROR"
                salida.mensaje = f"El insumo con ID '{insumo_data.idInsumo}' no existe en la base de datos."
                return salida

            # 5. Preparar el documento para la inserción
            insumo_dict = jsonable_encoder(insumo_data)
            insumo_dict["_id"] = ObjectId()  # ID único para el subdocumento de aplicación
            insumo_dict["idUsuario"] = obj_id_usuario  # Guardar ObjectId validado
            insumo_dict["idInsumo"] = obj_id_insumo_ref  # Guardar ObjectId validado del insumo


            # 6. Actualizar el cultivo, añadiendo la aplicación al array 'aplicacionesInsumos'
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$push": {"aplicacionesInsumos": insumo_dict}}
            )

            # 7. Verificar resultado
            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Aplicación de insumo registrada con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = "Se encontró el cultivo, pero no se pudo registrar la aplicación (no hubo modificación)."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al registrar la aplicación (cultivo no encontrado)."

        except Exception as ex:
            print(f"Error en CultivoDAO.registrarAplicacionInsumo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar la aplicación del insumo. Consulte al administrador."
        return salida


    def editarAplicacionInsumo(self, id_cultivo: str, id_insumo_aplicacion: str,
                               insumo_data: AplicacionInsumoUpdate) -> Salida:

        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar IDs
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
                obj_id_insumo_app = ObjectId(id_insumo_aplicacion)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID de cultivo o de aplicación de insumo no válido."
                return salida

            # 2. Construir payload de actualización
            update_payload = {}
            insumo_update_dict = insumo_data.model_dump(exclude_unset=True)

            if not insumo_update_dict:
                salida.estatus = "INFO"
                salida.mensaje = "No se proporcionaron datos para actualizar."
                return salida

            # Validaciones existentes
            if 'cantidadAplicada' in insumo_update_dict:
                if not (isinstance(insumo_update_dict['cantidadAplicada'], (int, float)) and insumo_update_dict[
                    'cantidadAplicada'] > 0):
                    salida.estatus = "ERROR"
                    salida.mensaje = "Cantidad aplicada debe ser un número mayor a cero."
                    return salida

            # Validar y preparar idUsuario si se actualiza
            if 'idUsuario' in insumo_update_dict and insumo_update_dict['idUsuario'] is not None:
                try:
                    obj_id_usuario_update = ObjectId(insumo_update_dict['idUsuario'])
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Formato del nuevo idUsuario no válido."
                    return salida
                usuario_existente = self.db.usuarios.find_one({"_id": obj_id_usuario_update}, {"_id": 1})
                if not usuario_existente:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"Nuevo usuario con ID '{insumo_update_dict['idUsuario']}' no existe."
                    return salida
                insumo_update_dict['idUsuario'] = obj_id_usuario_update  # Usar el ObjectId
            elif 'idUsuario' in insumo_update_dict and insumo_update_dict['idUsuario'] is None:
                del insumo_update_dict['idUsuario']  # Evitar setear a null si no se desea

            # Validar y preparar idInsumo si se actualiza (NUEVO)
            if 'idInsumo' in insumo_update_dict and insumo_update_dict['idInsumo'] is not None:
                try:
                    obj_id_insumo_ref_update = ObjectId(insumo_update_dict['idInsumo'])
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Formato del nuevo idInsumo no válido."
                    return salida
                insumo_ref_existente = self.db.insumos.find_one({"_id": obj_id_insumo_ref_update}, {"_id": 1})
                if not insumo_ref_existente:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"Nuevo insumo con ID '{insumo_update_dict['idInsumo']}' no existe."
                    return salida
                insumo_update_dict['idInsumo'] = obj_id_insumo_ref_update  # Usar el ObjectId
            elif 'idInsumo' in insumo_update_dict and insumo_update_dict['idInsumo'] is None:
                del insumo_update_dict['idInsumo']  # Evitar setear a null

            if not insumo_update_dict:
                salida.estatus = "INFO"
                salida.mensaje = "No hay campos válidos para actualizar."
                return salida

            for key, value in insumo_update_dict.items():
                update_payload[f"aplicacionesInsumos.$.{key}"] = value

            # 3. Realizar la actualización
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo, "aplicacionesInsumos._id": obj_id_insumo_app},
                {"$set": update_payload}
            )

            # 4. Verificar resultado
            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = "Aplicación del insumo actualizada con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "INFO"
                salida.mensaje = "Registro encontrado, pero datos no produjeron cambios."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró cultivo ID '{id_cultivo}' o aplicación de insumo ID '{id_insumo_aplicacion}'."

        except Exception as ex:
            print(f"Error en CultivoDAO.editarAplicacionInsumo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al editar la aplicación del insumo. Consulte al administrador."
        return salida


    def eliminarAplicacionInsumo(self, id_cultivo: str, id_insumo: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar los IDs
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
                obj_id_insumo = ObjectId(id_insumo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "Uno de los IDs proporcionados (cultivo o insumo) no tiene un formato válido."
                return salida


            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$pull": {"aplicacionesInsumos": {"_id": obj_id_insumo}}}
            )

            # 3. Verificar el resultado de la operación
            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = "La aplicación del insumo fue eliminada con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = (f"Se encontró el cultivo con ID '{id_cultivo}', pero no se encontró un registro "
                                  f"de insumo con ID '{id_insumo}' para eliminar.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID '{id_cultivo}'."

        except Exception as ex:
            print(f"Error en CultivoDAO.eliminarAplicacionInsumo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar la aplicación del insumo. Consulte al administrador."

        return salida


    def consultarAplicacionInsumo(self, id_cultivo: str, id_insumo_aplicacion: str) -> AplicacionInsumoSalidaIndividual:

        salida = AplicacionInsumoSalidaIndividual(estatus="", mensaje="", insumo=None)
        try:
            # 1. Validar los IDs
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
                obj_id_insumo_app = ObjectId(id_insumo_aplicacion)  # ID of the specific application
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID de cultivo o de aplicación de insumo no tiene un formato válido."
                return salida

            # 2. Buscar el cultivo y proyectar solo la aplicación de insumo que coincida
            filtro = {"_id": obj_id_cultivo, "aplicacionesInsumos._id": obj_id_insumo_app}
            proyeccion = {"aplicacionesInsumos.$": 1, "_id": 0}  # Get only the matching sub-document

            cultivo_con_aplicacion = self.db.cultivos.find_one(filtro, proyeccion)

            # 3. Procesar el resultado
            if cultivo_con_aplicacion and "aplicacionesInsumos" in cultivo_con_aplicacion and cultivo_con_aplicacion[
                "aplicacionesInsumos"]:
                aplicacion_dict_db = cultivo_con_aplicacion["aplicacionesInsumos"][0]

                nombre_usuario_str = "Usuario Desconocido"
                id_usuario_obj = aplicacion_dict_db.get("idUsuario")
                if isinstance(id_usuario_obj, ObjectId):
                    usuario_doc = self.db.usuarios.find_one({"_id": id_usuario_obj}, {"nombre": 1})
                    if usuario_doc and "nombre" in usuario_doc:
                        nombre_usuario_str = usuario_doc["nombre"]
                    elif usuario_doc:
                        nombre_usuario_str = f"Usuario (ID: {str(id_usuario_obj)}) sin nombre"

                nombre_insumo_str = "Insumo Desconocido"
                tipo_insumo_str = "Tipo Desconocido"
                unidad_medida_str = "Unidad Desconocida"

                id_insumo_ref_obj = aplicacion_dict_db.get("idInsumo")
                if isinstance(id_insumo_ref_obj, ObjectId):

                    insumo_ref_doc = self.db.insumos.find_one(
                        {"_id": id_insumo_ref_obj},
                        {"nombreInsumo": 1, "tipoInsumo": 1, "unidadMedida": 1}
                    )
                    if insumo_ref_doc:
                        nombre_insumo_str = insumo_ref_doc.get("nombreInsumo", nombre_insumo_str)
                        tipo_insumo_str = insumo_ref_doc.get("tipoInsumo", tipo_insumo_str)
                        unidad_medida_str = insumo_ref_doc.get("unidadMedida", unidad_medida_str)

                datos_para_subconsulta = {
                    "_id": str(aplicacion_dict_db["_id"]),  # _id of the application sub-document
                    "tipoInsumo": tipo_insumo_str,
                    "nombreInsumo": nombre_insumo_str,
                    "cantidadAplicada": aplicacion_dict_db.get("cantidadAplicada"),
                    "unidadMedida": unidad_medida_str,
                    "fechaAplicacion": aplicacion_dict_db.get("fechaAplicacion"),
                    "metodoAplicacion": aplicacion_dict_db.get("metodoAplicacion"),
                    "observaciones": aplicacion_dict_db.get("observaciones"),  # Will be None if not present
                    "nombreUsuario": nombre_usuario_str
                }

                try:
                    salida.insumo = AplicacionInsumoSubConsulta(**datos_para_subconsulta)
                    salida.estatus = "OK"
                    salida.mensaje = "Registro de aplicación de insumo encontrado."
                except Exception as pydantic_ex:
                    print(f"Error al mapear datos a AplicacionInsumoSubConsulta: {pydantic_ex}")
                    print(f"Datos problemáticos: {datos_para_subconsulta}")
                    salida.estatus = "ERROR"
                    salida.mensaje = "Error al procesar datos de la aplicación del insumo."

            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró aplicación de insumo ID '{id_insumo_aplicacion}' en cultivo ID '{id_cultivo}'."

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarAplicacionInsumo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la aplicación del insumo."
            salida.insumo = None
        return salida



    def consultarListaAplicacionInsumo(self, id_cultivo: str) -> AplicacionInsumoListSalida:
        salida = AplicacionInsumoListSalida(estatus="", mensaje="", aplicaciones=[])  # Default to empty list
        try:
            # Convertir id_cultivo a ObjectId
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Buscar el cultivo activo y proyectar el array 'aplicacionesInsumos' y 'nomCultivo'
            cultivo_doc = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True},
                {"aplicacionesInsumos": 1, "nomCultivo": 1, "_id": 0}
            )

            if not cultivo_doc:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            nombre_cultivo_para_mensaje = cultivo_doc.get("nomCultivo", id_cultivo)

            lista_aplicaciones_db = cultivo_doc.get("aplicacionesInsumos")

            if not lista_aplicaciones_db:
                salida.estatus = "OK"
                salida.mensaje = (f"El cultivo '{nombre_cultivo_para_mensaje}' (ID: {id_cultivo}) "
                                  f"no tiene aplicaciones de insumo registradas.")
                salida.aplicaciones = []
                return salida

            aplicaciones_procesadas_list = []
            for app_item_db in lista_aplicaciones_db:

                nombre_del_insumo_str = "Insumo Desconocido"
                id_insumo_ref_obj = app_item_db.get("idInsumo")
                if isinstance(id_insumo_ref_obj, ObjectId):
                    insumo_ref_doc = self.db.insumos.find_one({"_id": id_insumo_ref_obj}, {"nombreInsumo": 1})
                    if insumo_ref_doc and "nombreInsumo" in insumo_ref_doc:
                        nombre_del_insumo_str = insumo_ref_doc["nombreInsumo"]
                    elif insumo_ref_doc:
                        nombre_del_insumo_str = f"Insumo (ID: {str(id_insumo_ref_obj)}) sin nombre"


                nombre_del_usuario_str = "Usuario Desconocido"
                id_usuario_obj = app_item_db.get("idUsuario")
                if isinstance(id_usuario_obj, ObjectId):
                    usuario_doc = self.db.usuarios.find_one({"_id": id_usuario_obj}, {"nombre": 1})
                    if usuario_doc and "nombre" in usuario_doc:
                        nombre_del_usuario_str = usuario_doc["nombre"]
                    elif usuario_doc:
                        nombre_del_usuario_str = f"Usuario (ID: {str(id_usuario_obj)}) sin nombre"

                detalle_data = {
                    "_id": str(app_item_db.get("_id")),
                    "fechaAplicacion": app_item_db.get("fechaAplicacion"),
                    "cantAplicada": app_item_db.get("cantidadAplicada"),
                    "nombreInsumo": nombre_del_insumo_str,
                    "nombreUsuario": nombre_del_usuario_str,
                }

                try:
                    aplicacion_procesada = AplicacionInsumoDetalle(**detalle_data)
                    aplicaciones_procesadas_list.append(aplicacion_procesada)
                except Exception as pydantic_error:
                    print(f"Error al procesar datos para AplicacionInsumoDetalle: {pydantic_error}")
                    print(
                        f"Datos problemáticos para el item de aplicación con _id {app_item_db.get('_id')}: {detalle_data}")

            salida.aplicaciones = aplicaciones_procesadas_list
            salida.estatus = "OK"
            salida.mensaje = (f"Se encontraron {len(aplicaciones_procesadas_list)} aplicaciones de insumo "
                              f"para el cultivo '{nombre_cultivo_para_mensaje}' (ID: {id_cultivo}).")

            if lista_aplicaciones_db and len(aplicaciones_procesadas_list) < len(lista_aplicaciones_db):
                salida.mensaje += " Algunos items no pudieron ser procesados debido a datos incompletos o inválidos."

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarListaAplicacionInsumo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la lista de aplicaciones de insumo."
            salida.aplicaciones = []
        return salida








