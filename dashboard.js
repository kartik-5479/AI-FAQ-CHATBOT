/**
 * Dashboard - Statistics and analytics
 */

let categoryChart = null;
let intentChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
});

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();

        if (data.success) {
            renderStatistics(data.statistics);
            renderCharts(data.statistics);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showNotification('Error loading statistics', 'error');
    }
}

function renderStatistics(stats) {
    const statsGrid = document.getElementById('statsGrid');
    statsGrid.innerHTML = '';

    const statCards = [
        {
            title: 'Total Questions',
            value: stats.total_questions,
            icon: 'fa-comments',
            color: '#4F46E5'
        },
        {
            title: 'Total FAQs',
            value: stats.total_faqs,
            icon: 'fa-question-circle',
            color: '#7C3AED'
        },
        {
            title: 'Avg Confidence',
            value: stats.avg_confidence.toFixed(1) + '%',
            icon: 'fa-chart-pie',
            color: '#06B6D4'
        },
        {
            title: 'Most Asked',
            value: stats.most_asked_category,
            icon: 'fa-fire',
            color: '#F59E0B'
        }
    ];

    statCards.forEach(stat => {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3>${stat.title}</h3>
                    <div class="stat-value">${stat.value}</div>
                </div>
                <i class="fas ${stat.icon}" style="font-size: 2.5rem; color: ${stat.color}; opacity: 0.2;"></i>
            </div>
        `;
        statsGrid.appendChild(card);
    });
}

function renderCharts(stats) {
    // Category chart
    if (stats.categories_breakdown && stats.categories_breakdown.length > 0) {
        renderCategoryChart(stats.categories_breakdown);
    }

    // Intent chart
    if (stats.intent_distribution && stats.intent_distribution.length > 0) {
        renderIntentChart(stats.intent_distribution);
    }
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    
    if (!ctx) return;

    // Clear previous chart
    if (categoryChart) {
        categoryChart.destroy();
    }

    const labels = categories.map(cat => cat.category);
    const data = categories.map(cat => cat.count);

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4F46E5',
                    '#7C3AED',
                    '#06B6D4',
                    '#10B981',
                    '#F59E0B',
                    '#EF4444',
                    '#EC4899',
                    '#8B5CF6'
                ],
                borderColor: 'var(--background)',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'var(--text)',
                        font: { size: 12 },
                        padding: 15
                    }
                }
            }
        }
    });
}

function renderIntentChart(intents) {
    const ctx = document.getElementById('intentChart');
    
    if (!ctx) return;

    // Clear previous chart
    if (intentChart) {
        intentChart.destroy();
    }

    const labels = intents.map(intent => intent.intent);
    const data = intents.map(intent => intent.count);

    intentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Queries',
                data: data,
                backgroundColor: [
                    'rgba(79, 70, 229, 0.8)',
                    'rgba(124, 58, 237, 0.8)',
                    'rgba(6, 182, 212, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderColor: 'var(--primary)',
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: 'var(--text)',
                        font: { size: 12 }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: 'var(--text-light)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'var(--text-light)'
                    }
                }
            }
        }
    });
}
