#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calculs_textils_gui.py — Entorn gràfic (Tkinter) per a calculs_textils.py

Ús: posa aquest fitxer a la MATEIXA carpeta que calculs_textils.py i executa'l
amb doble clic o amb:  python calculs_textils_gui.py
No cal instal·lar res (Tkinter ve amb Python).
"""

import tkinter as tk
from tkinter import ttk, font

import calculs_textils as ct

MATERIES = ["polièster", "cotó", "poliamida", "niló", "llana", "viscosa", "raió",
            "lli", "seda", "acrílic", "polipropilè", "elastà", "vidre", "aramida"]
TIPUS = list(ct.EMPAQUETAMENT)
LLIGAMENTS = list(ct.LLIGAMENTS)


# ---- helpers de conversió des dels camps de text --------------------------

def _f(s):
    s = (s or "").strip().replace(",", ".")
    return float(s) if s else None

def _i(s):
    s = (s or "").strip()
    return int(s) if s else None


# ---- pestanya genèrica ----------------------------------------------------

class Pestanya(ttk.Frame):
    """Construeix un formulari a partir d'una llista de camps i un callback."""

    def __init__(self, parent, camps, calcula, ajuda=""):
        super().__init__(parent, padding=12)
        self.calcula = calcula
        self.widgets = {}

        if ajuda:
            ttk.Label(self, text=ajuda, foreground="#555",
                      wraplength=560).grid(row=0, column=0, columnspan=2,
                                           sticky="w", pady=(0, 8))

        r = 1
        for camp in camps:
            ttk.Label(self, text=camp["label"]).grid(row=r, column=0, sticky="e",
                                                     padx=(0, 8), pady=3)
            if camp.get("tipus") == "combo":
                w = ttk.Combobox(self, values=camp["opcions"], state="readonly", width=24)
                w.set(camp.get("def", camp["opcions"][0]))
            else:
                w = ttk.Entry(self, width=26)
                if camp.get("def") is not None:
                    w.insert(0, str(camp["def"]))
            w.grid(row=r, column=1, sticky="w", pady=3)
            self.widgets[camp["key"]] = w
            r += 1

        barra = ttk.Frame(self)
        barra.grid(row=r, column=0, columnspan=2, pady=(10, 8))
        ttk.Button(barra, text="Calcula", command=self._run).pack(side="left", padx=4)
        ttk.Button(barra, text="Copiar resultat", command=self._copia).pack(side="left", padx=4)
        r += 1

        self.resultat = tk.Text(self, width=64, height=13, wrap="word",
                                relief="solid", borderwidth=1)
        self.resultat.grid(row=r, column=0, columnspan=2, sticky="nsew")
        self.resultat.configure(state="disabled")
        mono = font.nametofont("TkFixedFont")
        self.resultat.configure(font=mono)
        self.resultat.tag_configure("titol", font=(mono.actual("family"), 10, "bold"))
        self.resultat.tag_configure("avis", foreground="#b00")
        self.resultat.tag_configure("error", foreground="#b00",
                                    font=(mono.actual("family"), 10, "bold"))

    def _vals(self):
        return {k: (w.get()) for k, w in self.widgets.items()}

    def _copia(self):
        txt = self.resultat.get("1.0", "end").strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)

    def _run(self):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        try:
            titol, files, avis = self.calcula(self._vals())
            self.resultat.insert("end", titol + "\n", "titol")
            self.resultat.insert("end", "─" * len(titol) + "\n")
            for etiqueta, valor in files:
                if valor is None:
                    continue
                self.resultat.insert("end", f"  {etiqueta:<26} {valor}\n")
            if avis:
                self.resultat.insert("end", f"\n⚠ {avis}\n", "avis")
        except Exception as e:  # noqa: BLE001
            self.resultat.insert("end", f"Error: {e}", "error")
        self.resultat.configure(state="disabled")


# ---- callbacks de càlcul (retornen: titol, [(etiqueta, valor)...], avis) --

def calc_titol(v):
    c = ct.converteix_titol(v["titol"]); i = c["_info"]
    files = [("Nm", c["Nm"]), ("Ne", c["Ne"]), ("dTex", c["dTex"]), ("den", c["den"]),
             ("Caps", i["caps"]), ("Tex per cap", round(i["tex_cap"], 2)),
             ("Tex total (amb caps)", round(i["tex_total"], 2)),
             ("Títol resultant", f"{round(i['titol_resultant'],3)} {i['sistema'].capitalize()}")]
    return f"Títol: {v['titol']}", files, None


def calc_diametre(v):
    r = ct.diametre_fil(titol=v["titol"], materia=v["materia"], tipus=v["tipus"])
    files = [("Diàmetre", f"{r['d_mm']} mm"), ("Tex total", r["tex_total"]),
             ("ρ fibra", f"{r['rho_fibra']} g/cm³"), ("φ empaquetament", r["phi"]),
             ("ρ fil efectiva", f"{r['rho_fil']} g/cm³")]
    return f"Diàmetre · {v['titol']} · {r['materia']} · {r['tipus']}", files, None


