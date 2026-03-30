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

// Conversation history sent to backend
let conversationHistory = [];
let isStreaming = false;
let selectedModel = '';

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
    // Escape HTML
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

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');
    html = html.replace(/<p>(<h[23]>)/g, '$1');
    html = html.replace(/(<\/h[23]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<table>)/g, '$1');
    html = html.replace(/(<\/table>)<\/p>/g, '$1');

    return html;
}

// --- Message rendering ---
function addMessage(role, content) {
    // Remove welcome screen if present
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    if (role === 'jensen') {
        avatar.innerHTML = '<img src="/static/jensen-avatar.svg" alt="Jensen" style="width:28px;height:28px">';
    } else {
        avatar.textContent = '💬';
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = renderMarkdown(content);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatContainer.appendChild(msgDiv);
    scrollToBottom();

    return bubble;
}

function createStreamingMessage() {
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message jensen';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = '<img src="/static/jensen-avatar.svg" alt="Jensen" style="width:28px;height:28px">';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = '<p></p>';

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatContainer.appendChild(msgDiv);

    return bubble;
}

function showThinking() {
    const thinking = document.createElement('div');
    thinking.className = 'thinking';
    thinking.id = 'thinking-indicator';
    thinking.innerHTML = `
        <div class="dots">
            <span></span><span></span><span></span>
        </div>
        <span>Jensen is thinking...</span>
    `;
    chatContainer.appendChild(thinking);
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
    if (enabled) {
        messageInput.focus();
    }
}

// --- SSE streaming ---
async function streamResponse(url, body = null) {
    isStreaming = true;
    setInputEnabled(false);
    showThinking();

    let fullText = '';
    let bubble = null;

    try {
        const options = {
            method: body ? 'POST' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body || {}),
        };

        const response = await fetch(url, options);

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

                const jsonStr = line.slice(6);
                let data;
                try {
                    data = JSON.parse(jsonStr);
                } catch {
                    continue;
                }

                if (data.error) {
                    hideThinking();
                    addMessage('jensen', `⚠️ Error: ${data.error}`);
                    isStreaming = false;
                    setInputEnabled(true);
                    return null;
                }

                if (data.done) {
                    break;
                }

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
        addMessage('jensen', `⚠️ Connection error: ${err.message}`);
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
        // Store the opening exchange in history
        conversationHistory.push({
            role: 'user',
            content: '[The user has just entered the strategy meeting room. Jensen is at the whiteboard. Open the meeting in character — set the scene and invite them to share what they\'re building.]'
        });
        conversationHistory.push({
            role: 'assistant',
            content: jensenText
        });
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

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + 'px';
});

startBtn.addEventListener('click', startMeeting);
newMeetingBtn.addEventListener('click', newMeeting);

// Load models on startup
loadModels();
