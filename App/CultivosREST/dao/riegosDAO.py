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
            # Validar y convertir el ID del cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                print("ID de cultivo inválido:", id_cultivo)
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Verificar que el cultivo exista
            cultivo_existente = self.db.cultivos.find_one({"_id": obj_id_cultivo})
            print("Cultivo encontrado:", cultivo_existente)  # Este es importante
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con el ID: {id_cultivo}."
                return salida

            # Verificar que el usuario exista
            print("ID Usuario recibido:", riego_data.idUsuario)
            try:
                usuario_existente = self.db.usuarios.find_one({"_id": ObjectId(riego_data.idUsuario)})
            except Exception as e:
                print("Error convirtiendo ID de usuario:", riego_data.idUsuario)
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del usuario proporcionado no tiene un formato válido."
                return salida

            print("Usuario encontrado:", usuario_existente)  # Este también es importante
            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con el ID: {riego_data.idUsuario}."
                return salida

            # Preparar documento del nuevo riego
            nuevo_riego_dict = riego_data.model_dump()
            nuevo_riego_dict["idRiego"] = str(ObjectId())
            nuevo_riego_dict["idUsuario"] = ObjectId(nuevo_riego_dict["idUsuario"])
            
            nuevo_riego_dict["fechaRiego"] = datetime.combine(riego_data.fechaRiego, datetime.min.time())

            # Insertar el riego en el array 'riegos' del cultivo
            result = self.db.cultivos.update_one(
                {"_id": obj_id_cultivo},
                {"$push": {"riegos": nuevo_riego_dict}}
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = (
                    f"Riego agregado exitosamente al cultivo con ID '{id_cultivo}'. "
                    f"ID del riego: {nuevo_riego_dict['idRiego']}."
                )
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el riego. Verifica que el cultivo siga existiendo."

        except Exception as ex:
            print(f"Error en CultivoDAO.registrarNuevoRiego: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar el riego. Consulte al administrador."
        return salida

    def actualizarRiegoDeCultivo(self, id_cultivo: str, id_riego: str, riego_data: RiegoParcialUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # Validar ID del cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID del cultivo no válido."
                return salida

            # Preparar los campos a actualizar
            campos_actualizar = {}

            # Convertir fechaRiego de date a datetime.datetime si se proporciona
            if riego_data.fechaRiego is not None:
                campos_actualizar["riegos.$.fechaRiego"] = datetime.combine(riego_data.fechaRiego, datetime.min.time())

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

            if riego_data.eliminado is not None:
                campos_actualizar["riegos.$.eliminado"] = riego_data.eliminado

            # Validar que haya algo para actualizar
            if not campos_actualizar:
                salida.estatus = "ERROR"
                salida.mensaje = "No se proporcionaron campos para actualizar."
                return salida

            # Realizar la actualización
            result = self.db.cultivos.update_one(
                {
                    "_id": obj_id_cultivo,
                    "riegos.idRiego": id_riego,
                    "riegos.eliminado": False
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
                salida.mensaje = f"No se realizaron cambios; los datos son iguales a los existentes."

        except Exception as ex:
            print(f"Error en CultivoDAO.actualizarRiegoDeCultivo: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar el riego."
        return salida


    def consultarRiegoDeCultivoPorId(self, id_cultivo: str, id_riego: str) -> RiegoConsultaIndividual:
        salida = RiegoConsultaIndividual(estatus="", mensaje="", riego=None)
        try:
            # Validar el ID del cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "El ID del cultivo proporcionado no tiene un formato válido."
                return salida

            # Buscar el cultivo con el riego que coincida y que no esté eliminado
            cultivo_doc = self.db.cultivos.find_one(
                {
                    "_id": obj_id_cultivo,
                    "riegos": {
                        "$elemMatch": {
                            "idRiego": id_riego,
                            "eliminado": False
                        }
                    }
                },
                {
                    "_id": 0,
                    "riegos": {
                        "$elemMatch": {
                            "idRiego": id_riego,
                            "eliminado": False
                        }
                    }
                }
            )

            if cultivo_doc and "riegos" in cultivo_doc and cultivo_doc["riegos"]:
                riego_encontrado = cultivo_doc["riegos"][0]

                # Obtener el nombre del usuario
                id_usuario = riego_encontrado.get("idUsuario")
                if isinstance(id_usuario, ObjectId):
                    id_usuario = str(id_usuario)
                
                try:
                    usuario_doc = self.db.usuarios.find_one({"_id": ObjectId(id_usuario)}, {"nombre": 1})
                    nombre_usuario = usuario_doc["nombre"] if usuario_doc else "Desconocido"
                except:
                    nombre_usuario = "Desconocido"

                # Reemplazar idUsuario por nombre
                riego_encontrado["idUsuario"] = nombre_usuario

                # Asegurarse que tenga idRiego
                if "idRiego" not in riego_encontrado:
                    riego_encontrado["idRiego"] = id_riego

                salida.riego = RiegoConsulta(**riego_encontrado)
                salida.estatus = "OK"
                salida.mensaje = f"Riego con ID '{id_riego}' encontrado en el cultivo."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el riego con ID '{id_riego}' en el cultivo o está marcado como eliminado."

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarRiegoDeCultivoPorId: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar el riego. Consulte al administrador."

        return salida


    def consultarRiegosDeCultivo(self, id_cultivo: str) -> RiegosSalida:
        salida = RiegosSalida(riegos=[])
        try:
            # Validar ID del cultivo
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                return salida

            # Buscar el cultivo
            cultivo_doc = self.db.cultivos.find_one(
                {"_id": obj_id_cultivo},
                {"_id": 0, "riegos": 1}
            )

            if cultivo_doc and "riegos" in cultivo_doc:
                riegos_filtrados = []
                for r in cultivo_doc["riegos"]:
                    if not r.get("eliminado", False):
                        # Convertir ObjectId a string si es necesario
                        id_usuario = str(r["idUsuario"]) if isinstance(r["idUsuario"], ObjectId) else r["idUsuario"]
                        
                        # Consultar nombre del usuario
                        usuario_doc = self.db.usuarios.find_one({"_id": ObjectId(id_usuario)}, {"nombre": 1})
                        nombre_usuario = usuario_doc["nombre"] if usuario_doc else "Desconocido"
                        
                        # Armar nuevo riego con nombre en vez de id
                        r_copy = r.copy()
                        r_copy["idUsuario"] = nombre_usuario
                        
                        # Añadir idRiego si no tiene
                        if "idRiego" not in r_copy:
                            r_copy["idRiego"] = "Sin ID"

                        riegos_filtrados.append(RiegoConsulta(**r_copy))

                salida.riegos = riegos_filtrados

        except Exception as ex:
            print(f"Error en CultivoDAO.consultarRiegosDeCultivo: {ex}")

        return salida




    def eliminarRiegoLogico(self, id_cultivo: str, id_riego: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            try:
                obj_id_cultivo = ObjectId(id_cultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = "ID de cultivo no válido."
                return salida

            # Solo actualizar si el riego NO está ya eliminado
            result = self.db.cultivos.update_one(
                {
                    "_id": obj_id_cultivo,
                    "riegos.idRiego": id_riego,
                    "riegos.eliminado": False  # evita actualizar si ya está eliminado
                },
                {"$set": {"riegos.$.eliminado": True}}
            )

            if result.matched_count == 0:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró el riego con ID '{id_riego}' activo en el cultivo '{id_cultivo}'."
                return salida

            if result.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Riego con ID '{id_riego}' eliminado lógicamente."
            else:
                salida.estatus = "OK"
                salida.mensaje = "El riego ya estaba marcado como eliminado."

        except Exception as ex:
            print(f"Error en eliminarRiegoLogico: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar el riego."
        return salida
