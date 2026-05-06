const API_URL = 'http://localhost:8000';
let sessionId = null;
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = 'login.html';
}

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name-display');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const resultsSection = document.getElementById('results-section');
const uploadSection = document.getElementById('upload-section');
const actionArea = document.getElementById('action-area');

let selectedFile = null;

// ── File Upload Logic ──

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|jpg|jpeg|png|bmp|tiff|webp)$/i)) {
        alert('Please upload a PDF or image file (JPG, PNG).');
        return;
    }
    selectedFile = file;
    fileNameDisplay.textContent = `Selected: ${file.name}`;
    fileNameDisplay.classList.remove('hidden');
    actionArea.classList.remove('hidden');
    analyzeBtn.disabled = false;
}

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    loadingIndicator.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to analyze document');
        }

        const data = await response.json();
        sessionId = data.session_id;
        populateResults(data);
        
        loadingIndicator.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert(`Error: ${error.message}`);
        analyzeBtn.disabled = false;
        loadingIndicator.classList.add('hidden');
    }
});

// ── Results Population ──

function populateResults(data) {
    const { summary, missing_clauses, risk_scores, doc_type } = data;

    // Stats
    const highRisks = risk_scores.filter(r => r.score >= 7).length;
    const missingCount = missing_clauses.missing_count || 0;
    
    document.getElementById('stat-high-risk').textContent = highRisks;
    document.getElementById('stat-missing').textContent = missingCount;
    document.getElementById('stat-found').textContent = missing_clauses.found_count || 0;

    // Summary Tab
    document.getElementById('plain-summary').innerHTML = `<i class="fa-solid fa-lightbulb"></i> ${summary.plain_summary || 'No summary available.'}`;
    
    const keyDetailsHtml = (summary.key_details || []).map(d => `
        <div class="detail-row">
            <span class="detail-label">${d.label}</span>
            <span class="detail-value">${d.value}</span>
        </div>
    `).join('');
    document.getElementById('key-details-list').innerHTML = keyDetailsHtml;

    const risksHtml = (summary.top_risks || []).map(r => {
        const icon = r.severity === 'high' ? '🔴' : r.severity === 'medium' ? '🟡' : '🟢';
        return `<div class="risk-item">${icon} ${r.risk}</div>`;
    }).join('');
    document.getElementById('top-risks-list').innerHTML = risksHtml;

    // Risks Tab
    const risksAccordion = document.getElementById('risks-accordion');
    if (risk_scores && risk_scores.length) {
        risksAccordion.innerHTML = risk_scores.map((r, i) => {
            const labelClass = `badge-${r.risk_label.toLowerCase()}`;
            const bar = (r.score >= 7) ? '🔴'.repeat(Math.min(Math.floor(r.score/2),5)) : 
                        (r.score >= 4) ? '🟡'.repeat(Math.min(Math.floor(r.score/2),5)) : 
                        '🟢'.repeat(Math.min(Math.floor(r.score/2)+1,5));
                        
            return `
                <div class="accordion-item">
                    <button class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">
                            <span>Clause ${r.clause_index}</span>
                            <span style="font-size:0.8rem;color:#888">Risk: ${r.score}/10 ${bar}</span>
                            <span class="badge ${labelClass}">${r.risk_label}</span>
                        </div>
                        <i class="fa-solid fa-chevron-down"></i>
                    </button>
                    <div class="accordion-content">
                        <div class="clause-text">"${r.clause_text}"</div>
                        <p><strong>Risk Reason:</strong> ${r.risk_reason}</p>
                        <p><strong>Favors:</strong> <span style="text-transform:capitalize">${r.favors}</span></p>
                        ${r.suggestion && r.suggestion !== "No action needed" ? `<div class="suggestion-box">💡 <strong>Suggestion:</strong> ${r.suggestion}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    } else {
        risksAccordion.innerHTML = '<p>No clause risk data available.</p>';
    }

    // Missing Tab
    const missingList = document.getElementById('missing-items-list');
    const foundList = document.getElementById('found-items-list');
    
    if (missing_clauses.clauses && missing_clauses.clauses.length) {
        const missing = missing_clauses.clauses.filter(c => !c.found);
        const found = missing_clauses.clauses.filter(c => c.found);
        
        missingList.innerHTML = missing.map(c => `
            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: #F9FAFB; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                <span><strong>${c.name}</strong></span>
                <span class="badge badge-${c.severity || 'high'}">${(c.severity || 'high').toUpperCase()}</span>
            </div>
        `).join('');
        
        foundList.innerHTML = found.map(c => `
            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: #F9FAFB; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                <span>${c.name}</span>
                <span class="badge badge-low">FOUND</span>
            </div>
        `).join('');
    }

    // Reset Chat
    document.getElementById('chat-history').innerHTML = `
        <div class="chat-suggestions" id="chat-suggestions">
            <p>💡 Try asking:</p>
            <div class="suggestion-chips">
                <button class="chip" onclick="sendSuggestion('Can the landlord increase rent anytime?')">Can the landlord increase rent anytime?</button>
                <button class="chip" onclick="sendSuggestion('What happens if I want to leave early?')">What happens if I want to leave early?</button>
                <button class="chip" onclick="sendSuggestion('When will I get my deposit back?')">When will I get my deposit back?</button>
                <button class="chip" onclick="sendSuggestion('What are my rights in this document?')">What are my rights in this document?</button>
            </div>
        </div>
    `;
}

// ── Tabs Logic ──

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
});

// ── Accordion Logic ──

function toggleAccordion(header) {
    const item = header.parentElement;
    item.classList.toggle('active');
}

// ── Chat Logic ──

function sendSuggestion(text) {
    document.getElementById('chat-input').value = text;
    handleChatSubmit(new Event('submit'));
}

async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg || !sessionId) return;

    // Hide suggestions if present
    const suggs = document.getElementById('chat-suggestions');
    if (suggs) suggs.style.display = 'none';

    const history = document.getElementById('chat-history');
    
    // Add user message
    history.innerHTML += `<div class="chat-msg chat-user">🧑 ${msg}</div>`;
    input.value = '';
    
    // Scroll to bottom
    history.scrollTop = history.scrollHeight;

    // Loading
    const loadingId = 'loading-' + Date.now();
    history.innerHTML += `<div class="chat-msg chat-ai" id="${loadingId}">🤖 Thinking...</div>`;
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ question: msg, session_id: sessionId })
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }

        const data = await response.json();
        
        document.getElementById(loadingId).remove();
        
        let aiHtml = `<div class="chat-msg chat-ai">🤖 ${data.answer}`;
        if (data.source) {
            aiHtml += `<div class="chat-source">📌 Source: ${data.source}</div>`;
        }
        aiHtml += `</div>`;
        
        history.innerHTML += aiHtml;
        history.scrollTop = history.scrollHeight;

    } catch (error) {
        document.getElementById(loadingId).remove();
        history.innerHTML += `<div class="chat-msg chat-ai text-red">❌ Error: Could not get response</div>`;
        history.scrollTop = history.scrollHeight;
    }
}
