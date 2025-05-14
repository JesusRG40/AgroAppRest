from bson import ObjectId
from models.riegosModels import RiegoInsert, RiegoUpdate, Salida, RiegosSalida, RiegoDetalleSalida, RiegoDetalle
from datetime import datetime, date

class RiegosDAO:
    def __init__(self, db):
        self.db = db
        self.coleccion = db["riegos"]

    def registrar(self, riego: RiegoInsert) -> Salida:
        # Convertir los nombres de los campos de RiegoInsert a los nombres esperados por MongoDB
        nuevo = {
            "fecha": datetime.combine(riego.fechaRiego, datetime.min.time()),  # Convertir date a datetime
            "cantidad": riego.cantidadAgua,
            "metodo": riego.metodoRiego,
            "duracion": riego.duracionRiego,
            "idUsuario": riego.idUsuario
        }

        # Insertar el nuevo riego
        resultado = self.coleccion.insert_one(nuevo)

        if not resultado.inserted_id:
            return Salida(mensaje="Error al registrar riego", success=False, estatus=400)

        return Salida(mensaje="Riego registrado exitosamente", success=True, estatus=201)
    def editar(self, idRiego: str, datos: RiegoUpdate) -> Salida:
        try:
            filtro = {"_id": ObjectId(idRiego)}
        except Exception:
            return Salida(mensaje="ID de riego inválido", success=False, estatus=400)

        datos_actualizados = {}
        for k, v in datos.dict().items():
            if v is not None:
                # Convertir date a datetime
                if isinstance(v, date) and not isinstance(v, datetime):
                    v = datetime.combine(v, datetime.min.time())
                datos_actualizados[k] = v

        resultado = self.coleccion.update_one(filtro, {"$set": datos_actualizados})

        if resultado.matched_count == 0:
            return Salida(mensaje="Riego no encontrado", success=False, estatus=404)

        return Salida(mensaje="Riego actualizado correctamente", success=True, estatus=200)

    def borrar(self, idRiego: str) -> Salida:
        try:
            filtro = {"_id": ObjectId(idRiego)}
        except Exception:
            return Salida(mensaje="ID de riego inválido", success=False, estatus=400)

        resultado = self.coleccion.delete_one(filtro)

        if resultado.deleted_count == 0:
            return Salida(mensaje="Riego no encontrado", success=False, estatus=404)

        return Salida(mensaje="Riego eliminado correctamente", success=True, estatus=200)

    def consultar_lista(self) -> RiegosSalida:
        lista = []
        for riego in self.coleccion.find():
            riego_detalle = RiegoDetalle(
                idRiego=str(riego["_id"]),
                fechaRiego=riego["fecha"],  # Cambié 'fecha' a 'fechaRiego'
                cantidadAgua=riego["cantidad"],  # Cambié 'cantidad' a 'cantidadAgua'
                metodoRiego=riego["metodo"],  # Cambié 'metodo' a 'metodoRiego'
                duracionRiego=riego["duracion"],  # Cambié 'duracion' a 'duracionRiego'
                idUsuario=riego["idUsuario"]
            )
            lista.append(riego_detalle)
        return RiegosSalida(riegos=lista)

    def consultar(self, idRiego: str) -> RiegoDetalleSalida:
        try:
            # Convertir la ID a ObjectId
            filtro = {"_id": ObjectId(idRiego)}
        except Exception as e:
            # Captura cualquier error al convertir la ID
            return Salida(mensaje="ID de riego inválido", success=False, estatus=400)

        # Consulta a la base de datos
        riego = self.coleccion.find_one(filtro)

        if not riego:
            return Salida(mensaje="Riego no encontrado", success=False, estatus=404)

        return RiegoDetalleSalida(
            riego=RiegoDetalle(
                idRiego=str(riego["_id"]),
                fechaRiego=riego["fecha"],
                cantidadAgua=riego["cantidad"],
                metodoRiego=riego["metodo"],
                duracionRiego=riego["duracion"],
                idUsuario=riego["idUsuario"]
            ),
            mensaje="Riego encontrado",
            success=True,
            estatus=200
        )
