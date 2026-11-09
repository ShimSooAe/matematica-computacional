# Matemática Computacional — Agente Viajero

Aplicación de escritorio en Python para explorar el **Problema del Agente Viajero (TSP)** en grafos ponderados no dirigidos. Permite generar grafos manualmente o al azar, revisar matrices y conectividad, y ejecutar una búsqueda por fuerza bruta de ciclos hamiltonianos.

## Funcionalidades

- Generación manual o aleatoria de grafos de 5 a 10 nodos.
- Visualización de la matriz de costos, matriz de adyacencia y grafo ponderado.
- Verificación de grados, componentes conexas y existencia de ciclos hamiltonianos.
- Ejecución paso a paso de la búsqueda por fuerza bruta y comparación de costos.
- Exportación de los ciclos encontrados a CSV.

## Requisitos

- Python 3.9 o posterior.
- Tkinter, incluido normalmente con Python (en algunas distribuciones de Linux se instala por separado).
- Matplotlib, instalado mediante `requirements.txt`.

## Instalación y ejecución

Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

Activa el entorno virtual:

- Windows: `.venv\\Scripts\\activate`
- macOS/Linux: `source .venv/bin/activate`

Instala las dependencias y ejecuta la aplicación:

```bash
python -m pip install -r requirements.txt
python Codigo_Grupo8.py
```

En Linux, si Tkinter no está disponible, instálalo desde el gestor de paquetes de tu distribución (por ejemplo, `python3-tk` en Debian/Ubuntu).

## Estructura

```text
matematica-computacional/
├── Codigo_Grupo8.py   # Aplicación principal
├── requirements.txt   # Dependencias de Python
├── .gitignore
└── README.md
```

## Nota sobre el algoritmo

La búsqueda por fuerza bruta enumera rutas que comienzan y terminan en el nodo A. Por su complejidad factorial, el tiempo de ejecución crece rápidamente al aumentar la cantidad de nodos; el rango de la aplicación está limitado a 5–10 nodos con fines didácticos.

## Contexto académico

Proyecto de Matemática Computacional. Los pesos de las aristas pueden representar distancias, costos o tiempos.
