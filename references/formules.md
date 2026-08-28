# Fórmules, constants i limitacions

Aquest document recull la base de càlcul de `scripts/calculs_textils.py`: d'on
surt cada fórmula, quines constants s'han tabulat i què no es pot esperar dels
resultats.

## Provinença

Les fórmules són de bibliografia tèxtil clàssica publicada (Peirce, Galcerán) i
de les definicions d'unitat dels sistemes de numeració de fils. Les constants
tabulades s'han transcrit de les fonts citades a cada secció. **No hi ha cap
constant ajustada empíricament ni cap dada de producció.**

Cap valor no ha estat validat contra mesures independents pels autors d'aquest
mòdul. Si en trobes cap de desviat, obre una incidència amb les teves dades
mesurades.

## Conversions de títol

Definicions d'unitat:

```
Tex  = 1000 / Nm
dTex = 10 · Tex
den  = 9 · Tex
Ne   = 590.5 / Tex
Nm   = 1.6934 · Ne
```

La constant 590.5 surt de la definició de la numeració anglesa de cotó
(840 iardes per lliura = 768.096 m / 453.592 g).

## Diàmetre del fil

```
d(mm) = 0.03568 · √(Tex / ρ_fil)          amb  ρ_fil = ρ_fibra · φ
```

La constant es valida contra l'expressió de Peirce per al cotó:
`d(inch) = 1 / (28 · √Ne)`.

**Densitats de fibra** (g/cm³, valors típics):

| Fibra | ρ | Fibra | ρ |
|---|---|---|---|
| cotó | 1.54 | seda | 1.34 |
| polièster | 1.38 | acrílic | 1.18 |
| poliamida | 1.14 | polipropilè | 0.91 |
| llana | 1.31 | vidre | 2.55 |
| viscosa | 1.52 | | |

**Factors d'empaquetament φ** (típics): fibra tallada / anelles 0.60,
open-end 0.48, filament continu 0.65, texturat 0.40, retorçat 0.55.

## Pes del teixit

Per sistema (ordit, trama):

```
massa (g/m²) = dens(fils/cm) · 0.1 · (1 + encongiment) · Tex_total
```

El pes total és la suma d'ordit i trama. `g/ml = g/m² · amplada(m)`.

## Encongiment teòric

Model de Peirce amb alçada d'ona `h = D/2`, on `D = d₁ + d₂`. Es resol

```
h = p · tanθ − D · (secθ − 1)
c = l/p − 1
```

i s'escala pel coeficient de lligadura `Kl` del lligament.

## Cobertura geomètrica (Peirce)

```
cob      = n · d                       (per sistema)
cob_total = cob_o + cob_t − cob_o · cob_t
```

## Tupidesa de Galcerán

Font: V. Galcerán Escobet, *Tecnología del tejido*. Les constants s'han pres de
la reproducció d'aquestes taules a la tesi doctoral d'I. Algaba (UPC),
capítol 8, taules 8.2 i 8.3.

```
Kd          = (fils/cm) / √Nm
Kdm,ordit   = Q / (1 + 0.73 · Kl,trama)
Kdm,trama   = Q / (1 + 0.73 · Kl,ordit)
Tupidesa(%) = 100 · Kd,total / Kdm,total
```

**Constants Q per matèria** (taula 8.2): viscosa / raió / lli 10.0, cotó 9.8,
polièster 9.6, llana / acetat 9.5, seda 9.2, acrílic 8.9, poliamida / niló 8.8.

**Coeficients Kl per lligament** (taula 8.3): tafetà 1, sarja 3 → 0.666,
sarja 4 → 0.5, sarja 5 → 0.4, sarja 6 → 0.333.

100 % correspon a la densitat màxima teòrica amb fil a un cap.

## Densitat màxima

Mateix marc de Galcerán:

```
max_fils/cm     = Kdm,ordit · √Nm_ordit · factor_practic
max_passades/cm = Kdm,trama · √Nm_trama · factor_practic
```

`factor_practic` (0.90–0.95 típic) baixa del màxim teòric *jammed* al màxim
realment teixible segons teler i acabat. `factor_practic = 1.0` dona el màxim
teòric pur.

## Espai lliure a la pua

`espai_pua` calcula quin percentatge de l'amplada de la pua queda lliure un cop
hi passen els fils previstos.

---

## Limitacions (llegir abans d'usar cap resultat)

- **L'encongiment teòric és una estimació.** No queda determinat només pel lligament,
  els títols i les densitats: depèn de la **tensió d'ordit i de trama al teler**
  (intercanvi d'encongiment) i de l'acabat. Error possible de diversos punts. Usa el
  valor mesurat sempre que el tinguis (`encongiment_*_pct` a `pes_teixit`). **El pes
  calculat hereta aquesta incertesa.**

- Totes les fórmules geomètriques suposen **secció circular regular** del fil.
  Els fils reals s'aplanen i tenen vellositat, de manera que la tupidesa i la
  cobertura reals solen ser més altes que les teòriques. El mateix Galcerán ho
  adverteix.

- **Diàmetre de fil retorçat**: la funció retorna el cilindre equivalent de
  massa total. L'envolupant real del retort és més gran (aproximadament entre
  ×√caps i ×caps segons la torsió).

- **Densitat màxima**: les constants Q de Galcerán es van deduir per a **fil a
  un cap**. Amb retorçats s'aplica el Nm resultant, però és una aproximació.
  Ajusta amb `factor_practic` per acostar-te al màxim real del teu teler.

- **"Palleta" s'interpreta com la pua (dent) de la pinta.** Si al teu taller el
  terme designa una altra cosa, revisa `espai_pua` abans de fer-lo servir.

- Els resultats són **de disseny i verificació prèvia**, no substitueixen una
  mostra teixida i mesurada.
