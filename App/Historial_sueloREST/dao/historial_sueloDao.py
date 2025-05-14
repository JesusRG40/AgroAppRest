from bson import ObjectId
from models.historial_sueloModels import HistorialSueloInsert, HistorialSueloUpdate, Salida, HistorialSueloSalida, HistorialSueloDetalleSalida, HistorialSueloDetalle
from datetime import datetime, date

class HistorialSueloDAO:
    def __init__(self, db):
        self.db = db
        self.coleccion = db["historial_suelo"]

    def registrar(self, historial_suelo: HistorialSueloInsert) -> Salida:
        # Convertir los datos de HistorialSueloInsert a la estructura que espera MongoDB
        nuevo = {
            "fechaMedicion": datetime.combine(historial_suelo.fechaMedicion, datetime.min.time()),  # Convertir date a datetime
            "pH": historial_suelo.pH,
            "nutrientes": historial_suelo.nutrientes,
            "observaciones": historial_suelo.observaciones,
            "idCultivo": historial_suelo.idCultivo,
            "idUsuario": historial_suelo.idUsuario
        }

        # Insertar el nuevo historial de suelo
        resultado = self.coleccion.insert_one(nuevo)

        if not resultado.inserted_id:
            return Salida(mensaje="Error al registrar historial de suelo", success=False, estatus=400)

        return Salida(mensaje="Historial de suelo registrado exitosamente", success=True, estatus=201)

    def editar(self, idHistorial: str, datos: HistorialSueloUpdate) -> Salida:
        try:
            filtro = {"_id": ObjectId(idHistorial)}
        except Exception:
            return Salida(mensaje="ID de historial de suelo inválido", success=False, estatus=400)

        datos_actualizados = {}
        for k, v in datos.dict().items():
            if v is not None:
                # Convertir date a datetime
                if isinstance(v, date) and not isinstance(v, datetime):
                    v = datetime.combine(v, datetime.min.time())
                datos_actualizados[k] = v

        resultado = self.coleccion.update_one(filtro, {"$set": datos_actualizados})

        if resultado.matched_count == 0:
            return Salida(mensaje="Historial de suelo no encontrado", success=False, estatus=404)

        return Salida(mensaje="Historial de suelo actualizado correctamente", success=True, estatus=200)

    def borrar(self, idHistorial: str) -> Salida:
        try:
            filtro = {"_id": ObjectId(idHistorial)}
        except Exception:
            return Salida(mensaje="ID de historial de suelo inválido", success=False, estatus=400)

        resultado = self.coleccion.delete_one(filtro)

        if resultado.deleted_count == 0:
            return Salida(mensaje="Historial de suelo no encontrado", success=False, estatus=404)

        return Salida(mensaje="Historial de suelo eliminado correctamente", success=True, estatus=200)

    def consultar_lista(self) -> HistorialSueloSalida:
        lista = []
        for historial in self.coleccion.find():
            historial_detalle = HistorialSueloDetalle(
                idHistorial=str(historial["_id"]),
                fechaMedicion=historial["fechaMedicion"],
                pH=historial["pH"],
                nutrientes=historial["nutrientes"],
                observaciones=historial["observaciones"],
                idCultivo=historial["idCultivo"],
                idUsuario=historial["idUsuario"]
            )
            lista.append(historial_detalle)
        return HistorialSueloSalida(historiales=lista)

    def consultar(self, idHistorial: str) -> HistorialSueloDetalleSalida:
        try:
            # Convertir la ID a ObjectId
            filtro = {"_id": ObjectId(idHistorial)}
        except Exception as e:
            # Captura cualquier error al convertir la ID
            return Salida(mensaje="ID de historial de suelo inválido", success=False, estatus=400)

        # Consulta a la base de datos
        historial = self.coleccion.find_one(filtro)

        if not historial:
            return Salida(mensaje="Historial de suelo no encontrado", success=False, estatus=404)

        return HistorialSueloDetalleSalida(
            historial=HistorialSueloDetalle(
                idHistorial=str(historial["_id"]),
                fechaMedicion=historial["fechaMedicion"],
                pH=historial["pH"],
                nutrientes=historial["nutrientes"],
                observaciones=historial["observaciones"],
                idCultivo=historial["idCultivo"],
                idUsuario=historial["idUsuario"]
            ),
            mensaje="Historial de suelo encontrado",
            success=True,
            estatus=200
        )
