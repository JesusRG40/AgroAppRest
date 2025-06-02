from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from models.InsumosModel import InsumoInsert, Salida, InsumoUpdate, InsumoDetalleSalida, InsumoListado, InsumosSalida


class InsumoDAO:
    VALID_TIPOS = {"Insecticidas", "Fertilizantes", "Herbicidas", "Pesticidas", "Semillas"}

    def __init__(self, db):
        self.db = db

    def registrar(self, insumo: InsumoInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # 1. Verificar campos obligatorios y que no sean nulos/empty
            if insumo.nombreInsumo is None or insumo.nombreInsumo.strip() == "":
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'nombreInsumo' es obligatorio y no puede estar vacío."
                return salida

            if insumo.tipoInsumo is None or insumo.tipoInsumo.strip() == "":
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'tipoInsumo' es obligatorio y no puede estar vacío."
                return salida

            # 2. Verificar que cantDisponible sea un valor numérico >= 0
            if insumo.cantDisponible is None or insumo.cantDisponible < 0:
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'cantDisponible' debe ser un número mayor o igual a cero."
                return salida

            if insumo.unidadMedida is None or insumo.unidadMedida.strip() == "":
                salida.estatus = "ERROR"
                salida.mensaje = "El campo 'unidadMedida' es obligatorio y no puede estar vacío."
                return salida

            # 3. Validar que tipoInsumo pertenezca a la lista de tipos válidos
            if insumo.tipoInsumo not in self.VALID_TIPOS:
                salida.estatus = "ERROR"
                salida.mensaje = (
                    f"Tipo de insumo inválido. Los tipos permitidos son: {', '.join(self.VALID_TIPOS)}."
                )
                return salida

            # 4. Verificar unicidad de nombreInsumo
            existente = self.db.insumos.find_one({"nombreInsumo": insumo.nombreInsumo.strip()})
            if existente:
                salida.estatus = "ERROR"
                salida.mensaje = "Ya existe un insumo con el mismo nombre."
                return salida

            # 5. Insertar el insumo en la colección
            doc = jsonable_encoder(insumo)
            result = self.db.insumos.insert_one(doc)

            salida.estatus = "OK"
            salida.mensaje = f"Insumo registrado con éxito con id: {result.inserted_id}"
            return salida

        except Exception as ex:
            print("ERROR en registrar insumo:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al registrar el insumo, consulte al administrador."
            return salida

    def actualizar(self, id_insumo: str, datos: InsumoUpdate) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # 1. Verificar que el ID sea un ObjectId válido
            try:
                oid_insumo = ObjectId(id_insumo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de insumo inválido: {id_insumo}"
                return salida

            # 2. Verificar que el insumo exista en la base de datos
            existente = self.db.insumos.find_one({"_id": oid_insumo})
            if not existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un insumo con id: {id_insumo}"
                return salida

            update_fields = {}

            # 3. Si se proporciona 'nombreInsumo', validar no vacío y unicidad
            if datos.nombreInsumo is not None:
                nuevo_nombre = datos.nombreInsumo.strip()
                if nuevo_nombre == "":
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'nombreInsumo' no puede estar vacío si se envía."
                    return salida
                otro = self.db.insumos.find_one({
                    "nombreInsumo": nuevo_nombre,
                    "_id": {"$ne": oid_insumo}
                })
                if otro:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Ya existe otro insumo con el mismo nombre."
                    return salida
                update_fields["nombreInsumo"] = nuevo_nombre

            # 4. Si se proporciona 'tipoInsumo', validar que pertenezca a la lista válida
            if datos.tipoInsumo is not None:
                if datos.tipoInsumo not in self.VALID_TIPOS:
                    salida.estatus = "ERROR"
                    salida.mensaje = (
                        f"Tipo de insumo inválido. Los tipos permitidos son: {', '.join(self.VALID_TIPOS)}."
                    )
                    return salida
                update_fields["tipoInsumo"] = datos.tipoInsumo

            # 5. Si se proporciona 'cantDisponible', validar ≥ 0
            if datos.cantDisponible is not None:
                if datos.cantDisponible < 0:
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'cantDisponible' debe ser mayor o igual a cero si se envía."
                    return salida
                update_fields["cantDisponible"] = datos.cantDisponible

            # 6. Si se proporciona 'unidadMedida', validar no vacío
            if datos.unidadMedida is not None:
                if datos.unidadMedida.strip() == "":
                    salida.estatus = "ERROR"
                    salida.mensaje = "El campo 'unidadMedida' no puede estar vacío si se envía."
                    return salida
                update_fields["unidadMedida"] = datos.unidadMedida

            # 7. Si no se proporcionó ningún campo para actualizar
            if not update_fields:
                salida.estatus = "ERROR"
                salida.mensaje = "No se proporcionaron campos para actualizar."
                return salida

            # 8. Ejecutar la actualización
            result = self.db.insumos.update_one(
                {"_id": oid_insumo},
                {"$set": jsonable_encoder(update_fields)},
            )

            if result.modified_count == 1:
                salida.estatus = "OK"
                salida.mensaje = f"Insumo {id_insumo} actualizado con éxito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo actualizar el insumo (sin cambios detectados)."

            return salida

        except Exception as ex:
            print("ERROR en actualizar insumo:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al actualizar el insumo, consulte al administrador."
            return salida

    def eliminar(self, id_insumo: str) -> Salida:
        salida = Salida(estatus="", mensaje="")

        try:
            # Validar ID
            try:
                oid = ObjectId(id_insumo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de insumo inválido: {id_insumo}"
                return salida

            # Buscar insumo
            insumo_existente = self.db.insumos.find_one({"_id": oid})
            if not insumo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un insumo con ID: {id_insumo}"
                return salida

            # Verificar si ya está inactivo
            if insumo_existente.get("estatus", "Activo") == "Inactivo":
                salida.estatus = "ERROR"
                salida.mensaje = "El insumo ya ha sido eliminado previamente."
                return salida

            # Marcar como inactivo
            self.db.insumos.update_one(
                {"_id": oid},
                {"$set": {"estatus": "Inactivo"}}
            )

            salida.estatus = "OK"
            salida.mensaje = "Insumo eliminado (lógicamente) con éxito."
            return salida

        except Exception as ex:
            print("ERROR en eliminar insumo:", ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Ocurrió un error al intentar eliminar el insumo."
            return salida

    def obtener_por_id(self, id_insumo: str) -> InsumoDetalleSalida:
        salida = InsumoDetalleSalida(estatus="", mensaje="", insumo=None)

        try:
            # Validar formato del ID
            try:
                oid = ObjectId(id_insumo)
            except Exception:
                salida.estatus = "ERROR"
                salida.mensaje = f"ID de insumo inválido: {id_insumo}"
                return salida

            # Buscar el insumo
            insumo = self.db.insumos.find_one({"_id": oid})

            if not insumo:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontró un insumo activo con el ID: {id_insumo}"
                return salida

            # Preparar salida
            insumo["id"] = str(insumo["_id"])
            insumo.pop("_id", None)

            salida.estatus = "OK"
            salida.mensaje = "Insumo encontrado exitosamente."
            salida.insumo = insumo
            return salida

        except Exception as e:
            print("Error al obtener insumo:", e)
            salida.estatus = "ERROR"
            salida.mensaje = "Ocurrió un error al consultar el insumo. Contacte al administrador."
            return salida

    def consultaGeneral(self) -> InsumosSalida:
        salida = InsumosSalida(estatus="", mensaje="", insumos=[])
        try:

            documentos = self.db.insumos.find()

            insumos_list = []
            for doc in documentos:
                insumos_list.append({
                    "idInsumo": str(doc["_id"]),
                    "nombreInsumo": doc.get("nombreInsumo", ""),
                    "tipoInsumo": doc.get("tipoInsumo", ""),
                    "cantDisponible": doc.get("cantDisponible", 0.0),
                    "unidadMedida": doc.get("unidadMedida", "")
                })

            salida.estatus = "OK"
            salida.mensaje = "Listado de insumos"
            salida.insumos = insumos_list
        except Exception as e:
            salida.estatus = "ERROR"
            salida.mensaje = f"No se pudo obtener el listado: {str(e)}"
        return salida