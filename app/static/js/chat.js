document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('chat-toggle');
    const closeBtn = document.getElementById('chat-close');
    const chatPanel = document.getElementById('chat-panel');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const messagesContainer = document.getElementById('chat-messages');
    
    // Generate or get session ID
    let sessionId = localStorage.getItem('nodus_chat_session');
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('nodus_chat_session', sessionId);
    }
    
    let conversationId = null;

    // Toggle chat
    toggleBtn.addEventListener('click', () => {
        chatPanel.classList.remove('hidden');
        chatInput.focus();
    });

    closeBtn.addEventListener('click', () => {
        chatPanel.classList.add('hidden');
    });

    // Send message
    const sendMessage = async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add user message to UI
        appendMessage(text, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: sessionId,
                    language: API_LANG,
                    conversation_id: conversationId
                })
            });

            const data = await response.json();
            removeTypingIndicator(typingId);
            
            if (data.error) {
                appendMessage('Sorry, I encountered an error. Please try again.', 'ai');
                return;
            }

            conversationId = data.conversation_id;
            
            // Render AI response text
            appendMessage(data.response, 'ai');
            
            // Render recommended items if any
            if (data.recommended_items && data.recommended_items.length > 0) {
                renderRecommendations(data.recommended_items);
            }

        } catch (error) {
            console.error('Chat error:', error);
            removeTypingIndicator(typingId);
            appendMessage('Connection error. Please check your internet.', 'ai');
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;
        const p = document.createElement('p');
        // Basic markdown formatting for bold text safely
        const parts = text.split(/(\*\*.*?\*\*)/g);
        parts.forEach(part => {
            if (part.startsWith('**') && part.endsWith('**')) {
                const strong = document.createElement('strong');
                strong.textContent = part.slice(2, -2);
                p.appendChild(strong);
            } else {
                // Handle newlines
                const lines = part.split('\n');
                lines.forEach((line, index) => {
                    if (index > 0) p.appendChild(document.createElement('br'));
                    p.appendChild(document.createTextNode(line));
                });
            }
        });
        div.appendChild(p);
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function renderRecommendations(items) {
        const container = document.createElement('div');
        container.className = 'chat-recommendations';
        
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'chat-rec-card';
            
            const imgSrc = item.image_path || 'data:image/gif;base64,R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=='; // gray pixel
            
            card.innerHTML = `
                <img src="${imgSrc}" alt="${item.name}">
                <div class="chat-rec-info">
                    <h4>${item.name}</h4>
                    <div class="price">₹${item.price}</div>
                    <a href="/menu" style="font-size:0.8rem; color:var(--text-secondary); text-decoration:underline;">View Menu</a>
                </div>
            `;
            container.appendChild(card);
        });
        
        messagesContainer.appendChild(container);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.className = 'message ai-message typing';
        div.id = id;
        div.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
