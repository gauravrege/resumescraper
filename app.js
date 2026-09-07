const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const statusDiv = document.getElementById('status');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultDiv = document.getElementById('result');
const successText = document.getElementById('successText');
const btnDownloadCombined = document.getElementById('btnDownloadCombined');
const resetBtn = document.getElementById('resetBtn');

let allExtractedData = [];

const TECH_SKILLS = [
    "JavaScript", "Python", "Java", "C++", "C#", "React", "Node.js", "Angular", "Vue",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "AWS", "Azure", "GCP", "Docker",
    "Kubernetes", "Git", "CI/CD", "Machine Learning", "Data Science", "HTML", "CSS", "Tailwind",
    "TypeScript", "Go", "Rust", "Ruby", "PHP", "Laravel", "Django", "Flask", "Spring Boot",
    "Next.js", "GraphQL", "REST API", "Salesforce", "Excel", "Data Analysis", "Project Management"
];

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-indigo-500', 'bg-indigo-50');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-indigo-500', 'bg-indigo-50');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-indigo-500', 'bg-indigo-50');
    const files = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf') || f.name.toLowerCase().endsWith('.docx'));
    if (files.length > 0) {
        processFiles(files);
    } else {
        alert("Please drop valid .pdf or .docx files.");
    }
});

dropzone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        processFiles(files);
    }
});

async function extractTextFromPDF(file) {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
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

async function processFiles(files) {
    dropzone.classList.add('hidden');
    statusDiv.classList.remove('hidden');
    allExtractedData = [];
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update Progress UI
        const percent = Math.round(((i) / files.length) * 100);
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `Extracting ${file.name} (${i + 1} of ${files.length})...`;

        try {
            let fullText = "";
            const filenameLower = file.name.toLowerCase();

            if (filenameLower.endsWith('.pdf')) {
                fullText = await extractTextFromPDF(file);
            } else if (filenameLower.endsWith('.docx')) {
                fullText = await extractTextFromDOCX(file);
            }

            const parsedData = parseResumeText(fullText, file.name);
            allExtractedData.push(parsedData);
            
            // Inject row into preview table
            const tr = document.createElement('tr');
            tr.className = "hover:bg-gray-50 transition-colors";
            tr.innerHTML = `
                <td class="px-4 py-3 font-medium text-gray-900 border-b">${parsedData["Candidate Name"]}</td>
                <td class="px-4 py-3 border-b">${parsedData["Email"]}</td>
                <td class="px-4 py-3 border-b">${parsedData["Phone"]}</td>
                <td class="px-4 py-3 border-b">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                        ${parsedData["Top Skills"].split(', ').slice(0,3).join('</span> <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 ml-1">')}
                    </span>
                </td>
            `;
            document.getElementById('previewTableBody').appendChild(tr);

        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
        }
    }

    // Finished
    progressBar.style.width = \`100%\`;
    progressText.textContent = \`\${files.length} of \${files.length} completed\`;
    
    setTimeout(() => {
        statusDiv.classList.add('hidden');
        resultDiv.classList.remove('hidden');
        successText.textContent = \`Successfully extracted \${files.length} resume(s)!\`;
    }, 500);
}

// Highly targeted regex parser for resumes
function parseResumeText(text, filename) {
    // 1. Email
    const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/i;
    const emailMatch = text.match(emailRegex);
    const email = emailMatch ? emailMatch[1].trim() : "Not Found";

    // 2. Phone
    const phoneRegex = /(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/;
    const phoneMatch = text.match(phoneRegex);
    const phone = phoneMatch ? phoneMatch[0].trim() : "Not Found";

    // 3. Extract Name (Heuristic: usually at the very top, before long texts)
    // Grab the first non-empty line that doesn't have an @ or numbers
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 2);
    let name = "Not Found";
    for (let i = 0; i < Math.min(10, lines.length); i++) {
        let line = lines[i];
        if (!line.includes('@') && !/\d{5}/.test(line) && line.split(' ').length <= 4) {
            // Remove common header fluff
            line = line.replace(/resume|cv|curriculum vitae/ig, '').trim();
            if (line.length > 2) {
                name = line;
                break;
            }
        }
    }

    // If still not found, try to use filename without extension
    if (name === "Not Found" || name.toLowerCase() === "not found") {
        name = filename.replace(/\.(pdf|docx)$/i, '').replace(/[-_]/g, ' ').trim();
    }

    // 4. Skills extraction
    const foundSkills = [];
    const lowerText = text.toLowerCase();
    TECH_SKILLS.forEach(skill => {
        // Use word boundary to avoid partial matches
        const skillRegex = new RegExp(`\\b${skill.toLowerCase().replace('+', '\\+')}\\b`, 'i');
        if (skillRegex.test(lowerText)) {
            foundSkills.push(skill);
        }
    });

    const topSkills = foundSkills.length > 0 ? foundSkills.slice(0, 5).join(", ") : "None Detected";
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

// --- Helper: Generate Beautiful Excel ---
async function generateStyledExcel(dataArray, filename) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet("Resume Data");

    // Define columns and optimal widths
    worksheet.columns = [
        { header: 'Candidate Name', key: 'Candidate Name', width: 25 },
        { header: 'Email', key: 'Email', width: 30 },
        { header: 'Phone', key: 'Phone', width: 20 },
        { header: 'Top Skills', key: 'Top Skills', width: 40 },
        { header: 'All Skills', key: 'All Skills', width: 60 },
        { header: 'File Name', key: 'File Name', width: 25 },
        { header: 'Status', key: 'Status', width: 15 }
    ];

    // Add data rows
    worksheet.addRows(dataArray);

    // Style the Header Row
    worksheet.getRow(1).eachCell((cell) => {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4F46E5' } }; // Indigo 600
        cell.font = { color: { argb: 'FFFFFFFF' }, bold: true, size: 12 };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = {
            top: {style:'thin', color: {argb:'FFD1D5DB'}}, left: {style:'thin', color: {argb:'FFD1D5DB'}},
            bottom: {style:'thin', color: {argb:'FFD1D5DB'}}, right: {style:'thin', color: {argb:'FFD1D5DB'}}
        };
    });

    // Style Data Rows
    worksheet.eachRow((row, rowNumber) => {
        if (rowNumber === 1) return; // Skip header

        row.eachCell((cell, colNumber) => {
            cell.border = {
                top: {style:'thin', color: {argb:'FFD1D5DB'}}, left: {style:'thin', color: {argb:'FFD1D5DB'}},
                bottom: {style:'thin', color: {argb:'FFD1D5DB'}}, right: {style:'thin', color: {argb:'FFD1D5DB'}}
            };
            
            // Left-align text for better readability on long skills strings
            if ([4, 5].includes(colNumber)) {
                cell.alignment = { vertical: 'top', horizontal: 'left', wrapText: true };
            } else {
                cell.alignment = { vertical: 'middle', horizontal: 'left' };
            }
        });
    });

    // Create file buffer and trigger download in browser
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// --- Download Combined Excel ---
btnDownloadCombined.addEventListener('click', async () => {
    if (allExtractedData.length === 0) return;
    await generateStyledExcel(allExtractedData, "parsed_resumes.xlsx");
});

// Reset UI
resetBtn.addEventListener('click', () => {
    resultDiv.classList.add('hidden');
    dropzone.classList.remove('hidden');
    fileInput.value = '';
    allExtractedData = [];
    document.getElementById('previewTableBody').innerHTML = '';
    progressBar.style.width = '0%';
});
