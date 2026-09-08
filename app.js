const fileInput = document.getElementById('fileInput');
const dropzone = document.getElementById('dropzone');

const viewUpload = document.getElementById('view-upload');
const viewProcessing = document.getElementById('view-processing');
const viewResults = document.getElementById('view-results');
const viewShortlist = document.getElementById('view-shortlist');

const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const successText = document.getElementById('successText');
const previewTableBody = document.getElementById('previewTableBody');
const shortlistTableBody = document.getElementById('shortlistTableBody');

const btnDownload = document.getElementById('btnDownload');
const btnReset = document.getElementById('btnReset');
const btnShortlist = document.getElementById('btnShortlist');
const btnBackToResults = document.getElementById('btnBackToResults');
const btnRunSearch = document.getElementById('btnRunSearch');

const jdInput = document.getElementById('jdInput');
const nameFilter = document.getElementById('nameFilter');

let allExtractedData = [];

// Comprehensive tech skills list
const TECH_SKILLS = [
    "JavaScript", "Python", "Java", "C++", "C#", "React", "Node.js", "Angular", "Vue",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "AWS", "Azure", "GCP", "Docker",
    "Kubernetes", "Git", "CI/CD", "Machine Learning", "Data Science", "HTML", "CSS", "Tailwind",
    "TypeScript", "Go", "Rust", "Ruby", "PHP", "Laravel", "Django", "Flask", "Spring Boot",
    "Next.js", "GraphQL", "REST API", "Salesforce", "Excel", "Data Analysis", "Project Management",
    "Figma", "UI/UX", "Product Management", "Agile", "Scrum"
];

// --- File Selection Handlers ---

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-gray-500', 'bg-white/10');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-gray-500', 'bg-white/10');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-gray-500', 'bg-white/10');
    
    // File input is handled via change event if we assign files, but let's just trigger process directly
    const files = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf') || f.name.toLowerCase().endsWith('.docx'));
    if (files.length > 0) {
        processFiles(files);
    } else {
        alert("Please drop valid .pdf or .docx files.");
    }
});

fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        processFiles(files);
    }
    // Reset input so the same files can be selected again if needed
    fileInput.value = '';
});

// --- Extraction Logic ---

async function extractTextFromPDF(file) {
    const arrayBuffer = await file.arrayBuffer();
    // Use Uint8Array for maximum compatibility with pdf.js
    const uint8Array = new Uint8Array(arrayBuffer);
    const pdf = await pdfjsLib.getDocument({ data: uint8Array }).promise;
    let fullText = "";

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(" ");
        fullText += pageText + "\n";
    }
    return fullText;
}

async function extractTextFromDOCX(file) {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer });
    return result.value;
}

// --- Main Processing Flow ---

async function processFiles(files) {
    // Switch to Processing View
    viewUpload.classList.add('hidden');
    viewProcessing.classList.remove('hidden');
    viewProcessing.classList.add('flex');
    
    allExtractedData = [];
    previewTableBody.innerHTML = '';
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update Progress UI
        const percent = Math.round((i / files.length) * 100);
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `Analyzing ${file.name} (${i + 1}/${files.length})`;

        try {
            let fullText = "";
            const filenameLower = file.name.toLowerCase();

            if (filenameLower.endsWith('.pdf')) {
                fullText = await extractTextFromPDF(file);
            } else if (filenameLower.endsWith('.docx')) {
                fullText = await extractTextFromDOCX(file);
            }

            const parsedData = parseResumeText(fullText, file.name);
            parsedData.fullText = fullText; // Store full text for JD matching algorithm
            allExtractedData.push(parsedData);
            
            // Inject row into preview table
            renderTableRow(parsedData);

        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            // Push failed row
            const failedData = {
                "File Name": file.name,
                "Candidate Name": "Extraction Failed",
                "Email": "N/A",
                "Phone": "N/A",
                "Top Skills": "N/A",
                "All Skills": "N/A",
                "Status": "Error"
            };
            allExtractedData.push(failedData);
            renderTableRow(failedData);
        }
    }

    // Processing Complete
    progressBar.style.width = `100%`;
    progressText.textContent = `Finalizing database...`;
    
    // Add artificial tiny delay for smooth UX transition
    setTimeout(() => {
        viewProcessing.classList.remove('flex');
        viewProcessing.classList.add('hidden');
        
        viewResults.classList.remove('hidden');
        viewResults.classList.add('flex');
        
        successText.textContent = `Successfully processed ${files.length} document${files.length > 1 ? 's' : ''}.`;
    }, 800);
}

