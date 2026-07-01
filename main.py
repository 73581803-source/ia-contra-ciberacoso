# -*- coding: utf-8 -*-
"""
IA contra el Ciberacoso — App Android (Kivy)
Misma detección que la web y el .exe (usa motor.py).
Este archivo se compila a .apk con Buildozer (ver buildozer.spec y GitHub Actions).
Para probar en PC:  pip install kivy   y luego   python main.py
"""
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput

from motor import clasificar, SET_PRUEBA, EJEMPLO_100

# Colores
BG      = (0.059, 0.090, 0.165, 1)   # #0f172a
PANEL   = (0.118, 0.161, 0.231, 1)   # #1e293b
INPUTBG = (0.043, 0.071, 0.125, 1)   # #0b1220
TXT     = (0.886, 0.910, 0.941, 1)
MUTED   = (0.58, 0.64, 0.72, 1)
ACCENT  = (0.388, 0.400, 0.945, 1)   # #6366f1
SAFE    = (0.133, 0.773, 0.369, 1)   # #22c55e
DANGER  = (0.937, 0.267, 0.267, 1)   # #ef4444

Window.clearcolor = BG


def boton(texto, cb, color=ACCENT):
    b = Button(text=texto, background_normal="", background_color=color,
               color=(1, 1, 1, 1), size_hint_y=None, height="48dp",
               bold=True, font_size="15sp")
    b.bind(on_release=cb)
    return b


def entrada(hint="", multiline=True, height="120dp"):
    return TextInput(hint_text=hint, multiline=multiline, size_hint_y=None,
                     height=height, background_color=INPUTBG, foreground_color=TXT,
                     cursor_color=TXT, padding=[10, 10], font_size="15sp")


class Tarjeta(BoxLayout):
    """Contenedor con padding vertical."""
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=14, spacing=10, **kw)


