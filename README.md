# Contextduiding voor Preekvoorbereiding

Dit is een tool die een uitgebreide hoordersanalyse uitvoert voor protestantse preekvoorbereiding, gebaseerd op de homiletische methodiek van De Leede & Stark (2017).

## Achtergrond

Friedrich Niebergall constateerde: *"Menige preek geeft antwoorden op vragen die niemand stelt, en gaat niet in op vragen die iedereen stelt."* Dit script helpt predikanten om hun hoorders beter te kennen door systematisch de context in kaart te brengen.

## Documentatie

| Document | Beschrijving |
|----------|--------------|
| [Homiletisch Kader](homiletisch_kader_hoordersanalyse.md) | Uitgebreide samenvatting van de vier pijlers van hoordersanalyse volgens De Leede & Stark |
| [System Prompt](system_prompt_contextduiding.md) | De instructies voor het taalmodel inclusief Motivaction-model en bronnen |

## Wat doet dit script?

Het script voert vier uitgebreide analyses uit met behulp van een taalmodel (Gemini API met Google Search):

1. **Sociaal-maatschappelijke context** - Demografische, economische en sociale gegevens (via CBS, AlleCijfers, NOS)
2. **Waardenoriëntatie** - De vijf V's en Motivaction Mentality-analyse
3. **Geloofsoriëntatie** - Hoe staan de hoorders geloofsmatig in het leven?
4. **Interpretatieve synthese** - Duiding en vertaling naar homiletische handvatten

### Gebruikte bronnen en modellen

- **NOS.nl** - Actueel landelijk en regionaal nieuws
- **CBS / AlleCijfers** - Demografische en statistische gegevens
- **Motivaction Mentality-model** - Acht sociale milieus voor waardenoriëntatie:
  - Traditionele burgerij
  - Gemaksgeoriënteerden
  - Moderne burgerij
  - Nieuwe conservatieven
  - Kosmopolieten
  - Postmaterialisten
  - Postmoderne hedonisten
  - Opwaarts mobielen

## Installatie

```bash
# Clone of download de repository
cd contextduiding

# Installeer dependencies
pip install -r requirements.txt

# Stel je Gemini API key in
export GEMINI_API_KEY='jouw-api-key'

# Of maak een .env bestand:
echo "GEMINI_API_KEY=jouw-api-key" > .env
```

## Gebruik

```bash
python contextduiding.py
```

Het script vraagt interactief om:

1. **Plaatsnaam** - Waar wordt de preek gehouden?
2. **Gemeente** - Welke kerkelijke gemeente?
3. **Datum** - Wanneer is de preek? (bijv. "25 december 2025")
4. **Extra context** (optioneel) - Bijzondere dienst, thema, etc.

## Output

Het script genereert een map in `output/` met:

- `00_overzicht.md` - Samenvattend overzicht
- `01_sociaal_maatschappelijke_context.md` - Demografische en sociale analyse
- `02_waardenorientatie.md` - Analyse van de vijf V's, Motivaction-groepen en trends
- `03_geloofsorientatie.md` - Religieuze context en geloofstaal
- `04_interpretatieve_synthese.md` - Integrerende analyse met homiletische aanbevelingen

### Voorbeelden

In de `output/` map staan twee concrete voorbeelden van gegenereerde analyses:

- **Waddinxveen** (Bethelkerk, 4 januari 2026)
- **Lexmond** (31 december 2025)

## Projectstructuur

```
contextduiding/
├── contextduiding.py                    # Hoofdscript
├── system_prompt_contextduiding.md      # Instructies voor Gemini (NOS, Motivaction, etc.)
├── homiletisch_kader_hoordersanalyse.md # Theoretisch kader De Leede & Stark
├── requirements.txt                     # Python dependencies
├── .env                                 # API key (niet in git)
└── output/                              # Gegenereerde analyses
```

## Methodiek

De analyse is gebaseerd op de vier pijlers van hoordersanalyse volgens De Leede & Stark (2017):

### 1. Sociaal-maatschappelijke context
- Demografische gegevens (CBS, AlleCijfers)
- Economische situatie
- Sociale structuur
- Recente gebeurtenissen (NOS, regionale media)
- Kerkelijke context

### 2. Waardenoriëntatie
**De vijf V's:**
- Visioenen, Verlangens, Vreugden, Verdriet, Vragen

**Motivaction Mentality-groepen:**
- Analyse welke sociale milieus vertegenwoordigd zijn
- Implicaties voor taal, beelden en benadering

**Trendanalyse:**
- Mesotrends (5-15 jaar)
- Microtrends (actueel nieuws via NOS)

### 3. Geloofsoriëntatie
Zes fundamentele ervaringsgebieden:

1. Schepping en het goede leven
2. Eindigheid en zingeving
3. Menselijk tekort (falen, schuld)
4. Lijden en het kwaad
5. Wijsheid der volken
6. Humaniteit en gemeenschap

### 4. Interpretatieve synthese
- Congruentie tussen officieel geloof en geleefde praktijk
- Verbindingspunten voor de preek
- Confrontatiepunten
- Context van de specifieke datum
- Aanbevelingen per Mentality-groep

## API Key

Je hebt een Gemini API key nodig. Deze kun je verkrijgen via:
https://aistudio.google.com/app/api-keys

## Bronnen

- De Leede, H. & Stark, C. (2017). *Ontvouwen: Protestantse prediking in de praktijk*. Zoetermeer: Boekencentrum, pp. 73-81.
- Niebergall, F. (1971). 'Die moderne Predigt', in: Hummel, G., *Aufgabe der Predigt*. Darmstadt: Wissenschaftliche Buchgesellschaft.
- Motivaction. *Mentality-model*. https://www.motivaction.nl/mentality
