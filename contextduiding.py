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
import re
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
OUTPUT_DIR = SCRIPT_DIR / "output"
PROMPTS_DIR = SCRIPT_DIR / "prompts"

# Model keuze: Gemini 3 flash (i.p.v. pro)
MODEL_NAME = "gemini-3-flash-preview"


def load_prompt(filename: str, user_input: dict) -> str:
    """Laad een prompt uit een markdown bestand en vervang placeholders.

    Placeholders:
        {{plaatsnaam}} - wordt vervangen door user_input['plaatsnaam']
        {{gemeente}}   - wordt vervangen door user_input['gemeente']
        {{datum}}      - wordt vervangen door user_input['datum']
    """
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt bestand niet gevonden: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Vervang placeholders
    content = content.replace("{{plaatsnaam}}", user_input.get("plaatsnaam", ""))
    content = content.replace("{{gemeente}}", user_input.get("gemeente", ""))
    content = content.replace("{{datum}}", user_input.get("datum", ""))

    return content


def get_user_input() -> dict:
    """Vraag de gebruiker om de benodigde informatie."""
    print("\n" + "=" * 60)
    print("CONTEXTDUIDING VOOR PREEKVOORBEREIDING")
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


def build_first_analysis(user_input: dict) -> dict:
    """Bouw de eerste analyse: Zondag van het Kerkelijk Jaar.

    Deze wordt eerst uitgevoerd zodat de lezingen en liturgische context
    beschikbaar zijn voor de andere analyses.
    """
    base_prompt = load_prompt("base_prompt.md", user_input)

    context_info = f"""
## Preekgegevens
- **Plaatsnaam:** {user_input['plaatsnaam']}
- **Gemeente:** {user_input['gemeente']}
- **Datum:** {user_input['datum']}
"""
    if user_input.get('extra_context'):
        context_info += f"- **Extra context:** {user_input['extra_context']}\n"

    task_prompt = load_prompt("00_zondag_kerkelijk_jaar.md", user_input)
    full_prompt = f"{base_prompt}\n\n{context_info}\n\n{task_prompt}"

    return {
        "name": "00_zondag_kerkelijk_jaar",
        "title": "Zondag van het Kerkelijk Jaar",
        "prompt": full_prompt
    }


def build_remaining_analyses(user_input: dict, kerkelijk_jaar_context: str) -> list[dict]:
    """Bouw de overige analyses, inclusief de liturgische context.

    Args:
        user_input: De gebruikersinvoer (plaatsnaam, gemeente, datum)
        kerkelijk_jaar_context: De output van de eerste analyse (lezingen, etc.)
    """
    base_prompt = load_prompt("base_prompt.md", user_input)

    # Context info nu inclusief de liturgische informatie
    context_info = f"""
## Preekgegevens
- **Plaatsnaam:** {user_input['plaatsnaam']}
- **Gemeente:** {user_input['gemeente']}
- **Datum:** {user_input['datum']}
"""
    if user_input.get('extra_context'):
        context_info += f"- **Extra context:** {user_input['extra_context']}\n"

    # Voeg de liturgische context toe
    context_info += f"""
## Liturgische Context (uit eerder onderzoek)

{kerkelijk_jaar_context}
"""

    # De overige analyses (01-05)
    analysis_definitions = [
        ("01_sociaal_maatschappelijke_context", "Sociaal-Maatschappelijke Context"),
        ("02_waardenorientatie", "Waardenoriëntatie"),
        ("03_geloofsorientatie", "Geloofsoriëntatie"),
        ("04_interpretatieve_synthese", "Interpretatieve Synthese"),
        ("05_actueel_wereldnieuws", "Actueel Wereldnieuws"),
    ]

    analyses = []
    for name, title in analysis_definitions:
        task_prompt = load_prompt(f"{name}.md", user_input)
        full_prompt = f"{base_prompt}\n\n{context_info}\n\n{task_prompt}"

        analyses.append({
            "name": name,
            "title": title,
            "prompt": full_prompt
        })

    return analyses


def run_analysis(client: genai.Client, prompt: str, title: str) -> str:
    """Voer een analyse uit met Taalmodel en Search."""
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

    # 1. Zorg voor een lege regel VÓÓR elke kop (behalve de allereerste regel)
    content = re.sub(r'([^\n])\n(#+ .*)', r'\1\n\n\2', content)
    
    # 2. Zorg voor een lege regel NA elke kop
    content = re.sub(r'^(#+ .*)\n+(?=[^\n])', r'\1\n\n', content, flags=re.MULTILINE)
    
    # 3. Zorg voor een lege regel rondom scheidingslijnen (---)
    content = re.sub(r'([^\n])\n(---)', r'\1\n\n\2', content)
    content = re.sub(r'(---)\n+(?=[^\n])', r'\1\n\n', content)

    # 4. Zorg dat bullet points op een nieuwe regel staan als ze direct na een dubbele punt of zin komen
    # Zoekt naar: dubbele punt/punt, optionele spaties, dan een asterisk of streepje met spatie
    content = re.sub(r'([:.:])\s*(\n*)\s*([\*\-] )', r'\1\n\n\3', content)

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

    user_input = get_user_input()

    print("\nGoogle GenAI Client (v1.0+) initialiseren...")
    client = get_gemini_client()

    output_dir = create_output_directory(user_input['plaatsnaam'], user_input['datum'])
    print(f"Output directory: {output_dir}")

    print("\n" + "=" * 60)
    print(f"STARTEN MET MODEL: {MODEL_NAME}")
    print("=" * 60)

    # FASE 1: Eerst de liturgische context ophalen
    print("\n" + "─" * 60)
    print("FASE 1: Liturgische context verzamelen")
    print("─" * 60)

    first_analysis = build_first_analysis(user_input)
    kerkelijk_jaar_result = run_analysis(
        client,
        first_analysis['prompt'],
        first_analysis['title']
    )
    save_analysis(
        output_dir,
        first_analysis['name'],
        kerkelijk_jaar_result,
        first_analysis['title']
    )

    # FASE 2: De overige analyses met de liturgische context
    print("\n" + "─" * 60)
    print("FASE 2: Contextanalyses met liturgische informatie")
    print("─" * 60)

    remaining_analyses = build_remaining_analyses(user_input, kerkelijk_jaar_result)

    all_analyses = [first_analysis] + remaining_analyses

    for analysis in remaining_analyses:
        result = run_analysis(client, analysis['prompt'], analysis['title'])
        save_analysis(output_dir, analysis['name'], result, analysis['title'])

    create_summary(output_dir, user_input, all_analyses)

    print("\n" + "=" * 60)
    print("KLAAR")
    print(f"Locatie: {output_dir}")


if __name__ == "__main__":
    main()

