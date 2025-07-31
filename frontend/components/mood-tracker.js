// Mood Tracker Component
class MoodTracker {
    constructor() {
        this.container = null;
        this.currentMood = null;
        this.moodHistory = [];
        this.moodEmojis = {
            1: '😢', 2: '😞', 3: '😐', 4: '🙂', 5: '😊',
            6: '😄', 7: '😁', 8: '🤩', 9: '🥰', 10: '😍'
        };
        this.moodLabels = {
            1: 'Terrible', 2: 'Very Bad', 3: 'Bad', 4: 'Okay', 5: 'Neutral',
            6: 'Good', 7: 'Very Good', 8: 'Great', 9: 'Excellent', 10: 'Amazing'
        };
    }

    async init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Mood tracker container not found');
            return;
        }

        await this.loadMoodHistory();
        this.render();
        this.setupEventListeners();
    }

    async loadMoodHistory() {
        try {
            const response = await apiCall('analytics/mood?days=7');
            this.moodHistory = response.data || [];
        } catch (error) {
            console.error('Error loading mood history:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="mood-tracker">
                <div class="mood-header">
                    <h2><i class="fas fa-heart"></i> How are you feeling today?</h2>
                    <p class="mood-subtitle">Track your mood and discover patterns</p>
                </div>

                <!-- Current Mood Input -->
                <div class="mood-input-section">
                    <div class="mood-scale">
                        <div class="mood-scale-header">
                            <span>Rate your current mood</span>
                        </div>
                        <div class="mood-options">
                            ${this.renderMoodOptions()}
                        </div>
                        <div class="mood-note">
                            <textarea id="mood-note" placeholder="How are you feeling? (optional)"></textarea>
                        </div>
                        <button id="save-mood" class="btn btn-primary" disabled>
                            <i class="fas fa-save"></i> Save Mood
                        </button>
                    </div>
                </div>

                <!-- Mood History -->
                <div class="mood-history-section">
                    <div class="section-header">
                        <h3><i class="fas fa-chart-line"></i> Your Mood History</h3>
                        <div class="history-controls">
                            <select id="history-range" class="history-select">
                                <option value="7">Last 7 Days</option>
                                <option value="30">Last 30 Days</option>
                                <option value="90">Last 90 Days</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="mood-history-chart">
                        <canvas id="mood-history-chart"></canvas>
                    </div>

                    <div class="mood-insights">
                        <div class="insight-card">
                            <div class="insight-icon">
                                <i class="fas fa-trending-up"></i>
                            </div>
                            <div class="insight-content">
                                <h4>Average Mood</h4>
                                <span class="insight-value">${this.calculateAverageMood()}</span>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <i class="fas fa-calendar-check"></i>
                            </div>
                            <div class="insight-content">
                                <h4>Tracking Streak</h4>
                                <span class="insight-value">${this.calculateTrackingStreak()} days</span>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <i class="fas fa-lightbulb"></i>
                            </div>
                            <div class="insight-content">
                                <h4>Mood Pattern</h4>
                                <span class="insight-value">${this.analyzeMoodPattern()}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Mood Insights -->
                <div class="mood-insights-section">
                    <h3><i class="fas fa-brain"></i> Mood Insights</h3>
                    <div class="insights-grid">
                        <div class="insight-item">
                            <h4>Best Day of the Week</h4>
                            <p>${this.getBestDayOfWeek()}</p>
                        </div>
                        <div class="insight-item">
                            <h4>Mood Triggers</h4>
                            <p>${this.getMoodTriggers()}</p>
                        </div>
                        <div class="insight-item">
                            <h4>Improvement Trend</h4>
                            <p>${this.getImprovementTrend()}</p>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="mood-actions">
                    <h3><i class="fas fa-magic"></i> Quick Actions</h3>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="moodTracker.startMoodJournal()">
                            <i class="fas fa-book-open"></i>
                            <span>Journal Entry</span>
                        </button>
                        <button class="action-btn" onclick="moodTracker.startTherapySession()">
                            <i class="fas fa-comments"></i>
                            <span>Therapy Session</span>
                        </button>
                        <button class="action-btn" onclick="moodTracker.viewMoodAnalytics()">
                            <i class="fas fa-chart-bar"></i>
                            <span>Detailed Analytics</span>
                        </button>
                        <button class="action-btn" onclick="moodTracker.exportMoodData()">
                            <i class="fas fa-download"></i>
                            <span>Export Data</span>
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.initializeMoodChart();
    }

    renderMoodOptions() {
        return Object.entries(this.moodEmojis).map(([score, emoji]) => `
            <div class="mood-option" data-score="${score}">
                <div class="mood-emoji">${emoji}</div>
                <div class="mood-label">${this.moodLabels[score]}</div>
                <div class="mood-score">${score}</div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Mood option selection
        const moodOptions = document.querySelectorAll('.mood-option');
        moodOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectMood(parseInt(option.dataset.score));
            });
        });

        // Save mood button
        const saveButton = document.getElementById('save-mood');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                this.saveMood();
            });
        }

        // History range selector
        const historyRange = document.getElementById('history-range');
        if (historyRange) {
            historyRange.addEventListener('change', (e) => {
                this.updateHistoryRange(e.target.value);
            });
        }
    }

    selectMood(score) {
        // Remove previous selection
        document.querySelectorAll('.mood-option').forEach(option => {
            option.classList.remove('selected');
        });

        // Add selection to clicked option
        const selectedOption = document.querySelector(`[data-score="${score}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }

        this.currentMood = score;

        // Enable save button
        const saveButton = document.getElementById('save-mood');
        if (saveButton) {
            saveButton.disabled = false;
        }
    }

    async saveMood() {
        if (!this.currentMood) return;

        const note = document.getElementById('mood-note')?.value || '';
        
        try {
            const response = await apiCall('analytics/mood', {
                method: 'POST',
                body: JSON.stringify({
                    mood_score: this.currentMood,
                    note: note,
                    timestamp: new Date().toISOString()
                })
            });

            if (response.success) {
                this.showMessage('Mood saved successfully!', 'success');
                await this.loadMoodHistory();
                this.render();
                this.resetMoodInput();
            } else {
                this.showMessage('Failed to save mood. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error saving mood:', error);
            this.showMessage('Error saving mood. Please try again.', 'error');
        }
    }

    resetMoodInput() {
        this.currentMood = null;
        document.querySelectorAll('.mood-option').forEach(option => {
            option.classList.remove('selected');
        });
        const saveButton = document.getElementById('save-mood');
        if (saveButton) {
            saveButton.disabled = true;
        }
        const noteInput = document.getElementById('mood-note');
        if (noteInput) {
            noteInput.value = '';
        }
    }

    initializeMoodChart() {
        const ctx = document.getElementById('mood-history-chart');
        if (!ctx) return;

        const chartData = this.moodHistory.map(item => ({
            x: new Date(item.timestamp),
            y: item.mood_score
        }));

        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Mood Score',
                    data: chartData,
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#FF6B6B',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
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
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    calculateAverageMood() {
        if (this.moodHistory.length === 0) return 'N/A';
        const total = this.moodHistory.reduce((sum, item) => sum + item.mood_score, 0);
        const average = total / this.moodHistory.length;
        return average.toFixed(1);
    }

    calculateTrackingStreak() {
        // Calculate consecutive days of mood tracking
        const today = new Date();
        let streak = 0;
        
        for (let i = 0; i < 30; i++) {
            const checkDate = new Date(today);
            checkDate.setDate(today.getDate() - i);
            
            const hasEntry = this.moodHistory.some(entry => {
                const entryDate = new Date(entry.timestamp);
                return entryDate.toDateString() === checkDate.toDateString();
            });
            
            if (hasEntry) {
                streak++;
            } else {
                break;
            }
        }
        
        return streak;
    }

    analyzeMoodPattern() {
        if (this.moodHistory.length < 3) return 'Need more data';
        
        const recentMoods = this.moodHistory.slice(-3).map(item => item.mood_score);
        const trend = recentMoods[recentMoods.length - 1] - recentMoods[0];
        
        if (trend > 1) return 'Improving';
        if (trend < -1) return 'Declining';
        return 'Stable';
    }

    getBestDayOfWeek() {
        const dayScores = {};
        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        
        this.moodHistory.forEach(entry => {
            const date = new Date(entry.timestamp);
            const dayName = dayNames[date.getDay()];
            
            if (!dayScores[dayName]) {
                dayScores[dayName] = { total: 0, count: 0 };
            }
            
            dayScores[dayName].total += entry.mood_score;
            dayScores[dayName].count++;
        });
        
        let bestDay = 'N/A';
        let bestAverage = 0;
        
        Object.entries(dayScores).forEach(([day, data]) => {
            const average = data.total / data.count;
            if (average > bestAverage) {
                bestAverage = average;
                bestDay = day;
            }
        });
        
        return bestDay;
    }

    getMoodTriggers() {
        // Analyze notes for common triggers
        const triggers = ['stress', 'work', 'family', 'exercise', 'sleep', 'food'];
        const triggerCounts = {};
        
        this.moodHistory.forEach(entry => {
            if (entry.note) {
                const note = entry.note.toLowerCase();
                triggers.forEach(trigger => {
                    if (note.includes(trigger)) {
                        triggerCounts[trigger] = (triggerCounts[trigger] || 0) + 1;
                    }
                });
            }
        });
        
        const topTrigger = Object.entries(triggerCounts)
            .sort(([,a], [,b]) => b - a)[0];
        
        return topTrigger ? topTrigger[0].charAt(0).toUpperCase() + topTrigger[0].slice(1) : 'Various factors';
    }

    getImprovementTrend() {
        if (this.moodHistory.length < 7) return 'Need more data';
        
        const recentWeek = this.moodHistory.slice(-7);
        const firstHalf = recentWeek.slice(0, 3);
        const secondHalf = recentWeek.slice(-3);
        
        const firstAvg = firstHalf.reduce((sum, item) => sum + item.mood_score, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((sum, item) => sum + item.mood_score, 0) / secondHalf.length;
        
        const improvement = secondAvg - firstAvg;
        
        if (improvement > 0.5) return 'Positive trend';
        if (improvement < -0.5) return 'Needs attention';
        return 'Stable';
    }

    async updateHistoryRange(days) {
        try {
            const response = await apiCall(`analytics/mood?days=${days}`);
            this.moodHistory = response.data || [];
            this.render();
        } catch (error) {
            console.error('Error updating history range:', error);
        }
    }

    startMoodJournal() {
        // Navigate to journaling section
        window.location.hash = '#journaling';
    }

    startTherapySession() {
        // Navigate to therapy section
        window.location.hash = '#therapy';
    }

    viewMoodAnalytics() {
        // Navigate to analytics section
        window.location.hash = '#analytics';
    }

    async exportMoodData() {
        try {
            const csv = this.convertToCSV(this.moodHistory);
            this.downloadCSV(csv, 'mood-data.csv');
        } catch (error) {
            console.error('Error exporting mood data:', error);
            this.showMessage('Error exporting data. Please try again.', 'error');
        }
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = ['Date', 'Mood Score', 'Note'];
        const csvRows = [headers.join(',')];
        
        data.forEach(item => {
            const date = new Date(item.timestamp).toLocaleDateString();
            const score = item.mood_score;
            const note = item.note ? `"${item.note.replace(/"/g, '""')}"` : '';
            csvRows.push(`${date},${score},${note}`);
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

    showMessage(message, type = 'info') {
        // Show a temporary message to the user
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        this.container.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// Initialize the mood tracker
const moodTracker = new MoodTracker(); 