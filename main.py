from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import csv

import pandas as pd

app = FastAPI()

# Configuración de CORS para permitir solicitudes desde http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get('/hola')
def message():
    return "Hola mundo"

@app.get('/listar_usuarios')
def listar_usuarios():
    # Lee los datos del archivo CSV desde otra ruta
    ruta_csv = "users/usuarios.csv"
    df = pd.read_csv(ruta_csv)
    usuarios = df.to_dict(orient="records")
    return usuarios

@app.get('/obtiene-usuario/{id_usuario}')
def obtener_usuario(id_usuario: int):
    ruta_csv = "users/usuarios.csv"
    df = pd.read_csv(ruta_csv)  
    
    # Busca el usuario por ID
    usuario = df[df['idUsuario'] == id_usuario]

    # Si no se encuentra el usuario, devuelve un error HTTP 404
    if usuario.empty:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Obtiene el nombre completo y apellidos
    nombre_completo = f"{usuario['nombre'].values[0]} {usuario['apellidoPaterno'].values[0]} {usuario['apellidoMaterno'].values[0]}"

    # Devuelve el resultado
    return {"idUsuario": id_usuario, "nombreCompleto": nombre_completo, "apellidos": {
        "apellidoPaterno": usuario['apellidoPaterno'].values[0],
        "apellidoMaterno": usuario['apellidoMaterno'].values[0]
    }}


# Lista todas las cuentas del usuario
@app.get('/listar_cuentas/{idUsuario}')
def listar_cuentas(idUsuario: int):
    try:
        ruta_csv = "users/usuarios.csv"
        df = pd.read_csv(ruta_csv)
        # Filtra las filas del DataFrame correspondientes al idUsuario
        user_data = df[df['idUsuario'] == idUsuario].iloc[0]

        # Crea un diccionario con la información de las cuentas
        cuentas = {
            "cuentaBancaria1": user_data['cuentaBancaria1'],
            "saldoCuenta1": user_data['saldoCuenta1'],
            "tipoC1": user_data['tipoC1'],
            "CCI1": user_data['CCI1'],
        }

        # Verifica si la segunda cuenta no es nula
        if not pd.isna(user_data['cuentaBancaria2']):
            cuentas["cuentaBancaria2"] = user_data['cuentaBancaria2']
            cuentas["saldoCuenta2"] = user_data['saldoCuenta2']
            cuentas["tipoC2"] = user_data['tipoC2']
            cuentas["CCI2"] = user_data['CCI2']

        return cuentas
    except IndexError:
        return {"error": "No se encontró el idUsuario"}

@app.get("/info-cuenta/")
async def obtener_informacion_cuenta(cci: str = Query(..., description="CCI de la cuenta")):
    # Lee el archivo CSV
    ruta_csv = "users/usuarios.csv"
    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Busca la cuenta por CCI
            if row["CCI1"] == cci:
                return {
                    "cuentaBancaria": row["cuentaBancaria1"],
                    "saldoCuenta": row["saldoCuenta1"],
                    "tipoCuenta": row["tipoC1"],
                    "CCI": row["CCI1"]
                }
            elif row["CCI2"] == cci:
                return {
                    "cuentaBancaria": row["cuentaBancaria2"],
                    "saldoCuenta": row["saldoCuenta2"],
                    "tipoCuenta": row["tipoC2"],
                    "CCI": row["CCI2"]
                }
        # Si no se encuentra la cuenta, devuelve un error
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")


@app.get("/obtener_tarjeta/{idUsuario}")
def obtener_tarjeta(idUsuario: int):
    ruta_csv = "users/usuarios.csv"
    df = pd.read_csv(ruta_csv)
    usuario = df[df['idUsuario'] == idUsuario]
    
    if usuario.empty:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    tarjeta = usuario['tarjeta'].values[0]
    
    return {"idUsuario": idUsuario, "tarjeta": tarjeta}


