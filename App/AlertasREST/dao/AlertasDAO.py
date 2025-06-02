from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from models.AlertasModel import AlertaInsert, AlertaUpdate, AlertaSalida, Salida

class AlertasDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db.alertas

    def registrarAlerta(self, alerta: AlertaInsert) -> Salida:
        try:
            doc = alerta.dict()
            doc["fechaGenerada"] = datetime.combine(doc["fechaGenerada"], datetime.min.time())
            res = self.collection.insert_one(doc)
            if res.inserted_id:
                return Salida(estatus="OK", mensaje="Alerta registrada correctamente")
            else:
                return Salida(estatus="ERROR", mensaje="No se pudo registrar la alerta")
        except Exception as e:
            return Salida(estatus="ERROR", mensaje=f"Error interno: {str(e)}")

    def actualizarAlerta(self, id_alerta: str, alerta_data: AlertaUpdate) -> Salida:
        try:
            update_fields = {k: v for k, v in alerta_data.dict().items() if v is not None}
            if not update_fields:
                return Salida(estatus="ERROR", mensaje="No hay campos para actualizar")

            result = self.db.alertas.update_one(
                {"_id": ObjectId(id_alerta)},
                {"$set": update_fields}
            )

            if result.modified_count == 0:
                return Salida(estatus="ERROR", mensaje="Alerta no encontrada o sin cambios")

            return Salida(estatus="OK", mensaje="Alerta actualizada")
        except Exception as e:
            return Salida(estatus="ERROR", mensaje=str(e))

    def eliminarAlerta(self, id_alerta: str) -> Salida:
        try:
            res = self.collection.delete_one({"_id": ObjectId(id_alerta)})
            if res.deleted_count == 1:
                return Salida(estatus="OK", mensaje="Alerta eliminada correctamente")
            else:
                return Salida(estatus="ERROR", mensaje="No se encontró la alerta")
        except Exception as e:
            return Salida(estatus="ERROR", mensaje=f"Error interno: {str(e)}")

    def consultarAlertaPorId(self, id_alerta: str) -> Optional[AlertaSalida]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(id_alerta)})
            if doc:
                doc["idAlerta"] = str(doc["_id"])
                del doc["_id"]
                return AlertaSalida(**doc)
            return None
        except Exception:
            return None

    def listarAlertas(self) -> List[AlertaSalida]:
        alertas = []
        try:
            cursor = self.collection.find()
            for doc in cursor:
                doc["idAlerta"] = str(doc["_id"])
                del doc["_id"]
                alertas.append(AlertaSalida(**doc))
        except Exception:
            pass
        return alertas
