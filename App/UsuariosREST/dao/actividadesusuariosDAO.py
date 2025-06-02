from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import date

from models.ActividadesUsuariosModel import ActividadUsuarioInsert, Salida, ActividadUsuarioUpdate, \
    ActividadUsuarioDetalle, ActividadUsuarioDetalleSalida, ActividadesUsuariosSalida


class ActividadUsuarioDAO:
    VALID_ESTATUS = {"Pendiente", "Completada", "Cancelada"}

    def __init__(self, db):
        self.db = db

    def registrar(self, actividad: ActividadUsuarioInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # 1. Verificar campos requeridos y que no sean nulos/empty
            if actividad.actividad is None or actividad.actividad.strip() == "":
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'actividad' es obligatorio y no puede estar vacío."
                return salida

            if actividad.fechaActividad is None:
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'fechaActividad' es obligatorio."
                return salida

            if actividad.estatus is None or actividad.estatus.strip() == "":
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'estatus' es obligatorio y no puede estar vacío."
                return salida

            # 2. Validar que fechaActividad tenga un formato válido de fecha
            if not isinstance(actividad.fechaActividad, date):
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'fechaActividad' debe ser una fecha válida (YYYY-MM-DD)."
                return salida

            # 3. Verificar que estatus tenga un valor permitido
            if actividad.estatus not in self.VALID_ESTATUS:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"Estatus inválido. Los valores permitidos son: {', '.join(self.VALID_ESTATUS)}."
                )
                return salida

            # 4. Verificar que el cultivo exista en la base de datos
            try:
                oid_cultivo = ObjectId(actividad.idCultivo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de cultivo inválido: {actividad.idCultivo}"
                return salida

            cultivo_existente = self.db.cultivos.find_one({"_id": oid_cultivo})
            if not cultivo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un cultivo con id: {actividad.idCultivo}"
                return salida

            # 5. Verificar que el usuario exista en la base de datos
            try:
                oid_usuario = ObjectId(actividad.idUsuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de usuario inválido: {actividad.idUsuario}"
                return salida

            usuario_existente = self.db.usuarios.find_one({"_id": oid_usuario})
            if not usuario_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con id: {actividad.idUsuario}"
                return salida

            # 6. Insertar la actividad de usuario en la colección
            doc = jsonable_encoder(actividad)
            result = self.db.actividades_usuarios.insert_one(doc)

            salida.estatus = "OK"
            salida.mensaje = f"Actividad de usuario registrada con éxito con id: {result.inserted_id}"
            return salida

        except Exception as ex:
            print("ERROR en registrar actividad de usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al registrar la actividad de usuario, consulte al administrador."
            return salida

    def actualizar(self, id_actividad: str, datos: ActividadUsuarioUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid_act = ObjectId(id_actividad)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de actividad inválido: {id_actividad}"
                return salida

            # 2. Verificar que la actividad exista en la BD
            existente = self.db.actividades_usuarios.find_one({"_id": oid_act})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró una actividad con id: {id_actividad}"
                return salida

            update_fields = {}

            # 3. Si se proporcionó 'actividad', validar que no esté vacío
            if datos.actividad is not None:
                if datos.actividad.strip() == "":
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'actividad' no puede estar vacío si se envía."
                    return salida
                update_fields["actividad"] = datos.actividad

            # 4. Si se proporcionó 'fechaActividad', validar tipo y formato
            if datos.fechaActividad is not None:
                if not isinstance(datos.fechaActividad, date):
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'fechaActividad' debe ser una fecha válida (YYYY-MM-DD)."
                    return salida
                update_fields["fechaActividad"] = datos.fechaActividad

            # 5. Si se proporcionó 'estatus', validar que no esté vacío y sea permitido
            if datos.estatus is not None:
                if datos.estatus.strip() == "":
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'estatus' no puede estar vacío si se envía."
                    return salida
                if datos.estatus not in self.VALID_ESTATUS:
                    salida.estatus = "ERROR"
                    salida.mensaje = (
                        f"Estatus inválido. Los valores permitidos son: {', '.join(self.VALID_ESTATUS)}."
                    )
                    return salida
                update_fields["estatus"] = datos.estatus

            # 6. Si se proporcionó 'idCultivo', verificar que el cultivo exista
            if datos.idCultivo is not None:
                try:
                    oid_cultivo = ObjectId(datos.idCultivo)
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"ID de cultivo inválido: {datos.idCultivo}"
                    return salida

                cultivo_existente = self.db.cultivos.find_one({"_id": oid_cultivo})
                if not cultivo_existente:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"No se encontró un cultivo con id: {datos.idCultivo}"
                    return salida
                update_fields["idCultivo"] = datos.idCultivo

            # 7. Si se proporcionó 'idUsuario', verificar que el usuario exista
            if datos.idUsuario is not None:
                try:
                    oid_usuario = ObjectId(datos.idUsuario)
                except Exception:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"ID de usuario inválido: {datos.idUsuario}"
                    return salida

                usuario_existente = self.db.usuarios.find_one({"_id": oid_usuario})
                if not usuario_existente:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"No se encontró un usuario con id: {datos.idUsuario}"
                    return salida
                update_fields["idUsuario"] = datos.idUsuario

            # 8. Si no se proporcionó ningún campo (todos son None), no hay nada que actualizar
            if not update_fields:
                salida.estatus = "ERROR"
                salida.mensaje = "No se proporcionaron campos para actualizar."
                return salida

            # 9. Ejecutar la actualización
            result = self.db.actividades_usuarios.update_one(
                {"_id": oid_act},
                {"$set": jsonable_encoder(update_fields)},
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Actividad {id_actividad} actualizada con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo actualizar la actividad (sin cambios detectados)."

            return salida

        except Exception as ex:
            print("ERROR en actualizar actividad de usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al actualizar la actividad de usuario, consulte al administrador."
            return salida

    def eliminar(self, id_actividad: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid_act = ObjectId(id_actividad)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de actividad inválido: {id_actividad}"
                return salida

            # 2. Verificar que la actividad exista en la BD
            existente = self.db.actividades_usuarios.find_one({"_id": oid_act})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró una actividad con id: {id_actividad}"
                return salida

            # 3. Realizar la eliminación lógica: cambiar estatus a "Cancelada"
            result = self.db.actividades_usuarios.update_one(
                {"_id": oid_act},
                {"$set": {"estatus": "Cancelada"}},
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Actividad {id_actividad} cancelada con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo eliminar la actividad (sin cambios detectados)."

            return salida

        except Exception as ex:
            print("ERROR en eliminar actividad de usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al eliminar la actividad de usuario, consulte al administrador."
            return salida

    def consultar(self, id_actividad: str) -> ActividadUsuarioDetalleSalida:
        salida = ActividadUsuarioDetalleSalida(estatus="", mensaje="", actividad=None)
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid_act = ObjectId(id_actividad)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de actividad inválido: {id_actividad}"
                return salida

            # 2. Buscar la actividad en la colección
            doc = self.db.actividades_usuarios.find_one({"_id": oid_act})
            if not doc:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró una actividad con id: {id_actividad}"
                return salida

            # 3. Obtener nombre del cultivo asociado
            cultivo_id = doc.get("idCultivo")
            nombre_cultivo = ""
            try:
                oid_cultivo = ObjectId(cultivo_id)
                cultivo_doc = self.db.cultivos.find_one({"_id": oid_cultivo})
                if cultivo_doc:
                    nombre_cultivo = cultivo_doc.get("nomCultivo", "")
            except Exception:
                # Si idCultivo no es un ObjectId válido, dejamos nombre_cultivo vacío
                nombre_cultivo = ""

            # 4. Obtener nombre del usuario asociado
            usuario_id = doc.get("idUsuario")
            nombre_usuario = ""
            try:
                oid_usuario = ObjectId(usuario_id)
                usuario_doc = self.db.usuarios.find_one({"_id": oid_usuario})
                if usuario_doc:
                    nombre_usuario = usuario_doc.get("nombre", "")
            except Exception:
                # Si idUsuario no es un ObjectId válido, dejamos nombre_usuario vacío
                nombre_usuario = ""

            # 5. Mapear el documento a ActividadUsuarioDetalle (incluyendo nombres)
            actividad_detalle = ActividadUsuarioDetalle(
                idActividad=id_actividad,
                actividad=doc.get("actividad", ""),
                fechaActividad=doc.get("fechaActividad"),
                estatus=doc.get("estatus", ""),
                idCultivo=doc.get("idCultivo", ""),
                idUsuario=doc.get("idUsuario", ""),
                nombreCultivo=nombre_cultivo,
                nombreUsuario=nombre_usuario,
            )

            # 6. Preparar la salida
            salida.estatus = "OK"
            salida.mensaje = f"Actividad {id_actividad} encontrada."
            salida.actividad = actividad_detalle
            return salida

        except Exception as ex:
            print("ERROR en consultar actividad de usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar la actividad de usuario, consulte al administrador."
            return salida

    def consultaGeneral(self) -> ActividadesUsuariosSalida:
        salida = ActividadesUsuariosSalida(estatus="", mensaje="", actividades=[])
        try:
            cursor = self.db.actividades_usuarios.find()
            lista_detalles = []

            for doc in cursor:
                # 1. Convertir _id a string
                id_act = str(doc.get("_id"))

                # 2. forzar estatus a string
                estatus_str = str(doc.get("estatus", ""))

                # 3. Convertir idCultivo a string y obtener nombreCultivo
                cultivo_id = doc.get("idCultivo")
                nombre_cultivo = ""
                cultivo_id_str = ""
                try:
                    # si está guardado como ObjectId
                    if isinstance(cultivo_id, ObjectId):
                        cultivo_id_str = str(cultivo_id)
                    else:
                        cultivo_id_str = str(cultivo_id)
                    oid_cult = ObjectId(cultivo_id_str)
                    cult_doc = self.db.cultivos.find_one({"_id": oid_cult})
                    if cult_doc:
                        nombre_cultivo = cult_doc.get("nomCultivo", "")
                except Exception:
                    cultivo_id_str = str(cultivo_id or "")
                    nombre_cultivo = ""

                # 4. Convertir idUsuario a string y obtener nombreUsuario
                usuario_id = doc.get("idUsuario")
                nombre_usuario = ""
                usuario_id_str = ""
                try:
                    if isinstance(usuario_id, ObjectId):
                        usuario_id_str = str(usuario_id)
                    else:
                        usuario_id_str = str(usuario_id)
                    oid_usr = ObjectId(usuario_id_str)
                    usr_doc = self.db.usuarios.find_one({"_id": oid_usr})
                    if usr_doc:
                        nombre_usuario = usr_doc.get("nombre", "")
                except Exception:
                    usuario_id_str = str(usuario_id or "")
                    nombre_usuario = ""

                # 5. Construir el detalle convirtiendo todos los campos a los tipos adecuados
                detalle = ActividadUsuarioDetalle(
                    idActividad=id_act,
                    actividad=doc.get("actividad", ""),
                    fechaActividad=doc.get("fechaActividad"),
                    estatus=estatus_str,
                    idCultivo=cultivo_id_str,
                    idUsuario=usuario_id_str,
                    nombreCultivo=nombre_cultivo,
                    nombreUsuario=nombre_usuario,
                )
                lista_detalles.append(detalle)

            salida.estatus = "OK"
            salida.mensaje = "Listado de todas las actividades con detalle."
            salida.actividades = lista_detalles
            return salida

        except Exception as ex:
            print("ERROR en consulta general actividades:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al obtener listado de actividades, consulte al administrador."
            return salida