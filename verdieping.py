#!/usr/bin/env python3
"""
Verdieping: Exegese en Kunst/Cultuur voor Preekvoorbereiding

Dit script bouwt voort op de basisanalyse van contextduiding.py en voegt toe:
- 06_exegese: Exegetische analyse van de Schriftlezingen
- 07_kunst_cultuur: Kunst, cultuur en film bij de lezingen

Het leest de output van de vorige analyses (00-05) en gebruikt deze als context.
Voor de exegese worden de bijbelteksten opgehaald van naardensebijbel.nl.

W.M. Otte (w.m.otte@umcutrecht.nl)
"""

import os
import sys
import re
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("FOUT: De nieuwe 'google-genai' library is niet geïnstalleerd.")
    print("Installeer deze met: pip install google-genai")
    sys.exit(1)

try:
    from naardense_bijbel import download_lezingen, laad_bijbelteksten
except ImportError:
    print("FOUT: naardense_bijbel module niet gevonden.")
    print("Zorg dat naardense_bijbel.py in dezelfde directory staat.")
    sys.exit(1)

# Configuratie
SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = SCRIPT_DIR / "output"
PROMPTS_DIR = SCRIPT_DIR / "prompts"

MODEL_NAME = "gemini-3-flash-preview"


def load_prompt(filename: str, user_input: dict) -> str:
    """Laad een prompt uit een markdown bestand en vervang placeholders."""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt bestand niet gevonden: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{plaatsnaam}}", user_input.get("plaatsnaam", ""))
    content = content.replace("{{gemeente}}", user_input.get("gemeente", ""))
    content = content.replace("{{datum}}", user_input.get("datum", ""))

    return content


def list_output_folders() -> list[Path]:
    """Lijst alle beschikbare output folders."""
    if not OUTPUT_DIR.exists():
        return []

    folders = []
    for item in OUTPUT_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Controleer of er een 00_zondag_kerkelijk_jaar.md bestaat
            if (item / "00_zondag_kerkelijk_jaar.md").exists():
                folders.append(item)

    return sorted(folders, key=lambda x: x.stat().st_mtime, reverse=True)


