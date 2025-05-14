import uvicorn
from fastapi import FastAPI

from dao.mongo import Conexion  # Importamos la clase de conexión
from routers import riegosRouters  # Importamos el router de riegos

# Crear la instancia de FastAPI
app = FastAPI()

# Registrar el router de riegos
app.include_router(riegosRouters.router)

@app.get("/")
async def home():
    salida = {"mensaje": "Bienvenido a RiegosRest"}
    return salida

@app.on_event("startup")
async def startup():
    print("Conectando con MongoDB")
    conexion = Conexion()
    app.conexion = conexion
    app.db = conexion.getDB()

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexión con MongoDB")
    app.conexion.cerrar()

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', reload=True)
