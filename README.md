# integrador_Varela_Fernandez — CSV + API + Flask

## Requisitos
```bash
pip install flask requests
```

## Modo consola
```bash
python main.py
```
Menú con búsqueda, filtros, orden, estadísticas y exportación a CSV.

## Modo web con estilos (Flask)
```bash
python app.py
```
Abrí http://127.0.0.1:5000

## Endpoint usado
```
https://restcountries.com/v3.1/all?fields=name,population,area,region,continents
```

## Link Imagen Docker
```
- https://hub.docker.com/repository/docker/pablodocker0611/paises-app/general
```

## Notas
- `funciones.py` concentra toda la lógica (CSV, API, combinar, filtros, orden, estadísticas, exportar).
- `main.py` usa esa lógica por consola.
- `app.py` la reutiliza para la interfaz web (templates + Bootstrap).