def select_folder() -> Path:
    """Laat de gebruiker een output folder kiezen."""
    folders = list_output_folders()

    if not folders:
        print("\nFOUT: Geen output folders gevonden met basisanalyses.")
        print("Voer eerst contextduiding.py uit om basisanalyses te genereren.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("VERDIEPING: EXEGESE EN KUNST/CULTUUR")
    print("=" * 60)
    print("\nBeschikbare analyses:\n")

    for i, folder in enumerate(folders, 1):
        # Tel bestaande analyses
        existing = []
        for num in range(8):
            pattern = f"{num:02d}_*.md"
            if list(folder.glob(pattern)):
                existing.append(f"{num:02d}")

        print(f"  {i}. {folder.name}")
        print(f"     Analyses: {', '.join(existing)}")

    print()
    while True:
        try:
            choice = input("Kies een nummer (of 'q' om te stoppen): ").strip()
            if choice.lower() == 'q':
                sys.exit(0)
            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                return folders[idx]
            print("Ongeldig nummer, probeer opnieuw.")
        except ValueError:
            print("Voer een geldig nummer in.")


def read_previous_analyses(folder: Path) -> dict:
    """Lees alle vorige analyses uit de folder."""
    analyses = {}

    # Bestanden die we willen lezen
    files_to_read = [
        ("00_zondag_kerkelijk_jaar.md", "liturgische_context"),
        ("01_sociaal_maatschappelijke_context.md", "sociaal_maatschappelijk"),
        ("02_waardenorientatie.md", "waardenorientatie"),
        ("03_geloofsorientatie.md", "geloofsorientatie"),
        ("04_interpretatieve_synthese.md", "synthese"),
        ("05_actueel_wereldnieuws.md", "wereldnieuws"),
    ]

    for filename, key in files_to_read:
        filepath = folder / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                analyses[key] = f.read()
        else:
            analyses[key] = ""

    return analyses


def extract_user_input_from_folder(folder: Path) -> dict:
    """Probeer plaatsnaam, gemeente en datum te extraheren uit de foldernaam of overzicht."""
    # Probeer uit overzicht.md
    overzicht = folder / "00_overzicht.md"
    user_input = {"plaatsnaam": "", "gemeente": "", "datum": ""}

    if overzicht.exists():
        with open(overzicht, "r", encoding="utf-8") as f:
            content = f.read()

        for line in content.split("\n"):
            if "**Plaatsnaam:**" in line:
                user_input["plaatsnaam"] = line.split("**Plaatsnaam:**")[-1].strip()
            elif "**Gemeente:**" in line:
                user_input["gemeente"] = line.split("**Gemeente:**")[-1].strip()
            elif "**Datum" in line:
                # Datum preek: of Datum:
                parts = line.split(":**")
                if len(parts) > 1:
                    user_input["datum"] = parts[-1].strip()

    # Fallback: gebruik foldernaam
    if not user_input["plaatsnaam"]:
        parts = folder.name.split("_")
        if parts:
            user_input["plaatsnaam"] = parts[0]

    return user_input


def get_gemini_client() -> genai.Client:
    """Initialiseer de Gemini Client."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("\nFOUT: Geen API key gevonden.")
        print("Stel de GEMINI_API_KEY environment variable in.")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def build_context_string(previous_analyses: dict) -> str:
    """Bouw een context string van alle vorige analyses."""
    sections = []

    if previous_analyses.get("liturgische_context"):
        sections.append("## Liturgische Context en Schriftlezingen\n\n" +
                       previous_analyses["liturgische_context"])

    if previous_analyses.get("sociaal_maatschappelijk"):
        sections.append("## Sociaal-Maatschappelijke Context\n\n" +
                       previous_analyses["sociaal_maatschappelijk"])

    if previous_analyses.get("waardenorientatie"):
        sections.append("## Waardenoriëntatie\n\n" +
                       previous_analyses["waardenorientatie"])

    if previous_analyses.get("geloofsorientatie"):
        sections.append("## Geloofsoriëntatie\n\n" +
                       previous_analyses["geloofsorientatie"])

    if previous_analyses.get("synthese"):
        sections.append("## Interpretatieve Synthese\n\n" +
                       previous_analyses["synthese"])

    if previous_analyses.get("wereldnieuws"):
        sections.append("## Actueel Wereldnieuws\n\n" +
                       previous_analyses["wereldnieuws"])

    return "\n\n---\n\n".join(sections)


def run_analysis(client: genai.Client, prompt: str, title: str) -> str:
    """Voer een analyse uit met Gemini en Google Search."""
    print(f"\n{'─' * 50}")
    print(f"Analyseren: {title}")
    print(f"{'─' * 50}")
    print("Bezig met redeneren en zoeken...")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,  # Lager voor minder hallucinaties
                top_p=0.90,
                top_k=30,
                max_output_tokens=8192,
                tools=[types.Tool(
                    google_search=types.GoogleSearch()
                )],
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
    content = re.sub(r'([:.:])\s*(\n*)\s*([\*\-] )', r'\1\n\n\3', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Opgeslagen: {filepath.name}")


def update_summary(output_dir: Path):
    """Update het overzichtsbestand met de nieuwe analyses."""
    overzicht_path = output_dir / "00_overzicht.md"

    if not overzicht_path.exists():
        return

    with open(overzicht_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Voeg nieuwe analyses toe als ze nog niet in het overzicht staan
    new_analyses = [
        ("06_exegese", "Exegese van de Schriftlezingen"),
        ("07_kunst_cultuur", "Kunst, Cultuur en Film"),
    ]

    for name, title in new_analyses:
        if (output_dir / f"{name}.md").exists() and f"[{title}]" not in content:
            # Zoek het einde van de analyses sectie
            if "## Analyses" in content:
                # Voeg toe aan het einde van de analyses lijst
                content = content.rstrip()
                content += f"\n- [{title}]({name}.md)\n"

    with open(overzicht_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Hoofdfunctie."""
    # Laad environment variables uit .env
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"\'')

    # Selecteer folder
    folder = select_folder()
    print(f"\nGeselecteerd: {folder.name}")

    # Lees vorige analyses
    print("\nVorige analyses laden...")
    previous_analyses = read_previous_analyses(folder)
    user_input = extract_user_input_from_folder(folder)

    print(f"  Plaatsnaam: {user_input['plaatsnaam']}")
    print(f"  Gemeente: {user_input['gemeente']}")
    print(f"  Datum: {user_input['datum']}")

    # Controleer of liturgische context aanwezig is
    if not previous_analyses.get("liturgische_context"):
        print("\nFOUT: Geen liturgische context gevonden (00_zondag_kerkelijk_jaar.md)")
        print("Deze is nodig voor de exegese en kunst/cultuur analyse.")
        sys.exit(1)

    # Download bijbelteksten van de Naardense Bijbel
    print("\n" + "─" * 50)
    print("BIJBELTEKSTEN OPHALEN")
    print("─" * 50)

    bijbelteksten_map = download_lezingen(folder, previous_analyses["liturgische_context"])

    if bijbelteksten_map:
        print(f"\n✓ {len(bijbelteksten_map)} bijbeltekst(en) opgehaald en opgeslagen")
    else:
        print("\n! Geen bijbelteksten kunnen ophalen (exegese gaat door zonder grondtekst)")

    # Laad de bijbelteksten voor de context
    bijbelteksten = laad_bijbelteksten(folder)

    # Initialiseer client
    print("\nGoogle GenAI Client initialiseren...")
    client = get_gemini_client()

    # Bouw context (inclusief bijbelteksten)
    context_string = build_context_string(previous_analyses)

    # Voeg bijbelteksten toe aan de context
    if bijbelteksten:
        context_string += f"""

---

## Bijbelteksten (Naardense Bijbel - Pieter Oussoren)

{bijbelteksten}
"""

    # Laad prompts
    base_prompt = load_prompt("base_prompt.md", user_input)

    # Analyses uitvoeren
    print("\n" + "=" * 60)
    print(f"VERDIEPING STARTEN MET MODEL: {MODEL_NAME}")
    print("=" * 60)

    analysis_definitions = [
        ("06_exegese", "Exegese van de Schriftlezingen"),
        ("07_kunst_cultuur", "Kunst, Cultuur en Film"),
    ]

    for name, title in analysis_definitions:
        # Controleer of analyse al bestaat
        if (folder / f"{name}.md").exists():
            overwrite = input(f"\n{name}.md bestaat al. Overschrijven? (j/n): ").strip().lower()
            if overwrite != 'j':
                print(f"  Overgeslagen: {name}")
                continue

        # Bouw prompt
        task_prompt = load_prompt(f"{name}.md", user_input)

        full_prompt = f"""{base_prompt}

# Eerdere Analyses (Context)

{context_string}

---

# Huidige Opdracht

{task_prompt}
"""

        # Voer analyse uit
        result = run_analysis(client, full_prompt, title)
        save_analysis(folder, name, result, title)

    # Update overzicht
    update_summary(folder)

    print("\n" + "=" * 60)
    print("KLAAR")
    print(f"Locatie: {folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()
