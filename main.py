from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd


app = FastAPI()

# Configuración de CORS para permitir solicitudes desde http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get('/hola')
def message():
    return "Hola mundo"

@app.get('/usuarios')
def listar_usuarios():
    # Lee los datos del archivo CSV desde otra ruta
    ruta_csv = "users/usuarios.csv"
    df = pd.read_csv(ruta_csv)
    usuarios = df.to_dict(orient="records")
    return usuarios

