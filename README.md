# Problema del Agente Viajero por fuerza bruta

Aplicación de escritorio en Python que resuelve el Problema del Agente Viajero (TSP) en grafos no dirigidos y ponderados de 5 a 10 nodos. El usuario construye el grafo, comprueba que admita ciclos hamiltonianos y recorre paso a paso la generación y evaluación de cada ruta hasta obtener el ciclo de menor costo, que se resalta sobre el grafo.

Proyecto del Grupo 8 del curso 1AMA0726 Matemática Computacional, Universidad Peruana de Ciencias Aplicadas (UPC), 2026-20. Tema 4: Problema del Agente Viajero.

## Qué hace

1. **Construcción del grafo.** El usuario indica la cantidad de nodos (5 a 10) y elige entre generación manual, escribiendo el peso de cada arista, o aleatoria, con el porcentaje de aristas presentes que prefiera.
2. **Matrices.** Muestra la matriz de costos y la matriz de adyacencia del grafo.
3. **Verificación.** Calcula los grados de los vértices, la matriz de caminos y las componentes conexas, y revisa si existe al menos un ciclo hamiltoniano. Si no existe, indica qué aristas faltan para que exista.
4. **Búsqueda paso a paso.** Genera las rutas que parten del nodo A y evalúa su costo de una en una, de diez en diez o hasta el final, con un panel de progreso.
5. **Resultados.** Informa cuántos ciclos hamiltonianos hay, el costo mínimo y el ciclo óptimo, que se dibuja en rojo sobre el grafo. Al elegir un ciclo de la tabla, el grafo lo resalta.
6. **Exportación.** Guarda todos los ciclos encontrados, con su costo, en un archivo CSV.

## Requisitos

- Python 3.9 o posterior.
- Tkinter, que viene con la instalación estándar de Python en Windows y macOS. En Debian y Ubuntu se instala con `sudo apt install python3-tk`.
- Matplotlib, que se instala con `requirements.txt`.

## Instalación y ejecución

Desde la carpeta del proyecto, crea y activa un entorno virtual:

```bash
python -m venv .venv
```

- Windows: `.venv\Scripts\activate`
- macOS y Linux: `source .venv/bin/activate`

Instala las dependencias y abre la aplicación:

```bash
python -m pip install -r requirements.txt
python Codigo_Grupo8.py
```

El programa está pensado para Windows: usa las fuentes Segoe UI y Consolas y activa la alta resolución propia de ese sistema. En macOS y Linux se ejecuta, pero Tkinter reemplaza esas fuentes y la interfaz puede verse distinta.

## Cómo usarlo

1. En el panel izquierdo, escribe la cantidad de nodos o ajústala con los botones `−` y `+`.
2. Pulsa **Generación manual** para escribir los pesos de las aristas (un campo vacío significa que esa arista no existe) o **Generación aleatoria** para que el programa elija las aristas según el porcentaje indicado.
3. Pulsa **Verificar ciclos hamiltonianos** y revisa la pestaña *Verificación*. La búsqueda solo se habilita si el grafo admite al menos un ciclo.
4. Avanza con **Siguiente paso**, **Avanzar 10 pasos** o **Ejecutar hasta el final**. La pestaña *Paso a paso* registra cada ruta evaluada, y **Reiniciar ejecución** vuelve al inicio con el mismo grafo.
5. Consulta la pestaña *Resultados* para ver los ciclos ordenados por costo y usa **Exportar todos los ciclos (CSV)** si quieres guardarlos. El archivo usa el separador `;` y la codificación UTF-8, de modo que Excel lo abre directamente.

## Sobre el algoritmo

La búsqueda por fuerza bruta fija el nodo A como inicio y fin, y genera todas las rutas que pasan una vez por cada uno de los demás nodos. Como recorrer un ciclo en sentido contrario tiene el mismo costo, el programa conserva solo una de las dos direcciones, y el número de rutas candidatas es (n − 1)!/2. Para cada ruta suma el costo de sus aristas y la descarta si usa una arista inexistente. Entre las rutas válidas, que son los ciclos hamiltonianos, conserva la de menor costo.

| Nodos (n) | Rutas candidatas |
| :-: | -: |
| 5 | 12 |
| 6 | 60 |
| 7 | 360 |
| 8 | 2 520 |
| 9 | 20 160 |
| 10 | 181 440 |

El número de rutas se multiplica por n al agregar un nodo, y por eso la aplicación se limita a 10 nodos. Con 10 nodos la búsqueda completa tarda menos de un segundo. Si un grafo denso tiene más de 2 000 ciclos, la tabla de resultados muestra los 2 000 de menor costo y el CSV contiene la lista completa.

## Estructura del repositorio

```text
matematica-computacional/
├── Codigo_Grupo8.py   # Aplicación completa (lógica del problema e interfaz)
├── requirements.txt   # Dependencias de Python
├── .gitignore
└── README.md
```

El archivo `Codigo_Grupo8.py` separa la lógica del problema (matrices, verificación, generación de rutas y la clase `MotorFuerzaBruta`) de la interfaz, que está en la clase `App`.
