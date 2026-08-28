# Com usar `calculs_textils.py`

Guia d'ús detallada. Cobreix les tres maneres d'usar el mòdul: **CLI** (línia de
comandes, sense escriure Python), **entorn gràfic** i com a **mòdul** importable
des d'altres scripts.

## Requisits

- Python 3.8 o superior.
- Cap dependència externa (només `math`, `re`, `argparse` de la biblioteca estàndard).

## Posar-la en marxa

Des de l'arrel del repositori (o de la carpeta `scripts/`):

```bash
python calculs_textils.py test        # comprova que tot funciona (demo + autotests)
python calculs_textils.py -h          # llista de subcomandes
python calculs_textils.py pes -h      # ajuda d'una subcomanda concreta
```

A Windows, si `python` no funciona, prova `py calculs_textils.py test`.

## Entorn gràfic (finestra)

Per no escriure comandes: posa `calculs_textils_gui.py` a la mateixa carpeta que
`calculs_textils.py` i obre'l amb doble clic (o `python calculs_textils_gui.py`).
Té una pestanya per càlcul (Títol, Diàmetre, Pes, Encongiment, Tupidesa, Màxim, Pua),
amb desplegables per a matèria, tipus i lligament, i els botons **Calcula** i
**Copiar resultat** (copia el text del resultat al porta-retalls). No cal instal·lar res: Tkinter ve amb el Python
oficial de Windows.

---

## Ús per CLI

Estructura general:

```
python calculs_textils.py SUBCOMANDA [opcions]
```

**Els títols de fil que porten `/` o espais van SEMPRE entre cometes**: `'Ne 30/2c'`, `'2/50 Nm'`.
La matèria per defecte és **polièster**; canvia-la amb `--materia`. Passa-la sempre
explícitament: entra al diàmetre i a la tupidesa.

### Subcomandes

| Subcomanda  | Què fa                                              |
|-------------|-----------------------------------------------------|
| `titol`     | Converteix un títol entre Nm, Ne, dTex, den         |
| `diametre`  | Diàmetre del fil (mm)                               |
| `pes`       | Pes teòric del teixit (g/m² i g/metre lineal)       |
| `encongiment` | Encongiment teòric d'ordit i trama (%)            |
| `tupidesa`  | Grau de tupidesa (Galcerán) + cobertura geomètrica  |
| `maxim`     | Densitat màxima de fils i passades + marge          |
| `pua`       | Espai lliure a la pua de la pinta (%)               |
| `test`      | Demo i autotests                                    |

### 1. Conversió de títol

```bash
python calculs_textils.py titol 'Ne 30/2c'
```

Convenció de plegat: **Ne** s'escriu `base/caps` (`Ne 30/2c` = 2 caps de Ne 30);
**Nm** s'escriu `caps/base` (`2/50 Nm` = 2 caps de Nm 50). El títol resultant i el
Tex total ja tenen en compte els caps.

### 2. Diàmetre del fil

```bash
python calculs_textils.py diametre 'Ne 30' --materia cotó --tipus anelles
```

### 3. Pes teòric del teixit

```bash
python calculs_textils.py pes --ordit '167 dtex' --trama '167 dtex' \
       --fils 40 --passades 22 --lligament sarja_2_2 --ample 1.8
```

- `--fils` = fils/cm (ordit); `--passades` = passades/cm (trama).
- `--ample` (m) és opcional; si el poses, també calcula g/metre lineal.
- Si tens l'encongiment **mesurat**, passa'l amb `--encongiment-ordit` i
  `--encongiment-trama` (%) i deixa de ser teòric. Molt recomanable (vegeu *Limitacions*).

### 4. Encongiment teòric

```bash
python calculs_textils.py encongiment --ordit 'Ne 30' --trama 'Ne 30' \
       --fils 24 --passades 20 --lligament tafeta --materia cotó
```

### 5. Tupidesa

```bash
python calculs_textils.py tupidesa --ordit 'Ne 30' --trama 'Ne 30' \
       --fils 24 --passades 20 --lligament tafeta
```

