import uvicorn
from fastapi import FastAPI
from dao.database import Conexion
from rooters import cultivosRouter, usuariosRouter, riegosRouter, historial_sueloRouter, aplicacionesInsumoRouter

app=FastAPI()
app.include_router(cultivosRouter.router)
app.include_router(usuariosRouter.router)
app.include_router(riegosRouter.router)
app.include_router(historial_sueloRouter.router)
app.include_router(aplicacionesInsumoRouter.router)


@app.get("/")
async def home():
    salida={"mensaje: Bienvenido a Agrosystem"}
    return salida

@app.on_event("startup")
async def startup():
    print("Conectando con MongoDB")
    conexion=Conexion()
    app.conexion=conexion
    app.db=conexion.getDB()

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexion con MongoDB")
    app.conexion.cerrar()


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', reload=True)
