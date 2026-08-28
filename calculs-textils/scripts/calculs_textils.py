#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calculs_textils.py — Càlculs tèxtils per a teixits de calada

Funcionalitats:
  1. Conversió de títol de fil entre Nm, Ne, dTex, den (i Tex intern).
  2. Pes teòric d'un teixit (g/m² i g/metre lineal).
  3. Encongiment teòric d'ordit i trama (Peirce, hipòtesi h1=h2=D/2).
  4. Tupidesa: cobertura geomètrica (Peirce) + grau de tupidesa de Galcerán.
  5. Diàmetre del fil segons títol, matèria i tipus de fil.
  6. Percentatge d'espai lliure en una pua/palleta de la pinta.

PROVINENÇA DE LES DADES (valors de bibliografia publicada, no validats
empíricament pels autors d'aquest mòdul — vegeu references/formules.md):
  - Conversions: derivades de definicions d'unitats.
        Tex = 1000/Nm ; dTex = 10·Tex ; den = 9·Tex ; Ne = 590.5/Tex
        (590.5 ve de: 1 fideu Ne = 840 yd / lliura = 768.096 m / 453.592 g).
        Nm = 1.6934·Ne.
  - Densitats de fibra (g/cm³): valors típics de bibliografia (veure FIBRES).
  - Factors d'empaquetament: valors típics per sistema de filatura (veure EMPAQUETAMENT).
  - Constant diàmetre 0.03568: d(mm)=0.03568·√(Tex/ρ_fil). Es valida contra
        la constant de Peirce per al cotó d(inch)=1/(28·√Ne).
  - Galcerán (grau de tupidesa): constants Q i coeficients de lligadura Kl
        segons V. Galcerán Escobet, via tesi UPC d'I. Algaba (cap. 8, taules 8.2 i 8.3).
        Kdm,ordit = Q/(1+0.73·Kl,trama) ; Kdm,trama = Q/(1+0.73·Kl,ordit).
        Cobertura(%) = (Kd,total / Kdm,total)·100 ; Kd = (fils/cm)/√Nm.
"""

import math
import re

# ---------------------------------------------------------------------------
# TAULES DE DADES (valors típics — sobreescriptibles pels arguments)
# ---------------------------------------------------------------------------

# Densitat de fibra en g/cm³ (valors bibliogràfics típics)
FIBRES = {
    "cotó":          1.54,
    "polièster":     1.38,
    "poliamida":     1.14,   # niló
    "niló":          1.14,
    "llana":         1.31,
    "viscosa":       1.52,
    "raió":          1.52,
    "lli":           1.50,
    "seda":          1.34,
    "acrílic":       1.18,
    "polipropilè":   0.91,
    "elastà":        1.10,
    "vidre":         2.55,
    "aramida":       1.44,
}

# Factor d'empaquetament φ (fracció de la secció ocupada per fibra).
# Valors típics per sistema de filatura. ρ_fil = ρ_fibra · φ.
EMPAQUETAMENT = {
    "fibra_tallada":     0.60,   # filat clàssic de fibra curta
    "anelles":           0.60,   # contínua d'anelles (ring)
    "open_end":          0.48,   # rotor / OE (més voluminós)
    "filament_continu":  0.65,   # multifilament pla
    "texturat":          0.40,   # filament texturat/voluminós
    "retorçat":          0.55,   # fil retorçat (envolupant real més gran; veure nota)
}

# Constants Q de Galcerán per matèria (taula 8.2, Algaba/UPC citant Galcerán)
GALCERAN_Q = {
    "viscosa":     10.0, "raió": 10.0, "lli": 10.0, "cupro": 10.0,
    "cotó":         9.8,
    "polièster":    9.6,   # Tergal/Teriber/Rhovyl
    "llana":        9.5, "acetat": 9.5,
    "seda":         9.2,
    "acrílic":      8.9,   # Acrilan
    "poliamida":    8.8, "niló": 8.8,   # Nylon/Perlon/Orlon
}

DIAMETRE_CONST = 0.03568   # d(mm) = DIAMETRE_CONST · √(Tex / ρ_fil)

# ---------------------------------------------------------------------------
# 1. TÍTOL DE FIL: parseig i conversions
# ---------------------------------------------------------------------------

SISTEMES_INDIRECTES = {"nm", "ne"}          # més alt = més fi
SISTEMES_DIRECTES   = {"tex", "dtex", "den"}  # més alt = més gruixut


def _to_tex(sistema, valor):
    """Títol simple -> Tex (g/1000 m)."""
    s = sistema.lower()
    if s == "nm":   return 1000.0 / valor
    if s == "ne":   return 590.5 / valor
    if s == "tex":  return valor
    if s == "dtex": return valor / 10.0
    if s == "den":  return valor / 9.0
    raise ValueError(f"Sistema desconegut: {sistema}")


def _from_tex(sistema, tex):
    """Tex -> títol en el sistema demanat."""
    s = sistema.lower()
    if s == "nm":   return 1000.0 / tex
    if s == "ne":   return 590.5 / tex
    if s == "tex":  return tex
    if s == "dtex": return tex * 10.0
    if s == "den":  return tex * 9.0
    raise ValueError(f"Sistema desconegut: {sistema}")


def parse_titol(text):
    """
    Interpreta una cadena de títol i retorna un dict amb tota la info.

    Convenció de plegat (segons l'usuari):
      - Ne:  base/caps   ->  'Ne 30/2c' = 2 caps de Ne 30
      - Nm:  caps/base   ->  '2/50 Nm'  = 2 caps de Nm 50
      - tex/dtex/den:     base/caps (p. ex. '167 dtex /2' = 2 caps de 167 dtex)

    Sistemes indirectes (Nm, Ne): títol resultant = base / caps.
    Sistemes directes (tex, dtex, den): títol resultant = base · caps.
    """
    t = text.strip().lower().replace("den ", "den").replace("denier", "den")
    # sistema
    m_sis = re.search(r"(nm|ne|dtex|tex|den)", t)
    if not m_sis:
        raise ValueError(f"No s'ha trobat cap sistema (Nm/Ne/dTex/den/tex) a: {text!r}")
    sistema = m_sis.group(1)
    # números (poden ser 'a/b')
    nums = re.findall(r"\d+(?:[.,]\d+)?", t.replace(",", "."))
    nums = [float(x) for x in nums]
    if not nums:
        raise ValueError(f"No s'ha trobat cap número a: {text!r}")

    caps = 1
    if "/" in t and len(nums) >= 2:
        a, b = nums[0], nums[1]
        if sistema == "nm":          # caps/base
            caps, base = int(round(a)), b
        else:                        # Ne, tex, dtex, den -> base/caps
            base, caps = a, int(round(b))
    else:
        base = nums[0]

    if sistema in SISTEMES_INDIRECTES:
        titol_result = base / caps
    else:
        titol_result = base * caps

    tex_simple = _to_tex(sistema, base)
    tex_total  = tex_simple * caps    # massa lineal total (sempre suma de caps)

    return {
        "text": text,
        "sistema": sistema,
        "base": base,
        "caps": caps,
        "titol_resultant": titol_result,   # en el sistema d'origen
        "tex_cap": tex_simple,
        "tex_total": tex_total,
    }


def converteix_titol(text, a=("Nm", "Ne", "dTex", "den", "Tex")):
    """
    Converteix un títol (amb plegat) a tots els sistemes demanats.
    Retorna el títol RESULTANT del fil sencer (tenint en compte els caps).
    """
    info = parse_titol(text)
    tex_total = info["tex_total"]
    sortida = {sis: round(_from_tex(sis, tex_total), 4) for sis in a}
    sortida["_info"] = info
    return sortida


# ---------------------------------------------------------------------------
# 5. DIÀMETRE DEL FIL
# ---------------------------------------------------------------------------

def diametre_fil(titol=None, tex=None, materia="cotó", tipus="anelles",
                 phi=None, rho_fibra=None):
    """
    Diàmetre teòric del fil en mm.

        d(mm) = 0.03568 · √( Tex_total / ρ_fil )      ρ_fil = ρ_fibra · φ

    Paràmetres:
      titol : cadena de títol (p.ex. 'Ne 30/2c'); s'usa el Tex TOTAL (amb caps).
      tex   : alternativament, Tex total directe.
      materia : clau de FIBRES (o passa rho_fibra).
      tipus   : clau d'EMPAQUETAMENT (o passa phi).
    Retorna dict amb d_mm, i les hipòtesis usades.

    NOTA fil retorçat: aquesta d és la del cilindre equivalent de massa total.
    El diàmetre ENVOLUPANT real d'un retorçat és més gran (~×√caps a ×caps).
    Per a càlculs de pinta/cobertura pot convenir el diàmetre envolupant.
    """
    if tex is None:
        if titol is None:
            raise ValueError("Cal 'titol' o 'tex'.")
        tex = parse_titol(titol)["tex_total"]

    if rho_fibra is None:
        if materia.lower() not in FIBRES:
            raise ValueError(f"Matèria desconeguda: {materia}. Opcions: {list(FIBRES)}")
        rho_fibra = FIBRES[materia.lower()]
    if phi is None:
        if tipus.lower() not in EMPAQUETAMENT:
            raise ValueError(f"Tipus desconegut: {tipus}. Opcions: {list(EMPAQUETAMENT)}")
        phi = EMPAQUETAMENT[tipus.lower()]

    rho_fil = rho_fibra * phi
    d_mm = DIAMETRE_CONST * math.sqrt(tex / rho_fil)
    return {
        "d_mm": round(d_mm, 4),
        "tex_total": round(tex, 3),
        "materia": materia, "rho_fibra": rho_fibra,
        "tipus": tipus, "phi": phi, "rho_fil": round(rho_fil, 4),
    }


# ---------------------------------------------------------------------------
# LLIGAMENTS: matriu, generadors i comptatge de punts de contacte
# ---------------------------------------------------------------------------

def teixit_pla():
    return [[1, 0], [0, 1]]


def sarja(salt_amunt, salt_avall, direccio=1):
    """Sarja genèrica salt_amunt/salt_avall (p.ex. 2/2, 3/1). Repeticio R=suma."""
    R = salt_amunt + salt_avall
    fila0 = [1] * salt_amunt + [0] * salt_avall
    return [[fila0[(c - direccio * f) % R] for c in range(R)] for f in range(R)]


def seti(R, contra=1, base=0, cara="trama"):
    """
    Setí de R fils. cara='trama' (satí) o 'ordit'.
    contra = número de moviment (ha de ser primer amb R i != 1, R-1).
    """
    M = [[0] * R for _ in range(R)]
    for f in range(R):
        c = (base + contra * f) % R
        M[f][c] = 1
    if cara == "trama":
        # per defecte 1 basta per fila = satí cara-trama; invertim per cara-ordit
        return M
    return [[1 - x for x in fila] for fila in M]


def _transicions_columna(M):
    """Punts de contacte comptats en direcció ORDIT (per columnes, cíclic)."""
    files = len(M); cols = len(M[0])
    total = 0
    for c in range(cols):
        col = [M[f][c] for f in range(files)]
        total += sum(1 for i in range(files) if col[i] != col[(i + 1) % files])
    return total


def _transicions_fila(M):
    """Punts de contacte comptats en direcció TRAMA (per files, cíclic)."""
    files = len(M); cols = len(M[0])
    total = 0
    for f in range(files):
        fila = M[f]
        total += sum(1 for i in range(cols) if fila[i] != fila[(i + 1) % cols])
    return total


def coef_lligadura(M):
    """
    Coeficients de lligadura de Galcerán per a un lligament (matriu 0/1).
        Kl = punts_de_contacte / (nombre_fils · nombre_passades)   [en el repòs]
    Retorna (Kl_ordit, Kl_trama). Per al tafetà = (1, 1).
    """
    files = len(M); cols = len(M[0])
    area = files * cols
    Kl_ordit = _transicions_columna(M) / area
    Kl_trama = _transicions_fila(M) / area
    return round(Kl_ordit, 4), round(Kl_trama, 4)


LLIGAMENTS = {
    "tafeta": teixit_pla,
    "pla": teixit_pla,
    "sarja_2_2": lambda: sarja(2, 2),
    "sarja_2_1": lambda: sarja(2, 1),
    "sarja_3_1": lambda: sarja(3, 1),
    "sarja_1_3": lambda: sarja(1, 3),
    "seti_5": lambda: seti(5, 2),
    "seti_8": lambda: seti(8, 3),
}


def obté_lligament(x):
    """Accepta una matriu, o un nom de LLIGAMENTS."""
    if isinstance(x, str):
        clau = x.lower().replace("/", "_").replace(" ", "_").replace("-", "_")
        if clau in LLIGAMENTS:
            return LLIGAMENTS[clau]()
        raise ValueError(f"Lligament desconegut: {x}. Opcions: {list(LLIGAMENTS)}")
    return x


# ---------------------------------------------------------------------------
# 3. ENCONGIMENT TEÒRIC — Peirce, hipòtesi h1=h2=D/2
# ---------------------------------------------------------------------------

def _encongiment_peirce(p2_mm, D_mm):
    """
    Encongiment d'un fil segons geometria de Peirce amb alçada d'ona h = D/2.
    p2_mm = separació dels fils perpendiculars (pas), D_mm = d1+d2.
    Resol  h = p2·tanθ − D·(secθ−1)  amb h=D/2, després c = l/p2 − 1.
    Retorna la fracció d'encongiment (0.05 = 5%). None si no hi ha solució física.
    """
    if p2_mm <= 0 or D_mm <= 0:
        return 0.0
    h = D_mm / 2.0

    def f(theta):
        return p2_mm * math.tan(theta) - D_mm * (1.0 / math.cos(theta) - 1.0) - h

    lo, hi = 1e-6, 1.4  # θ en (0, ~80°)
    if f(hi) < 0:
        return None  # teixit massa atapeït per a aquesta hipòtesi
    for _ in range(80):  # bisecció
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    theta = 0.5 * (lo + hi)
    l = (p2_mm - D_mm * math.sin(theta)) / math.cos(theta) + D_mm * theta
    return max(0.0, l / p2_mm - 1.0)


def encongiment_teoric(fils_cm, passades_cm, d_ordit_mm, d_trama_mm, lligament="tafeta"):
    """
    Encongiment teòric d'ordit i trama (%).

    Model: Peirce amb alçada d'ona simètrica (h1=h2=D/2) sobre teixit pla,
    escalat pel coeficient de lligadura del lligament (Kl). Aproximació.

    ATENCIÓ: l'encongiment real depèn de la tensió d'ordit/trama al teler
    (intercanvi d'encongiment) i de l'acabat. Aquest valor és una ESTIMACIÓ
    de primer ordre; per a producció, usa sempre el valor MESURAT.
    """
    M = obté_lligament(lligament)
    Kl_o, Kl_t = coef_lligadura(M)
    D = d_ordit_mm + d_trama_mm

    p_trama = 10.0 / passades_cm   # pas entre passades (mm) -> afecta encongiment d'ordit
    p_ordit = 10.0 / fils_cm       # pas entre fils (mm)     -> afecta encongiment de trama

    c_ordit_pla = _encongiment_peirce(p_trama, D)
    c_trama_pla = _encongiment_peirce(p_ordit, D)

    avis = None
    if c_ordit_pla is None or c_trama_pla is None:
        avis = "Teixit massa dens per a la hipòtesi h=D/2; encongiment no resolt geomètricament."
        c_ordit_pla = c_ordit_pla or 0.0
        c_trama_pla = c_trama_pla or 0.0

    # escalat per freqüència de lligament (tafetà Kl=1)
    c_ordit = c_ordit_pla * Kl_o
    c_trama = c_trama_pla * Kl_t

    return {
        "encongiment_ordit_pct": round(c_ordit * 100, 2),
        "encongiment_trama_pct": round(c_trama * 100, 2),
        "Kl_ordit": Kl_o, "Kl_trama": Kl_t,
        "avis": avis,
        "nota": "Estimació geomètrica (Peirce h=D/2 × Kl). El valor mesurat mana.",
    }


# ---------------------------------------------------------------------------
# 2. PES TEÒRIC DEL TEIXIT
# ---------------------------------------------------------------------------

def pes_teixit(titol_ordit, titol_trama, fils_cm, passades_cm,
               lligament="tafeta", amplada_m=None,
               materia_ordit="cotó", materia_trama=None,
               tipus_ordit="anelles", tipus_trama=None,
               encongiment_ordit_pct=None, encongiment_trama_pct=None,
               crimp_ordit_pct=None, crimp_trama_pct=None):
    """
    Pes teòric del teixit en g/m² i (si es dona amplada) g/metre lineal.

    Massa_ordit (g/m²) = (fils/cm)·0.1·(1+c_ordit)·Tex_ordit
    Massa_trama (g/m²) = (passades/cm)·0.1·(1+c_trama)·Tex_trama

    Els Tex són TOTALS (tenint en compte els caps del plegat).
    Si no es donen encongiment_*_pct, s'estimen amb encongiment_teoric()
    (aproximat). Els arguments crimp_*_pct s'accepten com a àlies antic.
    """
    if encongiment_ordit_pct is None:
        encongiment_ordit_pct = crimp_ordit_pct
    if encongiment_trama_pct is None:
        encongiment_trama_pct = crimp_trama_pct
    io = parse_titol(titol_ordit)
    it = parse_titol(titol_trama)
    tex_o, tex_t = io["tex_total"], it["tex_total"]

    materia_trama = materia_trama or materia_ordit
    tipus_trama = tipus_trama or tipus_ordit

    do = diametre_fil(tex=tex_o, materia=materia_ordit, tipus=tipus_ordit)["d_mm"]
    dt = diametre_fil(tex=tex_t, materia=materia_trama, tipus=tipus_trama)["d_mm"]

    est = encongiment_teoric(fils_cm, passades_cm, do, dt, lligament)
    c_o = (encongiment_ordit_pct if encongiment_ordit_pct is not None
           else est["encongiment_ordit_pct"]) / 100.0
    c_t = (encongiment_trama_pct if encongiment_trama_pct is not None
           else est["encongiment_trama_pct"]) / 100.0

    massa_ordit = fils_cm * 0.1 * (1 + c_o) * tex_o
    massa_trama = passades_cm * 0.1 * (1 + c_t) * tex_t
    gm2 = massa_ordit + massa_trama

    res = {
        "g_m2": round(gm2, 1),
        "massa_ordit_g_m2": round(massa_ordit, 1),
        "massa_trama_g_m2": round(massa_trama, 1),
        "encongiment_ordit_pct": round(c_o * 100, 2),
        "encongiment_trama_pct": round(c_t * 100, 2),
        "encongiment_origen": "mesurat" if encongiment_ordit_pct is not None else "estimat (teòric)",
        "d_ordit_mm": do, "d_trama_mm": dt,
        "avis": est["avis"] if encongiment_ordit_pct is None else None,
    }
    # àlies retrocompatibles (nomenclatura antiga 'crimp'); es retiraran més endavant
    res["crimp_ordit_pct"] = res["encongiment_ordit_pct"]
    res["crimp_trama_pct"] = res["encongiment_trama_pct"]
    res["crimp_origen"] = res["encongiment_origen"]
    if amplada_m:
        res["g_metre_lineal"] = round(gm2 * amplada_m, 1)
        res["amplada_m"] = amplada_m
    return res


# ---------------------------------------------------------------------------
# 4. TUPIDESA
# ---------------------------------------------------------------------------

def cobertura_geometrica(fils_cm, passades_cm, d_ordit_mm, d_trama_mm):
    """
    Cobertura geomètrica (Peirce): fracció d'àrea coberta pels fils.
        cob_ordit = (fils/cm)·(d_ordit_cm)   ; cob_trama = (passades/cm)·(d_trama_cm)
        cobertura_total = cob_o + cob_t − cob_o·cob_t   (evita doble compte)
    Retorna percentatges.
    """
    cob_o = fils_cm * (d_ordit_mm / 10.0)
    cob_t = passades_cm * (d_trama_mm / 10.0)
    total = cob_o + cob_t - cob_o * cob_t
    return {
        "cobertura_ordit_pct": round(cob_o * 100, 1),
        "cobertura_trama_pct": round(cob_t * 100, 1),
        "cobertura_total_pct": round(total * 100, 1),
    }


def tupidesa_galceran(nm_ordit, nm_trama, fils_cm, passades_cm,
                      lligament="tafeta", materia_ordit="cotó", materia_trama=None):
    """
    Grau de tupidesa de Galcerán (% respecte de la densitat màxima teòrica).

        Kd,ordit = (fils/cm)/√Nm_ordit ;  Kd,trama = (passades/cm)/√Nm_trama
        Kd,total = Kd,ordit + Kd,trama
        Kdm,ordit = Q_ordit/(1 + 0.73·Kl,trama)
        Kdm,trama = Q_trama/(1 + 0.73·Kl,ordit)
        Tupidesa(%) = 100 · Kd,total / (Kdm,ordit + Kdm,trama)

    Nm han de ser els RESULTANTS (amb els caps ja aplicats).
    100% = densitat màxima (teixit "encavalcat"/jammed segons Galcerán).
    """
    materia_trama = materia_trama or materia_ordit
    Qo = GALCERAN_Q.get(materia_ordit.lower())
    Qt = GALCERAN_Q.get(materia_trama.lower())
    if Qo is None or Qt is None:
        raise ValueError(f"Sense Q de Galcerán per a {materia_ordit}/{materia_trama}. "
                         f"Opcions: {list(GALCERAN_Q)}")

    M = obté_lligament(lligament)
    Kl_o, Kl_t = coef_lligadura(M)

    Kd_o = fils_cm / math.sqrt(nm_ordit)
    Kd_t = passades_cm / math.sqrt(nm_trama)
    Kd_total = Kd_o + Kd_t

    Kdm_o = Qo / (1 + 0.73 * Kl_t)
    Kdm_t = Qt / (1 + 0.73 * Kl_o)
    Kdm_total = Kdm_o + Kdm_t

    tup = 100.0 * Kd_total / Kdm_total
    return {
        "tupidesa_galceran_pct": round(tup, 1),
        "Kd_total": round(Kd_total, 3),
        "Kdm_total": round(Kdm_total, 3),
        "Kl_ordit": Kl_o, "Kl_trama": Kl_t,
        "Q_ordit": Qo, "Q_trama": Qt,
        "interpretacio": "100% = densitat màxima teòrica de Galcerán (fil a un cap).",
    }


def densitat_maxima(nm_ordit, nm_trama, lligament="tafeta",
                    materia_ordit="cotó", materia_trama=None, factor_practic=1.0,
                    fils_cm=None, passades_cm=None):
    """
    Densitat màxima de fils i passades segons Galcerán (fil a un cap).

        Kdm,ordit = Q_ordit/(1 + 0.73·Kl,trama)
        Kdm,trama = Q_trama/(1 + 0.73·Kl,ordit)
        max_fils/cm     = Kdm,ordit · √Nm_ordit · factor_practic
        max_passades/cm = Kdm,trama · √Nm_trama · factor_practic

    factor_practic : ajust del màxim teòric al pràctic (típic 0.90–0.95 segons
                     teler i acabat; 1.0 = màxim teòric jammed).
    Si es donen fils_cm / passades_cm actuals, retorna el marge restant.

    ATENCIÓ: les constants Q de Galcerán es van deduir per a FILS A UN CAP.
    Amb fils retorçats s'usa el Nm resultant, però el resultat és aproximat.
    """
    materia_trama = materia_trama or materia_ordit
    Qo = GALCERAN_Q.get(materia_ordit.lower())
    Qt = GALCERAN_Q.get(materia_trama.lower())
    if Qo is None or Qt is None:
        raise ValueError(f"Sense Q de Galcerán per a {materia_ordit}/{materia_trama}. "
                         f"Opcions: {list(GALCERAN_Q)}")

    M = obté_lligament(lligament)
    Kl_o, Kl_t = coef_lligadura(M)
    Kdm_o = Qo / (1 + 0.73 * Kl_t)
    Kdm_t = Qt / (1 + 0.73 * Kl_o)

    max_fils = Kdm_o * math.sqrt(nm_ordit) * factor_practic
    max_pass = Kdm_t * math.sqrt(nm_trama) * factor_practic

    res = {
        "max_fils_cm": round(max_fils, 1),
        "max_passades_cm": round(max_pass, 1),
        "Kdm_ordit": round(Kdm_o, 3), "Kdm_trama": round(Kdm_t, 3),
        "Kl_ordit": Kl_o, "Kl_trama": Kl_t,
        "Q_ordit": Qo, "Q_trama": Qt,
        "factor_practic": factor_practic,
        "nota": "Màxim de Galcerán (fil a un cap). factor_practic<1 per al màxim real.",
    }
    if fils_cm is not None:
        res["fils_pct_del_maxim"] = round(100 * fils_cm / max_fils, 1)
        res["marge_fils_cm"] = round(max_fils - fils_cm, 1)
    if passades_cm is not None:
        res["passades_pct_del_maxim"] = round(100 * passades_cm / max_pass, 1)
        res["marge_passades_cm"] = round(max_pass - passades_cm, 1)
    return res


# ---------------------------------------------------------------------------
# 6. ESPAI LLIURE A LA PUA/PALLETA DE LA PINTA
# ---------------------------------------------------------------------------

def espai_pua(d_fil_mm, fils_per_pua, amplada_pua_mm=None,
              pues_cm=None, gruix_lamina_mm=0.0):
    """
    Percentatge d'espai lliure ("que sobra") a la pua de la pinta.

    ocupat = fils_per_pua · d_fil_mm
    lliure_% = (amplada_pua − ocupat) / amplada_pua · 100

    amplada_pua_mm : amplada útil de la pua (mm). Si no es dona, es calcula com
                     10/pues_cm − gruix_lamina_mm.
    NOTA: "palleta" s'interpreta com la pua/dent de la pinta (el pas del fil).
    """
    if amplada_pua_mm is None:
        if pues_cm is None:
            raise ValueError("Cal 'amplada_pua_mm' o 'pues_cm'.")
        amplada_pua_mm = 10.0 / pues_cm - gruix_lamina_mm
    if amplada_pua_mm <= 0:
        raise ValueError("Amplada de pua ≤ 0.")

    ocupat = fils_per_pua * d_fil_mm
    lliure = amplada_pua_mm - ocupat
    lliure_pct = lliure / amplada_pua_mm * 100.0

    avis = None
    if lliure_pct < 0:
        avis = "Sobrepassat: els fils no hi caben (>100% ocupat)."
    elif lliure_pct < 15:
        avis = "Marge escàs (<15%): risc de frec/fils trencats a la pinta."

    return {
        "amplada_pua_mm": round(amplada_pua_mm, 4),
        "ocupat_mm": round(ocupat, 4),
        "espai_lliure_mm": round(lliure, 4),
        "espai_lliure_pct": round(lliure_pct, 1),
        "ocupacio_pct": round(100 - lliure_pct, 1),
        "avis": avis,
    }


# ---------------------------------------------------------------------------
# CLI — mode línia de comandes (per usar sense escriure Python)
# ---------------------------------------------------------------------------

DEF_MATERIA = "polièster"   # per defecte; passa --materia sempre que sigui una altra fibra


def _p(titol, files):
    """Imprimeix un bloc de resultats amb capçalera."""
    print(f"\n{titol}")
    print("-" * len(titol))
    for etiqueta, valor in files:
        if valor is None:
            continue
        print(f"  {etiqueta:<28} {valor}")


def _d_de_titol(titol, materia, tipus):
    return diametre_fil(titol=titol, materia=materia, tipus=tipus)["d_mm"]


def _cli():
    import argparse

    ep = ("Exemples:\n"
          "  python calculs_textils.py titol 'Ne 30/2c'\n"
          "  python calculs_textils.py diametre 'Ne 30' --materia cotó --tipus anelles\n"
          "  python calculs_textils.py pes --ordit '167 dtex' --trama '167 dtex' "
          "--fils 40 --passades 22 --lligament sarja_2_2 --ample 1.8\n"
          "  python calculs_textils.py maxim --ordit 'Nm 50' --trama 'Nm 50' "
          "--lligament tafeta --passades 28 --factor 0.92\n"
          "  python calculs_textils.py tupidesa --ordit 'Ne 30' --trama 'Ne 30' --fils 24 --passades 20\n"
          "  python calculs_textils.py pua --fil 'Ne 30' --fils-pua 2 --pues 12\n"
          "  python calculs_textils.py test")
    p = argparse.ArgumentParser(
        prog="calculs_textils", description="Càlculs tèxtils per a teixits de calada",
        epilog=ep, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_mat(sp, trama=False):
        sp.add_argument("--materia", default=DEF_MATERIA,
                        help=f"matèria (def. {DEF_MATERIA}). Opcions: {list(FIBRES)}")
        sp.add_argument("--tipus", default="anelles",
                        help=f"tipus de fil (def. anelles). Opcions: {list(EMPAQUETAMENT)}")
        if trama:
            sp.add_argument("--materia-trama", default=None, help="matèria de trama si difereix")
            sp.add_argument("--tipus-trama", default=None, help="tipus de trama si difereix")

    a = sub.add_parser("titol", help="Converteix un títol de fil (Nm/Ne/dTex/den)")
    a.add_argument("titol")

    a = sub.add_parser("diametre", help="Diàmetre del fil (mm)")
    a.add_argument("titol"); add_mat(a)

    a = sub.add_parser("pes", help="Pes teòric del teixit (g/m² i g/ml)")
    a.add_argument("--ordit", required=True); a.add_argument("--trama", required=True)
    a.add_argument("--fils", type=float, required=True, help="fils/cm (ordit)")
    a.add_argument("--passades", type=float, required=True, help="passades/cm (trama)")
    a.add_argument("--lligament", default="tafeta")
    a.add_argument("--ample", type=float, default=None, help="amplada (m) per a g/ml")
    a.add_argument("--encongiment-ordit", "--crimp-ordit", type=float, default=None,
                   dest="encongiment_ordit", help="encongiment d'ordit %% MESURAT")
    a.add_argument("--encongiment-trama", "--crimp-trama", type=float, default=None,
                   dest="encongiment_trama", help="encongiment de trama %% MESURAT")
    add_mat(a, trama=True)

    a = sub.add_parser("encongiment", aliases=["crimp"],
                       help="Encongiment teòric d'ordit i trama (%)")
    a.add_argument("--ordit", required=True); a.add_argument("--trama", required=True)
    a.add_argument("--fils", type=float, required=True)
    a.add_argument("--passades", type=float, required=True)
    a.add_argument("--lligament", default="tafeta"); add_mat(a, trama=True)

    a = sub.add_parser("tupidesa", help="Tupidesa: Galcerán + cobertura geomètrica")
    a.add_argument("--ordit", required=True); a.add_argument("--trama", required=True)
    a.add_argument("--fils", type=float, required=True)
    a.add_argument("--passades", type=float, required=True)
    a.add_argument("--lligament", default="tafeta"); add_mat(a, trama=True)

    a = sub.add_parser("maxim", help="Densitat màxima de fils i passades (Galcerán)")
    a.add_argument("--ordit", required=True); a.add_argument("--trama", required=True)
    a.add_argument("--lligament", default="tafeta")
    a.add_argument("--fils", type=float, default=None, help="fils/cm actuals (marge)")
    a.add_argument("--passades", type=float, default=None, help="passades/cm actuals (marge)")
    a.add_argument("--factor", type=float, default=1.0, help="factor pràctic (0.90–0.95 típic)")
    add_mat(a, trama=True)

    a = sub.add_parser("pua", help="Espai lliure a la pua de la pinta")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--d", type=float, help="diàmetre del fil (mm) directe")
    g.add_argument("--fil", help="títol del fil (calcula la d)")
    a.add_argument("--fils-pua", type=int, required=True, help="fils per pua")
    a.add_argument("--pues", type=float, default=None, help="pues/cm")
    a.add_argument("--ample-pua", type=float, default=None, help="amplada de pua (mm) directa")
    a.add_argument("--gruix-lamina", type=float, default=0.0, help="gruix de làmina (mm)")
    add_mat(a)

    sub.add_parser("test", help="Executa la demo i els autotests")
    args = p.parse_args()

    if args.cmd == "titol":
        c = converteix_titol(args.titol); i = c["_info"]
        _p(f"Títol: {args.titol}", [
            ("Nm", c["Nm"]), ("Ne", c["Ne"]), ("dTex", c["dTex"]), ("den", c["den"]),
            ("Caps", i["caps"]), ("Tex per cap", round(i["tex_cap"], 2)),
            ("Tex total (amb caps)", round(i["tex_total"], 2)),
            ("Títol resultant", f"{round(i['titol_resultant'],3)} {i['sistema'].capitalize()}"),
        ])

    elif args.cmd == "diametre":
        r = diametre_fil(titol=args.titol, materia=args.materia, tipus=args.tipus)
        _p(f"Diàmetre: {args.titol} · {r['materia']} · {r['tipus']}", [
            ("Diàmetre", f"{r['d_mm']} mm"), ("Tex total", r["tex_total"]),
            ("ρ fibra", f"{r['rho_fibra']} g/cm³"), ("φ empaquetament", r["phi"]),
            ("ρ fil efectiva", f"{r['rho_fil']} g/cm³"),
        ])

    elif args.cmd == "pes":
        r = pes_teixit(args.ordit, args.trama, args.fils, args.passades,
                       lligament=args.lligament, amplada_m=args.ample,
                       materia_ordit=args.materia, materia_trama=args.materia_trama,
                       tipus_ordit=args.tipus, tipus_trama=args.tipus_trama,
                       encongiment_ordit_pct=args.encongiment_ordit,
                       encongiment_trama_pct=args.encongiment_trama)
        _p(f"Pes teòric · {args.ordit} × {args.trama} · {args.fils}×{args.passades} f/cm · {args.lligament}", [
            ("PES", f"{r['g_m2']} g/m²"),
            ("Pes per metre lineal", f"{r.get('g_metre_lineal','—')} g/ml"
             + (f" (ample {r['amplada_m']} m)" if 'amplada_m' in r else "")),
            ("  massa ordit", f"{r['massa_ordit_g_m2']} g/m²"),
            ("  massa trama", f"{r['massa_trama_g_m2']} g/m²"),
            ("encongiment ordit", f"{r['encongiment_ordit_pct']} %"),
            ("encongiment trama", f"{r['encongiment_trama_pct']} %"),
            ("origen de l'encongiment", r["encongiment_origen"]),
            ("d ordit / trama", f"{r['d_ordit_mm']} / {r['d_trama_mm']} mm"),
            ("avís", r.get("avis")),
        ])
        if r["encongiment_origen"].startswith("estimat"):
            print("  ⚠  Encongiment ESTIMAT (teòric). Si el tens mesurat, passa'l amb"
                  " --encongiment-ordit/--encongiment-trama.")

    elif args.cmd in ("encongiment", "crimp"):
        do = _d_de_titol(args.ordit, args.materia, args.tipus)
        dt = _d_de_titol(args.trama, args.materia_trama or args.materia, args.tipus_trama or args.tipus)
        r = encongiment_teoric(args.fils, args.passades, do, dt, args.lligament)
        _p(f"Encongiment teòric · {args.fils}×{args.passades} f/cm · {args.lligament}", [
            ("Encongiment ordit", f"{r['encongiment_ordit_pct']} %"),
            ("Encongiment trama", f"{r['encongiment_trama_pct']} %"),
            ("Kl ordit / trama", f"{r['Kl_ordit']} / {r['Kl_trama']}"),
            ("d ordit / trama", f"{do} / {dt} mm"),
            ("avís", r["avis"]),
        ])
        print("  ⚠  Estimació geomètrica (Peirce h=D/2 × Kl). El valor mesurat mana.")

    elif args.cmd == "tupidesa":
        nm_o = converteix_titol(args.ordit)["Nm"]
        nm_t = converteix_titol(args.trama)["Nm"]
        g = tupidesa_galceran(nm_o, nm_t, args.fils, args.passades, args.lligament,
                              args.materia, args.materia_trama)
        do = _d_de_titol(args.ordit, args.materia, args.tipus)
        dt = _d_de_titol(args.trama, args.materia_trama or args.materia, args.tipus_trama or args.tipus)
        cg = cobertura_geometrica(args.fils, args.passades, do, dt)
        _p(f"Tupidesa · {args.ordit} × {args.trama} · {args.fils}×{args.passades} f/cm · {args.lligament}", [
            ("Grau de tupidesa (Galcerán)", f"{g['tupidesa_galceran_pct']} %"),
            ("Cobertura geomètrica (Peirce)", f"{cg['cobertura_total_pct']} %"),
            ("  cobertura ordit / trama", f"{cg['cobertura_ordit_pct']} / {cg['cobertura_trama_pct']} %"),
            ("Kd / Kdm (Galcerán)", f"{g['Kd_total']} / {g['Kdm_total']}"),
            ("Kl ordit / trama", f"{g['Kl_ordit']} / {g['Kl_trama']}"),
        ])

    elif args.cmd == "maxim":
        nm_o = converteix_titol(args.ordit)["Nm"]
        nm_t = converteix_titol(args.trama)["Nm"]
        r = densitat_maxima(nm_o, nm_t, args.lligament, args.materia, args.materia_trama,
                            factor_practic=args.factor, fils_cm=args.fils, passades_cm=args.passades)
        _p(f"Densitat màxima (Galcerán) · {args.ordit} × {args.trama} · {args.lligament} · factor {args.factor}", [
            ("MÀX passades/cm", r["max_passades_cm"]),
            ("MÀX fils/cm", r["max_fils_cm"]),
            ("passades actuals (% del màx)", f"{args.passades} ({r.get('passades_pct_del_maxim','—')} %)"
             if args.passades else None),
            ("marge de passades", f"{r.get('marge_passades_cm','—')} /cm" if args.passades else None),
            ("fils actuals (% del màx)", f"{args.fils} ({r.get('fils_pct_del_maxim','—')} %)"
             if args.fils else None),
            ("marge de fils", f"{r.get('marge_fils_cm','—')} /cm" if args.fils else None),
            ("Kdm ordit / trama", f"{r['Kdm_ordit']} / {r['Kdm_trama']}"),
            ("Kl ordit / trama", f"{r['Kl_ordit']} / {r['Kl_trama']}"),
        ])
        print("  ⚠  Màxim de Galcerán deduït per a FIL A UN CAP; amb retorçats és aproximat.")

    elif args.cmd == "pua":
        d = args.d if args.d is not None else _d_de_titol(args.fil, args.materia, args.tipus)
        r = espai_pua(d_fil_mm=d, fils_per_pua=args.fils_pua, amplada_pua_mm=args.ample_pua,
                      pues_cm=args.pues, gruix_lamina_mm=args.gruix_lamina)
        _p(f"Espai a la pua · d={d} mm · {args.fils_pua} fils/pua", [
            ("Amplada de pua", f"{r['amplada_pua_mm']} mm"),
            ("Ocupat pels fils", f"{r['ocupat_mm']} mm ({r['ocupacio_pct']} %)"),
            ("ESPAI LLIURE", f"{r['espai_lliure_mm']} mm ({r['espai_lliure_pct']} %)"),
            ("avís", r["avis"]),
        ])

    elif args.cmd == "test":
        _autotest()


def _autotest():
    print("=== Demo ===")
    for t in ["Ne 30/2c", "2/50 Nm", "167 dtex", "Nm 50", "150 den"]:
        c = converteix_titol(t)
        print(f"  {t:12s} -> Nm {c['Nm']}, Ne {c['Ne']}, dTex {c['dTex']}, den {c['den']}")
    d = diametre_fil(titol="Ne 30", materia="cotó", tipus="anelles")["d_mm"]
    print(f"  Ne30 cotó anelles: d = {d} mm (ref. Peirce ≈ 0.166)")
    print(f"  Pes: {pes_teixit('Ne 30','Ne 30',24,20,'tafeta',1.6,'cotó')['g_m2']} g/m²")
    nm = converteix_titol("Ne 30")["Nm"]
    print(f"  Tupidesa Galcerán: {tupidesa_galceran(nm,nm,24,20,'tafeta','cotó')['tupidesa_galceran_pct']} %")
    print(f"  Màx passades/cm: {densitat_maxima(nm,nm,'tafeta','cotó')['max_passades_cm']}")
    assert abs(converteix_titol("Nm 50")["Ne"] - 50 / 1.6934) < 0.05
    assert abs(converteix_titol("Ne 30/2c")["Nm"] - (1.6934 * 15)) < 0.5
    assert converteix_titol("2/50 Nm")["_info"]["titol_resultant"] == 25.0
    assert 0.16 < diametre_fil(titol="Ne 30", materia="cotó")["d_mm"] < 0.17
    assert densitat_maxima(nm, nm, "tafeta", "cotó")["max_passades_cm"] > 20
    print("OK — autotests passats.")


if __name__ == "__main__":
    _cli()
