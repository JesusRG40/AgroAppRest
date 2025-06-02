from datetime import datetime
from bson import ObjectId
from models.cultivosModel import CultivoInsert, Salida, CultivoUpdate, CultivoSalidaIndividual, CultivoSelect, \
    CultivosListSalida, UbicacionInsert, UbicacionUpdate, UbicacionSalidaIndividual, UbicacionSubConsulta, \
    SeguimientoInsert, SeguimientoUpdate, SeguimientoSelect, SeguimientoSalidaIndividual, SeguimientoListSalida, \
    SeguimientoSubConsulta
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database

class CultivoDAO:
    def __init__(self, db):
        self.db = db

    def agregarCultivo(self, cultivo: CultivoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # Validar que areaCultivo sea un valor numérico mayor a cero
            if not (isinstance(cultivo.areaCultivo, (int, float)) and cultivo.areaCultivo > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "El área del cultivo debe ser un número mayor a cero."
                return salida

            if not cultivo.nomCultivo.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El nombre del cultivo no puede estar vacío."
                return salida

            # Validar coherencia de fechas
            if cultivo.fechaCosechaEst <= cultivo.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha estimada no puede ser anterior o igual a la fecha de siembra."
                return salida

            if cultivo.fechaCosechaReal is not None and cultivo.fechaCosechaReal <= cultivo.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha real no puede ser anterior o igual a la fecha de siembra."
                return salida

            # Convertir idUsuario (string) a ObjectId y validar su formato
            try:
                obj_id_usuario = ObjectId(cultivo.idUsuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idUsuario no es válido."
                return salida

            # Verificar que el idUsuario exista en la colección usuarios
            usuario_existente = self.db.usuarios.find_one({"_id": obj_id_usuario})
            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"El usuario con ID '{cultivo.idUsuario}' no existe en la base de datos."
                return salida

            cultivo_dict = jsonable_encoder(cultivo)
            cultivo_dict["idUsuario"] = obj_id_usuario

            # Añadir campos array vacíos según la estructura de la colección Cultivos
            cultivo_dict["registroActivo"] = True
            cultivo_dict["estadoActual"] = "Sembrado"

            result = self.db.cultivos.insert_one(cultivo_dict)

            if result.inserted_id:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo '{cultivo.nomCultivo}' agregado con éxito con id: {str(result.inserted_id)}."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el cultivo (falló en la inserción)."
        except Exception as ex:
            print(f"Error en CultivoDAO.agregarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar el cultivo. Consulte al administrador."
        return salida


    def actualizarCultivo(self, id_cultivo: str, cultivo_data: CultivoUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Convertir id_cultivo a ObjectId y verificar existencia del cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            cultivo_existente_doc = self.db.cultivos.find_one({"_id": obj_id_cultivo})
            if not cultivo_existente_doc:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            # Preparar el diccionario de campos a actualizar
            update_fields = {}

            # Iterar sobre los campos del modelo de entrada y validar/agregar si se proporcionan

            if cultivo_data.nomCultivo is not None:
                if not cultivo_data.nomCultivo.strip():
                    salida.estatus = "ERROR"
                    salida.mensaje = "El nombre del cultivo no puede estar vacío si se actualiza."
                    return salida
                update_fields["nomCultivo"] = cultivo_data.nomCultivo

            if cultivo_data.areaCultivo is not None:
                if not (isinstance(cultivo_data.areaCultivo, (int, float)) and cultivo_data.areaCultivo > 0):
                    salida.estatus = "ERROR"
                    salida.mensaje = "El área del cultivo debe ser un número mayor a cero si se actualiza."
                    return salida
                update_fields["areaCultivo"] = cultivo_data.areaCultivo

            if cultivo_data.estadoActual is not None:
                estados_validos = ["Sembrado", "En Crecimiento", "Listo para Cosecha", "Cosechado"]
                if cultivo_data.estadoActual not in estados_validos:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"El estado '{cultivo_data.estadoActual}' no es válido para la actualización. Estados permitidos: {', '.join(estados_validos)}."
                    return salida
                update_fields["estadoActual"] = cultivo_data.estadoActual

            # Validación  de idUsuario si se proporciona
            if cultivo_data.idUsuario is not None:
                try:
                    obj_id_usuario_update = ObjectId(cultivo_data.idUsuario)
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El formato del idUsuario para la actualización no es válido."
                    return salida

                # Validar existencia del nuevo idUsuario
                usuario_para_actualizar_existe = self.db.usuarios.find_one({"_id": obj_id_usuario_update})
                if not usuario_para_actualizar_existe:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"El nuevo usuario con ID '{cultivo_data.idUsuario}' no existe en la base de datos."
                    return salida
                update_fields["idUsuario"] = obj_id_usuario_update

            #Validaciones de fechas
            if cultivo_data.fechaSiembra is not None:
                if cultivo_data.fechaCosechaReal is not None and cultivo_data.fechaCosechaReal <= cultivo_data.fechaSiembra:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La fecha de cosecha real no puede ser anterior o igual a la fecha de siembra."
                    return salida
            update_fields["fechaSiembra"] = cultivo_data.fechaSiembra
            if cultivo_data.fechaCosechaEst is not None:
                if cultivo_data.fechaCosechaEst <= cultivo_data.fechaSiembra:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La fecha de cosecha estimada no puede ser anterior o igual a la fecha de siembra."
                    return salida
            update_fields["fechaCosechaEst"] = cultivo_data.fechaCosechaEst
            if cultivo_data.fechaCosechaReal is not None:
                update_fields["fechaCosechaReal"] = cultivo_data.fechaCosechaReal

            # Si no hay campos para actualizar, informar
            if not update_fields:
                salida.estatus = "INFO"
                salida.mensaje = "No se proporcionaron datos para actualizar."
                return salida

            # Realizar la actualización
            result = self.db.cultivos.update_one({"_id": obj_id_cultivo}, {"$set": update_fields})

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo con ID '{id_cultivo}' actualizado con éxito."
            else:
                salida.estatus = "INFO"
                salida.mensaje = (f"El cultivo con ID '{id_cultivo}' fue encontrado, pero los datos proporcionados "
                                  "no produjeron cambios (o eran idénticos a los existentes).")

        except Exception as ex:
            print(f"Error en CultivoDAO.actualizarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar el cultivo. Consulte al administrador."

        return salida



    def borrarCultivo(self, id_cultivo: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        campo_estado_logico = "registroActivo"

        try:
            #Convertir id_cultivo a ObjectId
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Verificar si el cultivo existe y cuál es su estado actual
            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo}, {campo_estado_logico: 1})

            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            # Verificar si ya está lógicamente eliminado
            if cultivo_existente.get(campo_estado_logico) == False:
                salida.estatus = "INFO"
                salida.mensaje = f"El cultivo con ID '{id_cultivo}' ya se encuentra eliminado."
                return salida

            #Intentar la eliminación lógica (actualizar el estado)
            result = self.db.cultivos.update_one({"_id": obj_id_cultivo}, {"$set": {campo_estado_logico: False}})

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo con ID '{id_cultivo}' eliminado con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "INFO"
                salida.mensaje = f"El cultivo con ID '{id_cultivo}' ya se habia eliminado"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se pudo marcar como eliminado el cultivo con ID: {id_cultivo}. Es posible que no se haya encontrado."
        except Exception as ex:
            print(f"Error en CultivoDAO.borrarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al intentar la eliminación del cultivo. Consulte al administrador."

        return salida



    def consultarCultivoPorId(self, id_cultivo: str) -> CultivoSalidaIndividual:
        salida = CultivoSalidaIndividual(estatus="", mensaje="", cultivo=None)
        try:
            #Convertir id_cultivo a ObjectId
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Buscar el cultivo en la base de datos
            cultivo_db = self.db.cultivos.find_one({"_id": obj_id_cultivo, "registroActivo": True})

            if cultivo_db:
                cultivo_db["_id"] = str(cultivo_db["_id"])
                if "idUsuario" in cultivo_db and isinstance(cultivo_db["idUsuario"], ObjectId):
                    id_usuario_a_buscar = cultivo_db["idUsuario"]
                    nombre_del_usuario = "Usuario Desconocido"

                    usuario_encontrado = self.db.usuarios.find_one({"_id": id_usuario_a_buscar}, {"nombre": 1})

                    if usuario_encontrado and "nombre" in usuario_encontrado:
                        nombre_del_usuario = usuario_encontrado["nombre"]
                    elif usuario_encontrado:
                        nombre_del_usuario = f"Usuario (ID: {str(id_usuario_a_buscar)}) sin nombre"
                    else:
                        nombre_del_usuario = f"Usuario (ID: {str(id_usuario_a_buscar)}) no encontrado"

                    cultivo_db["nombreUsuario"] = nombre_del_usuario

                salida.cultivo = CultivoSelect(**cultivo_db)
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo con ID '{id_cultivo}' encontrado."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarCultivoPorId: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar el cultivo. Consulte al administrador."
            salida.cultivo = None
        return salida


    def consultarListaDeCultivos(self) -> CultivosListSalida:
        salida = CultivosListSalida(estatus="", mensaje="", cultivos=[])
        try:

            lista_cultivos_db = list(self.db.cultivos.find({"registroActivo": True}))
            if not lista_cultivos_db:
                salida.estatus = "OK"
                salida.mensaje = "No se encontraron cultivos registrados."
                salida.cultivos = []
                return salida

            cultivos_con_nombre_usuario_list = []
            for cultivo_item_db in lista_cultivos_db:
                cultivo_item_db["_id"] = str(cultivo_item_db["_id"])

                # Obtener idUsuario y buscar el nombre del usuario
                id_usuario_obj = None
                if "idUsuario" in cultivo_item_db and isinstance(cultivo_item_db["idUsuario"], ObjectId):
                    id_usuario_obj = cultivo_item_db["idUsuario"]

                nombre_del_usuario_str = "Usuario no especificado"

                if id_usuario_obj:
                    usuario_doc = self.db.usuarios.find_one({"_id": id_usuario_obj}, {"nombre": 1})
                    if usuario_doc and "nombre" in usuario_doc:
                        nombre_del_usuario_str = usuario_doc["nombre"]
                    elif usuario_doc:
                        nombre_del_usuario_str = f"Usuario (ID: {str(id_usuario_obj)}) sin nombre"
                    else:
                        nombre_del_usuario_str = f"Usuario (ID: {str(id_usuario_obj)}) no encontrado"

                cultivo_item_db["nombreUsuario"] = nombre_del_usuario_str
                cultivo_procesado = CultivoSelect(**cultivo_item_db)
                cultivos_con_nombre_usuario_list.append(cultivo_procesado)
                salida.cultivos = cultivos_con_nombre_usuario_list
                salida.estatus = "OK"
                salida.mensaje = f"Se encontraron {len(cultivos_con_nombre_usuario_list)} cultivos."

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarListaDeCultivos: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la lista de cultivos. Consulte al administrador."
            salida.cultivos = []

        return salida



    def registrarNuevaUbicacion(self, id_cultivo: str, ubicacion_data: UbicacionInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Verificar que el cultivo exista
            # Y verificar si ya tiene una ubicación asignada
            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo}, {"ubicacion": 1, "areaCultivo":1})

            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            #Solo una ubicación por cultivo
            if cultivo_existente.get("ubicacion") is not None:
                salida.estatus = "ERROR"
                salida.mensaje = f"El cultivo con ID '{id_cultivo}' ya tiene una ubicación registrada. No se puede agregar otra."
                return salida

            #Asegurarse que la superficie de la ubicación sea un número válido.
            if not isinstance(ubicacion_data.superficie, (int, float)):
                salida.estatus = "ERROR"
                salida.mensaje = "La superficie de la ubicación debe ser un valor numérico."
                return salida

            #Obtener el areaCultivo del cultivo existente.
            area_del_cultivo = cultivo_existente.get("areaCultivo")

            # Validación principal: superficie de la ubicación >= areaCultivo.
            if ubicacion_data.superficie < area_del_cultivo:
                salida.estatus = "ERROR"
                salida.mensaje = (f"La superficie de la ubicación ({ubicacion_data.superficie}) "
                                  f"no puede ser menor que el área del cultivo ({area_del_cultivo}). "
                                  "Debe ser mayor o igual.")
                return salida

            if not ubicacion_data.nombreUbicacion.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El nombre de la ubicación no puede estar vacío."
                return salida

            if not ubicacion_data.estado.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El estado/provincia de la ubicación no puede estar vacío."
                return salida

            if not ubicacion_data.municipio.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El municipio de la ubicación no puede estar vacío."
                return salida

            if not ubicacion_data.cp.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El Código Postal de la ubicación no puede estar vacío."
                return salida

            #Validar que todos los caracteres sean números
            codigo_postal_str = ubicacion_data.cp.strip()
            if not codigo_postal_str.isdigit():
                salida.estatus = "ERROR"
                salida.mensaje = "El Código Postal debe contener únicamente números."
                return salida

            #Validar una longitud específica
            codigo_postal_str = ubicacion_data.cp.strip()
            if len(codigo_postal_str) != 5:
                 salida.estatus = "ERROR"
                 salida.mensaje = "El Código Postal debe tener 5 dígitos."
                 return salida

            if not ubicacion_data.localidad.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "La localidad o ciudad no puede estar vacío."
                return salida

            # Preparar el documento de la nueva ubicación
            nueva_ubicacion_dict = jsonable_encoder(ubicacion_data)

            # Establecer la ubicación para el cultivo usando $set
            result = self.db.cultivos.update_one({"_id": obj_id_cultivo}, {"$set": {"ubicacion": nueva_ubicacion_dict}})

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = (f"Ubicación '{ubicacion_data.nombreUbicacion}' registrada con éxito para el "
                                  f"cultivo ID '{id_cultivo}'.")
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "INFO"
                salida.mensaje = "La ubicación ya estaba asignada con los mismos datos o no se requirió modificación."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo registrar la ubicación. El cultivo podría no existir."

        except Exception as ex:
            print(f"Error en CultivoDAO.registrarNuevaUbicacion: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar la ubicación. Consulte al administrador."

        return salida



    def actualizarUbicacionCultivo(self, id_cultivo: str, ubicacion_data: UbicacionUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Verificar que el cultivo exista y que tenga una ubicación para actualizar
            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo}, {"ubicacion": 1, "areaCultivo": 1})

            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            if cultivo_existente.get("ubicacion") is None:
                salida.estatus = "ERROR"
                salida.mensaje = f"El cultivo con ID '{id_cultivo}' no tiene una ubicación registrada para actualizar."
                return salida

            #Construir el diccionario de campos a actualizar ($set)
            update_payload_for_set = {}

            # Procesar cada campo opcional de ubicacion_data
            if ubicacion_data.nombreUbicacion is not None:
                nombre_ubic_stripped = ubicacion_data.nombreUbicacion.strip()
                if not nombre_ubic_stripped:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El nombre de la ubicación no puede estar vacío si se actualiza."
                    return salida
                update_payload_for_set["ubicacion.nombreUbicacion"] = nombre_ubic_stripped

            if ubicacion_data.estado is not None:
                estado_stripped = ubicacion_data.estado.strip()
                if not estado_stripped:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El estado/provincia de la ubicación no puede estar vacío si se actualiza."
                    return salida
                update_payload_for_set["ubicacion.estado"] = estado_stripped

            if ubicacion_data.municipio is not None:
                municipio_stripped = ubicacion_data.municipio.strip()
                if not municipio_stripped:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El municipio de la ubicación no puede estar vacío si se actualiza."
                    return salida
                update_payload_for_set["ubicacion.municipio"] = municipio_stripped

            if ubicacion_data.localidad is not None:
                localidad_stripped = ubicacion_data.localidad.strip()
                if not localidad_stripped:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La localidad o ciudad no puede estar vacía si se actualiza."
                    return salida
                update_payload_for_set["ubicacion.localidad"] = localidad_stripped

            if ubicacion_data.cp is not None:
                cp_str = ubicacion_data.cp.strip()
                if not cp_str:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El Código Postal no puede estar vacío si se actualiza."
                    return salida
                if not cp_str.isdigit():
                    salida.estatus = "ERROR"
                    salida.mensaje = "El Código Postal debe contener únicamente números."
                    return salida
                if len(cp_str) != 5:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El Código Postal debe tener 5 dígitos."
                    return salida
                update_payload_for_set["ubicacion.cp"] = cp_str

            if ubicacion_data.superficie is not None:
                if not isinstance(ubicacion_data.superficie, (int, float)):
                    salida.estatus = "ERROR"
                    salida.mensaje = "La superficie debe ser un valor numérico."
                    return salida
                if ubicacion_data.superficie <= 0:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La superficie debe ser un número mayor a cero."
                    return salida

                area_del_cultivo = cultivo_existente.get("areaCultivo")
                if area_del_cultivo is None or not isinstance(area_del_cultivo, (int, float)):
                    salida.estatus = "ERROR"
                    salida.mensaje = "No se pudo determinar el área del cultivo para validar la superficie."
                    return salida
                if ubicacion_data.superficie < area_del_cultivo:
                    salida.estatus = "ERROR"
                    salida.mensaje = (
                        f"La superficie de la ubicación ({ubicacion_data.superficie}) no puede ser menor que "
                        f"el área del cultivo ({area_del_cultivo}). Debe ser mayor o igual.")
                    return salida
                update_payload_for_set["ubicacion.superficie"] = ubicacion_data.superficie

            if ubicacion_data.coordenadas is not None:
                update_payload_for_set["ubicacion.coordenadas"] = {
                    "latitud": ubicacion_data.coordenadas.latitud,
                    "longitud": ubicacion_data.coordenadas.longitud }

            if ubicacion_data.tipoSuelo is not None:
                if not ubicacion_data.tipoSuelo.strip():
                    salida.estatus = "ERROR"
                    salida.mensaje = "El tipo de suelo no puede estar vacío si se actualiza."
                    return salida
                update_payload_for_set["ubicacion.tipoSuelo"] = ubicacion_data.tipoSuelo.strip()

            if ubicacion_data.accesoAgua is not None:  # bool
                update_payload_for_set["ubicacion.accesoAgua"] = ubicacion_data.accesoAgua

            if ubicacion_data.detalles is not None:
                update_payload_for_set["ubicacion.detalles"] = ubicacion_data.detalles

            if not update_payload_for_set:
                salida.estatus = "INFO"
                salida.mensaje = "No se proporcionaron datos válidos para actualizar o los datos son idénticos."
                return salida

            # Realizar la actualización en la base de datos
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo, "ubicacion": {"$exists": True}},{"$set": update_payload_for_set})

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Ubicación del cultivo ID '{id_cultivo}' actualizada con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "INFO"
                salida.mensaje = "La ubicación fue encontrada, pero los datos proporcionados no produjeron cambios (o eran idénticos)."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se encontró el cultivo o su ubicación para actualizar (verificación post-actualización)."

        except Exception as ex:
            print(f"Error en CultivoDAO.actualizarUbicacionCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la ubicación del cultivo. Consulte al administrador."

        return salida


    def consultarUbicacionDeCultivo(self, id_cultivo: str) -> UbicacionSalidaIndividual:
        salida = UbicacionSalidaIndividual(estatus="", mensaje="", ubicacion=None)
        campo_estado_logico_cultivo = "registroActivo"
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Buscar el cultivo activo y obtener su 'nomCultivo' y su objeto 'ubicacion'.
            cultivo_doc = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo,
                    campo_estado_logico_cultivo: True},{"nomCultivo": 1, "ubicacion": 1})

            if not cultivo_doc:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            if cultivo_doc.get("ubicacion") is not None and isinstance(cultivo_doc.get("ubicacion"), dict):
                ubicacion_data_from_db = cultivo_doc["ubicacion"]
                nombre_del_cultivo = cultivo_doc.get("nomCultivo", "Nombre de cultivo no disponible")

                datos_para_modelo_ubicacion = ubicacion_data_from_db.copy()
                datos_para_modelo_ubicacion["nombreCultivo"] = nombre_del_cultivo

                salida.ubicacion = UbicacionSubConsulta(**datos_para_modelo_ubicacion)
                salida.estatus = "OK"
                salida.mensaje = f"Ubicación encontrada para el cultivo {nombre_del_cultivo}."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"El cultivo con ID '{id_cultivo}' no tiene una ubicación registrada o es inválida.")

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarUbicacionDeCultivoPorId: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la ubicación. Consulte al administrador."
            salida.ubicacion = None

        return salida


    def agregar_seguimiento(self, id_cultivo: str, seguimiento_data: SeguimientoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Verificar que el cultivo exista y esté activo
            cultivo_existente = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True}
            )
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            # 2. Validar idUsuario del seguimiento_data
            if not seguimiento_data.idUsuario:  # Should be caught by Pydantic if not optional
                salida.estatus = "ERROR"
                salida.mensaje = "El idUsuario es obligatorio para registrar un seguimiento."
                return salida
            try:
                obj_id_usuario = ObjectId(seguimiento_data.idUsuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idUsuario proporcionado para el seguimiento no es válido."
                return salida

            # Verificar que el usuario exista
            usuario_existente = self.db.usuarios.find_one({"_id": obj_id_usuario})
            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"El usuario con ID '{seguimiento_data.idUsuario}' no existe en la base de datos."
                return salida

            # 3. Validar estadoCultivo
            if not seguimiento_data.estadoCultivo.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El estado del cultivo no puede estar vacío."
                return salida

            estados_cultivo_permitidos = ["Sano", "Enfermo", "Con Necesidad de Riego", "Plaga Detectada",
                                          "Deficiencia Nutricional"]  # Example states
            if seguimiento_data.estadoCultivo not in estados_cultivo_permitidos:
                salida.estatus = "ERROR"
                salida.mensaje = (f"Estado de cultivo '{seguimiento_data.estadoCultivo}' no es válido. "
                                  f"Permitidos: {', '.join(estados_cultivo_permitidos)}.")
                return salida

            # 4. Preparar el documento de seguimiento para la inserción
            seguimiento_dict = jsonable_encoder(seguimiento_data)

            # Asignar los ObjectIds validados
            seguimiento_dict["idCultivo"] = obj_id_cultivo
            seguimiento_dict["idUsuario"] = obj_id_usuario

            seguimiento_dict[
                "observaciones"] = seguimiento_data.observaciones if seguimiento_data.observaciones is not None else []
            seguimiento_dict[
                "recomendaciones"] = seguimiento_data.recomendaciones if seguimiento_data.recomendaciones is not None else []

            # 5. Insertar en la colección seguimiento_cultivo
            result = self.db.seguimiento_cultivo.insert_one(seguimiento_dict)

            if result.inserted_id:
                salida.estatus = "OK"
                salida.mensaje = (f"Seguimiento agregado con éxito al cultivo ID '{id_cultivo}' "
                                  f"con ID de seguimiento: {str(result.inserted_id)}.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el seguimiento (falló en la inserción)."

        except Exception as ex:
            print(f"Error en CultivoDAO.agregar_seguimiento: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar el seguimiento. Consulte al administrador."

        return salida



    def editar_seguimiento(self, id_cultivo: str, id_seguimiento: str, seguimiento_data: SeguimientoUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Verificar que el cultivo exista y esté activo
            cultivo_existente = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True}
            )
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            # 2. Validar id_seguimiento
            try:
                obj_id_seguimiento = ObjectId(id_seguimiento)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del seguimiento proporcionado no tiene un formato válido."
                return salida

            # 3. Verificar que el seguimiento exista y pertenezca al cultivo especificado
            seguimiento_existente_doc = self.db.seguimiento_cultivo.find_one(
                {"_id": obj_id_seguimiento, "idCultivo": obj_id_cultivo}
            )
            if not seguimiento_existente_doc:
                salida.estatus = "ERROR"
                salida.mensaje = (f"No se encontró un seguimiento con ID '{id_seguimiento}' "
                                  f"asociado al cultivo con ID '{id_cultivo}'.")
                return salida

            # 4. Preparar el diccionario de campos a actualizar
            update_fields = {}

            if seguimiento_data.fechaRevision is not None:
                update_fields["fechaRevision"] = seguimiento_data.fechaRevision

            if seguimiento_data.estadoCultivo is not None:
                if not seguimiento_data.estadoCultivo.strip():
                    salida.estatus = "ERROR"
                    salida.mensaje = "El estado del cultivo no puede estar vacío si se actualiza."
                    return salida
                estados_cultivo_permitidos = ["Sano", "Enfermo", "Con Necesidad de Riego", "Plaga Detectada",
                                              "Deficiencia Nutricional"]  # Example states from previous method
                if seguimiento_data.estadoCultivo not in estados_cultivo_permitidos:
                    salida.estatus = "ERROR"
                    salida.mensaje = (f"Estado de cultivo '{seguimiento_data.estadoCultivo}' no es válido. "
                                      f"Permitidos: {', '.join(estados_cultivo_permitidos)}.")
                    return salida
                update_fields["estadoCultivo"] = seguimiento_data.estadoCultivo

            if seguimiento_data.observaciones is not None:
                update_fields["observaciones"] = seguimiento_data.observaciones

            if seguimiento_data.recomendaciones is not None:
                update_fields["recomendaciones"] = seguimiento_data.recomendaciones

            if seguimiento_data.idUsuario is not None:
                try:
                    obj_id_usuario_update = ObjectId(seguimiento_data.idUsuario)
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El formato del idUsuario para la actualización no es válido."
                    return salida

                usuario_para_actualizar_existe = self.db.usuarios.find_one({"_id": obj_id_usuario_update})
                if not usuario_para_actualizar_existe:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"El nuevo usuario con ID '{seguimiento_data.idUsuario}' no existe en la base de datos."
                    return salida
                update_fields["idUsuario"] = obj_id_usuario_update

            # Si no hay campos para actualizar, informar
            if not update_fields:
                salida.estatus = "INFO"
                salida.mensaje = "No se proporcionaron datos para actualizar el seguimiento."
                return salida

            # 5. Realizar la actualización
            update_payload_encoded = jsonable_encoder(update_fields, exclude_none=True)

            result = self.db.seguimiento_cultivo.update_one(
                {"_id": obj_id_seguimiento, "idCultivo": obj_id_cultivo},
                {"$set": update_payload_encoded}
            )

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Seguimiento con ID '{id_seguimiento}' actualizado con éxito."
            elif result.matched_count == 1 and result.modified_count == 0:
                salida.estatus = "INFO"
                salida.mensaje = (
                    f"El seguimiento con ID '{id_seguimiento}' fue encontrado, pero los datos proporcionados "
                    "no produjeron cambios (o eran idénticos a los existentes).")
            else:

                salida.estatus = "ERROR"
                salida.mensaje = f"No se pudo actualizar el seguimiento con ID '{id_seguimiento}'. Verifique los IDs."


        except Exception as ex:
            print(f"Error en CultivoDAO.editar_seguimiento: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al editar el seguimiento. Consulte al administrador."

        return salida


    def eliminar_seguimiento(self, id_cultivo: str, id_seguimiento: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Validar id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida


            cultivo_existente = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True}
            )
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            # 2. Validar id_seguimiento
            try:
                obj_id_seguimiento = ObjectId(id_seguimiento)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del seguimiento proporcionado no tiene un formato válido."
                return salida

            # 3. Intentar la eliminación física del seguimiento
            result = self.db.seguimiento_cultivo.delete_one(
                {"_id": obj_id_seguimiento, "idCultivo": obj_id_cultivo}
            )

            if result.deleted_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Seguimiento con ID '{id_seguimiento}' eliminado con éxito del cultivo ID '{id_cultivo}'."
            elif result.deleted_count == 0:
                salida.estatus = "ERROR"  # O "INFO" si se prefiere indicar que no se encontró para eliminar
                salida.mensaje = (f"No se encontró el seguimiento con ID '{id_seguimiento}' asociado al "
                                  f"cultivo ID '{id_cultivo}', o ya fue eliminado.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Resultado inesperado durante la eliminación del seguimiento."

        except Exception as ex:
            print(f"Error en CultivoDAO.eliminar_seguimiento: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar el seguimiento. Consulte al administrador."

        return salida



    def consultar_seguimiento_por_id(self, id_cultivo: str, id_seguimiento: str) -> SeguimientoSalidaIndividual:
        salida = SeguimientoSalidaIndividual(estatus="", mensaje="", seguimiento=None)
        try:
            # 1. Validar id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Verificar que el cultivo exista y esté activo (contextual validation)
            cultivo_existente = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True}
            )
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            # 2. Validar id_seguimiento
            try:
                obj_id_seguimiento = ObjectId(id_seguimiento)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del seguimiento proporcionado no tiene un formato válido."
                return salida

            # 3. Buscar el seguimiento en la base de datos
            seguimiento_doc = self.db.seguimiento_cultivo.find_one(
                {"_id": obj_id_seguimiento, "idCultivo": obj_id_cultivo}
            )

            if seguimiento_doc:
                # Procesar el documento para el modelo SeguimientoSelect
                id_usuario_seguimiento = seguimiento_doc.get("idUsuario")
                nombre_del_usuario_seguimiento = "Usuario Desconocido"

                if isinstance(id_usuario_seguimiento, ObjectId):
                    usuario_encontrado = self.db.usuarios.find_one(
                        {"_id": id_usuario_seguimiento}, {"nombre": 1}
                    )
                    if usuario_encontrado and "nombre" in usuario_encontrado:
                        nombre_del_usuario_seguimiento = usuario_encontrado["nombre"]
                    elif usuario_encontrado:  # Usuario existe pero sin nombre
                        nombre_del_usuario_seguimiento = f"Usuario (ID: {str(id_usuario_seguimiento)}) sin nombre"
                    else:  # Usuario no encontrado
                        nombre_del_usuario_seguimiento = f"Usuario (ID: {str(id_usuario_seguimiento)}) no encontrado"
                elif id_usuario_seguimiento:
                    nombre_del_usuario_seguimiento = f"Usuario (ID: {str(id_usuario_seguimiento)}) con formato incorrecto en BD"

                # Crear el objeto SeguimientoSelect
                seguimiento_data_for_model = {
                    "_id": str(seguimiento_doc["_id"]),
                    "fechaRevision": seguimiento_doc.get("fechaRevision"),
                    "estadoCultivo": seguimiento_doc.get("estadoCultivo"),
                    "observaciones": seguimiento_doc.get("observaciones", []),
                    "recomendaciones": seguimiento_doc.get("recomendaciones", []),
                    "idCultivo": str(seguimiento_doc["idCultivo"]),
                    "nombreUsuario": nombre_del_usuario_seguimiento,

                }

                salida.seguimiento = SeguimientoSelect(**seguimiento_data_for_model)
                salida.estatus = "OK"
                salida.mensaje = f"Seguimiento con ID '{id_seguimiento}' encontrado."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = (f"No se encontró un seguimiento con ID '{id_seguimiento}' "
                                  f"asociado al cultivo ID '{id_cultivo}'.")

        except Exception as ex:
            print(f"Error en CultivoDAO.consultar_seguimiento_por_id: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar el seguimiento. Consulte al administrador."
            salida.seguimiento = None

        return salida


    def consultarListaSeguimiento(self, id_cultivo: str) -> SeguimientoListSalida:
        global obj_id_cultivo
        salida = SeguimientoListSalida(estatus="", mensaje="", seguimientos=[])
        try:
            # 1. Validar y convertir el ID del cultivo a ObjectId
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # 2. Verificar que el cultivo exista y esté activo para obtener su nombre
            cultivo_doc_for_name = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "registroActivo": True},
                {"nomCultivo": 1}
            )

            if not cultivo_doc_for_name:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo activo con el ID: {id_cultivo}."
                return salida

            salida.nombreCultivo = cultivo_doc_for_name.get("nomCultivo", "Nombre no disponible")

            # 3. Consultar la colección 'seguimiento_cultivo'
            lista_seguimientos_cursor = self.db.seguimiento_cultivo.find(
                {"idCultivo": obj_id_cultivo}
            )

            seguimientos_procesados_list = []
            for seguimiento_item_db in lista_seguimientos_cursor:
                id_usuario_seguimiento = seguimiento_item_db.get("idUsuario")
                nombre_del_usuario_seguimiento = "Usuario Desconocido"

                if isinstance(id_usuario_seguimiento, ObjectId):
                    usuario_encontrado = self.db.usuarios.find_one(
                        {"_id": id_usuario_seguimiento}, {"nombre": 1}
                    )
                    if usuario_encontrado and "nombre" in usuario_encontrado:
                        nombre_del_usuario_seguimiento = usuario_encontrado["nombre"]
                    elif usuario_encontrado:
                        nombre_del_usuario_seguimiento = f"Usuario (ID: {str(id_usuario_seguimiento)}) sin nombre"
                    else:
                        nombre_del_usuario_seguimiento = f"Usuario (ID: {str(id_usuario_seguimiento)}) no encontrado en BD"
                elif id_usuario_seguimiento:  # Should be ObjectId ideally
                    nombre_del_usuario_seguimiento = f"ID Usuario '{str(id_usuario_seguimiento)}' con formato inesperado"


                seguimiento_data_for_model = {
                    "_id": str(seguimiento_item_db["_id"]),
                    "fechaRevision": seguimiento_item_db.get("fechaRevision"),
                    "estadoCultivo": seguimiento_item_db.get("estadoCultivo"),
                    "observaciones": seguimiento_item_db.get("observaciones", []),
                    "recomendaciones": seguimiento_item_db.get("recomendaciones", []),
                    "idCultivo": str(seguimiento_item_db["idCultivo"]),  # Already obj_id_cultivo as ObjectId
                    "nombreUsuario": nombre_del_usuario_seguimiento,

                }
                try:
                    seguimiento_obj = SeguimientoSelect(**seguimiento_data_for_model)
                    seguimientos_procesados_list.append(seguimiento_obj)
                except Exception as ex:
                    print(f"Error al parsear seguimiento_item_db a SeguimientoSelect: {ex}")
                    print(f"Datos problemáticos: {seguimiento_data_for_model}")

            if seguimientos_procesados_list:
                salida.seguimientos = seguimientos_procesados_list
                salida.estatus = "OK"
                salida.mensaje = (f"Se encontraron {len(seguimientos_procesados_list)} registros de seguimiento "
                                  f"para el cultivo '{salida.nombreCultivo}'.")
            else:
                salida.estatus = "OK"
                salida.mensaje = f"No se encontraron seguimientos registrados para el cultivo '{salida.nombreCultivo}'."
                salida.seguimientos = []

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarListaSeguimiento: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar los seguimientos. Consulte al administrador."
            salida.seguimientos = []
            if salida.nombreCultivo is None and 'obj_id_cultivo' in locals():
                salida.nombreCultivo = f"Cultivo ID {str(obj_id_cultivo)}"

        return salida
