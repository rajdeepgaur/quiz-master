// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Progress chart for user dashboard
    const progressChart = document.getElementById('progressChart');
    if (progressChart) {
        new Chart(progressChart, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Quiz Scores',
                    data: [65, 78, 82, 75, 88, 95],
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
    if (statsChart) {
        new Chart(statsChart, {
            type: 'bar',
            data: {
                labels: ['Total Users', 'Active Quizzes', 'Completed Attempts', 'Avg Score'],
                datasets: [{
                    data: [150, 45, 320, 78],
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
    if (subjectStats) {
        new Chart(subjectStats, {
            type: 'doughnut',
            data: {
                labels: ['Mathematics', 'Science', 'History', 'English'],
                datasets: [{
                    data: [30, 25, 20, 25],
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