function renderTableRow(data) {
    const tr = document.createElement('tr');
    tr.className = "hover:bg-white/5 transition-colors";
    
    // Format skills cleanly
    let skillsHtml = '<span class="text-gray-400 italic">None</span>';
    if (data["Top Skills"] && data["Top Skills"] !== "None Detected" && data["Top Skills"] !== "N/A") {
        const skillsArray = data["Top Skills"].split(', ');
        skillsHtml = skillsArray.map(s => `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700 mr-1.5 mb-1 shadow-sm">${s}</span>`).join('');
    }

    // Format status
    const isError = data["Status"] === "Error";
    const statusHtml = isError 
        ? `<span class="inline-flex items-center gap-1 text-xs font-medium text-red-600"><i class="ph-fill ph-warning-circle"></i> Error</span>`
        : `<span class="inline-flex items-center gap-1 text-xs font-medium text-green-600"><i class="ph-bold ph-check"></i> OK</span>`;

    tr.innerHTML = `
        <td class="px-6 py-4 font-medium text-gray-200">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 shrink-0">
                    <i class="ph-fill ph-user"></i>
                </div>
                <div>
                    <p class="truncate max-w-[150px]" title="${data["Candidate Name"]}">${data["Candidate Name"]}</p>
                    <p class="text-[10px] text-gray-400 truncate max-w-[150px]" title="${data["File Name"]}">${data["File Name"]}</p>
                </div>
            </div>
        </td>
        <td class="px-6 py-4">
            <p class="text-sm truncate max-w-[180px] text-gray-400" title="${data["Email"]}"><i class="ph ph-envelope-simple mr-1 text-gray-400"></i>${data["Email"]}</p>
            <p class="text-xs text-gray-400 mt-0.5"><i class="ph ph-phone mr-1 text-gray-400"></i>${data["Phone"]}</p>
        </td>
        <td class="px-6 py-4 max-w-[200px] flex-wrap items-center pt-5 border-none">
            ${skillsHtml}
        </td>
        <td class="px-6 py-4">
            ${statusHtml}
        </td>
    `;
    previewTableBody.appendChild(tr);
}

// --- Regex Parser ---

