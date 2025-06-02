from bson import ObjectId
from models.riegosModel import  RiegoConsulta, \
    RiegoConsultaIndividual, RiegoInsert, RiegosSalida, RiegoParcialUpdate, Salida
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from datetime import datetime   


class RiegosDAO:
    def __init__(self, db):
        self.db = db
    
    def registrarNuevoRiego(self, id_cultivo: str, riego_data: RiegoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
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

            try:
                usuario_existente = self.db.usuarios.find_one({"_id": ObjectId(riego_data.idUsuario)})
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del usuario proporcionado no tiene un formato válido."
                return salida

            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con el ID: {riego_data.idUsuario}."
                return salida

            nuevo_riego_dict = riego_data.model_dump()
            nuevo_riego_dict["idRiego"] = str(ObjectId())
            nuevo_riego_dict["idUsuario"] = ObjectId(nuevo_riego_dict["idUsuario"])
            
            # Convertir fechas a datetime.datetime con tiempo mínimo para MongoDB
            nuevo_riego_dict["fechaEsperada"] = datetime.combine(riego_data.fechaEsperada, datetime.min.time())
            if riego_data.fechaAplicada:
                nuevo_riego_dict["fechaAplicada"] = datetime.combine(riego_data.fechaAplicada, datetime.min.time())
            else:
                nuevo_riego_dict["fechaAplicada"] = None

            # Insertar en el array riegos sin campo eliminado ni filtros de status
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$push": {"riegos": nuevo_riego_dict}}
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Riego agregado exitosamente al cultivo con ID '{id_cultivo}'. ID del riego: {nuevo_riego_dict['idRiego']}."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el riego. Verifica que el cultivo siga existiendo."

        except Exception as ex:
            print(f"Error en RiegosDAO.registrarNuevoRiego: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar el riego. Consulte al administrador."
        return salida


    def actualizarRiegoDeCultivo(self, id_cultivo: str, id_riego: str, riego_data: RiegoParcialUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID del cultivo no válido."
                return salida

            campos_actualizar = {}

            # Actualizar fechas con nueva estructura
            if riego_data.fechaEsperada is not None:
                campos_actualizar["riegos.$.fechaEsperada"] = datetime.combine(riego_data.fechaEsperada, datetime.min.time())

            if riego_data.fechaAplicada is not None:
                campos_actualizar["riegos.$.fechaAplicada"] = datetime.combine(riego_data.fechaAplicada, datetime.min.time())

            if riego_data.cantAgua is not None:
                if riego_data.cantAgua <= 0:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La cantidad de agua debe ser mayor a cero."
                    return salida
                campos_actualizar["riegos.$.cantAgua"] = riego_data.cantAgua

            if riego_data.metodoRiego is not None:
                if not riego_data.metodoRiego.strip():
                    salida.estatus = "ERROR"
                    salida.mensaje = "El método de riego no puede estar vacío."
                    return salida
                campos_actualizar["riegos.$.metodoRiego"] = riego_data.metodoRiego

            if riego_data.duracionRiego is not None:
                if riego_data.duracionRiego <= 0:
                    salida.estatus = "ERROR"
                    salida.mensaje = "La duración debe ser mayor a cero."
                    return salida
                campos_actualizar["riegos.$.duracionRiego"] = riego_data.duracionRiego

            if riego_data.idUsuario is not None:
                try:
                    id_usuario_obj = ObjectId(riego_data.idUsuario)
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = "ID de usuario no válido."
                    return salida

                usuario_existente = self.db.usuarios.find_one({"_id": id_usuario_obj})
                if not usuario_existente:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"No se encontró un usuario con el ID: {riego_data.idUsuario}."
                    return salida
                campos_actualizar["riegos.$.idUsuario"] = id_usuario_obj

            if riego_data.status is not None:
                if riego_data.status not in ["Pendiente", "Aplicado", "Cancelado"]:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Estado (status) inválido."
                    return salida
                campos_actualizar["riegos.$.status"] = riego_data.status

            if not campos_actualizar:
                salida.estatus = "ERROR"
                salida.mensaje = "No se proporcionaron campos para actualizar."
                return salida

            result = self.db.cultivos.update_one(
                {
                    "_id": obj_id_cultivo,
                    "riegos.idRiego": id_riego
                },
                {"$set": campos_actualizar}
            )

            if result.matched_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el cultivo con ID '{id_cultivo}' o el riego con ID '{id_riego}'."
            elif result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Riego con ID '{id_riego}' actualizado exitosamente."
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios; los datos son iguales a los existentes."

        except Exception as ex:
            print(f"Error en RiegosDAO.actualizarRiegoDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar el riego."
        return salida


    def consultarRiegoDeCultivoPorId(self, id_cultivo: str, id_riego: str) -> RiegoConsultaIndividual:
        salida = RiegoConsultaIndividual(estatus="", mensaje="", riego=None)
        try:
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Ya no filtramos por status o eliminado, solo por idRiego
            cultivo_doc = self.db.cultivos.find_one(
                {
                    "_id": obj_id_cultivo,
                    "riegos.idRiego": id_riego
                },
                {
                    "_id": 0,
                    "riegos": {"$elemMatch": {"idRiego": id_riego}}
                }
            )

            if cultivo_doc and "riegos" in cultivo_doc and cultivo_doc["riegos"]:
                riego_encontrado = cultivo_doc["riegos"][0]

                id_usuario = riego_encontrado.get("idUsuario")
                if isinstance(id_usuario, ObjectId):
                    id_usuario = str(id_usuario)
                
                try:
                    usuario_doc = self.db.usuarios.find_one({"_id": ObjectId(id_usuario)}, {"nombre": 1})
                    nombre_usuario = usuario_doc["nombre"] if usuario_doc else "Desconocido"
                except:
                    nombre_usuario = "Desconocido"

                riego_encontrado["idUsuario"] = nombre_usuario

                if "idRiego" not in riego_encontrado:
                    riego_encontrado["idRiego"] = id_riego

                salida.riego = RiegoConsulta(**riego_encontrado)
                salida.estatus = "OK"
                salida.mensaje = f"Riego con ID '{id_riego}' encontrado en el cultivo."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el riego con ID '{id_riego}' en el cultivo."

        except Exception as ex:
            print(f"Error en RiegosDAO.consultarRiegoDeCultivoPorId: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar el riego. Consulte al administrador."

        return salida


    def consultarRiegosDeCultivo(self, id_cultivo: str) -> RiegosSalida:
        salida = RiegosSalida(estatus="OK", mensaje="Consulta correcta", riegos=[])
        try:
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID de cultivo inválido"
                return salida

            cultivo_doc = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo},
                {"_id": 0, "riegos": 1}
            )

            if cultivo_doc and "riegos" in cultivo_doc:
                riegos_lista = []
                for r in cultivo_doc["riegos"]:
                    id_usuario = str(r["idUsuario"]) if isinstance(r["idUsuario"], ObjectId) else r["idUsuario"]
                    usuario_doc = self.db.usuarios.find_one({"_id": ObjectId(id_usuario)}, {"nombre": 1})
                    nombre_usuario = usuario_doc["nombre"] if usuario_doc else "Desconocido"

                    r_copy = r.copy()
                    r_copy["idUsuario"] = nombre_usuario

                    if "idRiego" not in r_copy:
                        r_copy["idRiego"] = "Desconocido"

                    riegos_lista.append(RiegoConsulta(**r_copy))
                salida.riegos = riegos_lista
            else:
                salida.mensaje = "No se encontraron riegos para este cultivo"
        except Exception as ex:
            print(f"Error en RiegosDAO.consultarRiegosDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno del servidor"

        return salida


    def eliminarRiegoDeCultivo(self, id_cultivo: str, id_riego: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID del cultivo no válido."
                return salida

            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$pull": {"riegos": {"idRiego": id_riego}}}
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Riego con ID '{id_riego}' eliminado físicamente del cultivo."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el riego con ID '{id_riego}' para eliminar."

        except Exception as ex:
            print(f"Error en RiegosDAO.eliminarRiegoDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar el riego."
        return salida
