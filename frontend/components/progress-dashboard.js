// Progress Dashboard Component
class ProgressDashboard {
    constructor() {
        this.container = null;
        this.charts = {};
        this.data = {
            moodTrend: [],
            therapySessions: [],
            journalEntries: [],
            achievements: []
        };
    }

    async init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Progress dashboard container not found');
            return;
        }

        await this.loadData();
        this.render();
        this.setupEventListeners();
    }

    async loadData() {
        try {
            // Load analytics data
            const [moodData, sessionsData, journalData, achievementsData] = await Promise.all([
                this.fetchMoodData(),
                this.fetchSessionsData(),
                this.fetchJournalData(),
                this.fetchAchievementsData()
            ]);

            this.data = {
                moodTrend: moodData,
                therapySessions: sessionsData,
                journalEntries: journalData,
                achievements: achievementsData
            };
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async fetchMoodData() {
        const response = await apiCall('analytics/mood?days=30');
        return response.data || [];
    }

    async fetchSessionsData() {
        const response = await apiCall('therapy/sessions?limit=50');
        return response.data || [];
    }

    async fetchJournalData() {
        const response = await apiCall('journaling/entries?limit=50');
        return response.data || [];
    }

    async fetchAchievementsData() {
        const response = await apiCall('gamification/achievements');
        return response.data || [];
    }

    render() {
        this.container.innerHTML = `
            <div class="progress-dashboard">
                <div class="dashboard-header">
                    <h2><i class="fas fa-chart-line"></i> Your Progress Dashboard</h2>
                    <div class="dashboard-controls">
                        <select id="time-range" class="dashboard-select">
                            <option value="7">Last 7 Days</option>
                            <option value="30" selected>Last 30 Days</option>
                            <option value="90">Last 90 Days</option>
                        </select>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <!-- Mood Trend Chart -->
                    <div class="dashboard-card mood-trend-card">
                        <div class="card-header">
                            <h3><i class="fas fa-heart"></i> Mood Trends</h3>
                            <div class="card-actions">
                                <button class="btn-icon" onclick="progressDashboard.exportMoodData()">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="mood-chart"></canvas>
                        </div>
                    </div>

                    <!-- Therapy Sessions -->
                    <div class="dashboard-card sessions-card">
                        <div class="card-header">
                            <h3><i class="fas fa-comments"></i> Therapy Sessions</h3>
                            <div class="card-actions">
                                <button class="btn-icon" onclick="progressDashboard.viewAllSessions()">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                        <div class="sessions-summary">
                            <div class="summary-item">
                                <span class="summary-number">${this.data.therapySessions.length}</span>
                                <span class="summary-label">Total Sessions</span>
                            </div>
                            <div class="summary-item">
                                <span class="summary-number">${this.getAverageSessionDuration()}</span>
                                <span class="summary-label">Avg Duration</span>
                            </div>
                            <div class="summary-item">
                                <span class="summary-number">${this.getMostUsedTherapy()}</span>
                                <span class="summary-label">Preferred Therapy</span>
                            </div>
                        </div>
                    </div>

                    <!-- Journal Insights -->
                    <div class="dashboard-card journal-card">
                        <div class="card-header">
                            <h3><i class="fas fa-book-open"></i> Journal Insights</h3>
                            <div class="card-actions">
                                <button class="btn-icon" onclick="progressDashboard.exportJournalData()">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        </div>
                        <div class="journal-insights">
                            <div class="insight-item">
                                <i class="fas fa-calendar-check"></i>
                                <span>${this.data.journalEntries.length} entries this month</span>
                            </div>
                            <div class="insight-item">
                                <i class="fas fa-clock"></i>
                                <span>${this.getAverageEntryLength()} words per entry</span>
                            </div>
                            <div class="insight-item">
                                <i class="fas fa-tags"></i>
                                <span>${this.getTopJournalTopics()}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Achievements Gallery -->
                    <div class="dashboard-card achievements-card">
                        <div class="card-header">
                            <h3><i class="fas fa-trophy"></i> Recent Achievements</h3>
                            <div class="card-actions">
                                <button class="btn-icon" onclick="progressDashboard.viewAllAchievements()">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                        </div>
                        <div class="achievements-gallery">
                            ${this.renderAchievements()}
                        </div>
                    </div>
                </div>

                <!-- Progress Summary -->
                <div class="progress-summary">
                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Mental Wellness Score</h4>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${this.calculateWellnessScore()}%"></div>
                            </div>
                            <span class="progress-text">${this.calculateWellnessScore()}%</span>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-fire"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Consistency Streak</h4>
                            <div class="streak-display">
                                <span class="streak-number">${this.calculateStreak()}</span>
                                <span class="streak-label">days</span>
                            </div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Total XP Earned</h4>
                            <div class="xp-display">
                                <span class="xp-number">${this.calculateTotalXP()}</span>
                                <span class="xp-label">experience points</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.initializeCharts();
    }

    renderAchievements() {
        const recentAchievements = this.data.achievements.slice(0, 6);
        return recentAchievements.map(achievement => `
            <div class="achievement-item ${achievement.unlocked ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">
                    <i class="${achievement.icon || 'fas fa-star'}"></i>
                </div>
                <div class="achievement-info">
                    <h5>${achievement.name}</h5>
                    <p>${achievement.description}</p>
                </div>
            </div>
        `).join('');
    }

    initializeCharts() {
        this.createMoodChart();
    }

    createMoodChart() {
        const ctx = document.getElementById('mood-chart');
        if (!ctx) return;

        const moodData = this.data.moodTrend.map(item => ({
            x: new Date(item.date),
            y: item.mood_score
        }));

        this.charts.mood = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Mood Score',
                    data: moodData,
                    borderColor: '#007AFF',
                    backgroundColor: 'rgba(0, 122, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        min: 1,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                }
            }
        });
    }

    getAverageSessionDuration() {
        if (this.data.therapySessions.length === 0) return '0 min';
        const totalDuration = this.data.therapySessions.reduce((sum, session) => 
            sum + (session.duration || 0), 0);
        return Math.round(totalDuration / this.data.therapySessions.length) + ' min';
    }

    getMostUsedTherapy() {
        const therapyCounts = {};
        this.data.therapySessions.forEach(session => {
            const therapy = session.therapy_type || 'Unknown';
            therapyCounts[therapy] = (therapyCounts[therapy] || 0) + 1;
        });
        
        const mostUsed = Object.entries(therapyCounts)
            .sort(([,a], [,b]) => b - a)[0];
        return mostUsed ? mostUsed[0].toUpperCase() : 'N/A';
    }

    getAverageEntryLength() {
        if (this.data.journalEntries.length === 0) return 0;
        const totalWords = this.data.journalEntries.reduce((sum, entry) => 
            sum + (entry.content?.split(' ').length || 0), 0);
        return Math.round(totalWords / this.data.journalEntries.length);
    }

    getTopJournalTopics() {
        // Simple topic extraction based on common keywords
        const topics = ['gratitude', 'anxiety', 'stress', 'happiness', 'goals', 'relationships'];
        const topicCounts = {};
        
        this.data.journalEntries.forEach(entry => {
            const content = entry.content?.toLowerCase() || '';
            topics.forEach(topic => {
                if (content.includes(topic)) {
                    topicCounts[topic] = (topicCounts[topic] || 0) + 1;
                }
            });
        });

        const topTopic = Object.entries(topicCounts)
            .sort(([,a], [,b]) => b - a)[0];
        return topTopic ? topTopic[0].charAt(0).toUpperCase() + topTopic[0].slice(1) : 'Various';
    }

    calculateWellnessScore() {
        // Calculate based on mood trends, session frequency, and journal consistency
        const moodScore = this.data.moodTrend.length > 0 ? 
            this.data.moodTrend.reduce((sum, item) => sum + item.mood_score, 0) / this.data.moodTrend.length : 5;
        const sessionScore = Math.min(this.data.therapySessions.length * 10, 100);
        const journalScore = Math.min(this.data.journalEntries.length * 5, 100);
        
        return Math.round((moodScore * 0.4 + sessionScore * 0.3 + journalScore * 0.3) * 10);
    }

    calculateStreak() {
        // Calculate current streak based on activity
        return Math.min(this.data.journalEntries.length + this.data.therapySessions.length, 30);
    }

    calculateTotalXP() {
        return this.data.achievements.reduce((sum, achievement) => 
            sum + (achievement.xp_earned || 0), 0);
    }

    setupEventListeners() {
        const timeRangeSelect = document.getElementById('time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.updateTimeRange(e.target.value);
            });
        }
    }

    async updateTimeRange(days) {
        await this.loadData();
        this.render();
    }

    exportMoodData() {
        const csv = this.convertToCSV(this.data.moodTrend);
        this.downloadCSV(csv, 'mood-data.csv');
    }

    exportJournalData() {
        const csv = this.convertToCSV(this.data.journalEntries);
        this.downloadCSV(csv, 'journal-data.csv');
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header];
                return typeof value === 'string' ? `"${value}"` : value;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }

    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    viewAllSessions() {
        // Navigate to sessions history
        window.location.hash = '#sessions';
    }

    viewAllAchievements() {
        // Navigate to achievements page
        window.location.hash = '#achievements';
    }
}

// Initialize the progress dashboard
const progressDashboard = new ProgressDashboard(); 