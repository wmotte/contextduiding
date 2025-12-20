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
    const backToTopBtn = document.getElementById('back-to-top');

    // --- State ---
    // Structure: { "GemeenteNaam": { "file.md": FileObject|String, ... } }
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

    function smartQuotes(text) {
        return text
            // Double quotes
            .replace(/(^|[-\u2014\s(\[{"'])"/g, '$1\u201c') // opening
            .replace(/"/g, '\u201d')                         // closing
            // Single quotes / apostrophes
            .replace(/(^|[-\u2014\s(\[{"'])'/g, '$1\u2018') // opening
            .replace(/'/g, '\u2019');                        // closing
    }

    // Fix relative links to point to the correct subdirectory
    function fixRelativeLinks(container, dirName) {
        const links = container.querySelectorAll('a');
        links.forEach(link => {
            const href = link.getAttribute('href');
            // Check if it's a relative link to a markdown file
            if (href && !href.startsWith('http') && !href.startsWith('/') && !href.startsWith('#') && href.endsWith('.md')) {
                link.setAttribute('href', `${dirName}/${href}`);
            }
        });
    }

    // Helper to read a File object as text or return string if already text
    function getFileContent(fileOrString) {
        if (typeof fileOrString === 'string') {
            return Promise.resolve(fileOrString);
        }
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(e);
            reader.readAsText(fileOrString);
        });
    }

    // --- Initialization ---
    function init() {
        if (window.CONTEXT_DATA) {
            municipalityData = window.CONTEXT_DATA;
            renderSidebar();
            setupScreen.classList.add('hidden');
            appContainer.classList.remove('hidden');
        }
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
            const parts = file.webkitRelativePath.split('/');
            
            if (parts.length < 2) continue;

            const fileName = parts[parts.length - 1];
            const dirName = parts[parts.length - 2];

            if (dirName.startsWith('.') || dirName === 'css' || dirName === 'js' || dirName === 'output') continue;
            if (['index.html', 'script.js', 'style.css', 'website_server.py', 'data.js', 'generate_data.py'].includes(fileName)) continue;
            if (!fileName.endsWith('.md')) continue;

            if (!municipalityData[dirName]) {
                municipalityData[dirName] = {};
            }
            municipalityData[dirName][fileName] = file;
        }

        renderSidebar();
        setupScreen.classList.add('hidden');
        appContainer.classList.remove('hidden');
    });

    // 2. Render Sidebar
    function renderSidebar() {
        municipalityList.innerHTML = '';
        const dirs = Object.keys(municipalityData).sort();

        if (dirs.length === 0) {
            municipalityList.innerHTML = '<li style="padding:20px; color:#999;">Geen geldige mappen gevonden.</li>';
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

        // Scroll to top of report container
        reportContainer.scrollTop = 0;
        // Hide FAB initially
        backToTopBtn.classList.remove('visible');

        // Reset content
        contentOverview.innerHTML = '<p>Laden...</p>';
        contentDetails.innerHTML = '';

        const filesMap = municipalityData[dirName];

        // --- Load Overview ---
        if (filesMap['00_overzicht.md']) {
            try {
                const text = await getFileContent(filesMap['00_overzicht.md']);
                contentOverview.innerHTML = marked.parse(smartQuotes(text));
                fixRelativeLinks(contentOverview, dirName);
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
                    const text = await getFileContent(filesMap[filename]);
                    
                    detailsHtml += `<div class="section-divider"></div>`;
                    // Note: Removed the injected button here
                    detailsHtml += `<div class="file-section" id="section-${filename}" data-file="${filename}">`;
                    detailsHtml += marked.parse(smartQuotes(text));
                    detailsHtml += `</div>`;
                } catch (e) {
                    console.warn(`Could not load ${filename}`, e);
                }
            }
        }

        contentDetails.innerHTML = detailsHtml;
        fixRelativeLinks(contentDetails, dirName);
    }

    // --- Link Handling ---
    document.body.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        // Check if it's an internal MD link
        if (href && href.endsWith('.md')) {
            e.preventDefault();
            
            const filename = href.split('/').pop();
            const targetSection = document.getElementById(`section-${filename}`);
            
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                console.warn(`Section for ${filename} not found.`);
            }
        }
    });

    // --- FAB Handling ---
    // Scroll listener on the report container
    reportContainer.addEventListener('scroll', () => {
        if (reportContainer.scrollTop > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    // Click listener for FAB
    backToTopBtn.addEventListener('click', () => {
        reportContainer.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Run Init
    init();
});