function parseResumeText(text, filename) {
    // 1. Email (Stricter regex to avoid false positives)
    const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i;
    const emailMatch = text.match(emailRegex);
    const email = emailMatch ? emailMatch[1].trim() : "Not Found";

    // 2. Phone
    const phoneRegex = /(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/;
    const phoneMatch = text.match(phoneRegex);
    const phone = phoneMatch ? phoneMatch[0].trim() : "Not Found";

    // 3. Name Heuristic
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 2);
    let name = "Not Found";
    for (let i = 0; i < Math.min(15, lines.length); i++) {
        let line = lines[i];
        if (!line.includes('@') && !/\d{4}/.test(line) && line.split(' ').length <= 4) {
            line = line.replace(/resume|cv|curriculum vitae|page/ig, '').trim();
            if (line.length > 3) {
                // Title case the name cleanly
                name = line.replace(
                    /\w\S*/g,
                    (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
                );
                break;
            }
        }
    }

    if (name === "Not Found") {
        name = filename.replace(/\.(pdf|docx)$/i, '').replace(/[-_]/g, ' ').trim();
    }

    // 4. Skills extraction
    const foundSkills = [];
    const lowerText = text.toLowerCase();
    TECH_SKILLS.forEach(skill => {
        const skillRegex = new RegExp(`\\b${skill.toLowerCase().replace('+', '\\+')}\\b`, 'i');
        if (skillRegex.test(lowerText)) {
            foundSkills.push(skill);
        }
    });

    const topSkills = foundSkills.length > 0 ? foundSkills.slice(0, 4).join(", ") : "None Detected";
    const allSkills = foundSkills.length > 0 ? foundSkills.join(", ") : "None Detected";

    return {
        "File Name": filename,
        "Candidate Name": name,
        "Email": email,
        "Phone": phone,
        "Top Skills": topSkills,
        "All Skills": allSkills,
        "Status": "Processed"
    };
}

// --- Excel Export ---

async function generateStyledExcel(dataArray, filename) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet("Resume Database");

    worksheet.columns = [
        { header: 'Candidate Name', key: 'Candidate Name', width: 25 },
        { header: 'Email', key: 'Email', width: 30 },
        { header: 'Phone', key: 'Phone', width: 20 },
        { header: 'Top Skills', key: 'Top Skills', width: 40 },
        { header: 'All Skills', key: 'All Skills', width: 60 },
        { header: 'File Name', key: 'File Name', width: 25 },
        { header: 'Status', key: 'Status', width: 12 }
    ];

    worksheet.addRows(dataArray);

    // Header Style
    worksheet.getRow(1).eachCell((cell) => {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0D1117' } }; // Black header
        cell.font = { color: { argb: 'FFFFFFFF' }, bold: true, size: 11 };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
    });

    // Row Styles
    worksheet.eachRow((row, rowNumber) => {
        if (rowNumber === 1) return;
        row.eachCell((cell, colNumber) => {
            cell.border = { bottom: {style:'thin', color: {argb:'FF1F2937'}} };
            if ([4, 5].includes(colNumber)) {
                cell.alignment = { vertical: 'top', horizontal: 'left', wrapText: true };
            } else {
                cell.alignment = { vertical: 'middle', horizontal: 'left' };
            }
        });
    });

    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// --- Buttons ---

btnDownload.addEventListener('click', async () => {
    if (allExtractedData.length === 0) return;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
    await generateStyledExcel(allExtractedData, `resume_database_${timestamp}.xlsx`);
});

btnReset.addEventListener('click', () => {
    viewResults.classList.remove('flex');
    viewResults.classList.add('hidden');
    
    viewUpload.classList.remove('hidden');
    viewUpload.classList.add('flex');
    
    allExtractedData = [];
    progressBar.style.width = '0%';
});

// --- Shortlist & JD Matching Logic ---

btnShortlist.addEventListener('click', () => {
    viewResults.classList.remove('flex');
    viewResults.classList.add('hidden');
    viewShortlist.classList.remove('hidden');
    viewShortlist.classList.add('flex');
});

btnBackToResults.addEventListener('click', () => {
    viewShortlist.classList.remove('flex');
    viewShortlist.classList.add('hidden');
    viewResults.classList.remove('hidden');
    viewResults.classList.add('flex');
});

btnRunSearch.addEventListener('click', () => {
    const jdText = jdInput.value.toLowerCase();
    const nameQuery = nameFilter.value.toLowerCase().trim();
    
    // Extract required keywords from JD (simple whitespace split and remove punctuation)
    const jdWords = [...new Set(jdText.replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length > 2))];

    // Score each resume
    let scoredData = allExtractedData.map(data => {
        let score = 0;
        
        // Skip rows that failed extraction
        if (data["Status"] === "Error") return null;

        // Name filter constraint
        if (nameQuery && !data["Candidate Name"].toLowerCase().includes(nameQuery)) {
            return null; 
        }
        
        // TF-IDF simplified: Keyword frequency
        if (jdWords.length > 0 && data.fullText) {
            const resumeTextLower = data.fullText.toLowerCase();
            let matches = 0;
            jdWords.forEach(word => {
                // Check if word exists as a whole word in resume text
                const regex = new RegExp(`\\b${word}\\b`);
                if (regex.test(resumeTextLower)) {
                    matches++;
                }
            });
            score = Math.round((matches / jdWords.length) * 100);
        } else if (jdWords.length === 0 && nameQuery) {
            score = 100; // If only name is searched, consider it a 100% match
        }
        
        return { ...data, matchScore: score };
    }).filter(d => d !== null);

    // Sort by descending score
    scoredData.sort((a, b) => b.matchScore - a.matchScore);

    // Render Shortlist
    shortlistTableBody.innerHTML = '';
    
    if (scoredData.length === 0) {
        shortlistTableBody.innerHTML = `<tr><td colspan="3" class="px-6 py-4 text-center text-gray-400">No matching candidates found.</td></tr>`;
        return;
    }

    scoredData.forEach(data => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-white/5 transition-colors";
        
        // Color code the score
        let scoreColor = "text-gray-400";
        if (data.matchScore >= 80) scoreColor = "text-green-600 font-bold";
        else if (data.matchScore >= 50) scoreColor = "text-yellow-600 font-medium";
        
        // Format skills cleanly
        let skillsHtml = '<span class="text-gray-400 italic">None</span>';
        if (data["Top Skills"] && data["Top Skills"] !== "None Detected" && data["Top Skills"] !== "N/A") {
            const skillsArray = data["Top Skills"].split(', ');
            skillsHtml = skillsArray.map(s => `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700 mr-1.5 mb-1 shadow-sm">${s}</span>`).join('');
        }

        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="${scoreColor} text-lg">${data.matchScore}%</span>
            </td>
            <td class="px-6 py-4 font-medium text-gray-200">
                <p class="truncate max-w-[200px]" title="${data["Candidate Name"]}">${data["Candidate Name"]}</p>
                <p class="text-[10px] text-gray-400 truncate max-w-[200px]" title="${data["File Name"]}">${data["File Name"]}</p>
            </td>
            <td class="px-6 py-4 max-w-[250px] flex-wrap items-center pt-5 border-none">
                ${skillsHtml}
            </td>
        `;
        shortlistTableBody.appendChild(tr);
    });
});
