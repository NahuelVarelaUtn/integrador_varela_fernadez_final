#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#el primer comentario es para que funcione en sistemas Unix/Linux/Mac si se da permiso de ejecución al archivo
#el segundo comentario es para indicar la codificación UTF-8


"""
En este archivo tratamos de realizar una aplicación web simple usando Flask para gestionar y mostrar datos de los paísesn
nos basamos en videos de youtube y consultamos a IA.

Requisitos:
    pip install flask requests
Ejecución:
    python app.py
Luego abrir: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for
import funciones as f

CSV_FILE_PATH = "paises_lite.csv"
API_URL = "https://restcountries.com/v3.1/all?fields=name,population,area,region,continents"
PREFERIR_CSV = True  # CSV pisa API en duplicados

app = Flask(__name__)

PAISES = []

def cargar_datos():
    """Carga CSV (si existe), API (si puede) y combina en PAISES."""
    global PAISES
    paises_csv = []
    if os.path.exists(CSV_FILE_PATH):
        try:
            paises_csv = f.cargar_paises_desde_csv(CSV_FILE_PATH)
        except Exception as e:
            print(" Error CSV:", e)
    try:
        paises_api = f.cargar_desde_api(API_URL, timeout_segundos=20)
    except Exception as e:
        paises_api = []
        print(" Error API:", e)
    PAISES = f.combinar_csv_y_api(paises_csv, paises_api, preferir_csv=PREFERIR_CSV)

@app.route("/")
def index():
    if not PAISES:
        cargar_datos()

    nombre = request.args.get("nombre", "").strip()
    continente = request.args.get("continente", "").strip()
    minpop = request.args.get("minpop", "").strip()
    maxpop = request.args.get("maxpop", "").strip()
    sort = request.args.get("sort", "nombre").strip().lower()
    asc = request.args.get("asc", "1").strip()

    lista = PAISES[:]
    if nombre:
        lista = f.buscar_por_nombre(lista, nombre, exacto=False)
    if continente:
        lista = f.filtrar_por_continente(lista, continente)

    minimo = int(minpop) if minpop.isdigit() else None
    maximo = int(maxpop) if maxpop.isdigit() else None
    if minimo is not None or maximo is not None:
        lista = f.filtrar_por_rango(lista, "poblacion", minimo, maximo)

    try:
        lista = f.ordenar(lista, sort, asc == "1")
    except Exception:
        pass

    stats = f.estadisticas(lista)

    return render_template("index.html",
                            paises=lista,
                            stats=stats,
                            nombre=nombre,
                            continente=continente,
                            minpop=minpop,
                            maxpop=maxpop,
                            sort=sort,
                            asc=asc)

@app.route("/refresh")
def refresh():
    cargar_datos()
    return redirect(url_for("index"))

if __name__ == "__main__":
    cargar_datos()
    app.run(host="0.0.0.0", port=5000, debug=True)