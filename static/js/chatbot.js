/**
 * AfIMMP Chatbot Widget
 * A floating chatbot powered by OpenAI
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        apiEndpoint: '/chatbot/api/',
        storageKey: 'afimpp_chatbot_session',
        typingDelay: 600,
        welcomeSuggestions: [
            'What courses do you offer?',
            'Tell me about Level 4 courses',
            'How do I enroll?',
            'What are the requirements?'
        ]
    };

    // State
    let state = {
        isOpen: false,
        sessionId: null,
        hasMessages: false,
        isTyping: false
    };

    // DOM Elements
    let elements = {};

    // Initialize
    function init() {
        // Get or create session ID
        state.sessionId = getSessionId();

        // Create widget HTML
        createWidget();

        // Bind events
        bindEvents();

        // Load session if exists
        loadSession();
    }

    // Get session ID from storage or create new
    function getSessionId() {
        const stored = localStorage.getItem(CONFIG.storageKey);
        if (stored) {
            try {
                const data = JSON.parse(stored);
                if (data.sessionId && data.timestamp > Date.now() - 24 * 60 * 60 * 1000) {
                    return data.sessionId;
                }
            } catch (e) {}
        }
        return null;
    }

    // Save session to storage
    function saveSession() {
        localStorage.setItem(CONFIG.storageKey, JSON.stringify({
            sessionId: state.sessionId,
            timestamp: Date.now()
        }));
    }

    // Create widget HTML
    function createWidget() {
        const container = document.createElement('div');
        container.className = 'chatbot-container';
        container.innerHTML = `
            <div class="chatbot-window" id="chatbot-window">
                <div class="chatbot-header">
                    <div class="chatbot-avatar">
                        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                    </div>
                    <div class="chatbot-title">
                        <h3>AfIMMP Assistant</h3>
                        <p>Ask me about courses & enrollment</p>
                    </div>
                </div>
                <div class="chatbot-messages" id="chatbot-messages">
                    <div class="welcome-message" id="welcome-message">
                        <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>
                        <h4>Welcome to AfIMMP!</h4>
                        <p>I'm here to help you learn about our courses and enrollment process.</p>
                        <p style="font-size: 11px; margin-top: 10px; color: #999;">Contact: +233 55 778 2728 | info@afimpp.institute</p>
                        <div class="suggestions" id="suggestions"></div>
                    </div>
                </div>
                <div class="chatbot-input">
                    <textarea id="chatbot-textarea" placeholder="Type your message..." rows="1"></textarea>
                    <button class="chatbot-send" id="chatbot-send" disabled>
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
                <div class="chatbot-footer">
                    <a href="https://www.afimpp.institute" target="_blank">www.afimpp.institute</a> | +233 55 778 2728
                </div>
            </div>
            <button class="chatbot-toggle" id="chatbot-toggle">
                <span class="chat-icon">
                    <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>
                </span>
                <span class="close-icon">
                    <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                </span>
            </button>
        `;

        document.body.appendChild(container);

        // Cache elements
        elements = {
            container: container,
            window: document.getElementById('chatbot-window'),
            toggle: document.getElementById('chatbot-toggle'),
            messages: document.getElementById('chatbot-messages'),
            textarea: document.getElementById('chatbot-textarea'),
            sendBtn: document.getElementById('chatbot-send'),
            welcomeMessage: document.getElementById('welcome-message'),
            suggestions: document.getElementById('suggestions')
        };

        // Create suggestion buttons
        if (elements.suggestions) {
            CONFIG.welcomeSuggestions.forEach(text => {
                const btn = document.createElement('button');
                btn.className = 'suggestion-btn';
                btn.textContent = text;
                btn.addEventListener('click', () => sendMessage(text));
                elements.suggestions.appendChild(btn);
            });
        }
    }

    // Bind events
    function bindEvents() {
        // Toggle button
        elements.toggle.addEventListener('click', toggleWindow);

        // Send button
        elements.sendBtn.addEventListener('click', () => sendMessage());

        // Textarea events
        elements.textarea.addEventListener('input', handleInput);
        elements.textarea.addEventListener('keydown', handleKeydown);

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (state.isOpen && !elements.container.contains(e.target)) {
                closeWindow();
            }
        });
    }

    // Toggle chat window
    function toggleWindow() {
        state.isOpen ? closeWindow() : openWindow();
    }

    function openWindow() {
        state.isOpen = true;
        elements.window.classList.add('open');
        elements.toggle.classList.add('open');
        if (!state.hasMessages) {
            elements.welcomeMessage.style.display = 'block';
        }
    }

    function closeWindow() {
        state.isOpen = false;
        elements.window.classList.remove('open');
        elements.toggle.classList.remove('open');
    }

    // Handle input changes
    function handleInput() {
        const textarea = elements.textarea;
        // Auto-resize textarea
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';

        // Enable/disable send button
        elements.sendBtn.disabled = !textarea.value.trim();
    }

    // Handle keyboard events
    function handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (elements.textarea.value.trim()) {
                sendMessage();
            }
        }
    }

    // Send message
    async function sendMessage(message = null) {
        const text = message || elements.textarea.value.trim();
        if (!text || state.isTyping) return;

        // Hide welcome message
        if (elements.welcomeMessage) {
            elements.welcomeMessage.style.display = 'none';
        }
        state.hasMessages = true;

        // Add user message
        addMessage('user', text);

        // Clear input
        elements.textarea.value = '';
        elements.textarea.style.height = 'auto';
        elements.sendBtn.disabled = true;

        // Show typing indicator
        showTyping();

        // Send to API
        try {
            const response = await fetch(CONFIG.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: text,
                    session_id: state.sessionId
                })
            });

            if (!response.ok) {
                throw new Error('API error');
            }

            const data = await response.json();

            // Save session ID
            if (data.session_id) {
                state.sessionId = data.session_id;
                saveSession();
            }

            // Remove typing indicator
            hideTyping();

            // Add assistant response
            addMessage('assistant', data.response);

        } catch (error) {
            hideTyping();
            addMessage('assistant', 'Sorry, I\'m having trouble connecting. Please try again or contact us at info@afimpp.edu.gh');
            console.error('Chatbot error:', error);
        }
    }

    // Add message to chat
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        // Convert links to clickable
        content = content.replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener">$1</a>'
        );

        // Convert line breaks
        content = content.replace(/\n/g, '<br>');

        messageDiv.innerHTML = content;
        elements.messages.appendChild(messageDiv);

        // Scroll to bottom
        scrollToBottom();
    }

    // Show typing indicator
    function showTyping() {
        state.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        elements.messages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Hide typing indicator
    function hideTyping() {
        state.isTyping = false;
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    // Scroll to bottom of messages
    function scrollToBottom() {
        elements.messages.scrollTop = elements.messages.scrollHeight;
    }

    // Load previous session (placeholder for future enhancement)
    function loadSession() {
        // Could implement message history restoration here
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
