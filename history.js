/**
 * History Page - Manage and display chat history
 */

let currentPage = 1;
let historyRecords = [];

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    bindHistoryEvents();
});

function bindHistoryEvents() {
    const searchInput = document.getElementById('historySearch');
    const sortSelect = document.getElementById('historySort');
    const clearAllBtn = document.getElementById('clear-history-btn');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterHistory, 300));
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', sortHistory);
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllHistory);
    }
}

async function loadHistory(page = 1) {
    try {
        const response = await fetch(`/api/history?page=${page}&limit=20`);
        const data = await response.json();

        if (data.success) {
            historyRecords = data.history;
            renderHistory(historyRecords);
            renderPagination(data);
        }
    } catch (error) {
        console.error('Error loading history:', error);
        showNotification('Error loading history', 'error');
    }
}

function renderHistory(records) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';

    if (records.length === 0) {
        historyList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No chat history</p>
                <span>Start chatting with Jarvis to see your conversations here</span>
            </div>
        `;
        return;
    }

    records.forEach((record, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-item-question">
                <i class="fas fa-user"></i> ${record.user_question}
            </div>
            <div class="history-item-answer">
                <i class="fas fa-robot"></i> ${record.bot_answer}
            </div>
            <div class="history-item-meta">
                <span class="time">
                    <i class="fas fa-clock"></i> ${formatDate(record.timestamp)}
                </span>
                <span class="confidence">
                    Confidence: ${record.confidence}%
                </span>
            </div>
            <div class="history-item-actions">
                <button class="btn-icon" title="Copy">
                    <i class="fas fa-copy"></i>
                </button>
                <button class="btn-icon" title="Read aloud">
                    <i class="fas fa-volume-up"></i>
                </button>
                <button class="btn-icon" title="Add to favorites">
                    <i class="fas fa-star"></i>
                </button>
                <button class="btn-icon" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        // Bind action buttons
        const buttons = historyItem.querySelectorAll('.history-item-actions button');
        buttons[0].addEventListener('click', () => copyToClipboard(record.bot_answer));
        buttons[1].addEventListener('click', () => readMessage(record.bot_answer));
        buttons[2].addEventListener('click', () => addToFavorites(record));
        buttons[3].addEventListener('click', () => deleteHistoryItem(record.id));

        historyList.appendChild(historyItem);
    });
}

function renderPagination(data) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    if (data.pages <= 1) return;

    for (let i = 1; i <= data.pages; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = i === data.page ? 'active' : '';
        btn.addEventListener('click', () => loadHistory(i));
        pagination.appendChild(btn);
    }
}

function filterHistory() {
    const searchText = document.getElementById('historySearch').value.toLowerCase();
    const filtered = historyRecords.filter(record => 
        record.user_question.toLowerCase().includes(searchText) ||
        record.bot_answer.toLowerCase().includes(searchText)
    );
    renderHistory(filtered);
}

function sortHistory() {
    const sortBy = document.getElementById('historySort').value;
    let sorted = [...historyRecords];

    switch (sortBy) {
        case 'recent':
            sorted.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        case 'oldest':
            sorted.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            break;
        case 'confidence':
            sorted.sort((a, b) => b.confidence - a.confidence);
            break;
    }

    renderHistory(sorted);
}

async function deleteHistoryItem(id) {
    if (confirm('Are you sure you want to delete this conversation?')) {
        try {
            const response = await fetch(`/api/history/${id}`, { method: 'DELETE' });
            const data = await response.json();

            if (data.success) {
                showNotification('Conversation deleted', 'success');
                loadHistory();
            }
        } catch (error) {
            showNotification('Error deleting conversation', 'error');
        }
    }
}

async function clearAllHistory() {
    if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        try {
            const response = await fetch('/api/history', { method: 'DELETE' });
            const data = await response.json();

            if (data.success) {
                showNotification('All history cleared', 'success');
                loadHistory();
            }
        } catch (error) {
            showNotification('Error clearing history', 'error');
        }
    }
}

async function addToFavorites(record) {
    try {
        const response = await fetch('/api/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: record.id,
                user_question: record.user_question,
                bot_answer: record.bot_answer
            })
        });

        const data = await response.json();
        if (data.success) {
            showNotification('Added to favorites', 'success');
        }
    } catch (error) {
        showNotification('Error adding to favorites', 'error');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
