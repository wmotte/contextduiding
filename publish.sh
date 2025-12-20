#!/bin/bash

# Controleer of we in de root van het project staan
if [ ! -d "output" ] || [ ! -d "docs" ]; then
    echo "❌ Fout: Draai dit script vanuit de root van het project (waar de mappen 'output' en 'docs' staan)."
    exit 1
fi

echo "🚀 Publiceren van output naar docs..."

# 1. Kopieer de inhoud van output naar docs
# -R = recursief (mappen en inhoud)
# -n = niet overschrijven als bestand al bestaat (veiligheid, optioneel, hier laten we het toe om updates te pushen)
cp -R output/* docs/

echo "✅ Bestanden gekopieerd naar docs/"

# 2. Ga naar de docs map en draai het generatie script
cd docs || exit
echo "⚙️  Bezig met genereren van data.js..."
python3 generate_data.py

# 3. Ga terug naar de root
cd ..

echo "🎉 Klaar! De website is bijgewerkt."
