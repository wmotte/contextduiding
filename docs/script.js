document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const setupScreen = document.getElementById('setup-screen');
    const appContainer = document.getElementById('app-container');
    const folderInput = document.getElementById('folder-input');
    const municipalityList = document.getElementById('municipality-list');
    const pageTitle = document.getElementById('page-title');
    const placeholder = document.getElementById('placeholder-message');
    const reportContainer = document.getElementById('report-container');
    const contentOverview = document.getElementById('content-overview');
    const contentDetails = document.getElementById('content-details');
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- State ---
    // Structure: { "GemeenteNaam": { "file.md": FileObject, ... } }
    let municipalityData = {};

    // List of files to load for the details view (in order)
    const detailFilesOrder = [
        '00_zondag_kerkelijk_jaar.md',
        '01_sociaal_maatschappelijke_context.md',
        '02_waardenorientatie.md',
        '03_geloofsorientatie.md',
        '04_interpretatieve_synthese.md',
        '05_actueel_wereldnieuws.md',
        '06_politieke_orientatie.md',
        '07_exegese.md',
        '08_kunst_cultuur.md',
        '09_focus_en_functie.md'
    ];

    // --- Helpers ---
    function formatName(name) {
        return name.replace(/_/g, ' ');
    }

    // Helper to read a File object as text
    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(e);
            reader.readAsText(file);
        });
    }

    // --- Event Listeners ---

    // 1. Handle Folder Selection
    folderInput.addEventListener('change', (event) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        municipalityData = {}; // Reset

        // Process files
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            // webkitRelativePath example: "output/Gemeente/file.md" or "Gemeente/file.md"
            // We want to detect the municipality folder.
            // Assumption: The user selects the 'output' folder, so path is like "output/Gemeente_X/file.md"
            // OR user selects inside output, so path is "Gemeente_X/file.md"
            
            const parts = file.webkitRelativePath.split('/');
            
            // We need at least 2 parts (Folder/File)
            if (parts.length < 2) continue;

            // Simple heuristic: The municipality is the folder directly containing the MD files.
            // We look for the folder that contains "00_overzicht.md" to confirm it's a valid target.
            // But since we are iterating, we just organize by parent folder name.
            
            // Let's assume the structure: Root -> Municipality -> File
            // If user selects "output", parts[0] is "output", parts[1] is Municipality
            // If user selects specific folders, parts[0] is Municipality.
            
            // Let's try to find the directory name that holds these specific files.
            const fileName = parts[parts.length - 1];
            const dirName = parts[parts.length - 2];

            // Filter out system files, css, js, etc.
            if (dirName.startsWith('.') || dirName === 'css' || dirName === 'js' || dirName === 'output') continue;
            
            // Ignore the website files themselves if they are in the list
            if (['index.html', 'script.js', 'style.css', 'website_server.py'].includes(fileName)) continue;

            // Only care about .md files for now
            if (!fileName.endsWith('.md')) continue;

            if (!municipalityData[dirName]) {
                municipalityData[dirName] = {};
            }
            municipalityData[dirName][fileName] = file;
        }

        // Render Sidebar
        renderSidebar();

        // Switch View
        setupScreen.classList.add('hidden');
        appContainer.classList.remove('hidden');
    });

    // 2. Render Sidebar
    function renderSidebar() {
        municipalityList.innerHTML = '';
        const dirs = Object.keys(municipalityData).sort();

        if (dirs.length === 0) {
            municipalityList.innerHTML = '<li style="padding:20px; color:#999;">Geen geldige mappen gevonden. Selecteer de "output" map.</li>';
            return;
        }

        dirs.forEach(dir => {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.textContent = formatName(dir);
            btn.onclick = () => loadReport(dir, btn);
            li.appendChild(btn);
            municipalityList.appendChild(li);
        });
    }

    // 3. Load Report Logic
    async function loadReport(dirName, btnElement) {
        // UI Update
        document.querySelectorAll('#municipality-list button').forEach(b => b.classList.remove('active'));
        btnElement.classList.add('active');
        
        pageTitle.textContent = formatName(dirName);
        placeholder.classList.add('hidden');
        reportContainer.classList.remove('hidden');

        // Reset content
        contentOverview.innerHTML = '<p>Laden...</p>';
        contentDetails.innerHTML = '<p>Laden...</p>';

        const filesMap = municipalityData[dirName];

        // --- Load Overview ---
        if (filesMap['00_overzicht.md']) {
            try {
                const text = await readFileAsText(filesMap['00_overzicht.md']);
                contentOverview.innerHTML = marked.parse(text);
            } catch (e) {
                console.error(e);
                contentOverview.innerHTML = '<p>Fout bij laden overzicht.</p>';
            }
        } else {
            contentOverview.innerHTML = '<p><em>Geen overzicht beschikbaar.</em></p>';
        }

        // --- Load Details ---
        let detailsHtml = '';
        
        for (const filename of detailFilesOrder) {
            if (filesMap[filename]) {
                try {
                    const text = await readFileAsText(filesMap[filename]);
                    
                    detailsHtml += `<div class="section-divider"></div>`;
                    detailsHtml += `<div class="file-section" data-file="${filename}">`;
                    detailsHtml += marked.parse(text);
                    detailsHtml += `</div>`;
                } catch (e) {
                    console.warn(`Could not load ${filename}`, e);
                }
            }
        }

        if (detailsHtml === '') {
            contentDetails.innerHTML = '<p>Geen detailbestanden gevonden.</p>';
        } else {
            contentDetails.innerHTML = detailsHtml;
        }
    }

    // 4. Tab Switching
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            navBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            
            // Show target
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
});