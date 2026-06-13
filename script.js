/**
 * JARVIS - Main JavaScript Application
 * Handles chat, UI interactions, and animations
 */

// ========== CONFIGURATION ==========
const API_BASE = '/api';
const TYPING_DELAY = 1200;
const MESSAGE_FADE_DELAY = 300;

// ========== GLOBAL STATE ==========
let chatHistory = [];
let currentChatId = null;
let isWaitingForResponse = false;
let darkMode = localStorage.getItem('darkMode') === 'true';

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Set dark mode
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }

    // Bind events
    bindEvents();
    
    // Load FAQs if on main page
    if (document.getElementById('messageInput')) {
        loadFAQCategories();
    }
}

// ========== EVENT BINDING ==========
function bindEvents() {
    // Chat events
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');

    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        messageInput.addEventListener('input', (e) => {
            updateCharCounter(e.target.value);
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (voiceBtn) {
        voiceBtn.addEventListener('click', startVoiceInput);
    }

    // Dark mode toggle
    document.getElementById('dark-mode-toggle')?.addEventListener('click', toggleDarkMode);

    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => navigateTo(btn.dataset.page));
    });

    // Export menu
    document.getElementById('export-menu-btn')?.addEventListener('click', () => {
        openModal('exportModal');
    });

    // FAQ button
    document.getElementById('faq-btn')?.addEventListener('click', () => {
        openModal('faqModal');
    });

    // Export buttons
    document.getElementById('export-pdf')?.addEventListener('click', exportPDF);
    document.getElementById('export-txt')?.addEventListener('click', exportTXT);
    document.getElementById('export-csv')?.addEventListener('click', exportCSV);

    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        });
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });

    // Suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('messageInput').value = btn.textContent;
            sendMessage();
        });
    });
}

// ========== CHAT FUNCTIONS ==========
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message || isWaitingForResponse) return;

    try {
        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';
        updateCharCounter('');

        isWaitingForResponse = true;

        // Show typing indicator
        showTypingIndicator();

        // Send to API
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error('Failed to get response');
        }

        const data = await response.json();

        // Hide typing indicator
        hideTypingIndicator();

        // Simulate typing delay
        await new Promise(resolve => setTimeout(resolve, TYPING_DELAY));

        // Add bot response
        if (data.success) {
            addMessage(data.answer, 'bot', {
                confidence: data.confidence,
                intent: data.intent,
                faq_id: data.faq_id,
                timestamp: data.timestamp
            });

            // Save to chat history
            currentChatId = data.faq_id;

            // Show success notification
            showNotification('Message sent successfully', 'success');
        } else {
            throw new Error(data.error);
        }

    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        showNotification('Error: ' + error.message, 'error');
    } finally {
        isWaitingForResponse = false;
    }
}

function addMessage(text, sender, metadata = {}) {
    const chatArea = document.getElementById('chatArea');

    // Remove welcome message on first real message
    if (chatArea.querySelector('.message-group.welcome')) {
        chatArea.querySelector('.message-group.welcome').remove();
    }

    const messageGroup = document.createElement('div');
    messageGroup.className = `message-group ${sender}`;

    let html = `
        <div class="message ${sender}">
            <div class="message-bubble">
                ${text}
    `;

    if (sender === 'bot' && metadata.confidence !== undefined) {
        const confidenceLevel = metadata.confidence;
        let confidenceColor = 'var(--success)';
        if (confidenceLevel < 50) {
            confidenceColor = 'var(--warning)';
        } else if (confidenceLevel < 70) {
            confidenceColor = 'var(--accent)';
        }

        html += `<div class="confidence" style="background-color: rgba(79, 70, 229, 0.1);">
            Confidence: ${confidenceLevel}%
        </div>`;
    }

    html += `</div>`;

    if (metadata.timestamp) {
        const time = new Date(metadata.timestamp).toLocaleTimeString();
        html += `<div class="message-time">${time}</div>`;
    }

    html += '</div>';

    messageGroup.innerHTML = html;
    chatArea.appendChild(messageGroup);

    // Auto-scroll to bottom
    setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 50);
}

function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'flex';
    
    const chatArea = document.getElementById('chatArea');
    chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'none';
}

function updateCharCounter(text) {
    const counter = document.getElementById('charCounter');
    if (counter) {
        counter.textContent = `${text.length} / 1000`;
        if (text.length > 900) {
            counter.style.color = 'var(--warning)';
        } else {
            counter.style.color = '';
        }
    }
}

// ========== VOICE INPUT ==========
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

function initVoiceRecognition() {
    if (!SpeechRecognition) {
        showNotification('Voice input not supported in your browser', 'error');
        return null;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        document.getElementById('voice-btn').classList.add('active');
    };

    recognition.onend = () => {
        document.getElementById('voice-btn').classList.remove('active');
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        document.getElementById('messageInput').value = transcript;
        updateCharCounter(transcript);
    };

    recognition.onerror = (event) => {
        showNotification('Error: ' + event.error, 'error');
    };

    return recognition;
}

