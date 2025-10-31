# -*- coding: utf-8 -*-
"""
Funciones principales del programa
"""


def _norm(s):
    if s is None: return ""
    return str(s).strip().lower()

def _to_int(value, campo, fila):
    try:
        return int(value)
    except Exception:
        raise ValueError("Fila {}: el campo '{}' debe ser entero (valor={!r})".format(fila, campo, value))

# CSV 

def cargar_paises_desde_csv(ruta):
    import csv
    req = ("nombre", "poblacion", "superficie", "continente")
    datos, errores = [], []
    with open(ruta, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.strip().lower() for h in (reader.fieldnames or [])]
        for c in req:
            if c not in headers:
                raise ValueError("Falta la columna requerida '{}' en el CSV.".format(c))
        for i, row in enumerate(reader, start=2):
            try:
                nombre = str(row.get("nombre", "")).strip()
                cont   = str(row.get("continente", "")).strip()
                if not nombre or not cont:
                    raise ValueError("campos 'nombre' y 'continente' no pueden estar vacíos.")
                pob = _to_int(row.get("poblacion", ""),  "poblacion",  i)
                sup = _to_int(row.get("superficie", ""), "superficie", i)
                if pob < 0 or sup <= 0:
                    raise ValueError("'poblacion' >= 0 y 'superficie' > 0")
                datos.append({"nombre": nombre, "poblacion": pob, "superficie": sup, "continente": cont})
            except Exception as e:
                errores.append("Fila {}: {}".format(i, e))
    if errores:
        print("Se omitieron filas inválidas:")
        for msg in errores: print(" -", msg)
    return datos

# API 

def _mapear_item_restcountries(item, idx):
    # nombre
    nombre, name_obj = None, item.get("name")
    if isinstance(name_obj, dict):
        nombre = name_obj.get("common") or name_obj.get("official")
        if not nombre and isinstance(name_obj.get("nativeName"), dict):
            for _, v in name_obj["nativeName"].items():
                if isinstance(v, dict):
                    nombre = v.get("common") or v.get("official")
                    if nombre: break
    if not nombre:
        raise ValueError("Ítem {}: falta 'name' con información suficiente".format(idx))

    # poblacion/superficie
    poblacion_val = item.get("population")
    area_val      = item.get("area")

    # continente
    continente_val = item.get("region")
    if not continente_val:
        continents = item.get("continents")
        if isinstance(continents, list) and continents:
            continente_val = continents[0]
    if not continente_val:
        raise ValueError("Ítem {}: falta 'region'/'continents'".format(idx))

    try:
        pob = int(poblacion_val) if poblacion_val is not None else 0
        sup = int(round(float(area_val))) if area_val is not None else 0
    except Exception:
        raise ValueError("Ítem {}: 'population'/'area' deben ser numéricos".format(idx))
    if pob < 0 or sup <= 0:
        raise ValueError("Ítem {}: 'population' >= 0 y 'area' > 0 requeridos".format(idx))

    return {"nombre": str(nombre).strip(), "poblacion": pob, "superficie": sup, "continente": str(continente_val).strip()}

def cargar_desde_api(api_url, timeout_segundos=20):
    try:
        import requests
        from requests.exceptions import SSLError, Timeout, ConnectionError
    except Exception:
        raise RuntimeError("Requiere 'requests'. Instale con: pip install requests")
    try:
        r = requests.get(api_url, timeout=timeout_segundos)
        r.raise_for_status()
    except SSLError as e:
        raise RuntimeError("Falla SSL al acceder a la API (certificados). Detalle: {}".format(e))
    except Timeout as e:
        raise RuntimeError("Timeout al consultar la API (red/proxy). Detalle: {}".format(e))
    except ConnectionError as e:
        raise RuntimeError("No hay conexión con la API (proxy/firewall/red). Detalle: {}".format(e))
    except Exception as e:
        raise RuntimeError("Error HTTP al consultar la API. Detalle: {}".format(e))

    try:
        data = r.json()
    except Exception:
        raise ValueError("La respuesta de la API no es JSON válido")
    if not isinstance(data, list):
        raise ValueError("Se esperaba una lista JSON")

    out, errs = [], []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            errs.append("Ítem {} no es dict".format(i)); continue
        try:
            out.append(_mapear_item_restcountries(item, i))
        except Exception as e:
            errs.append(str(e))
    if errs:
        print("Algunos elementos de la API fueron descartados:")
        for msg in errs[:10]: print(" -", msg)
        if len(errs) > 10: print("   ... (más errores)")
    return out