class AntiAcosoApp(App):
    title = "IA contra el Ciberacoso"

    def build(self):
        self.vigilando = False
        self._vig_ev = None
        tp = TabbedPanel(do_default_tab=False, tab_pos="top_mid",
                         background_color=BG, tab_height="46dp")
        tp.add_widget(self._tab_analizar())
        tp.add_widget(self._tab_masivo())
        tp.add_widget(self._tab_precision())
        tp.add_widget(self._tab_vigilancia())
        return tp

    def _lbl(self, texto="", **kw):
        kw.setdefault("color", TXT)
        kw.setdefault("markup", True)
        kw.setdefault("halign", "left")
        kw.setdefault("valign", "top")
        lb = Label(text=texto, **kw)
        lb.bind(size=lambda w, *_: setattr(w, "text_size", (w.width, None)))
        return lb

    # ---------- TAB 1 ----------
    def _tab_analizar(self):
        t = TabbedPanelItem(text="Analizar")
        c = Tarjeta()
        c.add_widget(self._lbl("[b]Escribe o pega un mensaje:[/b]", size_hint_y=None, height="26dp"))
        self.msg = entrada("Ej: Eres un inútil, nadie te quiere aquí.")
        c.add_widget(self.msg)
        c.add_widget(boton("Analizar", lambda *_: self.analizar_uno()))
        self.res1 = self._lbl("", size_hint_y=1, font_size="16sp")
        c.add_widget(self.res1)
        t.add_widget(c)
        return t

    def analizar_uno(self):
        import time
        texto = self.msg.text.strip()
        if not texto:
            return
        t0 = time.perf_counter()
        r = clasificar(texto)
        ms = (time.perf_counter() - t0) * 1000
        agg = r["etiqueta"] == "agresivo"
        color = "ef4444" if agg else "22c55e"
        titulo = "🚨 AGRESIVO" if agg else "✅ SEGURO"
        self.res1.text = (f"[size=22sp][color=#{color}][b]{titulo}[/b][/color][/size]\n\n"
                          f"[color=#94a3b8]Riesgo: {r['confianza']}%  ·  {ms:.1f} ms "
                          f"(límite 2000 ms)\n{' · '.join(r['motivos'])}[/color]")

    # ---------- TAB 2 ----------
    def _tab_masivo(self):
        t = TabbedPanelItem(text="Masivo")
        c = Tarjeta()
        c.add_widget(self._lbl("[b]Un mensaje por línea (hasta 100+):[/b]", size_hint_y=None, height="26dp"))
        self.bulk = entrada("Pega aquí la lista...", height="160dp")
        c.add_widget(self.bulk)
        fila = BoxLayout(size_hint_y=None, height="48dp", spacing=8)
        fila.add_widget(boton("Analizar todos", lambda *_: self.analizar_lote()))
        fila.add_widget(boton("Cargar 100", lambda *_: self.cargar_ejemplo(), color=PANEL))
        c.add_widget(fila)
        self.s2 = self._lbl("", size_hint_y=None, height="46dp", color=TXT)
        c.add_widget(self.s2)
        sv = ScrollView()
        self.tbl2 = self._lbl("", size_hint_y=None, font_size="13sp")
        self.tbl2.bind(texture_size=lambda w, v: setattr(w, "height", v[1]))
        sv.add_widget(self.tbl2)
        c.add_widget(sv)
        t.add_widget(c)
        return t

    def cargar_ejemplo(self):
        self.bulk.text = "\n".join(EJEMPLO_100)

    def analizar_lote(self):
        lineas = [l.strip() for l in self.bulk.text.splitlines() if l.strip()]
        if not lineas:
            return
        self.s2.text = "[color=#94a3b8]Analizando en segundo plano...[/color]"
        threading.Thread(target=self._lote_worker, args=(lineas,), daemon=True).start()

    def _lote_worker(self, lineas):
        import time
        t0 = time.perf_counter()
        res = [clasificar(x) for x in lineas]
        total = (time.perf_counter() - t0) * 1000
        Clock.schedule_once(lambda dt: self._lote_pintar(lineas, res, total))

    def _lote_pintar(self, lineas, res, total):
        nagg = sum(1 for r in res if r["etiqueta"] == "agresivo")
        self.s2.text = (f"[b]{len(lineas)}[/b] mensajes · [color=#ef4444]{nagg} agresivos[/color] · "
                        f"[color=#22c55e]{len(lineas)-nagg} seguros[/color] · {total:.0f} ms "
                        f"(en segundo plano)")
        filas = []
        for i, (linea, r) in enumerate(zip(lineas, res), 1):
            agg = r["etiqueta"] == "agresivo"
            col = "ef4444" if agg else "22c55e"
            et = "🚨" if agg else "✅"
            filas.append(f"[color=#{col}]{et}[/color] {i}. {linea[:60]}")
        self.tbl2.text = "\n".join(filas)

    # ---------- TAB 3 ----------
    def _tab_precision(self):
        t = TabbedPanelItem(text="Precisión")
        c = Tarjeta()
        c.add_widget(self._lbl("Prueba con 50 frases (25 insultos + 25 amigables). Meta ≥ 90%.",
                               size_hint_y=None, height="40dp", color=MUTED))
        c.add_widget(boton("Correr prueba", lambda *_: self.correr_prueba()))
        self.s3 = self._lbl("", size_hint_y=None, height="70dp")
        c.add_widget(self.s3)
        sv = ScrollView()
        self.tbl3 = self._lbl("", size_hint_y=None, font_size="13sp")
        self.tbl3.bind(texture_size=lambda w, v: setattr(w, "height", v[1]))
        sv.add_widget(self.tbl3)
        c.add_widget(sv)
        t.add_widget(c)
        return t

    def correr_prueba(self):
        import time
        ok = fp = fn = 0
        filas = []
        t0 = time.perf_counter()
        for texto, real in SET_PRUEBA:
            r = clasificar(texto)
            acerto = r["etiqueta"] == real
            if acerto: ok += 1
            elif real == "seguro": fp += 1
            else: fn += 1
            col = "22c55e" if acerto else "ef4444"
            mark = "✔" if acerto else "✘"
            filas.append(f"[color=#{col}]{mark}[/color] {texto[:48]}  ({r['etiqueta']})")
        ms = (time.perf_counter() - t0) * 1000
        pct = ok / len(SET_PRUEBA) * 100
        cumple = pct >= 90
        col = "22c55e" if cumple else "ef4444"
        self.s3.text = (f"[size=20sp][color=#{col}][b]{pct:.0f}%[/b][/color][/size]  "
                        f"({ok}/{len(SET_PRUEBA)}) · {ms:.0f} ms\n"
                        f"[color=#94a3b8]Falsos positivos: {fp} · Falsos negativos: {fn} · "
                        f"{'CUMPLE ✅' if cumple else 'NO CUMPLE'}[/color]")
        self.tbl3.text = "\n".join(filas)

    # ---------- TAB 4 ----------
    def _tab_vigilancia(self):
        t = TabbedPanelItem(text="Vigilancia")
        c = Tarjeta()
        c.add_widget(self._lbl("Analiza automáticamente mientras escribes o pegas.",
                               size_hint_y=None, height="30dp", color=MUTED))
        self.btn_vig = boton("▶️ Activar vigilancia", lambda *_: self.toggle_vig())
        c.add_widget(self.btn_vig)
        self.est_vig = self._lbl("[color=#94a3b8]Vigilancia desactivada.[/color]",
                                 size_hint_y=None, height="26dp")
        c.add_widget(self.est_vig)
        self.vig = entrada("Escribe o pega aquí. Se analiza solo...", height="130dp")
        self.vig.bind(text=lambda *_: self._vig_teclea())
        c.add_widget(self.vig)
        self.res4 = self._lbl("", size_hint_y=1, font_size="18sp")
        c.add_widget(self.res4)
        c.add_widget(self._lbl("[color=#94a3b8]⚠️ Por seguridad, una app no puede leer mensajes de "
                               "otras apps sin permisos especiales del sistema.[/color]",
                               size_hint_y=None, height="50dp"))
        t.add_widget(c)
        return t

    def toggle_vig(self):
        self.vigilando = not self.vigilando
        if self.vigilando:
            self.btn_vig.text = "⏸️ Desactivar vigilancia"
            self.est_vig.text = "[color=#22c55e]🟢 Vigilancia ACTIVA: analizando mientras escribes.[/color]"
        else:
            self.btn_vig.text = "▶️ Activar vigilancia"
            self.est_vig.text = "[color=#94a3b8]Vigilancia desactivada.[/color]"
            self.res4.text = ""

    def _vig_teclea(self):
        if not self.vigilando:
            return
        if self._vig_ev:
            self._vig_ev.cancel()
        self._vig_ev = Clock.schedule_once(lambda dt: self._vig_analiza(), 0.25)

    def _vig_analiza(self):
        txt = self.vig.text.strip()
        if not txt:
            self.res4.text = ""
            return
        r = clasificar(txt)
        agg = r["etiqueta"] == "agresivo"
        col = "ef4444" if agg else "22c55e"
        titulo = "🚨 AGRESIVO" if agg else "✅ SEGURO"
        self.res4.text = (f"[size=22sp][color=#{col}][b]{titulo}[/b][/color][/size]  "
                          f"[color=#94a3b8]riesgo {r['confianza']}%[/color]")


if __name__ == "__main__":
    AntiAcosoApp().run()
