const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const userXp = document.getElementById('user-xp');
const userLevel = document.getElementById('user-level');
const userTitle = document.getElementById('user-title');
const xpProgress = document.getElementById('xp-progress');

let sessionId = localStorage.getItem('tukokadi_session') || 'user_' + Math.random().toString(36).substr(2, 9);
localStorage.setItem('tukokadi_session', sessionId);

const levelThresholds = [
    { level: 1, xp: 0, title: "Mwananchi Mchanga" },
    { level: 2, xp: 100, title: "Mwananchi" },
    { level: 3, xp: 250, title: "Mtetezi" },
    { level: 4, xp: 500, title: "Mlinzi" },
    { level: 5, xp: 1000, title: "Shahidi" },
    { level: 6, xp: 2000, title: "Hodari" },
    { level: 7, xp: 3500, title: "Bingwa" },
    { level: 8, xp: 5500, title: "Kiongozi" },
    { level: 9, xp: 8000, title: "Mzee wa Katiba" },
    { level: 10, xp: 12000, title: "Simba wa Katiba" }
];

function updateUI(state) {
    userXp.innerText = state.xp;
    userLevel.innerText = state.level;
    
    const currentLevel = levelThresholds.find(l => l.level === state.level) || levelThresholds[0];
    const nextLevel = levelThresholds.find(l => l.level === state.level + 1) || { xp: state.xp };
    
    userTitle.innerText = currentLevel.title;
    
    const progress = state.level === 10 ? 100 : ((state.xp - currentLevel.xp) / (nextLevel.xp - currentLevel.xp)) * 100;
    xpProgress.style.width = `${Math.min(100, Math.max(0, progress))}%`;
}

function appendMessage(text, role) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = text.replace(/\n/g, '<br>');
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    msgDiv.appendChild(contentDiv);
    msgDiv.appendChild(timeSpan);
    chatMessages.appendChild(msgDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(text) {
    appendMessage(text, 'user');
    userInput.value = '';
    
    // Add typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing';
    typingDiv.innerHTML = '<div class="message-content">...</div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, user_id: sessionId })
        });
        
        const data = await response.json();
        
        chatMessages.removeChild(typingDiv);
        appendMessage(data.response, 'ai');
        updateUI(data.state);
        
    } catch (error) {
        chatMessages.removeChild(typingDiv);
        appendMessage('Samahani, kuna tatizo. Tafadhali jaribu tena baadaye.', 'ai');
    }
}

function sendQuickMsg(text) {
    sendMessage(text);
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (text) {
        sendMessage(text);
    }
});

// Initial load
fetch(`/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'STATUS', user_id: sessionId })
}).then(res => res.json()).then(data => updateUI(data.state));
