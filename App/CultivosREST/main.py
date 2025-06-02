import uvicorn
from fastapi import FastAPI
from dao.database import Conexion
from rooters import cultivosRouter, riegosRouters

app = FastAPI()

# Incluir routers
app.include_router(cultivosRouter.router)
app.include_router(riegosRouters.router)

# Ruta base
@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a Agrosystem"}  # Arreglado el diccionario

# Conexión a MongoDB al iniciar
@app.on_event("startup")
async def startup():
    print("Conectando con MongoDB")
    conexion = Conexion()
    app.conexion = conexion
    app.db = conexion.getDB()

# Cierre de conexión al terminar
@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexión con MongoDB")
    app.conexion.cerrar()

# Ejecutar el servidor si es archivo principal
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", reload=True)
