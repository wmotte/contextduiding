# Contextduiding voor Preekvoorbereiding

Dit is een tool die een uitgebreide hoordersanalyse uitvoert voor protestantse preekvoorbereiding in de PKN, gebaseerd op de homiletische methodiek van De Leede & Stark (2017).

## Voorbeelden

In de `output/` map staan concrete voorbeelden van gegenereerde analyses:

| Locatie | Datum | Overzicht |
|---------|-------|-----------|
| Dirksland (Ring 2) | 8 maart 2026 | [00_overzicht.md](output/Dirksland_8_maart_2026_Ring_2/00_overzicht.md) |
| Delft (Vierhovenkerk) | 18 januari 2026 | [00_overzicht.md](output/Delft_18_januari_2026_Vierhovenkerk/00_overzicht.md) |
| Waddinxveen (Bethelkerk) | 4 januari 2026 | [00_overzicht.md](output/Waddinxveen_4_januari_2026_Bethelkerk/00_overzicht.md) |
| Lexmond | 31 december 2025 | [00_overzicht.md](output/Lexmond_31_december_2025_PG/00_overzicht.md) |
| Utrecht (Lutherse Gemeente) | 25 december 2025 | [00_overzicht.md](output/Utrecht_25_december_2025_Lutherse_Gemeente/00_overzicht.md) |

## Achtergrond

Friedrich Niebergall constateerde: *"Menige preek geeft antwoorden op vragen die niemand stelt, en gaat niet in op vragen die iedereen stelt."* Dit script helpt predikanten om hun hoorders beter te kennen door systematisch de context in kaart te brengen.

## Wat doet dit script?

Het script voert zes uitgebreide analyses uit met behulp van Gemini API en Google Search, in twee fasen:

### Fase 1: Liturgische context
0. **Zondag van het Kerkelijk Jaar** - Lezingen, liturgische kleur, thematiek, liedsuggesties (PKN/Liedboek 2013)

### Fase 2: Contextanalyses (met liturgische informatie)
1. **Sociaal-maatschappelijke context** - Demografische, economische en sociale gegevens
2. **Waardenoriëntatie** - De vijf V's en Motivaction Mentality-analyse
3. **Geloofsoriëntatie** - Hoe staan de hoorders geloofsmatig in het leven?
4. **Interpretatieve synthese** - Duiding en vertaling naar homiletische handvatten
5. **Actueel wereldnieuws** - Schokkend nieuws van de afgelopen dagen dat hoorders bezighoudt

De liturgische context uit fase 1 wordt meegegeven aan alle analyses in fase 2, zodat bijvoorbeeld het wereldnieuws gerelateerd kan worden aan de Schriftlezingen.

### Verdieping (verdieping.py)

Na de basisanalyse kan een verdieping worden uitgevoerd met twee extra analyses:

6. **Exegese** - Gedegen schriftuitleg van de lezingen (tekstkritiek, literaire analyse, theologische lijnen)
7. **Kunst en Cultuur** - Schilderijen, iconen, films en muziek die aansluiten bij de lezingen en gemeentecontext

Deze verdieping leest de output van de basisanalyse (00-05) en gebruikt deze als context.