function startVoiceInput() {
    if (!recognition) {
        recognition = initVoiceRecognition();
    }

    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            // Recognition already started
        }
    }
}

// ========== TEXT-TO-SPEECH ==========
function readMessage(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;

        window.speechSynthesis.speak(utterance);
    }
}

// ========== MODALS ==========
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        if (modalId === 'faqModal') {
            loadFAQList();
        }
    }
}

function closeModal(modalElement) {
    if (modalElement) {
        modalElement.classList.remove('active');
    }
}

// ========== FAQ MANAGEMENT ==========
async function loadFAQCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const data = await response.json();

        if (data.success && data.categories) {
            const categoryFilter = document.getElementById('categoryFilter');
            if (categoryFilter) {
                data.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categoryFilter.appendChild(option);
                });

                categoryFilter.addEventListener('change', () => {
                    loadFAQList();
                });
            }
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadFAQList() {
    try {
        const categoryFilter = document.getElementById('categoryFilter');
        const category = categoryFilter ? categoryFilter.value : '';

        const url = category ? `${API_BASE}/faqs?category=${category}` : `${API_BASE}/faqs`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.faqs) {
            const faqList = document.getElementById('faqList');
            faqList.innerHTML = '';

            data.faqs.forEach(faq => {
                const faqItem = document.createElement('div');
                faqItem.className = 'faq-item';
                faqItem.innerHTML = `
                    <h4>${faq.question}</h4>
                    <p>${faq.answer}</p>
                    <span class="category">${faq.category}</span>
                `;
                faqItem.addEventListener('click', () => {
                    document.getElementById('messageInput').value = faq.question;
                    closeModal(document.getElementById('faqModal'));
                    document.getElementById('messageInput').focus();
                });
                faqList.appendChild(faqItem);
            });
        }
    } catch (error) {
        console.error('Error loading FAQs:', error);
    }
}

// ========== DARK MODE ==========
function toggleDarkMode() {
    darkMode = !darkMode;
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', darkMode);

    const toggle = document.getElementById('dark-mode-toggle');
    if (toggle) {
        toggle.innerHTML = darkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
}

// ========== EXPORT FUNCTIONS ==========
function exportPDF() {
    window.location.href = `${API_BASE}/export/pdf`;
    showNotification('PDF download started', 'success');
}

function exportTXT() {
    window.location.href = `${API_BASE}/export/txt`;
    showNotification('TXT download started', 'success');
}

function exportCSV() {
    window.location.href = `${API_BASE}/export/csv`;
    showNotification('CSV download started', 'success');
}

// ========== NOTIFICATIONS ==========
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.getElementById('notification');
    if (!notification) return;

    notification.textContent = message;
    notification.className = `notification show ${type}`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

// ========== NAVIGATION ==========
function navigateTo(page) {
    const pages = {
        'chat': '/',
        'history': '/history',
        'favorites': '/favorites',
        'dashboard': '/dashboard'
    };

    if (pages[page]) {
        window.location.href = pages[page];
    }
}

// ========== HELPERS ==========
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncateText(text, length = 100) {
    return text.length > length ? text.substring(0, length) + '...' : text;
}

// ========== ROBOT ANIMATIONS ==========
function initializeRobotAnimations() {
    // Robot eye tracking
    document.addEventListener('mousemove', (e) => {
        const eyes = document.querySelectorAll('.robot-eye, .eye-left, .eye-right');
        eyes.forEach(eye => {
            if (!eye) return;
            
            const eyeRect = eye.getBoundingClientRect();
            const eyeCenterX = eyeRect.left + eyeRect.width / 2;
            const eyeCenterY = eyeRect.top + eyeRect.height / 2;

            const angle = Math.atan2(e.clientY - eyeCenterY, e.clientX - eyeCenterX);
            const distance = 5;

            const pupilX = Math.cos(angle) * distance;
            const pupilY = Math.sin(angle) * distance;

            eye.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
        });
    });

    // Robot blinking
    setInterval(() => {
        const eyes = document.querySelectorAll('.robot-eye, .eye-left, .eye-right');
        eyes.forEach(eye => {
            eye.style.animation = 'scaleY(0) 0.1s ease-in-out';
        });

        setTimeout(() => {
            eyes.forEach(eye => {
                eye.style.animation = '';
            });
        }, 200);
    }, 5000);
}

// Initialize robot animations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRobotAnimations);
} else {
    initializeRobotAnimations();
}

// ========== KEYBOARD SHORTCUTS ==========
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus chat input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('messageInput')?.focus();
    }

    // Ctrl/Cmd + M for voice input
    if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
        e.preventDefault();
        startVoiceInput();
    }
});

// ========== PAGE VISIBILITY ==========
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (recognition) {
            recognition.abort();
        }
        window.speechSynthesis.cancel();
    }
});

console.log('JARVIS v1.0 Initialized');
