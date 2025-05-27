from fastapi.encoders import jsonable_encoder
import re
from bson import ObjectId
from models.UsuariosModel import UsuarioInsert, Salida, UsuarioUpdate, UsuariosSalida, UsuarioDetalleSalida, UsuarioDetalle


class UsuarioDAO:
    VALID_ROLES = {"Administrador", "Agricultor", "Supervisor"}

    def __init__(self, db):
        self.db = db

    def registrar(self, usuario: UsuarioInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # 1. Verificar que el email no exista
            existente = self.db.usuarios.find_one({"email": usuario.email})
            if existente:
                salida.estatus = "ERROR"
                salida.mensaje = "El correo electrónico ya está registrado."
                return salida

            # 2. Validar contraseña (mínimo 8 caracteres, mayúsculas, minúsculas y números)
            pwd = usuario.password
            if (
                len(pwd) < 8
                or not re.search(r"[A-Z]", pwd)
                or not re.search(r"[a-z]", pwd)
                or not re.search(r"\d", pwd)
            ):
                salida.estatus = "ERROR"
                salida.mensaje = (
                    "La contraseña debe tener al menos 8 caracteres, "
                    "incluir mayúsculas, minúsculas y números."
                )
                return salida

            # 3. Verificar que el rol sea válido
            if usuario.rol not in self.VALID_ROLES:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"Rol inválido. Los roles permitidos son: {', '.join(self.VALID_ROLES)}."
                )
                return salida

            # 4. Insertar el usuario en la base de datos
            doc = jsonable_encoder(usuario)
            result = self.db.usuarios.insert_one(doc)

            salida.estatus = "OK"
            salida.mensaje = f"Usuario registrado con éxito con id: {result.inserted_id}"
            return salida

        except Exception as ex:
            print("ERROR en registrar usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al registrar el usuario, consulte al administrador."
            return salida

    def actualizar(self, id_usuario: str, datos: UsuarioUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # 1. Verificar que el usuario exista
            oid = ObjectId(id_usuario)
            existente = self.db.usuarios.find_one({"_id": oid})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con id: {id_usuario}"
                return salida

            update_fields = {}

            # 2. Validar email si se va a modificar
            if datos.email is not None:
                otro = self.db.usuarios.find_one({
                    "email": datos.email,
                    "_id": {"$ne": oid}
                })
                if otro:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El correo electrónico ya está registrado en otro usuario."
                    return salida
                update_fields["email"] = datos.email

            # 3. Validar contraseña si se va a modificar
            if datos.password is not None:
                pwd = datos.password
                if (
                        len(pwd) < 8
                        or not re.search(r"[A-Z]", pwd)
                        or not re.search(r"[a-z]", pwd)
                        or not re.search(r"\d", pwd)
                ):
                    salida.estatus = "ERROR"
                    salida.mensaje = (
                        "La contraseña debe tener al menos 8 caracteres, "
                        "incluir mayúsculas, minúsculas y números."
                    )
                    return salida
                update_fields["password"] = datos.password

            # 4. Validar rol si se va a modificar
            if datos.rol is not None:
                if datos.rol not in self.VALID_ROLES:
                    salida.estatus = "ERROR"
                    salida.mensaje = (
                        f"Rol inválido. Los roles permitidos son: {', '.join(self.VALID_ROLES)}."
                    )
                    return salida
                update_fields["rol"] = datos.rol

            # 5. Campos simples
            for campo in ("nombre", "telefono", "estatus"):
                valor = getattr(datos, campo)
                if valor is not None:
                    update_fields[campo] = valor

            # 6. Domicilio completo si se provee
            if datos.domicilio is not None:
                update_fields["domicilio"] = jsonable_encoder(datos.domicilio)

            if not update_fields:
                salida.estatus = "ERROR"
                salida.mensaje = "No se proporcionaron campos para actualizar."
                return salida

            # 7. Ejecutar la actualización
            result = self.db.usuarios.update_one(
                {"_id": oid},
                {"$set": update_fields}
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Usuario {id_usuario} actualizado con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo actualizar el usuario (sin cambios detectados)."

            return salida

        except Exception as ex:
            print("ERROR en actualizar usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al actualizar el usuario, consulte al administrador."
            return salida

    def eliminar(self, id_usuario: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid = ObjectId(id_usuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de usuario inválido: {id_usuario}"
                return salida

            # 2. Verificar que el usuario exista
            existente = self.db.usuarios.find_one({"_id": oid})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con id: {id_usuario}"
                return salida

            # 3. Realizar la eliminación lógica (cambiar estatus a False)
            result = self.db.usuarios.update_one(
                {"_id": oid},
                {"$set": {"estatus": False}}
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Usuario {id_usuario} desactivado con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo eliminar el usuario (sin cambios detectados)."
            return salida

        except Exception as ex:
            print("ERROR en eliminar usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al eliminar el usuario, consulte al administrador."
            return salida

    def consultaGeneral(self):
        salida = UsuariosSalida(estatus="", mensaje="", usuarios=[])
        try:
            lista=list(self.db.usuariosListView.find())
            salida.estatus = "OK"
            salida.mensaje = "Listado de usuarios"
            salida.usuarios = lista
        except:
            salida.estatus="ERROR"
            salida.mensaje="No se pudo mostrar la lista"
        return salida

    def consultar(self, id_usuario: str) -> UsuarioDetalleSalida:
        salida = UsuarioDetalleSalida(estatus="", mensaje="", usuario=None)
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid = ObjectId(id_usuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de usuario inválido: {id_usuario}"
                return salida

            # 2. Buscar el usuario en la base de datos
            doc = self.db.usuarios.find_one({"_id": oid})
            if not doc:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con id: {id_usuario}"
                return salida

            # 3. Mapear el documento a UsuarioDetalle
            usuario_detalle = UsuarioDetalle(
                idUsuario=id_usuario,
                nombre=doc.get("nombre", ""),
                telefono=doc.get("telefono", ""),
                estatus=doc.get("estatus", False),
                domicilio=doc.get("domicilio"),
                email=doc.get("email", ""),
                password=doc.get("password", ""),
                rol=doc.get("rol", "")
            )

            # 4. Preparar la salida
            salida.estatus = "OK"
            salida.mensaje = f"Usuario {id_usuario} encontrado."
            salida.usuario = usuario_detalle
            return salida

        except Exception as ex:
            print("ERROR en consultar usuario:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar el usuario, consulte al administrador."
            return salida

    def iniciar_sesion(self, email: str, password: str) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # 1. Verificar que el email exista
            usuario = self.db.usuarios.find_one({"email": email})
            if not usuario:
                salida.estatus = "ERROR"
                salida.mensaje = "El correo electrónico no está registrado."
                return salida

            # 2. Comparar la contraseña
            if usuario.get("password") != password:
                salida.estatus = "ERROR"
                salida.mensaje = "Contraseña incorrecta."
                return salida

            # 3. Verificar que el usuario esté activo
            if not usuario.get("estatus", False):
                salida.estatus = "ERROR"
                salida.mensaje = "El usuario no está activo."
                return salida

            # 4. Credenciales correctas
            salida.estatus = "OK"
            salida.mensaje = f"Usuario {str(usuario['_id'])} autenticado con éxito."
            return salida

        except Exception as ex:
            print("ERROR en iniciar_sesion:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al iniciar sesión, consulte al administrador."
            return salida

    def asignar_rol(self, id_usuario: str, nuevo_rol: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid = ObjectId(id_usuario)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de usuario inválido: {id_usuario}"
                return salida

            # 2. Verificar que el usuario exista
            existente = self.db.usuarios.find_one({"_id": oid})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un usuario con id: {id_usuario}"
                return salida

            # 3. Verificar que el rol proporcionado sea válido
            if nuevo_rol not in self.VALID_ROLES:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"Rol inválido. Los roles permitidos son: {', '.join(self.VALID_ROLES)}."
                )
                return salida

            # 4. Actualizar el rol del usuario
            result = self.db.usuarios.update_one(
                {"_id": oid},
                {"$set": {"rol": nuevo_rol}}
            )
            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Rol de usuario {id_usuario} actualizado a '{nuevo_rol}'."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo actualizar el rol (sin cambios detectados)."
            return salida

        except Exception as ex:
            print("ERROR en asignar_rol:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al asignar rol, consulte al administrador."
            return salida

    def recuperar_password(self, email: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el email exista
            usuario = self.db.usuarios.find_one({"email": email})
            if not usuario:
                salida.estatus = "ERROR"
                salida.mensaje = "El correo electrónico no está registrado."
                return salida

            # 2. Devolver la contraseña en el mensaje
            pwd = usuario.get("password", "")
            salida.estatus = "OK"
            salida.mensaje = f"Tu contraseña es: {pwd}"
            return salida

        except Exception as ex:
            print("ERROR en recuperar_password:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al recuperar la contraseña, consulte al administrador."
            return salida