def calc_pes(v):
    r = ct.pes_teixit(v["ordit"], v["trama"], _f(v["fils"]), _f(v["passades"]),
                      lligament=v["lligament"], amplada_m=_f(v["ample"]),
                      materia_ordit=v["materia"], tipus_ordit=v["tipus"],
                      encongiment_ordit_pct=_f(v["encongiment_ordit"]),
                      encongiment_trama_pct=_f(v["encongiment_trama"]))
    files = [("PES", f"{r['g_m2']} g/m²"),
             ("Pes per metre lineal", f"{r.get('g_metre_lineal','—')} g/ml"),
             ("massa ordit", f"{r['massa_ordit_g_m2']} g/m²"),
             ("massa trama", f"{r['massa_trama_g_m2']} g/m²"),
             ("encongiment ordit", f"{r['encongiment_ordit_pct']} %"),
             ("encongiment trama", f"{r['encongiment_trama_pct']} %"),
             ("origen de l'encongiment", r["encongiment_origen"]),
             ("d ordit / trama", f"{r['d_ordit_mm']} / {r['d_trama_mm']} mm")]
    avis = r.get("avis")
    if r["encongiment_origen"].startswith("estimat") and not avis:
        avis = "Encongiment estimat (teòric). Omple els camps de mesurat si el tens."
    return f"Pes teòric · {v['ordit']} × {v['trama']}", files, avis


def calc_encongiment(v):
    do = ct.diametre_fil(titol=v["ordit"], materia=v["materia"], tipus=v["tipus"])["d_mm"]
    dt = ct.diametre_fil(titol=v["trama"], materia=v["materia"], tipus=v["tipus"])["d_mm"]
    r = ct.encongiment_teoric(_f(v["fils"]), _f(v["passades"]), do, dt, v["lligament"])
    files = [("Encongiment ordit", f"{r['encongiment_ordit_pct']} %"),
             ("Encongiment trama", f"{r['encongiment_trama_pct']} %"),
             ("Kl ordit / trama", f"{r['Kl_ordit']} / {r['Kl_trama']}"),
             ("d ordit / trama", f"{do} / {dt} mm")]
    avis = r.get("avis") or "Estimació geomètrica (Peirce h=D/2 × Kl). El valor mesurat mana."
    return f"Encongiment teòric · {v['lligament']}", files, avis


def calc_tupidesa(v):
    nm_o = ct.converteix_titol(v["ordit"])["Nm"]
    nm_t = ct.converteix_titol(v["trama"])["Nm"]
    g = ct.tupidesa_galceran(nm_o, nm_t, _f(v["fils"]), _f(v["passades"]),
                             v["lligament"], v["materia"])
    do = ct.diametre_fil(titol=v["ordit"], materia=v["materia"], tipus=v["tipus"])["d_mm"]
    dt = ct.diametre_fil(titol=v["trama"], materia=v["materia"], tipus=v["tipus"])["d_mm"]
    cg = ct.cobertura_geometrica(_f(v["fils"]), _f(v["passades"]), do, dt)
    files = [("Grau de tupidesa (Galcerán)", f"{g['tupidesa_galceran_pct']} %"),
             ("Cobertura geomètrica (Peirce)", f"{cg['cobertura_total_pct']} %"),
             ("  cobertura ordit / trama", f"{cg['cobertura_ordit_pct']} / {cg['cobertura_trama_pct']} %"),
             ("Kd / Kdm (Galcerán)", f"{g['Kd_total']} / {g['Kdm_total']}"),
             ("Kl ordit / trama", f"{g['Kl_ordit']} / {g['Kl_trama']}")]
    return f"Tupidesa · {v['ordit']} × {v['trama']} · {v['lligament']}", files, None


def calc_maxim(v):
    nm_o = ct.converteix_titol(v["ordit"])["Nm"]
    nm_t = ct.converteix_titol(v["trama"])["Nm"]
    r = ct.densitat_maxima(nm_o, nm_t, v["lligament"], v["materia"],
                           factor_practic=_f(v["factor"]) or 1.0,
                           fils_cm=_f(v["fils"]), passades_cm=_f(v["passades"]))
    files = [("MÀX passades/cm", r["max_passades_cm"]),
             ("MÀX fils/cm", r["max_fils_cm"]),
             ("passades actuals (% màx)", f"{v['passades']} → {r.get('passades_pct_del_maxim','—')} %"
              if v["passades"].strip() else None),
             ("marge de passades", f"{r.get('marge_passades_cm','—')} /cm" if v["passades"].strip() else None),
             ("fils actuals (% màx)", f"{v['fils']} → {r.get('fils_pct_del_maxim','—')} %"
              if v["fils"].strip() else None),
             ("marge de fils", f"{r.get('marge_fils_cm','—')} /cm" if v["fils"].strip() else None),
             ("Kdm ordit / trama", f"{r['Kdm_ordit']} / {r['Kdm_trama']}")]
    return f"Densitat màxima · {v['lligament']} · factor {v['factor']}", files, \
        "Màxim de Galcerán per a fil a un cap; amb retorçats és aproximat."


