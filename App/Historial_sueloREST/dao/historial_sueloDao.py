from bson import ObjectId
from models.historial_sueloModels import *
from datetime import datetime, date

class HistorialSueloDAO:
    def __init__(self, db):
        self.db = db
        self.coleccion = db["historial_suelo"]

    def registrar(self, historial_suelo: HistorialSueloInsert) -> Salida:
        nuevo = historial_suelo.dict()
        nuevo["fechaMedicion"] = datetime.combine(historial_suelo.fechaMedicion, datetime.min.time())
        resultado = self.coleccion.insert_one(nuevo)

        if not resultado.inserted_id:
            return Salida(mensaje="Error al registrar historial de suelo", success=False, estatus=400)

        return Salida(mensaje="Historial de suelo registrado exitosamente", success=True, estatus=201)

    def editar(self, idHistorial: str, datos: HistorialSueloUpdate) -> Salida:
        try:
            filtro = {"_id": ObjectId(idHistorial)}
        except Exception:
            return Salida(mensaje="ID inválido", success=False, estatus=400)

        datos_actualizados = {}
        for k, v in datos.dict().items():
            if v is not None:
                if isinstance(v, date) and not isinstance(v, datetime):
                    v = datetime.combine(v, datetime.min.time())
                datos_actualizados[k] = v

        resultado = self.coleccion.update_one(filtro, {"$set": datos_actualizados})
        if resultado.matched_count == 0:
            return Salida(mensaje="Historial no encontrado", success=False, estatus=404)

        return Salida(mensaje="Actualizado correctamente", success=True, estatus=200)

    def borrar(self, idHistorial: str) -> Salida:
        try:
            filtro = {"_id": ObjectId(idHistorial)}
        except Exception:
            return Salida(mensaje="ID inválido", success=False, estatus=400)

        resultado = self.coleccion.update_one(filtro, {"$set": {"eliminado": True}})
        if resultado.matched_count == 0:
            return Salida(mensaje="Historial no encontrado", success=False, estatus=404)

        return Salida(mensaje="Historial eliminado lógicamente", success=True, estatus=200)

    def consultar_lista(self) -> HistorialSueloSalida:
        lista = []
        for h in self.coleccion.find({"eliminado": False}):
            nombre_cultivo = self.db.cultivos.find_one({"_id": ObjectId(h["idCultivo"])}, {"nomCultivo": 1})
            nombre_usuario = self.db.usuarios.find_one({"_id": ObjectId(h["idUsuario"])}, {"nombre": 1})

            historial_detalle = HistorialSueloDetalle(
                idHistorial=str(h["_id"]),
                fechaMedicion=h["fechaMedicion"],
                pH=h["pH"],
                nutrientes=h["nutrientes"],
                observaciones=h["observaciones"],
                idCultivo=nombre_cultivo.get("nomCultivo", "Desconocido") if nombre_cultivo else "Desconocido",
                idUsuario=nombre_usuario.get("nombre", "Desconocido") if nombre_usuario else "Desconocido"
            )
            lista.append(historial_detalle)
        return HistorialSueloSalida(historiales=lista)

    def consultar(self, idHistorial: str) -> HistorialSueloDetalleSalida:
        try:
            filtro = {"_id": ObjectId(idHistorial), "eliminado": False}
        except Exception:
            return Salida(mensaje="ID inválido", success=False, estatus=400)

        historial = self.coleccion.find_one(filtro)
        if not historial:
            return Salida(mensaje="No encontrado", success=False, estatus=404)

        nombre_cultivo = self.db.cultivos.find_one({"_id": ObjectId(historial["idCultivo"])}, {"nomCultivo": 1})
        nombre_usuario = self.db.usuarios.find_one({"_id": ObjectId(historial["idUsuario"])}, {"nombre": 1})

        return HistorialSueloDetalleSalida(
            historial=HistorialSueloDetalle(
                idHistorial=str(historial["_id"]),
                fechaMedicion=historial["fechaMedicion"],
                pH=historial["pH"],
                nutrientes=historial["nutrientes"],
                observaciones=historial["observaciones"],
                idCultivo=nombre_cultivo.get("nomCultivo", "Desconocido") if nombre_cultivo else "Desconocido",
                idUsuario=nombre_usuario.get("nombre", "Desconocido") if nombre_usuario else "Desconocido"
            ),
            mensaje="Historial encontrado",
            success=True,
            estatus=200
        )
