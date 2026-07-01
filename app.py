# -*- coding: utf-8 -*-
"""
IA contra el Ciberacoso — App de escritorio (PC)
Interfaz gráfica equivalente a la versión web. Usa motor.py.
Ejecuta:  python app.py     |     o el .exe generado con PyInstaller.
"""
import threading
import time
import tkinter as tk
from tkinter import ttk

from motor import clasificar, SET_PRUEBA, EJEMPLO_100

# ---------- Colores (tema oscuro) ----------
BG      = "#0f172a"
PANEL   = "#1e293b"
TXT     = "#e2e8f0"
MUTED   = "#94a3b8"
ACCENT  = "#6366f1"
SAFE    = "#22c55e"
DANGER  = "#ef4444"
CARD_D  = "#3b1d22"   # fondo resultado agresivo
CARD_S  = "#12321f"   # fondo resultado seguro


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ IA contra el Ciberacoso")
        self.geometry("760x620")
        self.configure(bg=BG)
        self.vigilando = False
        self._vig_job = None

        self._estilo()
        self._cabecera()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._tab_analizar(nb)
        self._tab_masivo(nb)
        self._tab_precision(nb)
        self._tab_vigilancia(nb)

    # ---------- estilos ----------
    def _estilo(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=MUTED,
                    padding=(16, 8), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab", background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=PANEL)
        s.configure("TLabel", background=PANEL, foreground=TXT, font=("Segoe UI", 10))
        s.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Head.TLabel", background=BG, foreground=TXT)
        s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                    font=("Segoe UI", 10, "bold"), borderwidth=0, padding=8)
        s.map("Accent.TButton", background=[("active", "#4f46e5")])
        s.configure("Ghost.TButton", background=PANEL, foreground=TXT,
                    font=("Segoe UI", 10), borderwidth=0, padding=8)
        s.configure("Treeview", background="#0b1220", fieldbackground="#0b1220",
                    foreground=TXT, rowheight=24, borderwidth=0)
        s.configure("Treeview.Heading", background=PANEL, foreground=MUTED,
                    font=("Segoe UI", 9, "bold"))

    def _cabecera(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(12, 8))
        tk.Label(top, text="🛡️ IA contra el Ciberacoso", bg=BG, fg=TXT,
                 font=("Segoe UI", 17, "bold")).pack()
        tk.Label(top, text="Detección de agresividad en mensajes · 100% local, sin internet",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack()

    def _txt(self, parent, height=6):
        t = tk.Text(parent, height=height, bg="#0b1220", fg=TXT, insertbackground=TXT,
                    relief="flat", font=("Segoe UI", 11), wrap="word",
                    highlightthickness=1, highlightbackground="#334155",
                    highlightcolor=ACCENT, padx=10, pady=8)
        return t

    # ================= TAB 1: Analizar =================
    def _tab_analizar(self, nb):
        f = ttk.Frame(nb, style="Card.TFrame")
        nb.add(f, text="🔎 Analizar")
        ttk.Label(f, text="Escribe o pega un mensaje:").pack(anchor="w", padx=16, pady=(16, 4))
        self.msg = self._txt(f, 4)
        self.msg.pack(fill="x", padx=16)
        ttk.Button(f, text="Analizar", style="Accent.TButton",
                   command=self.analizar_uno).pack(anchor="w", padx=16, pady=12)

        self.res1 = tk.Frame(f, bg=PANEL)
        self.res1.pack(fill="x", padx=16, pady=6)
        self.v1 = tk.Label(self.res1, text="", bg=PANEL, fg=TXT, font=("Segoe UI", 15, "bold"))
        self.v1.pack(anchor="w", padx=12, pady=(10, 2))
        self.m1 = tk.Label(self.res1, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9),
                           justify="left", wraplength=680)
        self.m1.pack(anchor="w", padx=12, pady=(0, 10))

    def analizar_uno(self):
        texto = self.msg.get("1.0", "end").strip()
        if not texto:
            return
        t0 = time.perf_counter()
        r = clasificar(texto)
        ms = (time.perf_counter() - t0) * 1000
        agg = r["etiqueta"] == "agresivo"
        self.res1.configure(bg=CARD_D if agg else CARD_S)
        self.v1.configure(bg=CARD_D if agg else CARD_S,
                          fg=DANGER if agg else SAFE,
                          text="🚨 AGRESIVO" if agg else "✅ SEGURO")
        motivos = " · ".join(r["motivos"])
        self.m1.configure(bg=CARD_D if agg else CARD_S,
                          text=f"Nivel de riesgo: {r['confianza']}%  ·  {ms:.1f} ms "
                               f"(límite del proyecto: 2000 ms)\n{motivos}")

    # ================= TAB 2: Masivo =================
    def _tab_masivo(self, nb):
        f = ttk.Frame(nb, style="Card.TFrame")
        nb.add(f, text="📊 Masivo")
        ttk.Label(f, text="Pega una lista (un mensaje por línea, hasta 100+):").pack(
            anchor="w", padx=16, pady=(16, 4))
        self.bulk = self._txt(f, 7)
        self.bulk.pack(fill="x", padx=16)
        bar = tk.Frame(f, bg=PANEL)
        bar.pack(anchor="w", padx=16, pady=10)
        ttk.Button(bar, text="Analizar todos", style="Accent.TButton",
                   command=self.analizar_lote).pack(side="left")
        ttk.Button(bar, text="Cargar 100 de ejemplo", style="Ghost.TButton",
                   command=self.cargar_ejemplo).pack(side="left", padx=8)
        self.s2 = tk.Label(f, text="", bg=PANEL, fg=TXT, font=("Segoe UI", 10, "bold"))
        self.s2.pack(anchor="w", padx=16)
        cols = ("n", "msg", "res", "riesgo")
        self.tbl2 = ttk.Treeview(f, columns=cols, show="headings", height=9)
        for c, txt, w in [("n", "#", 40), ("msg", "Mensaje", 430),
                          ("res", "Resultado", 110), ("riesgo", "Riesgo", 70)]:
            self.tbl2.heading(c, text=txt)
            self.tbl2.column(c, width=w, anchor="w")
        self.tbl2.tag_configure("d", foreground="#fecaca")
        self.tbl2.tag_configure("s", foreground="#bbf7d0")
        self.tbl2.pack(fill="both", expand=True, padx=16, pady=(6, 14))

    def cargar_ejemplo(self):
        self.bulk.delete("1.0", "end")
        self.bulk.insert("1.0", "\n".join(EJEMPLO_100))

    def analizar_lote(self):
        lineas = [l.strip() for l in self.bulk.get("1.0", "end").splitlines() if l.strip()]
        if not lineas:
            return
        self.s2.configure(text="Analizando en segundo plano...")
        threading.Thread(target=self._lote_worker, args=(lineas,), daemon=True).start()

    def _lote_worker(self, lineas):
        t0 = time.perf_counter()
        res = [clasificar(x) for x in lineas]
        total = (time.perf_counter() - t0) * 1000
        self.after(0, self._lote_pintar, lineas, res, total)

    def _lote_pintar(self, lineas, res, total):
        for i in self.tbl2.get_children():
            self.tbl2.delete(i)
        nagg = sum(1 for r in res if r["etiqueta"] == "agresivo")
        self.s2.configure(
            text=f"{len(lineas)} mensajes  ·  {nagg} agresivos  ·  {len(lineas)-nagg} seguros  "
                 f"·  {total:.0f} ms total  (en segundo plano, sin congelarse)")
        for i, (linea, r) in enumerate(zip(lineas, res), 1):
            agg = r["etiqueta"] == "agresivo"
            self.tbl2.insert("", "end", tags=("d" if agg else "s",),
                             values=(i, linea[:70],
                                     "🚨 Agresivo" if agg else "✅ Seguro",
                                     f"{r['confianza']}%"))

    # ================= TAB 3: Precisión =================
    def _tab_precision(self, nb):
        f = ttk.Frame(nb, style="Card.TFrame")
        nb.add(f, text="✅ Precisión")
        ttk.Label(f, text="Prueba con 50 frases (25 insultos + 25 amigables). Meta ≥ 90%.").pack(
            anchor="w", padx=16, pady=(16, 6))
        ttk.Button(f, text="Correr prueba de precisión", style="Accent.TButton",
                   command=self.correr_prueba).pack(anchor="w", padx=16)
        self.s3 = tk.Label(f, text="", bg=PANEL, fg=TXT, font=("Segoe UI", 11, "bold"))
        self.s3.pack(anchor="w", padx=16, pady=8)
        cols = ("frase", "real", "dijo", "ok")
        self.tbl3 = ttk.Treeview(f, columns=cols, show="headings", height=10)
        for c, txt, w in [("frase", "Frase", 380), ("real", "Real", 90),
                          ("dijo", "IA dijo", 90), ("ok", "¿Acertó?", 80)]:
            self.tbl3.heading(c, text=txt)
            self.tbl3.column(c, width=w, anchor="w")
        self.tbl3.tag_configure("ok", foreground="#bbf7d0")
        self.tbl3.tag_configure("bad", foreground="#fecaca")
        self.tbl3.pack(fill="both", expand=True, padx=16, pady=(6, 14))

    def correr_prueba(self):
        for i in self.tbl3.get_children():
            self.tbl3.delete(i)
        ok = fp = fn = 0
        t0 = time.perf_counter()
        for texto, real in SET_PRUEBA:
            r = clasificar(texto)
            acerto = r["etiqueta"] == real
            if acerto: ok += 1
            elif real == "seguro": fp += 1
            else: fn += 1
            self.tbl3.insert("", "end", tags=("ok" if acerto else "bad",),
                             values=(texto[:55], real, r["etiqueta"], "✔" if acerto else "✘"))
        ms = (time.perf_counter() - t0) * 1000
        pct = ok / len(SET_PRUEBA) * 100
        cumple = pct >= 90
        self.s3.configure(
            fg=SAFE if cumple else DANGER,
            text=f"Precisión: {pct:.0f}%  ({ok}/{len(SET_PRUEBA)})  ·  {ms:.0f} ms  ·  "
                 f"Falsos positivos: {fp}  ·  Falsos negativos: {fn}  ·  "
                 f"{'CUMPLE ✅ (meta ≥90%)' if cumple else 'NO CUMPLE'}")

    # ================= TAB 4: Vigilancia =================
    def _tab_vigilancia(self, nb):
        f = ttk.Frame(nb, style="Card.TFrame")
        nb.add(f, text="📡 Vigilancia")
        ttk.Label(f, text="Analiza automáticamente mientras escribes o pegas.",
                  ).pack(anchor="w", padx=16, pady=(16, 6))
        self.btn_vig = ttk.Button(f, text="▶️ Activar vigilancia", style="Accent.TButton",
                                  command=self.toggle_vig)
        self.btn_vig.pack(anchor="w", padx=16)
        self.est_vig = tk.Label(f, text="Vigilancia desactivada.", bg=PANEL, fg=MUTED,
                                font=("Segoe UI", 9))
        self.est_vig.pack(anchor="w", padx=16, pady=6)
        self.vig = self._txt(f, 5)
        self.vig.pack(fill="x", padx=16)
        self.vig.bind("<KeyRelease>", self._vig_teclea)
        self.res4 = tk.Frame(f, bg=PANEL)
        self.res4.pack(fill="x", padx=16, pady=8)
        self.v4 = tk.Label(self.res4, text="", bg=PANEL, fg=TXT, font=("Segoe UI", 14, "bold"))
        self.v4.pack(anchor="w", padx=12, pady=6)

    def toggle_vig(self):
        self.vigilando = not self.vigilando
        if self.vigilando:
            self.btn_vig.configure(text="⏸️ Desactivar vigilancia")
            self.est_vig.configure(text="🟢 Vigilancia ACTIVA: analizando mientras escribes.")
        else:
            self.btn_vig.configure(text="▶️ Activar vigilancia")
            self.est_vig.configure(text="Vigilancia desactivada.")
            self.res4.configure(bg=PANEL)
            self.v4.configure(bg=PANEL, text="")

    def _vig_teclea(self, _e):
        if not self.vigilando:
            return
        if self._vig_job:
            self.after_cancel(self._vig_job)
        self._vig_job = self.after(250, self._vig_analiza)

    def _vig_analiza(self):
        txt = self.vig.get("1.0", "end").strip()
        if not txt:
            self.res4.configure(bg=PANEL); self.v4.configure(bg=PANEL, text="")
            return
        r = clasificar(txt)
        agg = r["etiqueta"] == "agresivo"
        self.res4.configure(bg=CARD_D if agg else CARD_S)
        self.v4.configure(bg=CARD_D if agg else CARD_S, fg=DANGER if agg else SAFE,
                          text=("🚨 AGRESIVO" if agg else "✅ SEGURO") +
                               f"   ·   riesgo {r['confianza']}%")


if __name__ == "__main__":
    App().mainloop()
