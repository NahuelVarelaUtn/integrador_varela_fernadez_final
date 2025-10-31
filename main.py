#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#el primer comentario es para que funcione en sistemas Unix/Linux/Mac si se da permiso de ejecución al archivo
#el segundo comentario es para indicar la codificación UTF-8

"""
Bienvenido/a al programa de gestión de datos de países de Nahuel y Pablo
En éste programa se pueden buscar, filtrar, ordenar y exportar datos de países
combinando datos de un archivo CSV local y una API remota.

Para que la ejecucion del programa funcione, instalar requests:
1) pip install requests

Luego ejecutar el programa con:
python main.py
"""

import sys
import os
import funciones as f

CSV_FILE_PATH = "paises_lite.csv"
API_URL       = "https://restcountries.com/v3.1/all?fields=name,population,area,region,continents"
PREFERIR_CSV  = True

def mostrar_menu():
    print("""
Bienvenido/a al gestor de países
1) Buscar país por nombre (exacto o parcial)
2) Filtrar por continente
3) Filtrar por rango de población
4) Filtrar por rango de superficie
5) Ordenar países (nombre/poblacion/superficie)
6) Mostrar estadísticas básicas
7) Mostrar todos los países
8) Exportar último listado mostrado a CSV
9) Refrescar desde la API (re-descargar y recombinar)
0) Salir
""")

def pedir_entero_opcional(mensaje):
    txt = input(mensaje).strip()
    if txt == "":
        return None
    try:
        return int(txt)
    except Exception:
        print(" Ingrese un número entero o Enter para dejar vacío.")
        return pedir_entero_opcional(mensaje)

def pedir_si_no(msg="¿Confirmás? (s/n): "):
    r = input(msg).strip().lower()
    if r in ("s", "si", "sí"): return True
    if r in ("n", "no"): return False
    print("Por favor Responda 's' o 'n'"); return pedir_si_no(msg)

def cargar_inicial():
    paises_csv = []
    if os.path.exists(CSV_FILE_PATH):
        try:
            paises_csv = f.cargar_paises_desde_csv(CSV_FILE_PATH)
            print(f" CSV cargado: {len(paises_csv)} registros.")
        except Exception as e:
            print(" No se pudo cargar el CSV:", e)
    else:
        print("• No se encontró CSV local, se continuará con la API.")

    try:
        paises_api = f.cargar_desde_api(API_URL, timeout_segundos=20)
        print(f" API cargada: {len(paises_api)} registros.")
    except Exception as e:
        paises_api = []
        print(" No se pudo cargar la API. Se usará solo CSV (si lo hay).")
        print(" Detalle:", e)

    paises = f.combinar_csv_y_api(paises_csv, paises_api, preferir_csv=PREFERIR_CSV)
    return paises

def main():
    paises = cargar_inicial()
    if not paises:
        print(" No hay países cargados (ni CSV ni API)."); sys.exit(1)
    print(f"→ Total combinados: {len(paises)} países.")

    ultimo = paises[:]

    while True:
        mostrar_menu()
        op = input("Elegí una opción: ").strip()

        if op == "0":
            print("¡Hasta luego!"); break

        elif op == "1":
            texto = input("Nombre (todo o parte): ").strip()
            exacto = pedir_si_no("¿Coincidencia exacta? (s/n): ")
            res = f.buscar_por_nombre(paises, texto, exacto)
            f.imprimir_listado(res); ultimo = res

        elif op == "2":
            cont = input("Continente (América/Europa/Asia/África/Oceanía): ").strip()
            res = f.filtrar_por_continente(paises, cont)
            f.imprimir_listado(res); ultimo = res

        elif op == "3":
            mn = pedir_entero_opcional("Población mínima (Enter si no): ")
            mx = pedir_entero_opcional("Población máxima (Enter si no): ")
            res = f.filtrar_por_rango(paises, "poblacion", mn, mx)
            f.imprimir_listado(res); ultimo = res

        elif op == "4":
            mn = pedir_entero_opcional("Superficie mínima (km²) (Enter si no): ")
            mx = pedir_entero_opcional("Superficie máxima (km²) (Enter si no): ")
            res = f.filtrar_por_rango(paises, "superficie", mn, mx)
            f.imprimir_listado(res); ultimo = res

        elif op == "5":
            clave = input("Clave (nombre/poblacion/superficie): ").strip().lower()
            asc = pedir_si_no("¿Ascendente? (s/n): ")
            try:
                res = f.ordenar(paises, clave, asc)
                f.imprimir_listado(res); ultimo = res
            except Exception as e:
                print("error", e)

        elif op == "6":
            stats = f.estadisticas(paises); f.imprimir_estadisticas(stats)

        elif op == "7":
            f.imprimir_listado(paises); ultimo = paises[:]

        elif op == "8":
            if not ultimo:
                print(" No hay último listado para exportar."); continue
            destino = input("Nombre de archivo CSV destino (ej.: salida.csv): ").strip() or "salida.csv"
            try:
                f.exportar_a_csv(ultimo, destino)
                print(f" Exportado a '{destino}' ({len(ultimo)} filas).")
            except Exception as e:
                print(" No se pudo exportar:", e)

        elif op == "9":
            print(" Refrescando desde la API.")
            try:
                paises_api = f.cargar_desde_api(API_URL, timeout_segundos=20)
                paises = f.combinar_csv_y_api(paises, paises_api, preferir_csv=PREFERIR_CSV)
                print(f" API refrescada. Total ahora: {len(paises)} países.")
            except Exception as e:
                print(" No se pudo refrescar desde la API:", e)

        else:
            print(" Opción inválida elige otra opcion (0-9).")

if __name__ == "__main__":
    main()