# Combinar + Consultas 

def combinar_csv_y_api(paises_csv, paises_api, preferir_csv=True):
    idx = {}
    for p in paises_csv:
        idx[_norm(p["nombre"])] = p
    for p in paises_api:
        k = _norm(p.get("nombre", ""))
        if not k: continue
        if k in idx:
            if not preferir_csv:
                idx[k] = p
        else:
            idx[k] = p
    return list(idx.values())

def buscar_por_nombre(paises, texto, exacto=False):
    t = _norm(texto)
    if t == "": return []
    if exacto:
        return [p for p in paises if _norm(p["nombre"]) == t]
    return [p for p in paises if t in _norm(p["nombre"])]

def filtrar_por_continente(paises, continente):
    c = _norm(continente)
    return [p for p in paises if _norm(p["continente"]) == c]

def filtrar_por_rango(paises, campo, minimo, maximo):
    if campo not in ("poblacion", "superficie"):
        raise ValueError("Campo inválido. Use 'poblacion' o 'superficie'.")
    out = []
    for p in paises:
        v = int(p[campo])
        if (minimo is None or v >= minimo) and (maximo is None or v <= maximo):
            out.append(p)
    return out

def ordenar(paises, clave, asc=True):
    k = str(clave).lower()
    if k not in ("nombre", "poblacion", "superficie"):
        raise ValueError("Clave inválida. Elija: nombre / poblacion / superficie.")
    return sorted(paises, key=(lambda p: _norm(p["nombre"]) if k == "nombre" else int(p[k])), reverse=not asc)

def estadisticas(paises):
    if not paises: return None
    mayor = max(paises, key=lambda p: p["poblacion"])
    menor = min(paises, key=lambda p: p["poblacion"])
    prom_pob = sum(p["poblacion"] for p in paises) / len(paises)
    prom_sup = sum(p["superficie"] for p in paises) / len(paises)
    conteo = {}
    for p in paises:
        cont = str(p["continente"])
        conteo[cont] = conteo.get(cont, 0) + 1
    return {"mayor_poblacion": mayor, "menor_poblacion": menor, "promedio_poblacion": prom_pob, "promedio_superficie": prom_sup, "conteo_por_continente": conteo}

def imprimir_listado(paises):
    if not paises: print("No hay países para mostrar."); return
    print("\nListado de países ({}):".format(len(paises)))
    print("-" * 72)
    for p in paises:
        print("{:22} | Pob: {:>12} | Sup(km²): {:>10} | {}".format(p["nombre"], p["poblacion"], p["superficie"], p["continente"]))
    print("-" * 72)

def imprimir_estadisticas(stats):
    if not stats: print("No hay datos para estadísticas."); return
    print("\n— Estadísticas —")
    print("• Mayor población: {} ({})".format(stats["mayor_poblacion"]["nombre"], stats["mayor_poblacion"]["poblacion"]))
    print("• Menor población: {} ({})".format(stats["menor_poblacion"]["nombre"], stats["menor_poblacion"]["poblacion"]))
    print("• Promedio de población: {:.2f}".format(stats["promedio_poblacion"]))
    print("• Promedio de superficie: {:.2f}".format(stats["promedio_superficie"]))
    print("• Cantidad por continente:")
    for cont, n in stats["conteo_por_continente"].items():
        print("   - {}: {}".format(cont, n))

# Exportar 

def exportar_a_csv(paises, ruta_salida):
    import csv
    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["nombre", "poblacion", "superficie", "continente"])
        writer.writeheader()
        for p in paises:
            writer.writerow({
                "nombre": p["nombre"],
                "poblacion": int(p["poblacion"]),
                "superficie": int(p["superficie"]),
                "continente": p["continente"]
            })
