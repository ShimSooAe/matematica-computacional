import csv
import itertools
import math
import random
import tkinter as tk
from collections import namedtuple
from tkinter import filedialog, messagebox, ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

INF = float("inf")
N_MIN, N_MAX = 5, 10
LIMITE_TABLA = 2000

FUENTE = "Segoe UI"
MONO = "Consolas"

FONDO = "#F1F4FA"
BLANCO = "#FFFFFF"
LATERAL = "#1B2540"
LATERAL_2 = "#2A3760"
LATERAL_TXT = "#9FB0D3"
TEXTO = "#1E293B"
TENUE = "#64748B"
BORDE = "#DDE3EE"
SUPERFICIE = "#EEF2FA"
PRIMARIO = "#3B6CF6"
OK, OK_FONDO = "#1F9D67", "#E1F5EB"
ERROR, ERROR_FONDO = "#D93A42", "#FDE8E9"
AVISO, AVISO_FONDO = "#E8811A", "#FFF1DF"

COLOR_BASE = "#B4BECC"
COLOR_ACTUAL = PRIMARIO
COLOR_FALTA = AVISO
COLOR_MEJOR = ERROR


def nombres_nodos(n):
    return [chr(65 + i) for i in range(n)]


def formato(x):
    if x == INF:
        return "∞"
    if float(x).is_integer():
        return str(int(x))
    return f"{x:.2f}"


def construir_matriz_costos(n, pesos):
    C = [[INF] * n for _ in range(n)]
    for i in range(n):
        C[i][i] = 0
    for (i, j), w in pesos.items():
        C[i][j] = w
        C[j][i] = w
    return C


def matriz_adyacencia(C):
    n = len(C)
    return [[1 if i != j and C[i][j] < INF else 0 for j in range(n)] for i in range(n)]


def grados(A):
    return [sum(fila) for fila in A]


def producto_booleano(X, Y):
    n = len(X)
    return [[1 if any(X[i][k] and Y[k][j] for k in range(n)) else 0
             for j in range(n)] for i in range(n)]


def matriz_de_caminos(A):
    n = len(A)
    M = [[1 if (i == j or A[i][j]) else 0 for j in range(n)] for i in range(n)]
    P = M
    for _ in range(n):
        Q = producto_booleano(P, M)
        if Q == P:
            break
        P = Q
    return P


def componentes_conexas(P):
    n = len(P)
    vistos, componentes = set(), []
    for i in range(n):
        if i not in vistos:
            comp = [j for j in range(n) if P[i][j]]
            componentes.append(comp)
            vistos.update(comp)
    return componentes


def candidatas(n):
    for perm in itertools.permutations(range(1, n)):
        if perm[0] < perm[-1]:
            yield perm


def buscar_ruta_con_menos_faltantes(C):
    n = len(C)
    mejor_ruta, mejor_faltantes = None, None
    for perm in candidatas(n):
        ruta = (0,) + perm + (0,)
        faltantes = []
        for a, b in zip(ruta, ruta[1:]):
            if C[a][b] == INF:
                faltantes.append((min(a, b), max(a, b)))
                if mejor_faltantes is not None and len(faltantes) >= len(mejor_faltantes):
                    break
        else:
            if mejor_faltantes is None or len(faltantes) < len(mejor_faltantes):
                mejor_ruta, mejor_faltantes = ruta, faltantes
                if not faltantes:
                    break
    return mejor_ruta, mejor_faltantes


def verificar(C):
    A = matriz_adyacencia(C)
    P = matriz_de_caminos(A)
    ruta, faltantes = buscar_ruta_con_menos_faltantes(C)
    return {
        "A": A,
        "grados": grados(A),
        "P": P,
        "componentes": componentes_conexas(P),
        "ruta": ruta,
        "faltantes": faltantes,
        "hamiltoniano": len(faltantes) == 0,
    }


Paso = namedtuple("Paso", "k ruta costo faltante mejora empate")


class MotorFuerzaBruta:
    def __init__(self, C):
        self.C = C
        self.n = len(C)
        self.total = sum(1 for _ in candidatas(self.n))
        self._rutas = candidatas(self.n)
        self.k = 0
        self.ciclos = []
        self.mejor_costo = INF
        self.optimos = []
        self.terminado = False

    def siguiente(self):
        try:
            perm = next(self._rutas)
        except StopIteration:
            self.terminado = True
            return None
        self.k += 1
        ruta = (0,) + perm + (0,)
        costo, faltante = 0, None
        for a, b in zip(ruta, ruta[1:]):
            w = self.C[a][b]
            if w == INF:
                faltante = (a, b)
                break
            costo += w
        mejora = empate = False
        if faltante is None:
            self.ciclos.append((ruta, costo))
            if costo < self.mejor_costo:
                self.mejor_costo, self.optimos = costo, [ruta]
                mejora = True
            elif costo == self.mejor_costo:
                self.optimos.append(ruta)
                empate = True
        if self.k == self.total:
            self.terminado = True
        return Paso(self.k, ruta, costo, faltante, mejora, empate)

    def avanzar(self, m, guardar=200):
        pasos = []
        for _ in range(m):
            p = self.siguiente()
            if p is None:
                break
            if m <= guardar:
                pasos.append(p)
        return pasos