**Bijbelteksten ophalen:** Het script haalt automatisch de bijbelteksten op van [naardensebijbel.nl](https://www.naardensebijbel.nl/) (de literaire vertaling van Pieter Oussoren). De teksten worden opgeslagen in `bijbelteksten/*.txt` en meegenomen in de exegese-prompt.

### Naardense Bijbel Tool

Het script `naardense_bijbel.py` is een hulpmiddel dat specifiek is ontwikkeld om bijbelteksten op te halen voor de exegese-fase.

**Functies:**
- **Automatisch ophalen:** Haalt teksten op van naardensebijbel.nl op basis van referenties (bijv. "Jesaja 9:1-6", "Psalm 121").
- **Slimme fallback:** Probeert eerst directe vers-URLs; als dat faalt (bijv. bij hele hoofdstukken of afwijkende URL-structuren), gebruikt het de zoekfunctie van de website.
- **Caching:** Slaat teksten op in de `bijbelteksten/` map binnen de output-directory. Als een tekst al is gedownload, wordt deze niet opnieuw opgehaald om de server te ontlasten en snelheid te winnen.
- **Ondersteuning:** Werkt voor alle boeken van de protestantse canon, inclusief specifieke versranges en hele hoofdstukken.

Dit script wordt automatisch aangeroepen door `verdieping.py`, maar kan ook standalone worden gebruikt of geïmporteerd in andere scripts.

## Installatie

```bash
# Clone of download de repository
cd contextduiding

# Installeer dependencies
pip install google-genai requests beautifulsoup4

# Stel je Gemini API key in
export GEMINI_API_KEY='jouw-api-key'

# Of maak een .env bestand:
echo "GEMINI_API_KEY=jouw-api-key" > .env
```

## Gebruik

### Basisanalyse

```bash
python contextduiding.py
```

Het script vraagt interactief om:

1. **Plaatsnaam** - Waar wordt de preek gehouden?
2. **Gemeente** - Welke kerkelijke gemeente?
3. **Datum** - Wanneer is de preek? (bijv. "25 december 2025")
4. **Extra context** (optioneel) - Bijzondere dienst, thema, etc.

### Verdieping (exegese en kunst)

```bash
python verdieping.py
```

Dit script toont een lijst van beschikbare basisanalyses en laat je er een kiezen. Vervolgens worden de exegese en kunst/cultuur analyses gegenereerd op basis van alle eerdere context.

## Output

Het script genereert een map in `output/` met:

```
output/Plaatsnaam_datum_timestamp/
├── 00_overzicht.md                        # Samenvattend overzicht met links
├── 00_zondag_kerkelijk_jaar.md            # Liturgische context, lezingen, liederen
├── 01_sociaal_maatschappelijke_context.md # Demografische en sociale analyse
├── 02_waardenorientatie.md                # Vijf V's, Motivaction, trends
├── 03_geloofsorientatie.md                # Religieuze context en geloofstaal
├── 04_interpretatieve_synthese.md         # Homiletische aanbevelingen
├── 05_actueel_wereldnieuws.md             # Recent wereldnieuws met duiding
├── 06_exegese.md                          # Exegese van de Schriftlezingen (via verdieping.py)
├── 07_kunst_cultuur.md                    # Kunst, cultuur en film (via verdieping.py)
└── bijbelteksten/                         # Naardense Bijbel teksten (via verdieping.py)
    ├── jesaja_91-6.txt
    ├── lucas_21-14.txt
    └── ...
```

## Projectstructuur

```
contextduiding/
├── contextduiding.py                       # Hoofdscript basisanalyse
├── verdieping.py                           # Verdieping: exegese en kunst/cultuur
├── naardense_bijbel.py                     # Module voor ophalen bijbelteksten
├── prompts/                                # Prompt-bestanden (aanpasbaar)
│   ├── base_prompt.md                      # Basis rol en werkwijze
│   ├── 00_zondag_kerkelijk_jaar.md         # Liturgische context (eerst)
│   ├── 01_sociaal_maatschappelijke_context.md
│   ├── 02_waardenorientatie.md
│   ├── 03_geloofsorientatie.md
│   ├── 04_interpretatieve_synthese.md
│   ├── 05_actueel_wereldnieuws.md
│   ├── 06_exegese.md                       # Exegese (verdieping)
│   └── 07_kunst_cultuur.md                 # Kunst en cultuur (verdieping)
├── system_prompt_contextduiding.md         # Referentiedocumentatie methodiek
├── homiletisch_kader_hoordersanalyse.md    # Theoretisch kader De Leede & Stark
├── .env                                    # API key (niet in git)
└── output/                                 # Gegenereerde analyses
```

## Prompts aanpassen

De prompts staan als losse markdown-bestanden in de `prompts/` map. Je kunt deze bewerken zonder de Python code aan te passen.

**Placeholders** die automatisch worden vervangen:
- `{{plaatsnaam}}` - De ingevoerde plaatsnaam
- `{{gemeente}}` - De ingevoerde gemeente
- `{{datum}}` - De ingevoerde datum

## Methodiek

De analyse is gebaseerd op de vier pijlers van hoordersanalyse volgens De Leede & Stark (2017), aangevuld met liturgische context en actueel nieuws:

### 0. Zondag van het Kerkelijk Jaar (PKN)
- Positie in het kerkelijk jaar (A/B/C cyclus)
- Lezingen volgens Gemeenschappelijk Leesrooster
- Liturgische kleur en sfeer
- Liedsuggesties uit Liedboek 2013
- Bijzondere zondagen (Israëlzondag, Vredeszondag, etc.)

### 1. Sociaal-maatschappelijke context
- Demografische gegevens (CBS, AlleCijfers)
- Economische situatie
- Sociale structuur
- Recente lokale gebeurtenissen
- Kerkelijke context

### 2. Waardenoriëntatie
**De vijf V's:** Visioenen, Verlangens, Vreugden, Verdriet, Vragen

**Motivaction Mentality-groepen:**
- Traditionele burgerij, Gemaksgeoriënteerden, Moderne burgerij
- Nieuwe conservatieven, Kosmopolieten, Postmaterialisten
- Postmoderne hedonisten, Opwaarts mobielen

**Trendanalyse:** Meso- en microtrends

### 3. Geloofsoriëntatie
Zes ervaringsgebieden: Schepping, Eindigheid, Menselijk tekort, Lijden, Wijsheid der volken, Humaniteit

### 4. Interpretatieve synthese
- Congruentie officieel geloof vs. praktijk
- Verbindings- en confrontatiepunten
- Homiletische aanbevelingen (toon, taal, beelden)

### 5. Actueel wereldnieuws
- Schokkende wereldgebeurtenissen (3-5 dagen)
- Theologische en existentiële vragen
- Pastorale, profetische en diaconale relevantie
- Relatie tot de Schriftlezingen

### 6. Exegese (verdieping)
- Tekstkritische opmerkingen en vertaalkeuzes
- Literaire analyse (genre, structuur, stijlfiguren)
- Historische context van de tekst
- Theologische lijnen en intertekstualiteit
- **Zoekmodellen voor Gods-, mens- en Jezusbeelden** (zie hieronder)
- Samenhang van de lezingen
- Receptiegeschiedenis
- Homiletische doorvertaling

#### Zoekmodellen (Hans Snoek)

De exegese maakt gebruik van de zoekmodellenmethode van Hans Snoek (*Een huis om in te wonen*, 2010). Deze methode biedt een systematische manier om de belangrijkste actanten in de Bijbel — God, mens en Jezus — te analyseren. Het zijn geen rigide rasters, maar heuristische hulpmiddelen die van geval tot geval hun nut moeten bewijzen.

**A. Godsbeelden (OT)**

Het OT kent drie soorten uitspraken over God:

1. *Werkwoordelijke uitspraken* — God bevrijdt, schept, leidt, spreekt (Brueggemann: Israël leerde God kennen in concrete historische gebeurtenissen)
2. *Metaforische uitspraken* — "De HEER is koning/herder/rechter/vader"
3. *Uitspraken over eigenschappen* — onderverdeeld in:
   - Overstijgende (transcendente): almachtig, eeuwig, heilig
   - Toebuigende (condescendente): barmhartig, trouw, genadig (Berkhof)

```
            overstijgende eigenschappen
                        |
metaforische uitspraken — God — werkwoordelijke uitspraken
                        |
            toebuigende eigenschappen
```

**B. Mensbeelden (OT)**

```
                    God
        (gebed, aanbidding, luisteren)
                    |
    kwaad doen — mens/mensen — goed doen
                    |
                    wereld
        (zorg voor naaste, belangen)
```

Gerichtheid op God en wereld sluiten elkaar niet uit — profeten roepen met beroep op Gods wil juist op tot zorg voor de naaste.

**C. Jezusbeelden (NT)**

Gebaseerd op Berkhof, aangepast door Snoek:

```
            van boven: Zoon van God
                        |
van achteren: jood — Jezus — van voren: aankondiger Koninkrijk
                        |
            van beneden: mens
```

- **Van achteren**: geworteld in Israëls traditie, Messias
- **Van boven**: goddelijke identiteit, zending, pre-existentie
- **Van beneden**: mens van vlees en bloed, emoties, lijden
- **Van voren**: uitspraken over Koninkrijk, eeuwig leven, toekomst

### 7. Kunst en Cultuur (verdieping)
- Klassieke christelijke kunst (schilderijen, iconen, miniaturen)
- Moderne en hedendaagse kunst
- Film en documentaire
- Muziek (klassiek, oratoria, populair)
- Literatuur en poëzie
- Praktische tips voor gebruik in de eredienst

Bronnen: artbible.info, De Bijbel Cultureel (Barnard), Rijksmuseum, Web Gallery of Art

## Bronnen

### Gebruikte bronnen door het script
- **CBS / AlleCijfers** - Demografische statistieken
- **NOS, NRC, Trouw, ND** - Nieuws en actualiteit
- **protestantsekerk.nl** - PKN-informatie, leesrooster
- **Liedboek 2013** - Liedsuggesties
- **naardensebijbel.nl** - Naardense Bijbel (Pieter Oussoren)
- **artbible.info** - Bijbelse kunst database
- **wga.hu** - Web Gallery of Art
- **De Bijbel Cultureel** - Barnard & Van der Meiden

### Literatuur
- De Leede, H. & Stark, C. (2017). *Ontvouwen: Protestantse prediking in de praktijk*. Zoetermeer: Boekencentrum, pp. 73-81.
- Niebergall, F. (1971). 'Die moderne Predigt', in: Hummel, G., *Aufgabe der Predigt*. Darmstadt: Wissenschaftliche Buchgesellschaft.
- Snoek, H. (2010). *Een huis om in te wonen: Uitleg en interpretatie van de Bijbel*. Kampen: Kok, 2e druk, pp. 180-199. (Zoekmodellen voor Gods-, mens- en Jezusbeelden)
- Motivaction. *Mentality-model*. https://www.motivaction.nl/mentality

## API Key

Je hebt een Gemini API key nodig: https://aistudio.google.com/app/apikey
