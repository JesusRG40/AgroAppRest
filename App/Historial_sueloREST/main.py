import uvicorn
from fastapi import FastAPI
from dao.mongo import Conexion
from routers import historial_sueloRouters  # Solo se importa historial_suelo

app = FastAPI()

# Registrar el router de historial_suelo
app.include_router(historial_sueloRouters.router)

@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a AgroApp - Historial de Suelo"}

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
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)