Dona el **grau de tupidesa de Galcerán** (% respecte de la densitat màxima) i la
**cobertura geomètrica de Peirce** (% d'àrea coberta).

### 6. Densitat màxima (passades i fils màxims)

```bash
python calculs_textils.py maxim --ordit 'Nm 50' --trama 'Nm 50' \
       --lligament tafeta --passades 28 --factor 0.92
```

- Dona `MÀX passades/cm` i `MÀX fils/cm` segons Galcerán.
- Si poses `--passades` i/o `--fils` actuals, calcula el **% del màxim** i el **marge** restant.
- `--factor` (0,90–0,95 típic) baixa del màxim teòric al realment teixible segons teler.

### 7. Espai lliure a la pua

```bash
python calculs_textils.py pua --fil 'Ne 30' --fils-pua 2 --pues 12
```

- `--fil` (títol) calcula la d automàticament; o passa la d directa amb `--d 0.165`.
- Amplada de pua: es calcula com `10/pues − gruix_làmina`, o dona-la directa amb `--ample-pua`.
- Avisa si el marge és escàs (<15%) o si els fils no hi caben.

---

## Ús com a mòdul Python

Per integrar-ho en altres scripts (KPIs, planificació, escandalls…):

```python
from calculs_textils import (
    converteix_titol, diametre_fil, pes_teixit, encongiment_teoric,
    tupidesa_galceran, cobertura_geometrica, densitat_maxima,
    espai_pua, coef_lligadura, obté_lligament, sarga, seti,
)

# Conversió
converteix_titol("Ne 30/2c")     # {'Nm':25.4,'Ne':15.0,'dTex':393.7,'den':354.3,...}

# Pes (amb encongiment mesurat si el tens)
pes_teixit("167 dtex", "167 dtex", fils_cm=40, passades_cm=22,
           lligament="sarja_2_2", amplada_m=1.8, materia_ordit="polièster",
           encongiment_ordit_pct=4.5, encongiment_trama_pct=2.0)

# Passades màximes amb marge sobre l'actual
densitat_maxima(nm_ordit=50, nm_trama=50, lligament="tafeta",
                materia_ordit="polièster", factor_practic=0.92, passades_cm=28)
```

Totes les funcions retornen un `dict`. Els títols poden anar amb notació de plegat
(`"Ne 30/2c"`, `"2/50 Nm"`) i el mòdul ja aplica els caps.

### Lligaments

Noms predefinits: `tafeta`/`pla`, `sarja_2_2`, `sarja_2_1`, `sarja_3_1`,
`sarja_1_3`, `seti_5`, `seti_8`. També pots:

```python
obté_lligament("sarja_2_2")      # matriu predefinida
sarja(3, 1)                       # sarja 3/1 generada
seti(5, 2)                        # setí de 5, moviment 2
coef_lligadura(M)                 # -> (Kl_ordit, Kl_trama)
```

O passar una **matriu 0/1** teva (1 = ordit per sobre) a qualsevol funció que
accepti `lligament`.

---

## Referència ràpida de paràmetres

**Matèries** (`--materia`): cotó, polièster, poliamida/niló, llana, viscosa/raió,
lli, seda, acrílic, polipropilè, elastà, vidre, aramida.

**Tipus de fil** (`--tipus`): `fibra_tallada`, `anelles` (contínua d'anelles),
`open_end`, `filament_continu`, `texturat`, `retorçat`.

Tots els valors de densitat de fibra i factor d'empaquetament són sobreescriptibles
passant `rho_fibra=` i `phi=` a `diametre_fil()`.

---

## Limitacions (important)

- **L'encongiment teòric és una estimació** (model de Peirce amb hipòtesi h=D/2).
  El valor real depèn de la tensió d'ordit/trama al teler i de l'acabat. **Usa el
  valor mesurat quan el tinguis.** El pes hereta aquesta incertesa.
- En teixits molt densos en una direcció, la hipòtesi h=D/2 no resol l'encongiment: el
  resultat surt amb un **avís explícit** (no un 0 amagat). Aquí el valor mesurat és imprescindible.
- Les fórmules geomètriques suposen **secció circular** del fil; els fils reals
  s'aplanen, així que tupidesa i cobertura reals solen ser una mica més altes.
- La **densitat màxima** de Galcerán es va deduir per a **fil a un cap**; amb retorçats
  s'usa el Nm resultant i és aproximat. Ajusta amb `--factor`.
- **"Palleta" = pua/dent de la pinta** en aquest mòdul.

## Provinença de les dades

- Conversions: definicions d'unitat (`Tex=1000/Nm`, `dTex=10·Tex`, `den=9·Tex`, `Ne=590,5/Tex`).
- Diàmetre: `d(mm)=0,03568·√(Tex/ρ_fil)`, validat contra Peirce per al cotó.
- Densitats de fibra i factors d'empaquetament: valors bibliogràfics típics.
- Tupidesa i densitat màxima de Galcerán: constants Q i coeficients de lligadura Kl
  de V. Galcerán Escobet, via la tesi de la UPC d'I. Algaba (cap. 8, taules 8.2 i 8.3).
