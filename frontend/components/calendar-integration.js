// Calendar Integration Component
class CalendarIntegration {
    constructor() {
        this.container = null;
        this.calendars = [];
        this.scheduledEvents = [];
        this.reminders = [];
        this.isConnected = false;
        this.supportedProviders = ['gmail', 'outlook', 'apple'];
    }

    async init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Calendar integration container not found');
            return;
        }

        await this.loadCalendarData();
        this.render();
        this.setupEventListeners();
    }

    async loadCalendarData() {
        try {
            const [calendarsResponse, eventsResponse, remindersResponse] = await Promise.all([
                apiCall('calendar/calendars'),
                apiCall('calendar/events'),
                apiCall('calendar/reminders')
            ]);

            this.calendars = calendarsResponse.data || [];
            this.scheduledEvents = eventsResponse.data || [];
            this.reminders = remindersResponse.data || [];
        } catch (error) {
            console.error('Error loading calendar data:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="calendar-integration">
                <div class="integration-header">
                    <h2><i class="fas fa-calendar-alt"></i> Calendar Integration</h2>
                    <div class="connection-status">
                        <span class="status-indicator ${this.isConnected ? 'connected' : 'disconnected'}"></span>
                        <span>${this.isConnected ? 'Connected' : 'Not Connected'}</span>
                    </div>
                </div>

                <!-- Calendar Connection -->
                <div class="calendar-connection">
                    <h3><i class="fas fa-link"></i> Connect Your Calendar</h3>
                    <div class="provider-options">
                        ${this.supportedProviders.map(provider => `
                            <button class="provider-btn ${this.isProviderConnected(provider) ? 'connected' : ''}" 
                                    onclick="calendarIntegration.connectProvider('${provider}')">
                                <i class="fab fa-${provider}"></i>
                                <span>${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                                ${this.isProviderConnected(provider) ? '<i class="fas fa-check"></i>' : ''}
                            </button>
                        `).join('')}
                    </div>
                </div>

                <!-- AI Agent Controls -->
                <div class="ai-agent-controls">
                    <h3><i class="fas fa-robot"></i> AI Agent Settings</h3>
                    <div class="agent-settings">
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" id="auto-booking" ${this.getSetting('auto_booking') ? 'checked' : ''}>
                                Enable automatic appointment booking
                            </label>
                        </div>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" id="auto-reminders" ${this.getSetting('auto_reminders') ? 'checked' : ''}>
                                Enable automatic reminders
                            </label>
                        </div>
                        <div class="setting-item">
                            <label>
                                <input type="checkbox" id="smart-scheduling" ${this.getSetting('smart_scheduling') ? 'checked' : ''}>
                                Smart scheduling based on availability
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Scheduled Events -->
                <div class="scheduled-events">
                    <div class="section-header">
                        <h3><i class="fas fa-calendar-check"></i> Scheduled Events</h3>
                        <button class="btn btn-primary" onclick="calendarIntegration.createEvent()">
                            <i class="fas fa-plus"></i> Create Event
                        </button>
                    </div>
                    <div class="events-list">
                        ${this.renderScheduledEvents()}
                    </div>
                </div>

                <!-- Reminders -->
                <div class="reminders-section">
                    <h3><i class="fas fa-bell"></i> Reminders</h3>
                    <div class="reminders-list">
                        ${this.renderReminders()}
                    </div>
                </div>

                <!-- AI Agent Actions -->
                <div class="ai-actions">
                    <h3><i class="fas fa-magic"></i> AI Agent Actions</h3>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="calendarIntegration.scheduleTherapySession()">
                            <i class="fas fa-comments"></i>
                            <span>Schedule Therapy Session</span>
                        </button>
                        <button class="action-btn" onclick="calendarIntegration.scheduleAssignment()">
                            <i class="fas fa-tasks"></i>
                            <span>Schedule Assignment</span>
                        </button>
                        <button class="action-btn" onclick="calendarIntegration.scheduleReminder()">
                            <i class="fas fa-bell"></i>
                            <span>Set Reminder</span>
                        </button>
                        <button class="action-btn" onclick="calendarIntegration.optimizeSchedule()">
                            <i class="fas fa-chart-line"></i>
                            <span>Optimize Schedule</span>
                        </button>
                    </div>
                </div>

                <!-- Event Creation Modal -->
                <div id="event-modal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Create Calendar Event</h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <form id="event-form">
                                <div class="form-group">
                                    <label for="event-title">Event Title</label>
                                    <input type="text" id="event-title" required>
                                </div>
                                <div class="form-group">
                                    <label for="event-description">Description</label>
                                    <textarea id="event-description" rows="3"></textarea>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="event-date">Date</label>
                                        <input type="date" id="event-date" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="event-time">Time</label>
                                        <input type="time" id="event-time" required>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="event-duration">Duration (minutes)</label>
                                    <input type="number" id="event-duration" value="60" min="15" step="15">
                                </div>
                                <div class="form-group">
                                    <label for="event-calendar">Calendar</label>
                                    <select id="event-calendar">
                                        ${this.calendars.map(cal => `
                                            <option value="${cal.id}">${cal.name}</option>
                                        `).join('')}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>
                                        <input type="checkbox" id="event-reminder">
                                        Set reminder
                                    </label>
                                </div>
                                <div class="form-actions">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-save"></i> Create Event
                                    </button>
                                    <button type="button" class="btn btn-secondary" onclick="calendarIntegration.hideEventModal()">
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderScheduledEvents() {
        if (this.scheduledEvents.length === 0) {
            return `
                <div class="empty-events">
                    <i class="fas fa-calendar-times"></i>
                    <p>No scheduled events yet</p>
                </div>
            `;
        }

        return this.scheduledEvents.map(event => `
            <div class="event-card">
                <div class="event-header">
                    <div class="event-icon">
                        <i class="fas fa-${this.getEventIcon(event.type)}"></i>
                    </div>
                    <div class="event-status">
                        <span class="status-badge ${event.status}">${event.status}</span>
                    </div>
                </div>
                <div class="event-content">
                    <h4>${event.title}</h4>
                    <p>${event.description}</p>
                    <div class="event-meta">
                        <span class="event-date">
                            <i class="fas fa-calendar"></i>
                            ${this.formatDate(event.start_time)}
                        </span>
                        <span class="event-time">
                            <i class="fas fa-clock"></i>
                            ${this.formatTime(event.start_time)} - ${this.formatTime(event.end_time)}
                        </span>
                        <span class="event-calendar">
                            <i class="fas fa-calendar-alt"></i>
                            ${event.calendar_name}
                        </span>
                    </div>
                </div>
                <div class="event-actions">
                    <button class="btn-icon" onclick="calendarIntegration.editEvent('${event.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="calendarIntegration.deleteEvent('${event.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderReminders() {
        if (this.reminders.length === 0) {
            return `
                <div class="empty-reminders">
                    <i class="fas fa-bell-slash"></i>
                    <p>No reminders set</p>
                </div>
            `;
        }

        return this.reminders.map(reminder => `
            <div class="reminder-card">
                <div class="reminder-icon">
                    <i class="fas fa-bell"></i>
                </div>
                <div class="reminder-content">
                    <h5>${reminder.title}</h5>
                    <p>${reminder.description}</p>
                    <div class="reminder-meta">
                        <span class="reminder-time">
                            <i class="fas fa-clock"></i>
                            ${this.formatDateTime(reminder.reminder_time)}
                        </span>
                        <span class="reminder-type">
                            <i class="fas fa-tag"></i>
                            ${reminder.type}
                        </span>
                    </div>
                </div>
                <div class="reminder-actions">
                    <button class="btn-icon" onclick="calendarIntegration.editReminder('${reminder.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="calendarIntegration.deleteReminder('${reminder.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Event form submission
        const eventForm = document.getElementById('event-form');
        if (eventForm) {
            eventForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createEventFromForm();
            });
        }

        // Settings checkboxes
        const settings = ['auto-booking', 'auto-reminders', 'smart-scheduling'];
        settings.forEach(setting => {
            const checkbox = document.getElementById(setting);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.updateSetting(setting, e.target.checked);
                });
            }
        });

        // Modal close
        const modalClose = document.querySelector('.modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                this.hideEventModal();
            });
        }
    }

    async connectProvider(provider) {
        try {
            const response = await apiCall('calendar/connect', {
                method: 'POST',
                body: JSON.stringify({ provider })
            });

            if (response.success) {
                this.isConnected = true;
                this.showMessage(`Successfully connected to ${provider}!`, 'success');
                await this.loadCalendarData();
                this.render();
            } else {
                this.showMessage(`Failed to connect to ${provider}. Please try again.`, 'error');
            }
        } catch (error) {
            console.error('Error connecting to calendar provider:', error);
            this.showMessage('Error connecting to calendar provider.', 'error');
        }
    }

    isProviderConnected(provider) {
        return this.calendars.some(cal => cal.provider === provider);
    }

    async scheduleTherapySession() {
        try {
            const response = await apiCall('calendar/schedule-therapy', {
                method: 'POST',
                body: JSON.stringify({
                    type: 'therapy_session',
                    duration: 60,
                    preferences: {
                        time_slot: 'preferred',
                        reminder: true,
                        auto_booking: true
                    }
                })
            });

            if (response.success) {
                this.showMessage('Therapy session scheduled successfully!', 'success');
                await this.loadCalendarData();
                this.render();
            }
        } catch (error) {
            console.error('Error scheduling therapy session:', error);
            this.showMessage('Error scheduling therapy session.', 'error');
        }
    }

    async scheduleAssignment() {
        try {
            const response = await apiCall('calendar/schedule-assignment', {
                method: 'POST',
                body: JSON.stringify({
                    type: 'assignment',
                    duration: 30,
                    preferences: {
                        reminder: true,
                        flexible_timing: true
                    }
                })
            });

            if (response.success) {
                this.showMessage('Assignment scheduled successfully!', 'success');
                await this.loadCalendarData();
                this.render();
            }
        } catch (error) {
            console.error('Error scheduling assignment:', error);
            this.showMessage('Error scheduling assignment.', 'error');
        }
    }

    async scheduleReminder() {
        try {
            const response = await apiCall('calendar/schedule-reminder', {
                method: 'POST',
                body: JSON.stringify({
                    type: 'general_reminder',
                    reminder_time: new Date(Date.now() + 24 * 60 * 60 * 1000), // Tomorrow
                    message: 'Time for your daily wellness check-in!'
                })
            });

            if (response.success) {
                this.showMessage('Reminder scheduled successfully!', 'success');
                await this.loadCalendarData();
                this.render();
            }
        } catch (error) {
            console.error('Error scheduling reminder:', error);
            this.showMessage('Error scheduling reminder.', 'error');
        }
    }

    async optimizeSchedule() {
        try {
            const response = await apiCall('calendar/optimize', {
                method: 'POST',
                body: JSON.stringify({
                    optimize_for: 'wellness',
                    constraints: {
                        max_sessions_per_week: 3,
                        preferred_times: ['morning', 'afternoon'],
                        break_duration: 30
                    }
                })
            });

            if (response.success) {
                this.showMessage('Schedule optimized successfully!', 'success');
                await this.loadCalendarData();
                this.render();
            }
        } catch (error) {
            console.error('Error optimizing schedule:', error);
            this.showMessage('Error optimizing schedule.', 'error');
        }
    }

    createEvent() {
        const modal = document.getElementById('event-modal');
        if (modal) {
            modal.style.display = 'block';
        }
    }

    hideEventModal() {
        const modal = document.getElementById('event-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async createEventFromForm() {
        const formData = {
            title: document.getElementById('event-title').value,
            description: document.getElementById('event-description').value,
            date: document.getElementById('event-date').value,
            time: document.getElementById('event-time').value,
            duration: parseInt(document.getElementById('event-duration').value),
            calendar_id: document.getElementById('event-calendar').value,
            reminder: document.getElementById('event-reminder').checked
        };

        try {
            const response = await apiCall('calendar/events', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            if (response.success) {
                this.showMessage('Event created successfully!', 'success');
                this.hideEventModal();
                await this.loadCalendarData();
                this.render();
            }
        } catch (error) {
            console.error('Error creating event:', error);
            this.showMessage('Error creating event.', 'error');
        }
    }

    getEventIcon(type) {
        const icons = {
            'therapy_session': 'comments',
            'assignment': 'tasks',
            'reminder': 'bell',
            'meditation': 'om',
            'exercise': 'dumbbell',
            'general': 'calendar'
        };
        return icons[type] || 'calendar';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    getSetting(key) {
        const settings = JSON.parse(localStorage.getItem('calendar_settings') || '{}');
        return settings[key] || false;
    }

    updateSetting(key, value) {
        const settings = JSON.parse(localStorage.getItem('calendar_settings') || '{}');
        settings[key] = value;
        localStorage.setItem('calendar_settings', JSON.stringify(settings));
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        this.container.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// Initialize the calendar integration
const calendarIntegration = new CalendarIntegration(); 