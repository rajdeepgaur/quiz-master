// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Progress chart for user dashboard
    const progressChart = document.getElementById('progressChart');
    if (progressChart && typeof chartData !== 'undefined') {
        new Chart(progressChart, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Quiz Scores',
                    data: chartData.scores,
                    borderColor: '#0dcaf0',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Stats chart for admin dashboard
    const statsChart = document.getElementById('statsChart');
    if (statsChart && typeof statsData !== 'undefined') {
        new Chart(statsChart, {
            type: 'bar',
            data: {
                labels: ['Total Users', 'Active Quizzes', 'Completed Attempts', 'Avg Score'],
                datasets: [{
                    data: [
                        statsData.total_users,
                        statsData.active_quizzes,
                        statsData.completed_attempts,
                        Math.round(statsData.avg_score)
                    ],
                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#0dcaf0'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Subject statistics chart
    const subjectStats = document.getElementById('subjectStats');
    if (subjectStats && typeof subjectChartData !== 'undefined') {
        new Chart(subjectStats, {
            type: 'doughnut',
            data: {
                labels: subjectChartData.labels,
                datasets: [{
                    data: subjectChartData.data,
                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#0dcaf0',
                        '#6c757d',
                        '#dc3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
});

// Function to update charts with new data
function updateCharts(data) {
    // Implementation for updating charts with new data
    console.log('Updating charts with:', data);
}