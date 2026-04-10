/**
 * Strategy Meeting with Jensen Huang — Frontend
 */

const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const welcomeScreen = document.getElementById('welcome');
const startBtn = document.getElementById('start-btn');
const newMeetingBtn = document.getElementById('new-meeting-btn');
const modelSelect = document.getElementById('model-select');

const exportGroup = document.getElementById('export-group');
const exportSummaryBtn = document.getElementById('export-summary-btn');
const exportTranscriptBtn = document.getElementById('export-transcript-btn');
const exportModal = document.getElementById('export-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const modalClose = document.getElementById('modal-close');
const modalCopy = document.getElementById('modal-copy');
const modalDownload = document.getElementById('modal-download');

let conversationHistory = [];
let isStreaming = false;
let selectedModel = '';
let currentExportMarkdown = '';

// --- Load available models ---
async function loadModels() {
    try {
        const resp = await fetch('/api/models');
        const data = await resp.json();
        modelSelect.innerHTML = '';
        for (const [id, name] of Object.entries(data.models)) {
            const opt = document.createElement('option');
            opt.value = id;
            opt.textContent = name;
            if (id === data.default) opt.selected = true;
            modelSelect.appendChild(opt);
        }
        selectedModel = modelSelect.value;
    } catch (e) {
        console.error('Failed to load models:', e);
    }
}

modelSelect.addEventListener('change', () => {
    selectedModel = modelSelect.value;
});

// --- Markdown rendering (lightweight) ---
function renderMarkdown(text) {
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Tables
    html = html.replace(/^(\|.+\|)\n(\|[-| :]+\|)\n((?:\|.+\|\n?)+)/gm, (match, headerRow, sepRow, bodyRows) => {
        const headers = headerRow.split('|').filter(c => c.trim());
        const rows = bodyRows.trim().split('\n').map(r => r.split('|').filter(c => c.trim()));
        let table = '<table><thead><tr>';
        headers.forEach(h => table += `<th>${h.trim()}</th>`);
        table += '</tr></thead><tbody>';
        rows.forEach(row => {
            table += '<tr>';
            row.forEach(cell => table += `<td>${cell.trim()}</td>`);
            table += '</tr>';
        });
        table += '</tbody></table>';
        return table;
    });

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');

    // Bold and italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Paragraphs
    html = html.replace(/\n\n+/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Clean up
    html = html.replace(/<p>\s*<\/p>/g, '');
    html = html.replace(/<p>(<h[23]>)/g, '$1');
    html = html.replace(/(<\/h[23]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<table>)/g, '$1');
    html = html.replace(/(<\/table>)<\/p>/g, '$1');

    return html;
}

// --- Message rendering ---
function addMessage(role, content) {
    if (welcomeScreen) welcomeScreen.style.display = 'none';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    const label = document.createElement('div');
    label.className = 'message-label';

    if (role === 'jensen') {
        label.innerHTML = `<img src="/static/jensen-avatar.svg" alt="" class="msg-avatar"><span>Jensen</span>`;
    } else {
        label.innerHTML = `<span>You</span>`;
    }

    const body = document.createElement('div');
    body.className = 'message-content';
    body.innerHTML = renderMarkdown(content);

    msgDiv.appendChild(label);
    msgDiv.appendChild(body);
    chatContainer.appendChild(msgDiv);
    scrollToBottom();

    return body;
}

function createStreamingMessage() {
    if (welcomeScreen) welcomeScreen.style.display = 'none';

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message jensen';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.innerHTML = `<img src="/static/jensen-avatar.svg" alt="" class="msg-avatar"><span>Jensen</span>`;

    const body = document.createElement('div');
    body.className = 'message-content';
    body.innerHTML = '<p></p>';

    msgDiv.appendChild(label);
    msgDiv.appendChild(body);
    chatContainer.appendChild(msgDiv);

    return body;
}

function showThinking() {
    const el = document.createElement('div');
    el.className = 'thinking';
    el.id = 'thinking-indicator';
    el.innerHTML = `
        <div class="thinking-pulse"><span></span><span></span><span></span></div>
        <span class="thinking-text">Jensen is thinking...</span>
    `;
    chatContainer.appendChild(el);
    scrollToBottom();
}

function hideThinking() {
    const el = document.getElementById('thinking-indicator');
    if (el) el.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function setInputEnabled(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    if (enabled) messageInput.focus();
}

// --- SSE streaming ---
async function streamResponse(url, body = null) {
    isStreaming = true;
    setInputEnabled(false);
    showThinking();

    let fullText = '';
    let bubble = null;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body || {}),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;

                let data;
                try {
                    data = JSON.parse(line.slice(6));
                } catch {
                    continue;
                }

                if (data.error) {
                    hideThinking();
                    addMessage('jensen', `Error: ${data.error}`);
                    isStreaming = false;
                    setInputEnabled(true);
                    return null;
                }

                if (data.done) break;

                if (data.text) {
                    if (!bubble) {
                        hideThinking();
                        bubble = createStreamingMessage();
                    }
                    fullText += data.text;
                    bubble.innerHTML = renderMarkdown(fullText);
                    scrollToBottom();
                }
            }
        }
    } catch (err) {
        hideThinking();
        addMessage('jensen', `Connection error: ${err.message}`);
        isStreaming = false;
        setInputEnabled(true);
        return null;
    }

    hideThinking();
    isStreaming = false;
    setInputEnabled(true);
    return fullText;
}

