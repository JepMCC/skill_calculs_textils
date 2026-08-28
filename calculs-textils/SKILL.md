---
name: calculs-textils
description: "Càlculs tèxtils per a teixits de calada: conversió de títol de fil (Nm, Ne, dTex, den), pes teòric del teixit (g/m² i g/metre lineal), encongiment teòric d'ordit i trama, tupidesa (cobertura geomètrica de Peirce i grau de tupidesa de Galcerán), diàmetre del fil segons títol/matèria/tipus, i percentatge d'espai lliure a la pua de la pinta. DISPARADORS: 'converteix Nm/Ne/dtex/den', 'títol de fil', 'quants grams pesa aquest teixit', 'pes per metre', 'g/m2', 'crimp', 'encongiment d'ordit/trama', 'tupidesa', 'cobertura', 'Galcerán', 'diàmetre del fil', 'quant ocupa el fil a la pua', 'espai a la palleta/pinta'. Usa aquesta skill sempre que la pregunta impliqui números de fil, densitats de fils/passades, lligaments, pes de teixit o geometria de fil/pinta."
license: MIT
---

# Càlculs tèxtils

Càlculs habituals de disseny i verificació de teixits de calada, implementats a
`scripts/calculs_textils.py`. Executa'l amb Python; totes les funcions retornen `dict`.

> **Els resultats són teòrics.** Abans de fer-los servir per a res que costi
> diners, llegeix `references/formules.md` § Limitacions: l'encongiment estimat pot
> desviar-se diversos punts del real i el pes n'hereta l'error.

## Quan usar-la

Sempre que aparegui títol de fil, densitat de fils/passades, lligament, pes de
teixit, o geometria fil/pinta. **No** per a preguntes conceptuals sense números.

## Convenció de plegat (IMPORTANT)

- **Ne**: `base/caps` → `Ne 30/2c` = 2 caps de Ne 30 (resultant Ne 15).
- **Nm**: `caps/base` → `2/50 Nm` = 2 caps de Nm 50 (resultant Nm 25).
- **tex/dtex/den**: `base/caps`.

Als sistemes indirectes (Nm, Ne) el títol resultant = base/caps; als directes
(tex, dtex, den) = base·caps. La **massa lineal total** (Tex) sempre és la suma
dels caps — és el que fan servir el pes i el diàmetre.

## Mode CLI (recomanat)

Executa el mòdul directament des de la carpeta de la skill. Els títols amb `/`
o espais van entre cometes.

```bash
python scripts/calculs_textils.py titol 'Ne 30/2c'
python scripts/calculs_textils.py diametre 'Ne 30' --materia cotó --tipus anelles
python scripts/calculs_textils.py pes --ordit '167 dtex' --trama '167 dtex' \
       --fils 40 --passades 22 --lligament sarja_2_2 --ample 1.8
python scripts/calculs_textils.py maxim --ordit 'Nm 50' --trama 'Nm 50' \
       --lligament tafeta --passades 28 --factor 0.92     # màx passades + marge
python scripts/calculs_textils.py tupidesa --ordit 'Ne 30' --trama 'Ne 30' --fils 24 --passades 20
python scripts/calculs_textils.py pua --fil 'Ne 30' --fils-pua 2 --pues 12
python scripts/calculs_textils.py test        # demo + autotests
```

Subcomandes: `titol`, `diametre`, `pes`, `encongiment`, `tupidesa`, `maxim`, `pua`, `test`.
`python scripts/calculs_textils.py -h` (o `<subcomanda> -h`) mostra totes les opcions.

**Matèria per defecte al CLI: `polièster`.** Passa `--materia` explícitament
sempre que treballis amb una altra fibra — la matèria entra al diàmetre (densitat
de fibra) i a la tupidesa (constant Q), i deixar-la per defecte per descuit dona
resultats silenciosament equivocats.

## Mode Python

El mòdul no està instal·lat com a paquet: afegeix `scripts/` al path.

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "scripts"))

from calculs_textils import (
    converteix_titol, diametre_fil, pes_teixit, encongiment_teoric,
    tupidesa_galceran, cobertura_geometrica, densitat_maxima, espai_pua,
    coef_lligadura, obté_lligament,
)

# 1. Conversió de títol
converteix_titol("Ne 30/2c")          # -> {'Nm':25.4,'Ne':15.0,'dTex':393.7,'den':354.3,...}

# 5. Diàmetre (mm)
diametre_fil(titol="Ne 30", materia="cotó", tipus="anelles")
# tipus: fibra_tallada | anelles | open_end | filament_continu | texturat | retorçat

# 2+3. Pes teòric (g/m² i g/ml) — estima l'encongiment si no el dones
pes_teixit("Ne 30", "Ne 30", fils_cm=24, passades_cm=20,
           lligament="tafeta", amplada_m=1.6, materia_ordit="cotó",
           encongiment_ordit_pct=None, encongiment_trama_pct=None)   # posa els mesurats si els tens

# 3. Encongiment teòric sol
encongiment_teoric(fils_cm=24, passades_cm=20, d_ordit_mm=0.165, d_trama_mm=0.165, lligament="tafeta")

# 4. Tupidesa
tupidesa_galceran(nm_ordit=25.4, nm_trama=25.4, fils_cm=24, passades_cm=20,
                  lligament="tafeta", materia_ordit="cotó")
cobertura_geometrica(fils_cm=24, passades_cm=20, d_ordit_mm=0.165, d_trama_mm=0.165)

# 4b. Densitat MÀXIMA de fils i passades (Galcerán) + marge sobre l'actual
densitat_maxima(nm_ordit=50, nm_trama=50, lligament="tafeta", materia_ordit="polièster",
                factor_practic=0.92, fils_cm=None, passades_cm=28)   # factor 1.0 = màxim teòric

# 6. Espai lliure a la pua ("palleta")
espai_pua(d_fil_mm=0.165, fils_per_pua=2, pues_cm=12)      # o amplada_pua_mm=...
```

## Lligaments

Noms predefinits: `tafeta`/`pla`, `sarja_2_2`, `sarja_2_1`, `sarja_3_1`,
`sarja_1_3`, `seti_5`, `seti_8`. També pots passar una **matriu 0/1**
(1 = ordit per sobre) directament, o generar-la amb `sarja(a,b)` / `seti(R,mov)`.
`coef_lligadura(M)` retorna `(Kl_ordit, Kl_trama)`.

Guia d'ús ampliada (totes les opcions de cada subcomanda, entorn gràfic):
`references/com-usar.md`.

## Fórmules, constants i limitacions

Totes les fórmules, les constants tabulades (densitats de fibra, factors
d'empaquetament, constants Q i Kl de Galcerán) i les limitacions conegudes de
cada càlcul són a **`references/formules.md`**. Consulta'l abans d'interpretar
un resultat com a definitiu o d'estendre el mòdul.