def calc_pua(v):
    d = _f(v["d"])
    if d is None:
        d = ct.diametre_fil(titol=v["fil"], materia=v["materia"], tipus=v["tipus"])["d_mm"]
    r = ct.espai_pua(d_fil_mm=d, fils_per_pua=_i(v["fils_pua"]),
                     amplada_pua_mm=_f(v["ample_pua"]), pues_cm=_f(v["pues"]),
                     gruix_lamina_mm=_f(v["gruix_lamina"]) or 0.0)
    files = [("Amplada de pua", f"{r['amplada_pua_mm']} mm"),
             ("Ocupat pels fils", f"{r['ocupat_mm']} mm ({r['ocupacio_pct']} %)"),
             ("ESPAI LLIURE", f"{r['espai_lliure_mm']} mm ({r['espai_lliure_pct']} %)")]
    return f"Espai a la pua · d={d} mm · {v['fils_pua']} fils/pua", files, r.get("avis")


# ---- muntatge de la finestra ---------------------------------------------

def main():
    arrel = tk.Tk()
    arrel.title("Càlculs tèxtils")
    arrel.geometry("640x560")
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass

    nb = ttk.Notebook(arrel)
    nb.pack(fill="both", expand=True, padx=8, pady=8)

    mat = {"key": "materia", "label": "Matèria", "tipus": "combo", "opcions": MATERIES, "def": "polièster"}
    tip = {"key": "tipus", "label": "Tipus de fil", "tipus": "combo", "opcions": TIPUS, "def": "anelles"}
    llig = {"key": "lligament", "label": "Lligament", "tipus": "combo", "opcions": LLIGAMENTS, "def": "tafeta"}

    pestanyes = [
        ("Títol", [
            {"key": "titol", "label": "Títol de fil", "def": "Ne 30/2c"},
        ], calc_titol, "Ne: base/caps (Ne 30/2c). Nm: caps/base (2/50 Nm)."),

        ("Diàmetre", [
            {"key": "titol", "label": "Títol de fil", "def": "Ne 30"}, mat, tip,
        ], calc_diametre, ""),

        ("Pes", [
            {"key": "ordit", "label": "Títol ordit", "def": "167 dtex"},
            {"key": "trama", "label": "Títol trama", "def": "167 dtex"},
            {"key": "fils", "label": "Fils/cm (ordit)", "def": "24"},
            {"key": "passades", "label": "Passades/cm (trama)", "def": "20"},
            llig, {"key": "ample", "label": "Amplada (m) — opcional", "def": "1.6"},
            mat, tip,
            {"key": "encongiment_ordit", "label": "Encongiment ordit % (mesurat)", "def": ""},
            {"key": "encongiment_trama", "label": "Encongiment trama % (mesurat)", "def": ""},
        ], calc_pes, "Deixa l'encongiment buit per estimar-lo; omple'l si el tens mesurat."),

        ("Encongiment", [
            {"key": "ordit", "label": "Títol ordit", "def": "Ne 30"},
            {"key": "trama", "label": "Títol trama", "def": "Ne 30"},
            {"key": "fils", "label": "Fils/cm", "def": "24"},
            {"key": "passades", "label": "Passades/cm", "def": "20"},
            llig, mat, tip,
        ], calc_encongiment, ""),

        ("Tupidesa", [
            {"key": "ordit", "label": "Títol ordit", "def": "Ne 30"},
            {"key": "trama", "label": "Títol trama", "def": "Ne 30"},
            {"key": "fils", "label": "Fils/cm", "def": "24"},
            {"key": "passades", "label": "Passades/cm", "def": "20"},
            llig, mat, tip,
        ], calc_tupidesa, ""),

        ("Màxim", [
            {"key": "ordit", "label": "Títol ordit", "def": "Nm 50"},
            {"key": "trama", "label": "Títol trama", "def": "Nm 50"},
            llig,
            {"key": "factor", "label": "Factor pràctic (0.90–0.95)", "def": "0.92"},
            {"key": "fils", "label": "Fils/cm actuals — opcional", "def": ""},
            {"key": "passades", "label": "Passades/cm actuals — opcional", "def": "28"},
            mat,
        ], calc_maxim, "Densitat màxima teixible + marge sobre l'actual."),

        ("Pua", [
            {"key": "fil", "label": "Títol de fil", "def": "Ne 30"},
            {"key": "d", "label": "o diàmetre directe (mm)", "def": ""},
            {"key": "fils_pua", "label": "Fils per pua", "def": "2"},
            {"key": "pues", "label": "Pues/cm", "def": "12"},
            {"key": "ample_pua", "label": "o amplada pua (mm)", "def": ""},
            {"key": "gruix_lamina", "label": "Gruix làmina (mm)", "def": "0"},
            mat, tip,
        ], calc_pua, "Espai lliure a la pua/dent de la pinta."),
    ]

    for nom, camps, cb, ajuda in pestanyes:
        nb.add(Pestanya(nb, camps, cb, ajuda), text=nom)

    arrel.mainloop()


if __name__ == "__main__":
    main()