// --- Start meeting ---
async function startMeeting() {
    if (startBtn) startBtn.disabled = true;

    const jensenText = await streamResponse('/api/start', { model: selectedModel });

    if (jensenText) {
        conversationHistory.push({
            role: 'user',
            content: '[The user has just entered the strategy meeting room. Jensen is at the whiteboard. Open the meeting in character — set the scene and invite them to share what they\'re building.]'
        });
        conversationHistory.push({
            role: 'assistant',
            content: jensenText
        });
        showExportButtons();
    }
}

// --- Send message ---
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isStreaming) return;

    messageInput.value = '';
    messageInput.style.height = 'auto';

    addMessage('user', text);
    conversationHistory.push({ role: 'user', content: text });

    const jensenText = await streamResponse('/api/chat', {
        messages: conversationHistory,
        model: selectedModel,
    });

    if (jensenText) {
        conversationHistory.push({ role: 'assistant', content: jensenText });
    }
}

// --- New meeting ---
function newMeeting() {
    conversationHistory = [];
    chatContainer.innerHTML = '';
    if (exportGroup) exportGroup.style.display = 'none';
    if (welcomeScreen) {
        welcomeScreen.style.display = 'flex';
        if (startBtn) startBtn.disabled = false;
    }
}

// --- Event listeners ---
sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + 'px';
});

startBtn.addEventListener('click', startMeeting);
newMeetingBtn.addEventListener('click', newMeeting);

// --- Export: show buttons once meeting starts ---
function showExportButtons() {
    if (exportGroup) exportGroup.style.display = 'flex';
}

// --- Export: full transcript ---
function exportTranscript() {
    const lines = conversationHistory
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => {
            const speaker = m.role === 'assistant' ? '**Jensen:**' : '**You:**';
            return `${speaker} ${m.content}`;
        });

    const md = lines.join('\n\n');
    showModal('Full Transcript', md);
}

// --- Export: AI-generated summary (streamed) ---
async function exportSummary() {
    if (isStreaming || conversationHistory.length === 0) return;

    showModal('Meeting Summary', '');
    modalBody.innerHTML = '<p class="generating">Jensen is preparing the summary...</p>';

    isStreaming = true;
    let fullText = '';

    try {
        const response = await fetch('/api/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversationHistory, model: selectedModel }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                let data;
                try { data = JSON.parse(line.slice(6)); } catch { continue; }

                if (data.error) {
                    modalBody.innerHTML = `<p>Error: ${data.error}</p>`;
                    isStreaming = false;
                    return;
                }
                if (data.done) break;
                if (data.text) {
                    fullText += data.text;
                    modalBody.innerHTML = renderMarkdown(fullText);
                }
            }
        }
    } catch (err) {
        modalBody.innerHTML = `<p>Error: ${err.message}</p>`;
    }

    currentExportMarkdown = fullText;
    isStreaming = false;
}

// --- Modal ---
function showModal(title, markdown) {
    currentExportMarkdown = markdown;
    modalTitle.textContent = title;
    modalBody.innerHTML = markdown ? renderMarkdown(markdown) : '';
    exportModal.style.display = 'flex';
}

function closeModal() {
    exportModal.style.display = 'none';
}

function copyExport() {
    navigator.clipboard.writeText(currentExportMarkdown).then(() => {
        const btn = modalCopy;
        btn.textContent = 'Copied';
        setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
    });
}

function downloadExport() {
    const title = modalTitle.textContent.toLowerCase().replace(/\s+/g, '-');
    const date = new Date().toISOString().slice(0, 10);
    const filename = `jensen-${title}-${date}.md`;
    const blob = new Blob([currentExportMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

modalClose.addEventListener('click', closeModal);
exportModal.addEventListener('click', (e) => { if (e.target === exportModal) closeModal(); });
modalCopy.addEventListener('click', copyExport);
modalDownload.addEventListener('click', downloadExport);
exportSummaryBtn.addEventListener('click', exportSummary);
exportTranscriptBtn.addEventListener('click', exportTranscript);

loadModels();
