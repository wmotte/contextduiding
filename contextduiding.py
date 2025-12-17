#!/usr/bin/env python3
"""
Contextduiding voor Protestantse Preekvoorbereiding

Dit script voert een uitgebreide hoordersanalyse uit voor preekvoorbereiding,
gebaseerd op de homiletische methodiek van De Leede & Stark.

Het gebruikt de NIEUWE Google GenAI SDK (v1.0+) met Gemini 3.0 en Google Search
grounding om actuele informatie te verzamelen.

W.M. Otte (w.m.otte@umcutrecht.nl)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Importeer de nieuwe SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("FOUT: De nieuwe 'google-genai' library is niet geïnstalleerd.")
    print("Installeer deze met: pip install google-genai")
    sys.exit(1)

# Configuratie
SCRIPT_DIR = Path(__file__).parent.resolve()
SYSTEM_PROMPT_FILE = SCRIPT_DIR / "system_prompt_contextduiding.md"
OUTPUT_DIR = SCRIPT_DIR / "output"

# Model keuze: Gemini 3
MODEL_NAME = "gemini-3-pro-preview"

def load_system_prompt() -> str:
    """Laad het system prompt uit het markdown bestand."""
    if not SYSTEM_PROMPT_FILE.exists():
        # Fallback als bestand niet bestaat, zodat script toch werkt
        return "Je bent een deskundige homileet en socioloog die predikanten helpt met contextanalyse."

    with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def get_user_input() -> dict:
    """Vraag de gebruiker om de benodigde informatie."""
    print("\n" + "=" * 60)
    print("CONTEXTDUIDING VOOR PREEKVOORBEREIDING (Gemini 3.0)")
    print("Gebaseerd op de homiletische methodiek van De Leede & Stark")
    print("=" * 60 + "\n")

    print("Dit programma voert een uitgebreide hoordersanalyse uit voor uw preek.")
    print("Vul de volgende gegevens in:\n")

    plaatsnaam = input("1. Plaatsnaam waar de preek gehouden wordt: ").strip()
    if not plaatsnaam:
        print("FOUT: Plaatsnaam is verplicht.")
        sys.exit(1)

    gemeente = input("2. Naam van de kerkelijke gemeente: ").strip()
    if not gemeente:
        print("FOUT: Gemeente is verplicht.")
        sys.exit(1)

    datum_str = input("3. Datum van de preek (bijv. 25 december 2025): ").strip()
    if not datum_str:
        print("FOUT: Datum is verplicht.")
        sys.exit(1)

    # Optionele extra context
    print("\n4. Eventuele extra context (optioneel, druk Enter om over te slaan):")
    print("   (bijv. bijzondere dienst, thema, doelgroep)")
    extra_context = input("   Extra context: ").strip()

    return {
        "plaatsnaam": plaatsnaam,
        "gemeente": gemeente,
        "datum": datum_str,
        "extra_context": extra_context
    }


def create_output_directory(plaatsnaam: str, datum: str) -> Path:
    """Maak een output directory aan voor de analyses."""
    safe_name = "".join(c if c.isalnum() or c in "- " else "_" for c in plaatsnaam)
    safe_date = "".join(c if c.isalnum() else "_" for c in datum)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{safe_name}_{safe_date}_{timestamp}"

    output_path = OUTPUT_DIR / dir_name
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def get_gemini_client() -> genai.Client:
    """Initialiseer de Gemini Client met de nieuwe SDK."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("\nFOUT: Geen API key gevonden.")
        print("Stel de GEMINI_API_KEY environment variable in.")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def build_analysis_prompts(user_input: dict, system_prompt: str) -> list[dict]:
    """Bouw de prompts voor elke analyse."""
    context_info = f"""
## Preekgegevens
- **Plaatsnaam:** {user_input['plaatsnaam']}
- **Gemeente:** {user_input['gemeente']}
- **Datum:** {user_input['datum']}
"""
    if user_input.get('extra_context'):
        context_info += f"- **Extra context:** {user_input['extra_context']}\n"

    # Hieronder volgen de prompts (ongewijzigd qua inhoud, alleen structuur)
    analyses = [
        {
            "name": "01_sociaal_maatschappelijke_context",
            "title": "Sociaal-Maatschappelijke Context",
            "prompt": f"""
{system_prompt}
{context_info}
## Jouw Taak
Voer de **SOCIAAL-MAATSCHAPPELIJKE CONTEXTANALYSE** uit (pijler 1 De Leede & Stark).
Doorzoek het internet grondig naar:
1. **Demografie:** Leeftijd, opleiding in {user_input['plaatsnaam']}.
2. **Economie:** Werk, sectoren, inkomen.
3. **Sociale structuur:** Verenigingen, cohesie.
4. **Relaties:** Gezinnen, alleenstaanden.
5. **Kerkelijke context:** Kerkelijke kaart, positie {user_input['gemeente']}.
6. **Actueel:** Recent lokaal nieuws.

Gebruik Google Search. Wees specifiek. Vermeld bronnen.
"""
        },
        {
            "name": "02_waardenorientatie",
            "title": "Waardenoriëntatie",
            "prompt": f"""
{system_prompt}
{context_info}
## Jouw Taak
Voer de **WAARDENORIËNTATIE-ANALYSE** uit (pijler 2).
### De Vijf V's
1. Visioenen (dromen)
2. Verlangens (gemis)
3. Vreugden (trots)
4. Verdriet (pijn)
5. Vragen (levensvragen)

### Trends & Mentaliteit
- Macro/Meso/Micro trends
- Dominante Motivaction Mentality-groepen in {user_input['plaatsnaam']}.

Gebruik Google Search om actuele sfeer te proeven.
"""
        },
        {
            "name": "03_geloofsorientatie",
            "title": "Geloofsoriëntatie",
            "prompt": f"""
{system_prompt}
{context_info}
## Jouw Taak
Voer de **GELOOFSORIËNTATIE-ANALYSE** uit (pijler 3).
### Analysepunten
1. **God-talk:** Is er nog religieuze taal?
2. **Ervaringsgebieden:** Schepping, Eindigheid, Schuld, Lijden, Wijsheid, Gemeenschap.
3. **Spirituele markt:** Concurrentie, zoektochten.
4. **Liturgie:** Hoe landt de traditie?

Gebruik Google Search voor kerkelijke trends in de regio.
"""
        },
        {
            "name": "04_interpretatieve_synthese",
            "title": "Interpretatieve Synthese",
            "prompt": f"""
{system_prompt}
{context_info}
## Jouw Taak
Voer de **INTERPRETATIEVE SYNTHESE** uit (pijler 4).
Integreer alles tot homiletische adviezen.

1. **Congruentie:** Spanning officieel geloof vs. praktijk.
2. **Verbinding & Confrontatie:** Waar sluit het Evangelie aan? Waar botst het?
3. **Diversiteit:** Hoe spreek je verschillende groepen aan?
4. **Advies:** Toon, taal, beeldspraak, balans pastoraal/profetisch.

Geef concreet advies aan de predikant.
"""
        }
    ]
    return analyses


