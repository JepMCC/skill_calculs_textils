# calculs-textils

Skill per a Claude (format [SKILL.md](https://agentskills.io)) amb els càlculs
habituals de disseny i verificació de **teixits de calada**: conversió de títols
de fil, pes teòric, encongiment, tupidesa, diàmetre de fil i espai a la
pinta.

Funciona també com a mòdul Python i com a eina de línia de comandes
independentment de Claude.

## Què calcula

| Càlcul | Funció / subcomanda |
|---|---|
| Conversió de títol (Nm, Ne, tex, dTex, den), amb caps | `converteix_titol` / `titol` |
| Diàmetre del fil segons títol, matèria i tipus de filatura | `diametre_fil` / `diametre` |
| Pes teòric del teixit (g/m² i g/metre lineal) | `pes_teixit` / `pes` |
| Encongiment teòric d'ordit i trama | `encongiment_teoric` / `encongiment` |
| Tupidesa de Galcerán i cobertura geomètrica de Peirce | `tupidesa_galceran`, `cobertura_geometrica` / `tupidesa` |
| Densitat màxima de fils i passades | `densitat_maxima` / `maxim` |
| Percentatge d'espai lliure a la pua de la pinta | `espai_pua` / `pua` |

Lligaments predefinits: tafetà, sarges 2/2, 2/1, 3/1, 1/3, setins de 5 i 8.
També accepta una matriu de lligament 0/1 arbitrària.

## Ús sense Claude

Només requereix Python 3 (provat amb 3.12). Sense dependències externes.

```bash
python scripts/calculs_textils.py titol 'Ne 30/2c'
python scripts/calculs_textils.py pes --ordit '167 dtex' --trama '167 dtex' \
       --fils 40 --passades 22 --lligament sarja_2_2 --ample 1.8
python scripts/calculs_textils.py test     # demo + autotests
```

`python scripts/calculs_textils.py -h` per a l'ajuda completa.

La matèria per defecte al CLI és **polièster**. Passa `--materia` explícitament
per a qualsevol altra fibra: entra al càlcul del diàmetre i al de la tupidesa.

## Instal·lació com a skill

**Claude Code** — copia la carpeta a les skills personals o del projecte:

```bash
git clone https://github.com/JepMCC/calculs-textils.git
cp -r calculs-textils ~/.claude/skills/
```

**Claude.ai** (plans de pagament) — comprimeix la carpeta en un `.zip` i puja'l
des de Settings → Capabilities → Skills.

**Altres agents compatibles amb SKILL.md** (Codex, Cursor, OpenClaw…) — copia la
carpeta al directori de skills corresponent.

## Advertència sobre els resultats

Els càlculs són **teòrics**. En particular, l'encongiment estimat depèn de la tensió
al teler i de l'acabat, no només de la geometria, i pot desviar-se diversos punts
del real; el pes calculat n'hereta l'error. Les fórmules geomètriques suposen fil
de secció circular.

Les limitacions de cada càlcul són a
[`references/formules.md`](references/formules.md). Llegeix-les abans de
prendre cap decisió de producció a partir d'un resultat.

## Fonts

Les fórmules provenen de bibliografia tèxtil publicada:

- **F. T. Peirce**, "The Geometry of Cloth Structure", *Journal of the Textile
  Institute*, 1937 — model d'ondulació del fil, encongiment i cobertura geomètrica.
- **V. Galcerán Escobet**, *Tecnología del tejido* — grau de tupidesa i densitat
  màxima. Les constants Q (per matèria) i Kl (per lligament) s'han transcrit de
  la reproducció d'aquestes taules a la tesi doctoral d'**I. Algaba** (UPC),
  capítol 8, taules 8.2 i 8.3.

Les constants tabulades són dades tècniques publicades i es reprodueixen amb
atribució a l'origen. Aquest projecte no té cap vinculació amb els autors ni amb
la UPC.

## Contribucions

Especialment benvingudes si tens **dades mesurades** que contradiguin un
resultat teòric: obre una incidència amb els títols, densitats, lligament,
matèria i el valor real mesurat. És la manera més útil de millorar les
estimacions d'encongiment i el `factor_practic` de densitat màxima.

## Autoria i llicència

Escrit per [@JepMCC](https://github.com/JepMCC). Titularitat dels drets: Texber S.A.

Distribuït sota llicència MIT — vegeu [LICENSE](LICENSE).
