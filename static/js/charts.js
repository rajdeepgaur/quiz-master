// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Colors for charts
    const colors = [
        '#0d6efd',
        '#198754',
        '#ffc107',
        '#0dcaf0',
        '#6c757d',
        '#dc3545'
    ];

    // Subject scores bar chart
    const scoresChart = document.getElementById('scoresChart');
    if (scoresChart && typeof barChartData !== 'undefined') {
        const barColors = barChartData.labels.map((_, index) =>
            colors[index % colors.length]
        );

        new Chart(scoresChart, {
            type: 'bar',
            data: {
                labels: barChartData.labels,
                datasets: [{
                    label: 'Average Score',
                    data: barChartData.data,
                    backgroundColor: barColors,
                    borderColor: barColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Score (%)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Subject attempts concentric donut chart
    const attemptsChart = document.getElementById('attemptsChart');
    if (attemptsChart && typeof donutChartData !== 'undefined') {
        const dataset = donutChartData.datasets[0];
        const totalRings = dataset.data.length;

        // Create datasets for each ring
        const datasets = dataset.data.map((value, index) => ({
            data: Array(totalRings).fill(0),
            backgroundColor: Array(totalRings).fill('transparent'),
            borderWidth: 0,
            weight: totalRings - index // Outer rings are thicker
        }));

        // Set the actual value and color for each dataset
        datasets.forEach((ds, i) => {
            ds.data[i] = dataset.data[i];
            ds.backgroundColor[i] = dataset.backgroundColor[i];
        });

        new Chart(attemptsChart, {
            type: 'doughnut',
            data: {
                labels: dataset.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => ({
                                        text: `${label} (${dataset.data[i]} attempts)`,
                                        fillStyle: dataset.backgroundColor[i],
                                        strokeStyle: dataset.backgroundColor[i],
                                        lineWidth: 0,
                                        hidden: false,
                                        index: i
                                    }));
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value} attempts`;
                            }
                        }
                    }
                },
                cutout: '30%'
            }
        });
    }


    // Colors for different attempt types
    const attemptColors = {
        'Successful Attempts': '#198754',  // Success green
        'Failed Attempts': '#dc3545'       // Danger red
    };

    // Create individual donut charts for each subject
    if (donutChartData && donutChartData.datasets) {
        donutChartData.datasets.forEach((dataset, index) => {
            const chartId = `attemptsChart${index + 1}`;
            const ctx = document.getElementById(chartId);

            if (ctx) {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: dataset.labels,
                        datasets: [{
                            data: dataset.data,
                            backgroundColor: dataset.labels.map(label => attemptColors[label]),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 10
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.label}: ${context.raw}`;
                                    }
                                }
                            }
                        },
                        cutout: '60%'
                    }
                });
            }
        });
    }


    // Subject-wise attempts bar chart (for user dashboard)
    const subjectAttemptsChart = document.getElementById('subjectAttemptsChart');
    if (subjectAttemptsChart && typeof barChartData !== 'undefined') {
        const barColors = barChartData.labels.map((_, index) =>
            colors[index % colors.length]
        );

        new Chart(subjectAttemptsChart, {
            type: 'bar',
            data: {
                labels: barChartData.labels,
                datasets: [{
                    label: 'Number of Attempts',
                    data: barChartData.data,
                    backgroundColor: barColors,
                    borderColor: barColors,
                    borderWidth: 1
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
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // Monthly attempts pie chart (for user dashboard)
    const monthlyAttemptsChart = document.getElementById('monthlyAttemptsChart');
    if (monthlyAttemptsChart && typeof pieChartData !== 'undefined') {
        new Chart(monthlyAttemptsChart, {
            type: 'pie',
            data: {
                labels: pieChartData.labels,
                datasets: [{
                    data: pieChartData.data,
                    backgroundColor: colors
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
    // Admin dashboard charts (keeping the existing code)
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
});

// Function to update charts with new data
function updateCharts(data) {
    // Implementation for updating charts with new data
    console.log('Updating charts with:', data);
}