@app.post('/realizar_deposito/{idUsuario}')
def realizar_deposito(idUsuario: int, CCI: str, monto: float, moneda: str):
    try:
        ruta_csv = "users/usuarios.csv"
        df = pd.read_csv(ruta_csv)
        # Tasas de conversión
        tasa_dolar_a_sol = 3.5  # Cambiar a la tasa de conversión real
        tasa_sol_a_dolar = 0.28  # Cambiar a la tasa de conversión real
        # Filtrar las filas del DataFrame correspondientes al idUsuario
        user_data = df[df['idUsuario'] == idUsuario].iloc[0]

        # Determinar si el CCI corresponde a la cuenta 1 o la cuenta 2
        if CCI == user_data['CCI1']:
            cuenta = 'cuentaBancaria1'
            saldo = 'saldoCuenta1'
            tipo_moneda = 'tipoC1'
        elif CCI == user_data['CCI2']:
            cuenta = 'cuentaBancaria2'
            saldo = 'saldoCuenta2'
            tipo_moneda = 'tipoC2'
        else:
            return {"error": "CCI no válido"}

        # Verificar el tipo de moneda y aplicar la tasa de conversión si es necesario
        if moneda == 'D' and user_data[tipo_moneda] == 'S':
            monto *= tasa_dolar_a_sol
        elif moneda == 'S' and user_data[tipo_moneda] == 'D':
            monto *= tasa_sol_a_dolar

        # Actualizar el saldo de la cuenta
        df.loc[df['idUsuario'] == idUsuario, saldo] += monto
        df.to_csv(ruta_csv, index=False)

        return {"mensaje": "Depósito exitoso"}
    except IndexError:
        raise HTTPException(status_code=404, detail="No se encontró el idUsuario")


@app.post('/realizar_retiro/{idUsuario}')
def realizar_retiro(idUsuario: int, CCI: str, monto: float, moneda: str):
    try:
        ruta_csv = "users/usuarios.csv"
        df = pd.read_csv(ruta_csv)
        
        # Tasas de conversión
        tasa_dolar_a_sol = 3.6  # Cambiar a la tasa de conversión real
        tasa_sol_a_dolar = 0.27  # Cambiar a la tasa de conversión real
        
        # Filtrar las filas del DataFrame correspondientes al idUsuario
        user_data = df[df['idUsuario'] == idUsuario].iloc[0]

        # Determinar si el CCI corresponde a la cuenta 1 o la cuenta 2
        if CCI == user_data['CCI1']:
            cuenta = 'cuentaBancaria1'
            saldo = 'saldoCuenta1'
            tipo_moneda = 'tipoC1'
        elif CCI == user_data['CCI2']:
            cuenta = 'cuentaBancaria2'
            saldo = 'saldoCuenta2'
            tipo_moneda = 'tipoC2'
        else:
            return {"error": "CCI no válido"}

        # Verificar el tipo de moneda y aplicar la tasa de conversión si es necesario
        if moneda == 'D' and user_data[tipo_moneda] == 'S':
            monto *= tasa_dolar_a_sol
        elif moneda == 'S' and user_data[tipo_moneda] == 'D':
            monto *= tasa_sol_a_dolar

        # Verificar si hay saldo suficiente
        if user_data[saldo] >= monto:
            # Realizar el retiro
            df.loc[df['idUsuario'] == idUsuario, saldo] -= monto
            df.to_csv(ruta_csv, index=False)
            return {"mensaje": "Retiro exitoso"}
        else:
            return {"error": "Saldo insuficiente"}

    except IndexError:
        raise HTTPException(status_code=404, detail="No se encontró el idUsuario")



@app.post('/realizar_cobro_comision/{idUsuario}')
def realizar_cobro_comision(idUsuario: int, CCI: str, comision: float):
    try:
        # Leemos el csv con los usuarios
        ruta_csv = "users/usuarios.csv"
        df = pd.read_csv(ruta_csv)
        
        # Tasas de conversión
        tasa_sol_a_dolar = 0.25  # Cambiar a la tasa de conversión real
        
        # Filtrar las filas del DataFrame correspondientes al idUsuario
        user_data = df[df['idUsuario'] == idUsuario].iloc[0]

        # Determinar si el CCI corresponde a la cuenta 1 o la cuenta 2
        if CCI == user_data['CCI1']:
            cuenta = 'cuentaBancaria1'
            saldo = 'saldoCuenta1'
            tipo_moneda = 'tipoC1'
        elif CCI == user_data['CCI2']:
            cuenta = 'cuentaBancaria2'
            saldo = 'saldoCuenta2'
            tipo_moneda = 'tipoC2'
        else:
            return {"error": "CCI no válido"}

        # Verificar el tipo de moneda y aplicar la tasa de conversión si es necesario
        if user_data[tipo_moneda] == 'D':
            comision *= tasa_sol_a_dolar

        # Restar la comisión al saldo
        if user_data[saldo] >= comision:
            df.loc[df['idUsuario'] == idUsuario, saldo] -= comision
            df.to_csv(ruta_csv, index=False)
            return {"mensaje": "Cobro de comisión exitoso"}
        else:
            return {"error": "Saldo insuficiente para el cobro de comisión"}

    except IndexError:
        raise HTTPException(status_code=404, detail="No se encontró el idUsuario")