def activar_dpi_alto():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def mezclar(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def aplicar_estilos(raiz, esc):
    est = ttk.Style(raiz)
    est.theme_use("clam")

    est.configure("TNotebook", background=FONDO, borderwidth=0, tabmargins=(0, 0, 0, 0),
                  bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE)
    est.configure("TNotebook.Tab", padding=(16, 9), font=(FUENTE, 10, "bold"),
                  background="#E2E8F3", foreground=TENUE, borderwidth=0,
                  bordercolor="#E2E8F3", lightcolor="#E2E8F3", darkcolor="#E2E8F3",
                  focuscolor="#E2E8F3")
    est.map("TNotebook.Tab",
            background=[("selected", BLANCO), ("active", SUPERFICIE)],
            foreground=[("selected", PRIMARIO)],
            bordercolor=[("selected", BORDE)], lightcolor=[("selected", BLANCO)],
            darkcolor=[("selected", BLANCO)], focuscolor=[("selected", BLANCO)],
            expand=[("selected", (0, 0, 0, 0))])

    est.configure("Treeview", background=BLANCO, fieldbackground=BLANCO, foreground=TEXTO,
                  font=(FUENTE, 10), rowheight=int(28 * esc), borderwidth=0)
    est.configure("Treeview.Heading", background=SUPERFICIE, foreground=TEXTO,
                  font=(FUENTE, 10, "bold"), relief="flat", padding=(6, 7), borderwidth=0)
    est.map("Treeview.Heading", background=[("active", BORDE)])
    est.map("Treeview", background=[("selected", PRIMARIO)], foreground=[("selected", BLANCO)])

    est.configure("Vertical.TScrollbar", background="#C5CEDD", troughcolor=FONDO,
                  bordercolor=FONDO, lightcolor="#C5CEDD", darkcolor="#C5CEDD",
                  arrowcolor=TENUE, relief="flat", gripcount=0)
    est.configure("Horizontal.TScrollbar", background="#C5CEDD", troughcolor=FONDO,
                  bordercolor=FONDO, lightcolor="#C5CEDD", darkcolor="#C5CEDD",
                  arrowcolor=TENUE, relief="flat", gripcount=0)
    est.map("Vertical.TScrollbar", background=[("active", "#9FADC4")])
    est.map("Horizontal.TScrollbar", background=[("active", "#9FADC4")])

    est.configure("Lateral.Horizontal.TProgressbar", troughcolor=LATERAL_2, background=PRIMARIO,
                  bordercolor=LATERAL_2, lightcolor=PRIMARIO, darkcolor=PRIMARIO, thickness=8)


def configurar_etiquetas(texto):
    texto.tag_configure("h1", font=(FUENTE, 14, "bold"), foreground=PRIMARIO, spacing1=2, spacing3=4)
    texto.tag_configure("h2", font=(FUENTE, 11, "bold"), foreground=TEXTO, spacing1=14, spacing3=4)
    texto.tag_configure("tenue", foreground=TENUE)
    texto.tag_configure("mal", foreground=ERROR, font=(MONO, 10, "bold"))
    texto.tag_configure("chip", background=SUPERFICIE, foreground=TEXTO, font=(MONO, 10, "bold"))
    texto.tag_configure("chip_mal", background=ERROR_FONDO, foreground=ERROR, font=(MONO, 10, "bold"))
    texto.tag_configure("badge_ok", background=OK_FONDO, foreground=OK, font=(FUENTE, 10, "bold"))
    texto.tag_configure("badge_mal", background=ERROR_FONDO, foreground=ERROR, font=(FUENTE, 10, "bold"))

    texto.tag_configure("cab", foreground=PRIMARIO, font=(MONO, 10, "bold"))
    texto.tag_configure("cab_sub", foreground=PRIMARIO, font=(MONO, 10, "bold"), underline=True)
    texto.tag_configure("val", foreground=TEXTO)
    texto.tag_configure("inf", foreground="#B6BFCC")
    texto.tag_configure("diag", foreground="#A3AEBF")
    texto.tag_configure("uno", foreground=PRIMARIO, font=(MONO, 10, "bold"))
    texto.tag_configure("cero", foreground="#A3AEBF")

    texto.tag_configure("linea", spacing3=1)
    texto.tag_configure("salto", spacing3=8)
    texto.tag_configure("paso", foreground=TENUE, font=(MONO, 10, "bold"))
    texto.tag_configure("ruta", foreground=TEXTO)
    texto.tag_configure("desc", foreground=ERROR)
    texto.tag_configure("ciclo", foreground=OK, font=(MONO, 10, "bold"))
    texto.tag_configure("mejor", background=OK_FONDO, foreground=OK, font=(MONO, 10, "bold"))
    texto.tag_configure("empate", background=AVISO_FONDO, foreground=AVISO, font=(MONO, 10, "bold"))


class Deslizador(tk.Canvas):
    def __init__(self, padre, desde, hasta, valor, paso=10, comando=None, escala=1.0):
        super().__init__(padre, height=int(24 * escala), bg=LATERAL, highlightthickness=0,
                         cursor="hand2")
        self.desde, self.hasta, self.paso, self.comando = desde, hasta, paso, comando
        self.valor = valor
        self.escala = escala
        self.margen = int(10 * escala)
        self.bind("<Configure>", lambda _e: self._dibujar())
        self.bind("<Button-1>", self._mover)
        self.bind("<B1-Motion>", self._mover)

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = min(self.hasta, max(self.desde, valor))
        self._dibujar()
        if self.comando:
            self.comando(self.valor)

    def _mover(self, evento):
        ancho = max(1, self.winfo_width() - 2 * self.margen)
        fraccion = min(1, max(0, (evento.x - self.margen) / ancho))
        bruto = self.desde + fraccion * (self.hasta - self.desde)
        nuevo = self.desde + round((bruto - self.desde) / self.paso) * self.paso
        if min(self.hasta, max(self.desde, nuevo)) != self.valor:
            self.set(nuevo)

    def _dibujar(self):
        self.delete("all")
        ancho, alto = self.winfo_width(), self.winfo_height()
        y, e = alto / 2, self.escala
        x0, x1 = self.margen, ancho - self.margen
        x = x0 + (self.valor - self.desde) / (self.hasta - self.desde) * (x1 - x0)
        self.create_line(x0, y, x1, y, fill=LATERAL_2, width=6 * e, capstyle="round")
        self.create_line(x0, y, x, y, fill=PRIMARIO, width=6 * e, capstyle="round")
        r = 8 * e
        self.create_oval(x - r, y - r, x + r, y + r, fill="white", outline=PRIMARIO, width=3 * e)


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        self.esc = raiz.winfo_fpixels("1i") / 96
        raiz.title("Problema del Agente Viajero - Fuerza Bruta")
        raiz.configure(bg=FONDO)
        self._ajustar_ventana()
        aplicar_estilos(raiz, self.esc)
        matplotlib.rcParams["font.family"] = [FUENTE, "DejaVu Sans"]

        self.n = 0
        self.nombres = []
        self.pesos = {}
        self.C = []
        self.verif = None
        self.motor = None
        self.ruta_actual = None
        self.faltante_actual = None
        self.ruta_resaltada = None
        self.info_actual = ""

        self._crear_panel_control()
        self._crear_paneles_texto()
        self._crear_grafico()
        self._escribir(self.txt_matrices, [("Genere un grafo para ver sus matrices.", "tenue")])
        self._escribir(self.txt_verif, [("Genere un grafo y pulse «Verificar ciclos hamiltonianos».",
                                         "tenue")])
        self._escribir(self.txt_pasos, [("Aquí se irá mostrando cada ruta evaluada.", "tenue")])
        self.dibujar()

    def _ajustar_ventana(self):
        raiz, e = self.raiz, self.esc
        sw, sh = raiz.winfo_screenwidth(), raiz.winfo_screenheight()
        w, h = min(int(1400 * e), int(sw * 0.96)), min(int(800 * e), int(sh * 0.92))
        raiz.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - 20)}")
        raiz.minsize(min(int(1150 * e), w), min(int(680 * e), h))

        compacto = h / e < 780
        self.compacto = compacto
        self.pad_boton = 3 if compacto else 6
        self.esp_seccion = 6 if compacto else 11

    def _boton(self, padre, texto, color, comando, fg="white", size=10, pady=None):
        pady = self.pad_boton if pady is None else pady
        hover = mezclar(color, "#FFFFFF", 0.18) if fg == "white" else mezclar(color, "#000000", 0.07)
        b = tk.Button(padre, text=texto, command=comando, bg=color, fg=fg, activebackground=hover,
                      activeforeground=fg, relief="flat", bd=0, font=(FUENTE, size, "bold"),
                      cursor="hand2", padx=12, pady=pady, highlightthickness=0)
        b.bind("<Enter>", lambda _e: b.config(bg=hover))
        b.bind("<Leave>", lambda _e: b.config(bg=color))
        return b

    def _logo(self, padre):
        t = int(44 * self.esc)
        c = tk.Canvas(padre, width=t, height=t, bg=LATERAL, highlightthickness=0)
        c.create_oval(1, 1, t - 1, t - 1, fill=PRIMARIO, outline="")
        r, cx = t * 0.27, t / 2
        pts = [(cx + r * math.cos(math.pi / 2 - 2 * math.pi * i / 5),
                cx - r * math.sin(math.pi / 2 - 2 * math.pi * i / 5)) for i in range(5)]
        for i in range(5):
            a, b = pts[i], pts[(i + 1) % 5]
            c.create_line(a[0], a[1], b[0], b[1], fill="#CFDBFF", width=2)
        rn = max(2, t * 0.07)
        for x, y in pts:
            c.create_oval(x - rn, y - rn, x + rn, y + rn, fill="white", outline="")
        return c

    def _seccion(self, padre, numero, titulo):
        fila = tk.Frame(padre, bg=LATERAL)
        fila.pack(fill="x", pady=(self.esp_seccion, 6))
        t = int(22 * self.esc)
        c = tk.Canvas(fila, width=t, height=t, bg=LATERAL, highlightthickness=0)
        c.create_oval(1, 1, t - 1, t - 1, fill=PRIMARIO, outline="")
        c.create_text(t / 2, t / 2, text=str(numero), fill="white", font=(FUENTE, 9, "bold"))
        c.pack(side="left")
        tk.Label(fila, text=titulo, bg=LATERAL, fg="white", font=(FUENTE, 11, "bold")
                 ).pack(side="left", padx=9)

    def _crear_panel_control(self):
        e = self.esc
        panel = tk.Frame(self.raiz, bg=LATERAL, width=int(292 * e))
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)
        cuerpo = tk.Frame(panel, bg=LATERAL)
        cuerpo.pack(fill="both", expand=True, padx=16, pady=(9, 9) if self.compacto else (16, 14))

        inferior = tk.Frame(cuerpo, bg=LATERAL)
        inferior.pack(side="bottom", fill="x")
        tk.Label(inferior, text="PROGRESO", font=(FUENTE, 8, "bold"), fg=LATERAL_TXT,
                 bg=LATERAL).pack(anchor="w")
        self.barra = ttk.Progressbar(inferior, style="Lateral.Horizontal.TProgressbar",
                                     maximum=100, mode="determinate")
        self.barra.pack(fill="x", pady=(3, 4) if self.compacto else (5, 6))
        self.lbl_progreso = tk.Label(inferior, text="", font=(FUENTE, 9), fg="#D5DEF5", bg=LATERAL,
                                     justify="left", anchor="nw", height=2 if self.compacto else 3)
        self.lbl_progreso.pack(fill="x")
        self.tarjeta_estado = tk.Frame(inferior, bg=LATERAL_2)
        self.tarjeta_estado.pack(fill="x", pady=(6, 0) if self.compacto else (10, 0))
        self.franja_estado = tk.Frame(self.tarjeta_estado, bg=LATERAL_TXT, width=5)
        self.franja_estado.pack(side="left", fill="y")
        self.lbl_estado = tk.Label(self.tarjeta_estado, text="", font=(FUENTE, 10), bg=LATERAL_2,
                                   wraplength=int(228 * e), justify="left", anchor="nw",
                                   padx=12, pady=8, height=2)
        self.lbl_estado.pack(side="left", fill="x", expand=True)
        self._estado("Ingrese la cantidad de nodos y genere un grafo.", "info")

        cab = tk.Frame(cuerpo, bg=LATERAL)
        cab.pack(fill="x")
        self._logo(cab).pack(side="left")
        tit = tk.Frame(cab, bg=LATERAL)
        tit.pack(side="left", padx=12)
        tk.Label(tit, text="Agente Viajero", font=(FUENTE, 17, "bold"), bg=LATERAL,
                 fg="white").pack(anchor="w")
        tk.Label(tit, text="Algoritmo de fuerza bruta", font=(FUENTE, 9), bg=LATERAL,
                 fg=LATERAL_TXT).pack(anchor="w")
        tk.Frame(cuerpo, bg=LATERAL_2, height=1).pack(fill="x", pady=(7, 7) if self.compacto else (13, 11))

        tk.Label(cuerpo, text=f"CANTIDAD DE NODOS  ({N_MIN} - {N_MAX})", font=(FUENTE, 8, "bold"),
                 fg=LATERAL_TXT, bg=LATERAL).pack(anchor="w")
        fila = tk.Frame(cuerpo, bg=LATERAL)
        fila.pack(fill="x", pady=(5, 0))
        self._boton(fila, "−", LATERAL_2, lambda: self._cambiar_nodos(-1), size=12, pady=2
                    ).pack(side="left")
        self.entrada_nodos = tk.Entry(fila, width=4, font=(FUENTE, 14, "bold"), justify="center",
                                      relief="flat", bd=0, bg=LATERAL_2, fg="white",
                                      insertbackground="white", highlightthickness=1,
                                      highlightbackground=LATERAL_2, highlightcolor=PRIMARIO)
        self.entrada_nodos.insert(0, "5")
        self.entrada_nodos.pack(side="left", padx=4, ipady=3)
        self._boton(fila, "+", LATERAL_2, lambda: self._cambiar_nodos(1), size=12, pady=2
                    ).pack(side="left")

        self._seccion(cuerpo, 1, "Generar el grafo")
        self._boton(cuerpo, "✎   Generación manual", "#7C5CFC", self.abrir_manual).pack(fill="x")
        marco = tk.Frame(cuerpo, bg=LATERAL)
        marco.pack(fill="x", pady=(10, 0))
        tk.Label(marco, text="Aristas presentes", font=(FUENTE, 9), fg=LATERAL_TXT,
                 bg=LATERAL).pack(side="left")
        self.lbl_densidad = tk.Label(marco, text="70 %", font=(FUENTE, 9, "bold"), fg="white",
                                     bg=LATERAL)
        self.lbl_densidad.pack(side="right")
        self.densidad = Deslizador(cuerpo, 30, 100, 70, escala=self.esc,
                                   comando=lambda v: self.lbl_densidad.config(text=f"{v} %"))
        self.densidad.pack(fill="x", pady=(2, 8))
        self._boton(cuerpo, "⚄   Generación aleatoria", "#14A3B8", self.generar_aleatorio
                    ).pack(fill="x")

        self._seccion(cuerpo, 2, "Verificar")
        self._boton(cuerpo, "✔   Verificar ciclos hamiltonianos", "#2EA66F", self.verificar_grafo
                    ).pack(fill="x")

        self._seccion(cuerpo, 3, "Fuerza bruta paso a paso")
        self._boton(cuerpo, "▶   Siguiente paso", PRIMARIO, lambda: self.avanzar(1)).pack(fill="x")
        self._boton(cuerpo, "▶▶   Avanzar 10 pasos", "#5B8DEF", lambda: self.avanzar(10)
                    ).pack(fill="x", pady=(6, 0))
        self._boton(cuerpo, "⏩   Ejecutar hasta el final", "#E8811A", lambda: self.avanzar(None)
                    ).pack(fill="x", pady=(6, 0))
        self._boton(cuerpo, "↻   Reiniciar ejecución", LATERAL_2, self.reiniciar, fg="#D5DEF5"
                    ).pack(fill="x", pady=(6, 0))

    def _cambiar_nodos(self, delta):
        try:
            n = int(self.entrada_nodos.get())
        except ValueError:
            n = N_MIN
        n = min(N_MAX, max(N_MIN, n + delta))
        self.entrada_nodos.delete(0, "end")
        self.entrada_nodos.insert(0, str(n))

    def _estado(self, texto, tipo="info"):
        color = {"info": LATERAL_TXT, "ok": "#5FD39A", "error": "#FF8A8F"}[tipo]
        self.franja_estado.config(bg=color)
        self.lbl_estado.config(text=texto, fg="#E8EEFC" if tipo == "info" else color)

    def _crear_grafico(self):
        contenedor = tk.Frame(self.raiz, bg=FONDO)
        contenedor.pack(side="left", fill="both", expand=True)
        tarjeta = tk.Frame(contenedor, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
        tarjeta.pack(fill="both", expand=True, padx=12, pady=12)
        self.fig = Figure(figsize=(6.4, 6.4), dpi=100, facecolor=BLANCO)
        self.ax = self.fig.add_axes([0.03, 0.08, 0.94, 0.82])
        self.canvas = FigureCanvasTkAgg(self.fig, master=tarjeta)
        self.canvas.get_tk_widget().configure(bg=BLANCO, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _crear_paneles_texto(self):
        contenedor = tk.Frame(self.raiz, bg=FONDO)
        contenedor.pack(side="right", fill="y", padx=(0, 12), pady=12)
        self.libro = ttk.Notebook(contenedor, width=int(450 * self.esc))
        self.libro.pack(fill="both", expand=True)

        self.txt_matrices = self._pestana_texto("Matrices", horizontal=True)
        self.txt_verif = self._pestana_texto("Verificación", "word")
        self.txt_pasos = self._pestana_texto("Paso a paso", "word")

        marco = tk.Frame(self.libro, bg=BLANCO)
        self.libro.add(marco, text="Resultados")
        fichas = tk.Frame(marco, bg=BLANCO)
        fichas.pack(fill="x", padx=14, pady=(14, 0))
        fichas.columnconfigure((0, 1), weight=1, uniform="ficha")
        self.val_ciclos = self._ficha(fichas, "CICLOS ENCONTRADOS", PRIMARIO, 0, 0)
        self.val_costo = self._ficha(fichas, "COSTO MÍNIMO", OK, 0, 1)
        self.val_optimo = self._ficha(fichas, "CICLO ÓPTIMO", ERROR, 1, 0, columnas=2, tam=12)
        self.lbl_resumen = tk.Label(marco, text="Aún no hay resultados.", font=(FUENTE, 9),
                                    fg=TENUE, bg=BLANCO, justify="left", anchor="w",
                                    wraplength=int(410 * self.esc))
        self.lbl_resumen.pack(fill="x", padx=16, pady=(8, 6))

        cuerpo = tk.Frame(marco, bg=BLANCO)
        cuerpo.pack(fill="both", expand=True, padx=14)
        self.tabla = ttk.Treeview(cuerpo, columns=("n", "ciclo", "costo"), show="headings")
        for col, txt, ancho in (("n", "N.º", 55), ("ciclo", "Ciclo hamiltoniano", 270),
                                ("costo", "Costo", 70)):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=int(ancho * self.esc), anchor="center")
        self.tabla.tag_configure("par", background=BLANCO)
        self.tabla.tag_configure("impar", background="#F6F8FC")
        self.tabla.tag_configure("optimo", background=OK_FONDO, foreground=OK)
        barra = ttk.Scrollbar(cuerpo, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar_ciclo)
        self._boton(marco, "⭳   Exportar todos los ciclos (CSV)", PRIMARIO, self.exportar_csv, pady=8
                    ).pack(fill="x", padx=14, pady=12)

    def _ficha(self, padre, titulo, color, fila, col, columnas=1, tam=20):
        f = tk.Frame(padre, bg=SUPERFICIE)
        f.grid(row=fila, column=col, columnspan=columnas, sticky="nsew",
               padx=(0 if col == 0 else 5, 5 if col == 0 and columnas == 1 else 0),
               pady=(0 if fila == 0 else 10, 0))
        tk.Frame(f, bg=color, width=4).pack(side="left", fill="y")
        interior = tk.Frame(f, bg=SUPERFICIE)
        interior.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        tk.Label(interior, text=titulo, font=(FUENTE, 8, "bold"), fg=TENUE, bg=SUPERFICIE
                 ).pack(anchor="w")
        valor = tk.Label(interior, text="–", font=(FUENTE, tam, "bold"), fg=color, bg=SUPERFICIE,
                         anchor="w", justify="left", wraplength=int(390 * self.esc))
        valor.pack(anchor="w")
        return valor

    def _pestana_texto(self, titulo, ajuste="none", horizontal=False):
        marco = tk.Frame(self.libro, bg=BLANCO)
        self.libro.add(marco, text=titulo)
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        texto = tk.Text(marco, wrap=ajuste, font=(MONO, 10), bg=BLANCO, fg=TEXTO, relief="flat",
                        bd=0, highlightthickness=0, padx=16, pady=14, width=1, height=1,
                        selectbackground="#CFE0FF", selectforeground=TEXTO,
                        inactiveselectbackground="#DCE8FF")
        texto.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(marco, orient="vertical", command=texto.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        texto.configure(yscrollcommand=vertical.set)
        if horizontal:
            horiz = ttk.Scrollbar(marco, orient="horizontal", command=texto.xview)
            horiz.grid(row=1, column=0, sticky="ew")
            texto.configure(xscrollcommand=horiz.set)
        configurar_etiquetas(texto)
        return texto

    @staticmethod
    def _escribir(widget, contenido):
        if isinstance(contenido, str):
            contenido = [(contenido, ())]
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for texto, etiqueta in contenido:
            widget.insert("end", texto, etiqueta)
        widget.configure(state="disabled")
        widget.see("1.0")

    def _ruta_texto(self, ruta):
        return " → ".join(self.nombres[i] for i in ruta)

    def _arista_texto(self, arista):
        return f"{self.nombres[arista[0]]}–{self.nombres[arista[1]]}"

    def _costo_ruta(self, ruta):
        return sum(self.C[a][b] for a, b in zip(ruta, ruta[1:]))

    def _matriz_texto(self, M, conv=str, binaria=False):
        celdas = [[conv(x) for x in fila] for fila in M]
        ancho = max(5, max(len(c) for fila in celdas for c in fila) + 2)
        seg = [(" " * 4, ()),
               ("".join(f"{nom:>{ancho}}" for nom in self.nombres) + " \n", "cab_sub")]
        for i, fila in enumerate(celdas):
            seg.append((f"{self.nombres[i]:>2} ", "cab"))
            seg.append(("│", "tenue"))
            for j, c in enumerate(fila):
                if i == j:
                    etq = "diag"
                elif c == "∞":
                    etq = "inf"
                elif binaria:
                    etq = "uno" if c == "1" else "cero"
                else:
                    etq = "val"
                seg.append((f"{c:>{ancho}}", etq))
            seg.append(("\n", ()))
        return seg

    def leer_n(self):
        try:
            n = int(self.entrada_nodos.get())
        except ValueError:
            messagebox.showerror("Error", f"Ingrese un número entero entre {N_MIN} y {N_MAX}.")
            return None
        if n < N_MIN or n > N_MAX:
            messagebox.showwarning("Cantidad inválida",
                                   f"El número de nodos debe estar entre {N_MIN} y {N_MAX}.")
            return None
        return n

    def generar_aleatorio(self):
        n = self.leer_n()
        if n is None:
            return
        try:
            prob = min(100, max(0, int(float(self.densidad.get())))) / 100
        except ValueError:
            prob = 0.7
        pesos = {}
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < prob:
                    pesos[(i, j)] = random.randint(10, 100)
        self.cargar_grafo(n, pesos, "Grafo aleatorio generado.")

    def abrir_manual(self):
        n = self.leer_n()
        if n is None:
            return
        nombres = nombres_nodos(n)
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Generación manual del grafo")
        ventana.configure(bg=FONDO)
        ventana.transient(self.raiz)
        ventana.resizable(False, False)

        cab = tk.Frame(ventana, bg=PRIMARIO)
        cab.pack(fill="x")
        tk.Label(cab, text="Ingrese los pesos de las aristas", font=(FUENTE, 15, "bold"),
                 bg=PRIMARIO, fg="white").pack(anchor="w", padx=22, pady=(16, 3))
        tk.Label(cab, text="Deje vacío un campo si no desea crear esa arista.\n"
                           "Los pesos representan distancias, costos o tiempos (deben ser > 0).",
                 font=(FUENTE, 9), bg=PRIMARIO, fg="#DCE6FF", justify="left"
                 ).pack(anchor="w", padx=22, pady=(0, 16))

        tarjeta = tk.Frame(ventana, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
        tarjeta.pack(padx=20, pady=(18, 4))
        marco = tk.Frame(tarjeta, bg=BLANCO)
        marco.pack(padx=16, pady=14)

        def letra(fila, col, nom):
            tk.Label(marco, text=nom, width=6, font=(FUENTE, 10, "bold"), bg=SUPERFICIE,
                     fg=PRIMARIO).grid(row=fila, column=col, padx=2, pady=2, ipady=3, sticky="nsew")

        for j, nom in enumerate(nombres):
            letra(0, j + 1, nom)
        entradas = {}
        previos = self.pesos if self.n == n else {}
        for i, nom_i in enumerate(nombres):
            letra(i + 1, 0, nom_i)
            for j in range(n):
                if j <= i:
                    tk.Label(marco, text="·", width=6, bg="#F6F8FC", fg="#B6BFCC"
                             ).grid(row=i + 1, column=j + 1, padx=2, pady=2, ipady=3, sticky="nsew")
                else:
                    e = tk.Entry(marco, width=6, justify="center", font=(FUENTE, 10), relief="flat",
                                 bd=0, bg=BLANCO, fg=TEXTO, highlightthickness=1,
                                 highlightbackground=BORDE, highlightcolor=PRIMARIO)
                    e.grid(row=i + 1, column=j + 1, padx=2, pady=2, ipady=4, sticky="nsew")
                    if (i, j) in previos:
                        e.insert(0, formato(previos[(i, j)]))
                    entradas[(i, j)] = e

        def construir(_evento=None):
            pesos, errores = {}, []
            for (i, j), e in entradas.items():
                e.config(highlightbackground=BORDE)
                v = e.get().strip().replace(",", ".")
                if v == "":
                    continue
                try:
                    w = float(v)
                    if not math.isfinite(w) or w <= 0:
                        raise ValueError
                    pesos[(i, j)] = int(w) if w.is_integer() else w
                except ValueError:
                    e.config(highlightbackground=ERROR)
                    errores.append(f"{nombres[i]}–{nombres[j]}: el peso debe ser un número mayor que 0.")
            if errores:
                messagebox.showerror("Errores", "\n".join(errores), parent=ventana)
                return
            if not pesos:
                messagebox.showwarning("Grafo vacío", "Debe ingresar al menos una arista.", parent=ventana)
                return
            ventana.destroy()
            self.cargar_grafo(n, pesos, "Grafo manual construido.")

        botones = tk.Frame(ventana, bg=FONDO)
        botones.pack(pady=14)
        self._boton(botones, "Cancelar", "#E2E8F3", ventana.destroy, fg=TEXTO, size=10, pady=8
                    ).pack(side="left", padx=6, ipadx=10)
        self._boton(botones, "✔   Construir grafo", "#2EA66F", construir, size=10, pady=8
                    ).pack(side="left", padx=6, ipadx=10)
        ventana.bind("<Return>", construir)
        ventana.bind("<Escape>", lambda _e: ventana.destroy())

        ventana.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - ventana.winfo_width()) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - ventana.winfo_height()) // 2
        ventana.geometry(f"+{max(0, x)}+{max(0, y)}")
        ventana.grab_set()
        if entradas:
            entradas[min(entradas)].focus_set()

    def cargar_grafo(self, n, pesos, mensaje):
        self.n, self.pesos = n, pesos
        self.nombres = nombres_nodos(n)
        self.C = construir_matriz_costos(n, pesos)
        self.verif = None
        self.reiniciar(silencioso=True)
        A = matriz_adyacencia(self.C)
        self._escribir(self.txt_matrices,
                       [("Matriz de costos\n", "h1"), ("∞ = no hay arista\n", "tenue")]
                       + self._matriz_texto(self.C, formato)
                       + [("\nMatriz de adyacencia\n", "h1")]
                       + self._matriz_texto(A, str, binaria=True)
                       + [("\n", ()), (f"Aristas: {sum(map(sum, A)) // 2}", "h2")])
        self._escribir(self.txt_verif, [("Pulse «Verificar ciclos hamiltonianos».", "tenue")])
        self.libro.select(0)
        self._estado(f"{mensaje}\nNodos: {n}   Aristas: {len(pesos)}", "ok")
        self.dibujar()

    def verificar_grafo(self):
        if not self.C:
            messagebox.showwarning("Sin grafo", "Primero debe generar un grafo.")
            return None
        v = verificar(self.C)
        self.verif = v
        nom = self.nombres

        seg = [("Verificación de ciclos hamiltonianos\n", "h1"),
               ("1) Grados de los vértices\n", "h2")]
        for i, g in enumerate(v["grados"]):
            seg.append((f" {nom[i]}:{g} ", "chip_mal" if g < 2 else "chip"))
            seg.append(("  ", ()))
        bajos = [nom[i] for i, g in enumerate(v["grados"]) if g < 2]
        seg.append(("\nVértices con grado < 2: ", "tenue"))
        seg.append((", ".join(bajos), "mal") if bajos else ("ninguno", "tenue"))

        seg += [("\n2) Matriz de caminos (A + I, producto booleano)\n", "h2")]
        seg += self._matriz_texto(v["P"], str, binaria=True)
        seg.append((f"Componentes conexas: {len(v['componentes'])}\n", "h2"))
        for k, comp in enumerate(v["componentes"], start=1):
            seg.append((f"V{k} = {{{', '.join(nom[i] for i in comp)}}}\n", "ruta"))
        conexo = len(v["componentes"]) == 1
        seg.append(("\n", ()))
        seg.append((" ✔ El grafo es conexo. " if conexo else " ✘ El grafo NO es conexo. ",
                    "badge_ok" if conexo else "badge_mal"))
        seg.append(("\n\nGrado >= 2 y conexión son condiciones necesarias, pero no bastan: "
                    "se comprueba con la búsqueda siguiente.", "tenue"))

        seg.append(("\n3) Búsqueda de un ciclo hamiltoniano\n", "h2"))
        if v["hamiltoniano"]:
            seg.append((" ✔ El grafo SÍ admite ciclos hamiltonianos. ", "badge_ok"))
            seg.append(("\n\nEjemplo:  ", "tenue"))
            seg.append((self._ruta_texto(v["ruta"]), "ciclo"))
            estado = "El grafo admite ciclos hamiltonianos."
        else:
            falt = ", ".join(self._arista_texto(a) for a in v["faltantes"])
            seg.append((" ✘ El grafo NO admite ciclos hamiltonianos. ", "badge_mal"))
            seg.append((f"\n\nPara completar al menos uno, agregue como mínimo "
                        f"{len(v['faltantes'])} arista(s):  ", "ruta"))
            seg.append((falt, "mal"))
            seg.append(("\n\nCiclo que se obtiene:  ", "tenue"))
            seg.append((self._ruta_texto(v["ruta"]), "ruta"))
            seg.append(("\n\n(Use «Generación manual» para agregarlas.)", "tenue"))
            estado = f"Sin ciclos hamiltonianos. Faltan: {falt}"
        self._escribir(self.txt_verif, seg)
        self.libro.select(1)
        self._estado(estado, "ok" if v["hamiltoniano"] else "error")
        if not v["hamiltoniano"]:

            self.ruta_resaltada = None
            self.ruta_actual = v["ruta"]
            self.faltante_actual = None
        self.dibujar()
        return v

    def reiniciar(self, silencioso=False):
        self.motor = None
        self.ruta_actual = self.faltante_actual = self.ruta_resaltada = None
        self.info_actual = ""
        self.tabla.delete(*self.tabla.get_children())
        self.lbl_resumen.config(text="Aún no hay resultados.")
        for valor in (self.val_ciclos, self.val_costo, self.val_optimo):
            valor.config(text="–")
        self._escribir(self.txt_pasos, [("Aquí se irá mostrando cada ruta evaluada.", "tenue")])
        self.lbl_progreso.config(text="")
        self.barra["value"] = 0
        if not silencioso:
            self._estado("Ejecución reiniciada.", "info")
            self.dibujar()

    def avanzar(self, m):
        if not self.C:
            messagebox.showwarning("Sin grafo", "Primero debe generar un grafo.")
            return
        if self.motor is None:
            v = self.verificar_grafo()
            if v is None:
                return
            if not v["hamiltoniano"]:
                messagebox.showwarning(
                    "Sin ciclos hamiltonianos",
                    "El grafo no admite ciclos hamiltonianos.\nAgregue estas aristas: "
                    + ", ".join(self._arista_texto(a) for a in v["faltantes"]))
                return
            self.motor = MotorFuerzaBruta(self.C)
            self._escribir(self.txt_pasos, "")
        motor = self.motor
        if motor.terminado:
            messagebox.showinfo("Fin", "Ya se evaluaron todas las rutas. Use «Reiniciar ejecución».")
            return
        restantes = motor.total - motor.k
        pedidos = restantes if m is None else min(m, restantes)
        pasos = motor.avanzar(pedidos)
        self.libro.select(2)
        self._registrar_pasos(pasos, pedidos)
        ultimo = pasos[-1] if pasos else None
        if pasos:
            self.ruta_actual, self.faltante_actual = ultimo.ruta, ultimo.faltante
            self.info_actual = (f"descartada: falta la arista {self._arista_texto(ultimo.faltante)}"
                                if ultimo.faltante else f"costo {formato(ultimo.costo)}")
        else:
            self.ruta_actual = self.faltante_actual = None
            self.info_actual = ""
        self.ruta_resaltada = motor.optimos[0] if motor.optimos else None
        if self.compacto:
            progreso = (f"Ruta {motor.k} de {motor.total}  ·  Ciclos: {len(motor.ciclos)}\n"
                        f"Mejor costo: {formato(motor.mejor_costo)}")
        else:
            progreso = (f"Ruta {motor.k} de {motor.total}\nCiclos encontrados: {len(motor.ciclos)}\n"
                        f"Mejor costo: {formato(motor.mejor_costo)}")
        self.lbl_progreso.config(text=progreso)
        self.barra["value"] = 100 * motor.k / motor.total
        if motor.terminado:
            self.ruta_actual = self.faltante_actual = None
            self.mostrar_resultados()
        self.dibujar()

    def _registrar_pasos(self, pasos, pedidos):
        txt = self.txt_pasos
        txt.configure(state="normal")
        if pasos:
            for p in pasos:
                txt.insert("end", f"Paso {p.k:<4} ", ("linea", "paso"))
                txt.insert("end", self._ruta_texto(p.ruta) + "\n", ("linea", "ruta"))
                if p.faltante:
                    txt.insert("end", f"    ✘ falta la arista {self._arista_texto(p.faltante)}"
                                      " → DESCARTADA\n", ("salto", "desc"))
                else:
                    txt.insert("end", f"    ✔ costo {formato(p.costo)} → CICLO HAMILTONIANO",
                               ("salto", "ciclo"))
                    if p.mejora:
                        txt.insert("end", " ", "salto")
                        txt.insert("end", " nuevo mejor ", ("salto", "mejor"))
                    elif p.empate:
                        txt.insert("end", " ", "salto")
                        txt.insert("end", " empata el mejor ", ("salto", "empate"))
                    txt.insert("end", "\n", "salto")
        else:
            m = self.motor
            txt.insert("end", f"Se evaluaron {pedidos} rutas seguidas (hasta la ruta {m.k}).\n", "tenue")
        if self.motor.terminado:
            txt.insert("end", "\nSe evaluaron todas las rutas candidatas.\n", "h2")
        txt.configure(state="disabled")
        txt.see("end")

    def mostrar_resultados(self):
        motor = self.motor
        ciclos = sorted(motor.ciclos, key=lambda x: x[1])
        opt = motor.optimos
        self.val_ciclos.config(text=str(len(ciclos)))
        self.val_costo.config(text=formato(motor.mejor_costo))
        self.val_optimo.config(text=self._ruta_texto(opt[0]))
        self.lbl_resumen.config(
            text=(f"{len(opt)} ciclos empatan con el costo mínimo." if len(opt) > 1
                  else "Un único ciclo alcanza el costo mínimo.")
                 + (f"\nSe muestran los {LIMITE_TABLA} de menor costo; exporte el CSV para ver todos."
                    if len(ciclos) > LIMITE_TABLA else "")
                 + "\nSeleccione una fila para verla resaltada en el grafo.")
        self.tabla.delete(*self.tabla.get_children())
        for i, (ruta, costo) in enumerate(ciclos[:LIMITE_TABLA], start=1):
            etiqueta = "optimo" if costo == motor.mejor_costo else ("par" if i % 2 else "impar")
            self.tabla.insert("", "end", tags=(etiqueta,),
                              values=(i, "→".join(self.nombres[k] for k in ruta), formato(costo)))
        self.libro.select(3)
        self._estado(f"Óptimo: {self._ruta_texto(opt[0])}\nCosto: {formato(motor.mejor_costo)}", "ok")

    def al_seleccionar_ciclo(self, _evento):
        sel = self.tabla.selection()
        if not sel or not self.motor:
            return
        texto = self.tabla.item(sel[0], "values")[1]
        letras = texto.replace("→", "").replace(" ", "")
        self.ruta_resaltada = tuple(ord(c) - 65 for c in letras)
        self.dibujar()

    def exportar_csv(self):
        if not self.motor or not self.motor.ciclos:
            messagebox.showinfo("Sin datos", "Primero ejecute el algoritmo hasta el final.")
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                               initialfile="ciclos_hamiltonianos.csv")
        if not archivo:
            return
        with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["N.º", "Ciclo hamiltoniano", "Costo"])
            for i, (ruta, costo) in enumerate(sorted(self.motor.ciclos, key=lambda x: x[1]), start=1):
                w.writerow([i, self._ruta_texto(ruta), formato(costo)])
        messagebox.showinfo("Exportado", f"Se guardaron {len(self.motor.ciclos)} ciclos en:\n{archivo}")

    @staticmethod
    def _aristas(ruta):
        return {(min(a, b), max(a, b)) for a, b in zip(ruta, ruta[1:])} if ruta else set()

    def _dibujar_vacio(self):
        ax, k = self.ax, 7
        pos = [(0.85 * math.cos(math.pi / 2 - 2 * math.pi * i / k),
                0.85 * math.sin(math.pi / 2 - 2 * math.pi * i / k)) for i in range(k)]
        for i in range(k):
            for j in range(i + 1, k):
                if j - i in (1, 2, k - 1):
                    ax.plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]], color="#E6EBF4",
                            lw=1.6, zorder=1)
        for x, y in pos:
            ax.scatter([x], [y], s=520, c=SUPERFICIE, edgecolors="#D5DCE8", linewidths=1.6, zorder=2)
        ax.text(0, 0.07, "Genere un grafo para comenzar", ha="center", va="center", fontsize=14,
                fontweight="bold", color=TEXTO, zorder=4,
                bbox=dict(boxstyle="round,pad=0.7", fc=BLANCO, ec=BORDE, lw=1))
        ax.text(0, -0.26, "Elija la cantidad de nodos y use la generación\nmanual o aleatoria.",
                ha="center", va="center", fontsize=10, color=TENUE, zorder=4, linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.3", fc=BLANCO, ec="none"))

    def _posiciones_pesos(self, pos):
        ocupados = list(pos)
        lugares = {}
        for (i, j) in sorted(self.pesos):
            (x1, y1), (x2, y2) = pos[i], pos[j]
            mejor = None
            for t in (0.5, 0.42, 0.58, 0.34, 0.66, 0.27, 0.73):
                x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
                libre = min(math.hypot(x - px, y - py) for px, py in ocupados)
                puntaje = min(libre, 0.24) - 0.04 * abs(t - 0.5)
                if mejor is None or puntaje > mejor[0]:
                    mejor = (puntaje, x, y)
            lugares[(i, j)] = mejor[1:]
            ocupados.append(mejor[1:])
        return lugares

    def dibujar(self):
        ax = self.ax
        ax.clear()
        ax.set_position([0.04, 0.11, 0.92, 0.70])
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.4, 1.4)
        if not self.C:
            self._dibujar_vacio()
            self.canvas.draw_idle()
            return
        n = self.n
        pos = [(math.cos(math.pi / 2 - 2 * math.pi * i / n),
                math.sin(math.pi / 2 - 2 * math.pi * i / n)) for i in range(n)]
        en_actual, en_mejor = self._aristas(self.ruta_actual), self._aristas(self.ruta_resaltada)
        denso = n >= 9
        area_nodo = 640 if denso else 920
        radio = math.sqrt(area_nodo) / 2 + 2

        def segmento(a, b, **kw):
            ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], solid_capstyle="round", **kw)

        def flecha(a, b, color, lw, alpha=1.0, z=2):
            ax.annotate("", xy=pos[b], xytext=pos[a], zorder=z,
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, alpha=alpha,
                                        shrinkA=radio, shrinkB=radio, mutation_scale=11 + 2 * lw))

        for (i, j) in self.pesos:
            segmento(i, j, color=COLOR_BASE, lw=1.0 if denso else 1.5, alpha=0.85 if denso else 1,
                     zorder=1)

        if self.ruta_actual:
            for a, b in zip(self.ruta_actual, self.ruta_actual[1:]):
                if self.C[a][b] == INF:
                    segmento(a, b, color=COLOR_FALTA, lw=2.4, ls=(0, (4, 3)), zorder=2)
                else:
                    flecha(a, b, COLOR_ACTUAL, 2.6)

        if self.ruta_resaltada:
            for a, b in zip(self.ruta_resaltada, self.ruta_resaltada[1:]):
                segmento(a, b, color=COLOR_MEJOR, lw=9, alpha=0.13, zorder=1.5)
                flecha(a, b, COLOR_MEJOR, 3.2, alpha=0.9, z=2.2)

        lugares = self._posiciones_pesos(pos)
        for (i, j), w in self.pesos.items():
            x, y = lugares[(i, j)]
            color = COLOR_MEJOR if (i, j) in en_mejor else (COLOR_ACTUAL if (i, j) in en_actual
                                                            else "#475569")
            borde = color if color != "#475569" else "#D5DBE6"
            ax.text(x, y, formato(w), fontsize=7.5 if denso else 8.5, fontweight="bold", color=color,
                    ha="center", va="center", zorder=3,
                    bbox=dict(boxstyle="round,pad=0.2" if denso else "round,pad=0.28",
                              fc=BLANCO, ec=borde, lw=0.9))

        color_ruta = COLOR_MEJOR if self.ruta_resaltada else (COLOR_ACTUAL if self.ruta_actual else None)
        for i, (x, y) in enumerate(pos):
            ax.scatter([x + 0.014], [y - 0.02], s=area_nodo * 1.15, c="#0F172A", alpha=0.10,
                       linewidths=0, zorder=3)
            if color_ruta and i == 0:
                fc, ec, tc = color_ruta, color_ruta, "white"
            elif color_ruta:
                fc, ec, tc = mezclar(color_ruta, "#FFFFFF", 0.88), color_ruta, TEXTO
            else:
                fc, ec, tc = BLANCO, "#64748B", TEXTO
            ax.scatter([x], [y], s=area_nodo, c=fc, edgecolors=ec, linewidths=2, zorder=4)
            ax.text(x, y, self.nombres[i], ha="center", va="center", fontsize=11 if denso else 12.5,
                    fontweight="bold", color=tc, zorder=5)
        if color_ruta:
            ax.text(pos[0][0], pos[0][1] + 0.2, "inicio", ha="center", va="center", fontsize=8.5,
                    color=color_ruta, fontweight="bold", zorder=5)

        info, color_info = "", TENUE
        if self.ruta_actual and self.motor is None and self.verif and not self.verif["hamiltoniano"]:
            titulo, ruta = "Ciclo sugerido", self.ruta_actual
            info, color_info = "la arista punteada es la que falta", COLOR_FALTA
        elif self.ruta_actual and self.motor and not self.motor.terminado:
            titulo, ruta = "Ruta en evaluación", self.ruta_actual
            info = self.info_actual
            color_info = COLOR_MEJOR if info.startswith("descartada") else COLOR_ACTUAL
        elif self.motor and self.motor.terminado and self.ruta_resaltada:
            titulo, ruta = "Ciclo hamiltoniano resaltado", self.ruta_resaltada
            info, color_info = f"costo {formato(self._costo_ruta(ruta))}", COLOR_MEJOR
        else:
            titulo, ruta = "Grafo ponderado no dirigido", None
            info = f"{n} nodos   ·   {len(self.pesos)} aristas"
        fig = self.fig.transFigure
        ax.text(0.5, 0.965, titulo, transform=fig, ha="center", va="top", fontsize=14,
                fontweight="bold", color=TEXTO)
        ax.annotate(self._ruta_texto(ruta) if ruta else info, xy=(0.5, 0.965), xycoords="figure fraction",
                    xytext=(0, -26), textcoords="offset points", ha="center", va="top",
                    fontsize=10.5, color=TENUE)
        if ruta and info:
            ax.annotate(info, xy=(0.5, 0.965), xycoords="figure fraction", xytext=(0, -45),
                        textcoords="offset points", ha="center", va="top", fontsize=10.5,
                        fontweight="bold", color=color_info)

        elementos = [Line2D([0], [0], color=COLOR_BASE, lw=1.8, label="Arista"),
                     Line2D([0], [0], color=COLOR_ACTUAL, lw=2.8, label="Ruta en evaluación"),
                     Line2D([0], [0], color=COLOR_FALTA, lw=2.4, ls=(0, (2, 1.5)),
                            label="Arista inexistente"),
                     Line2D([0], [0], color=COLOR_MEJOR, lw=4, label="Mejor ciclo")]
        ax.legend(handles=elementos, loc="upper center", ncol=2, fontsize=9, frameon=False,
                  labelcolor=TENUE, bbox_to_anchor=(0.5, -0.02), handlelength=1.8,
                  columnspacing=2.4, labelspacing=0.5)
        self.canvas.draw_idle()


if __name__ == "__main__":
    activar_dpi_alto()
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
