from bson import ObjectId

from models.cultivosModel import CultivoInsert, Salida, CultivoUpdate, CultivoSalidaIndividual, CultivoSelect, \
    CultivosListSalida, UbicacionInsert, UbicacionUpdate, UbicacionSalidaIndividual, UbicacionSubConsulta
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database

class CultivoDAO:
    def __init__(self, db):
        self.db = db

    def agregarCultivo(self, cultivo: CultivoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Validar que areaCultivo sea un valor numérico mayor a cero
            if not (isinstance(cultivo.areaCultivo, (int, float)) and cultivo.areaCultivo > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "El área del cultivo debe ser un número mayor a cero."
                return salida

            #Validar coherencia de fechas
            if cultivo.fechaCosechaEst < cultivo.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha estimada no puede ser anterior a la fecha de siembra."
                return salida

            if cultivo.fechaCosechaReal is not None and cultivo.fechaCosechaReal < cultivo.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha real no puede ser anterior a la fecha de siembra."
                return salida


            #Validar estadoActual contra una lista predefinida
            estados_validos = ["Sembrado", "En Crecimiento", "Listo para Cosecha", "Cosechado"]
            if cultivo.estadoActual not in estados_validos:
                salida.estatus = "ERROR"
                salida.mensaje = f"El estado '{cultivo.estadoActual}' no es válido."
                return salida

            cultivo_dict = jsonable_encoder(cultivo)

            #idUsuario debe ser ObjectId en la base de datos:
            try:
                 cultivo_dict["idUsuario"] = ObjectId(cultivo.idUsuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idUsuario no es válido."
                return salida

            #Añadir campos array vacíos a la estructura de la colección Cultivos
            cultivo_dict["aplicacionesInsumo"] = []
            cultivo_dict["riegos"] = []
            cultivo_dict["ubicacion"] = []

            result = self.db.cultivos.insert_one(cultivo_dict)

            if result.inserted_id:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo '{cultivo.nomCultivo}' agregado con éxito con id: {str(result.inserted_id)}."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el cultivo (falló la inserción)."

        except Exception as ex:
            print(f"Error en CultivoDAO.agregarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar el cultivo. Consulte al administrador."
        return salida



    def actualizarCultivo(self, id_cultivo: str, cultivo_data: CultivoUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Convertir id_cultivo a ObjectId y verificar existencia
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo})
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            #Validar datos de entrada (cultivo_data)
            if not (isinstance(cultivo_data.areaCultivo, (int, float)) and cultivo_data.areaCultivo > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "El área del cultivo debe ser un número mayor a cero."
                return salida

            if cultivo_data.fechaCosechaEst < cultivo_data.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha estimada no puede ser anterior a la fecha de siembra."
                return salida

            if cultivo_data.fechaCosechaReal is not None and cultivo_data.fechaCosechaReal < cultivo_data.fechaSiembra:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de cosecha real no puede ser anterior a la fecha de siembra."
                return salida

            #Validar estadoActual
            estados_validos = ["Sembrado", "En Crecimiento", "Listo para Cosecha", "Cosechado"]
            if cultivo_data.estadoActual not in estados_validos:
                salida.estatus = "ERROR"
                salida.mensaje = f"El estado '{cultivo_data.estadoActual}' no es válido para la actualización."
                return salida

            update_data_dict = jsonable_encoder(cultivo_data)
            try:
                if "idUsuario" in update_data_dict:
                    update_data_dict["idUsuario"] = ObjectId(update_data_dict["idUsuario"])
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El formato del idUsuario para la actualización no es válido."
                return salida

            result = self.db.cultivos.update_one({"_id": obj_id_cultivo}, {"$set": update_data_dict})

            if result.matched_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo} para actualizar."
                return salida

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo con ID '{id_cultivo}' actualizado con éxito."
            else:
                salida.estatus = "INFO"
                salida.mensaje = f"El cultivo con ID '{id_cultivo}' ya tenía los datos proporcionados. No se realizaron cambios."

        except Exception as ex:
            print(f"Error en CultivoDAO.actualizarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar el cultivo. Consulte al administrador."
        return salida


    def borrarCultivo(self, id_cultivo: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Convertir id_cultivo a ObjectId
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Intentar eliminar el cultivo
            result = self.db.cultivos.delete_one({"_id": obj_id_cultivo})

            if result.deleted_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Cultivo con ID '{id_cultivo}' eliminado con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}. No se eliminó nada."

        except Exception as ex:
            print(f"Error en CultivoDAO.borrarCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al intentar eliminar el cultivo. Consulte al administrador."
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
            cultivo_db = self.db.cultivos.find_one({"_id": obj_id_cultivo})

            if cultivo_db:
                cultivo_db["_id"] = str(cultivo_db["_id"])
                if "idUsuario" in cultivo_db and isinstance(cultivo_db["idUsuario"], ObjectId):
                    cultivo_db["idUsuario"] = str(cultivo_db["idUsuario"])

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
            projection = {
                "aplicacionesInsumo": 0,
                "riegos": 0,
                "ubicacion": 0
            }
            lista_cultivos_db = list(self.db.cultivos.find({}, projection))

            if not lista_cultivos_db:
                salida.estatus = "OK"
                salida.mensaje = "No se encontraron cultivos registrados."
                return salida

            cultivos_summary_list = []
            for cultivo_item_db in lista_cultivos_db:
                cultivo_item_db["_id"] = str(cultivo_item_db["_id"])
                if "idUsuario" in cultivo_item_db and isinstance(cultivo_item_db["idUsuario"], ObjectId):
                    cultivo_item_db["idUsuario"] = str(cultivo_item_db["idUsuario"])

                cultivos_summary_list.append(CultivoSelect(**cultivo_item_db))

            salida.cultivos = cultivos_summary_list
            salida.estatus = "OK"
            salida.mensaje = f"Se encontraron {len(cultivos_summary_list)} cultivos."

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

            #Verificar que el cultivo exista
            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo})
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            #Validar datos de la nueva ubicación
            if not ubicacion_data.nombreUbicacion.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El nombre de la ubicación no puede estar vacío."
                return salida

            if not (isinstance(ubicacion_data.superficie, (int, float)) and ubicacion_data.superficie > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "La superficie de la ubicación debe ser un número mayor a cero."
                return salida

            #Preparar el documento de la nueva ubicación
            # Para Pydantic V2, se usa model_dump() en lugar de jsonable_encoder(modelo)
            nueva_ubicacion_dict = ubicacion_data.model_dump()

            #Generar y añadir un ID único para la ubicación
            nueva_ubicacion_dict["idUbicacion"] = str(ObjectId())

            #Añadir la nueva ubicación al array 'ubicacion' del cultivo
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$push": {"ubicacion": nueva_ubicacion_dict}})

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = (f"Ubicación '{ubicacion_data.nombreUbicacion}' agregada con éxito al "
                                  f"cultivo ID '{id_cultivo}'. ID de ubicación: {nueva_ubicacion_dict['idUbicacion']}.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar la ubicación al cultivo (posiblemente el cultivo ya no existía)."

        except Exception as ex:
            print(f"Error en CultivoDAO.registrarNuevaUbicacion: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar la ubicación. Consulte al administrador."
        return salida



    def actualizarUbicacionDeCultivo(self, id_cultivo: str, id_ubicacion: str, ubicacion_data: UbicacionUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Validar datos de la ubicación a actualizar
            if not ubicacion_data.nombreUbicacion.strip():
                salida.estatus = "ERROR"
                salida.mensaje = "El nombre de la ubicación no puede estar vacío."
                return salida

            if not (isinstance(ubicacion_data.superficie, (int, float)) and ubicacion_data.superficie > 0):
                salida.estatus = "ERROR"
                salida.mensaje = "La superficie de la ubicación debe ser un número mayor a cero."
                return salida

            set_query = {
                "ubicacion.$.nombreUbicacion": ubicacion_data.nombreUbicacion,
                "ubicacion.$.coordenadas.latitud": ubicacion_data.coordenadas.latitud,
                "ubicacion.$.coordenadas.longitud": ubicacion_data.coordenadas.longitud,
                "ubicacion.$.superficie": ubicacion_data.superficie,
                "ubicacion.$.tipoSuelo": ubicacion_data.tipoSuelo,
                "ubicacion.$.accesoAgua": ubicacion_data.accesoAgua
            }

            #Actualizar la ubicación específica dentro del array 'ubicacion' del cultivo
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo, "ubicacion.idUbicacion": id_ubicacion},
                {"$set": set_query})

            if result.matched_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"No se encontró el cultivo con ID '{id_cultivo}' o la ubicación con ID '{id_ubicacion}' "
                    "dentro de ese cultivo.")
                return salida

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = (f"Ubicación con ID '{id_ubicacion}' del cultivo ID '{id_cultivo}' "
                                  "actualizada con éxito.")
            else:
                salida.estatus = "OK"
                salida.mensaje = (f"Los datos proporcionados para la ubicación ID '{id_ubicacion}' son los mismos "
                                  "que los existentes. No se realizaron cambios.")

        except Exception as ex:
            print(f"Error en CultivoDAO.actualizarUbicacionDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la ubicación. Consulte al administrador."
        return salida



    def borrarUbicacionDeCultivo(self, id_cultivo: str, id_ubicacion: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            result = self.db.cultivos.update_one({"_id": obj_id_cultivo}, {"$pull": {"ubicacion": {"idUbicacion": id_ubicacion}}})

            if result.matched_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el cultivo con ID '{id_cultivo}'."
                return salida

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = (f"Ubicación con ID '{id_ubicacion}' eliminada con éxito del "
                                  f"cultivo ID '{id_cultivo}'.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = (f"No se encontró la ubicación con ID '{id_ubicacion}' en el cultivo "
                                  f"ID '{id_cultivo}', o ya había sido eliminada.")

        except Exception as ex:
            print(f"Error en CultivoDAO.borrarUbicacionDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al intentar eliminar la ubicación. Consulte al administrador."
        return salida



    def consultarUbicacionDeCultivoPorId(self, id_cultivo: str, id_ubicacion: str) -> UbicacionSalidaIndividual:
        salida = UbicacionSalidaIndividual(estatus="", mensaje="", ubicacion=None)
        try:
            #Validar y convertir id_cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            #Buscar el cultivo y la ubicación específica.
            cultivo_doc = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo, "ubicacion.idUbicacion": id_ubicacion},
                {"_id": 0, "ubicacion": {"$elemMatch": {"idUbicacion": id_ubicacion}}})

            if cultivo_doc and "ubicacion" in cultivo_doc and cultivo_doc["ubicacion"]:
                ubicacion_encontrada_dict = cultivo_doc["ubicacion"][0]

                salida.ubicacion = UbicacionSubConsulta(**ubicacion_encontrada_dict)
                salida.estatus = "OK"
                salida.mensaje = (f"Ubicación con ID '{id_ubicacion}' encontrada en el "
                                  f"cultivo ID '{id_cultivo}'.")
            else:
                salida.estatus = "ERROR"
                salida.mensaje = (f"No se encontró la ubicación con ID '{id_ubicacion}' en el "
                                  f"cultivo ID '{id_cultivo}'.")

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarUbicacionDeCultivoPorId: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la ubicación. Consulte al administrador."
            salida.ubicacion = None
        return salida
