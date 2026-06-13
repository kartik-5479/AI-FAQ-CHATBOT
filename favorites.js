/**
 * Favorites Page - Manage bookmarked conversations
 */

document.addEventListener('DOMContentLoaded', () => {
    loadFavorites();
});

async function loadFavorites() {
    try {
        const response = await fetch('/api/favorites');
        const data = await response.json();

        if (data.success) {
            renderFavorites(data.favorites);
        }
    } catch (error) {
        console.error('Error loading favorites:', error);
        showNotification('Error loading favorites', 'error');
    }
}

function renderFavorites(favorites) {
    const favoritesList = document.getElementById('favoritesList');
    favoritesList.innerHTML = '';

    if (favorites.length === 0) {
        favoritesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star"></i>
                <p>No favorites yet</p>
                <span>Bookmark important conversations to find them quickly</span>
            </div>
        `;
        return;
    }

    favorites.forEach(favorite => {
        const card = document.createElement('div');
        card.className = 'favorite-card';
        card.innerHTML = `
            <h4>${truncateText(favorite.user_question, 50)}</h4>
            <p>${truncateText(favorite.bot_answer, 150)}</p>
            <div class="favorite-date">
                <i class="fas fa-calendar"></i> ${formatDate(favorite.date_saved)}
            </div>
            <div class="history-item-actions">
                <button class="btn-icon" title="Copy">
                    <i class="fas fa-copy"></i>
                </button>
                <button class="btn-icon" title="Read aloud">
                    <i class="fas fa-volume-up"></i>
                </button>
                <button class="btn-icon" title="Remove from favorites">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        const buttons = card.querySelectorAll('.history-item-actions button');
        buttons[0].addEventListener('click', () => copyToClipboard(favorite.bot_answer));
        buttons[1].addEventListener('click', () => readMessage(favorite.bot_answer));
        buttons[2].addEventListener('click', () => removeFavorite(favorite.id));

        favoritesList.appendChild(card);
    });
}

async function removeFavorite(id) {
    if (confirm('Remove from favorites?')) {
        try {
            const response = await fetch(`/api/favorites/${id}`, { method: 'DELETE' });
            const data = await response.json();

            if (data.success) {
                showNotification('Removed from favorites', 'success');
                loadFavorites();
            }
        } catch (error) {
            showNotification('Error removing favorite', 'error');
        }
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncateText(text, length = 100) {
    return text.length > length ? text.substring(0, length) + '...' : text;
}