def run_analysis(client: genai.Client, prompt: str, title: str) -> str:
    """Voer een analyse uit met Gemini 2.0 en Google Search (Nieuwe SDK)."""
    print(f"\n{'─' * 50}")
    print(f"Analyseren: {title}")
    print(f"{'─' * 50}")
    print("Bezig met redeneren en zoeken...")

    try:
        # Configuratie voor de generatie
        # We zetten safety filters UIT (BLOCK_NONE) omdat preekvoorbereiding
        # moet kunnen gaan over zonde, lijden, dood en religieus extremisme.
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7, # Lager zetten indien te veel hallucinatiess
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                # Nieuwe syntax voor Google Search Tool
                tools=[types.Tool(
                    google_search=types.GoogleSearch()
                )],
                # Nieuwe syntax voor Safety Settings
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                ]
            )
        )

        if response.text:
            print(f"✓ Analyse '{title}' voltooid")
            
            # Controleer of er grounding metadata is (bronvermeldingen vanuit Google Search)
            # In de nieuwe SDK zit dit vaak in response.candidates[0].grounding_metadata
            # Voor nu retourneren we de tekst, Gemini 3.0 verwerkt bronnen vaak al in de tekst.
            return response.text
        else:
            print(f"✗ Geen tekst ontvangen voor '{title}'")
            return f"# {title}\n\nGeen analyse beschikbaar."

    except Exception as e:
        error_msg = f"Fout bij analyse '{title}': {str(e)}"
        print(f"✗ {error_msg}")
        return f"# {title}\n\n**Fout:** {error_msg}"


def save_analysis(output_dir: Path, filename: str, content: str, title: str):
    """Sla een analyse op naar een markdown bestand."""
    filepath = output_dir / f"{filename}.md"

    if not content.strip().startswith("#"):
        content = f"# {title}\n\n{content}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Opgeslagen: {filepath.name}")


def create_summary(output_dir: Path, user_input: dict, analyses: list[dict]):
    """Maak een samenvattend overzichtsbestand."""
    summary = f"""# Contextduiding Preekvoorbereiding

## Gegevens
- **Plaatsnaam:** {user_input['plaatsnaam']}
- **Gemeente:** {user_input['gemeente']}
- **Datum preek:** {user_input['datum']}
- **Model:** {MODEL_NAME}
"""
    summary += "\n## Analyses\n"
    for analysis in analyses:
        summary += f"- [{analysis['title']}]({analysis['name']}.md)\n"

    filepath = output_dir / "00_overzicht.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(summary)


def main():
    """Hoofdfunctie."""
    # Laad environment variables uit .env (optioneel)
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"\'')

    system_prompt = load_system_prompt()
    user_input = get_user_input()

    print("\nGoogle GenAI Client (v1.0+) initialiseren...")
    client = get_gemini_client()
    
    output_dir = create_output_directory(user_input['plaatsnaam'], user_input['datum'])
    print(f"Output directory: {output_dir}")

    analyses = build_analysis_prompts(user_input, system_prompt)

    print("\n" + "=" * 60)
    print(f"STARTEN MET MODEL: {MODEL_NAME}")
    print("=" * 60)

    for analysis in analyses:
        result = run_analysis(client, analysis['prompt'], analysis['title'])
        save_analysis(output_dir, analysis['name'], result, analysis['title'])

    create_summary(output_dir, user_input, analyses)

    print("\n" + "=" * 60)
    print("KLAAR")
    print(f"Locatie: {output_dir}")


if __name__ == "__main__":
    main()

