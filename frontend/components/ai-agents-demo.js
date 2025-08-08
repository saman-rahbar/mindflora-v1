class AIAgentsDemo {
    constructor() {
        this.currentSession = JSON.parse(localStorage.getItem('currentSession')) || {};
        this.init();
    }

    async init() {
        try {
            console.log('🤖 Initializing AI Agents Demo...');
            this.render();
            this.setupEventListeners();
            await this.checkAgentsHealth();
        } catch (error) {
            console.error('Error initializing AI Agents Demo:', error);
        }
    }

    async checkAgentsHealth() {
        try {
            const response = await fetch('http://localhost:8000/api/v1/ai-agents/agents/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentSession.token}`
                }
            });

            if (response.ok) {
                const healthData = await response.json();
                this.updateHealthStatus(healthData);
            }
        } catch (error) {
            console.error('Error checking agents health:', error);
        }
    }

    updateHealthStatus(healthData) {
        const healthContainer = document.getElementById('agents-health');
        if (!healthContainer) return;

        let healthHTML = '<h4>🤖 AI Agents Status</h4>';
        
        if (healthData.agents) {
            for (const [agentName, status] of Object.entries(healthData.agents)) {
                const statusIcon = status.status === 'healthy' ? '✅' : '❌';
                const statusClass = status.status === 'healthy' ? 'healthy' : 'unhealthy';
                
                healthHTML += `
                    <div class="agent-status ${statusClass}">
                        <span class="agent-name">${agentName}</span>
                        <span class="status-icon">${statusIcon}</span>
                        <span class="status-text">${status.status}</span>
                    </div>
                `;
            }
        }

        healthContainer.innerHTML = healthHTML;
    }

    render() {
        const container = document.getElementById('ai-agents-demo');
        if (!container) return;

        container.innerHTML = `
            <div class="ai-agents-demo">
                <div class="demo-header">
                    <h2>🤖 AI Agents Demo</h2>
                    <p>Experience intelligent automation with calendar, email, and notification agents</p>
                </div>

                <div class="demo-content">
                    <div class="agents-overview">
                        <div class="agent-card calendar-agent">
                            <div class="agent-icon">📅</div>
                            <h3>Calendar Agent</h3>
                            <p>Automatically schedule appointments, therapy sessions, and manage your calendar</p>
                            <div class="agent-capabilities">
                                <span class="capability">Book appointments</span>
                                <span class="capability">Schedule therapy</span>
                                <span class="capability">Check availability</span>
                                <span class="capability">Send reminders</span>
                            </div>
                        </div>

                        <div class="agent-card email-agent">
                            <div class="agent-icon">📧</div>
                            <h3>Email Agent</h3>
                            <p>Send therapy summaries, reminders, and motivational messages automatically</p>
                            <div class="agent-capabilities">
                                <span class="capability">Send summaries</span>
                                <span class="capability">Reminders</span>
                                <span class="capability">Follow-ups</span>
                                <span class="capability">Motivational</span>
                            </div>
                        </div>

                        <div class="agent-card notification-agent">
                            <div class="agent-icon">🔔</div>
                            <h3>Notification Agent</h3>
                            <p>Send push notifications, SMS, and urgent alerts when needed</p>
                            <div class="agent-capabilities">
                                <span class="capability">Push notifications</span>
                                <span class="capability">SMS alerts</span>
                                <span class="capability">Urgent support</span>
                                <span class="capability">Mood checks</span>
                            </div>
                        </div>
                    </div>

                    <div class="demo-interaction">
                        <div class="interaction-header">
                            <h3>Try the AI Agents</h3>
                            <p>Ask for help with scheduling, reminders, or notifications</p>
                        </div>

                        <div class="demo-examples">
                            <div class="example-section">
                                <h4>📅 Calendar Examples:</h4>
                                <div class="example-buttons">
                                    <button class="example-btn" data-example="book therapy session for tomorrow at 2pm">Book therapy session</button>
                                    <button class="example-btn" data-example="check my availability for this week">Check availability</button>
                                    <button class="example-btn" data-example="schedule an appointment for next Monday">Schedule appointment</button>
                                </div>
                            </div>

                            <div class="example-section">
                                <h4>📧 Email Examples:</h4>
                                <div class="example-buttons">
                                    <button class="example-btn" data-example="send me a therapy session summary">Send summary</button>
                                    <button class="example-btn" data-example="send me a motivational message">Motivational message</button>
                                    <button class="example-btn" data-example="send me a reminder for my next session">Send reminder</button>
                                </div>
                            </div>

                            <div class="example-section">
                                <h4>🔔 Notification Examples:</h4>
                                <div class="example-buttons">
                                    <button class="example-btn" data-example="send me a push notification reminder">Push notification</button>
                                    <button class="example-btn" data-example="send me an SMS reminder">SMS reminder</button>
                                    <button class="example-btn" data-example="I need urgent support">Urgent support</button>
                                    <button class="example-btn" data-example="test sms">Test SMS</button>
                                </div>
                            </div>
                        </div>

                        <div class="custom-input">
                            <h4>Or type your own request:</h4>
                            <div class="input-container">
                                <textarea 
                                    id="agent-input" 
                                    placeholder="Try: 'Book a therapy session for next week' or 'Send me a motivational email'"
                                    rows="3"
                                ></textarea>
                                <button id="send-agent-request" class="send-btn">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>

                        <div id="agent-response" class="agent-response hidden">
                            <div class="response-header">
                                <h4>🤖 AI Agent Response</h4>
                                <button class="close-response">×</button>
                            </div>
                            <div class="response-content">
                                <div class="response-message"></div>
                                <div class="response-details"></div>
                                <div class="action-items"></div>
                            </div>
                        </div>
                    </div>

                    <div id="agents-health" class="agents-health">
                        <h4>🤖 AI Agents Status</h4>
                        <div class="loading">Loading agent status...</div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // Example buttons
        document.querySelectorAll('.example-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const example = e.target.dataset.example;
                document.getElementById('agent-input').value = example;
                this.sendAgentRequest(example);
            });
        });

        // Send button
        const sendButton = document.getElementById('send-agent-request');
        if (sendButton) {
            sendButton.addEventListener('click', () => {
                const input = document.getElementById('agent-input');
                const message = input.value.trim();
                if (message) {
                    this.sendAgentRequest(message);
                }
            });
        }

        // Enter key in textarea
        const input = document.getElementById('agent-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = input.value.trim();
                    if (message) {
                        this.sendAgentRequest(message);
                    }
                }
            });
        }

        // Close response
        document.querySelectorAll('.close-response').forEach(button => {
            button.addEventListener('click', () => {
                document.getElementById('agent-response').classList.add('hidden');
            });
        });
    }

    async sendAgentRequest(message) {
        try {
            const responseContainer = document.getElementById('agent-response');
            const messageDiv = responseContainer.querySelector('.response-message');
            const detailsDiv = responseContainer.querySelector('.response-details');
            const actionItemsDiv = responseContainer.querySelector('.action-items');

            // Show loading
            responseContainer.classList.remove('hidden');
            messageDiv.innerHTML = '<div class="loading">🤖 AI agents are processing your request...</div>';
            detailsDiv.innerHTML = '';
            actionItemsDiv.innerHTML = '';

            // Determine endpoint based on message
            let endpoint = 'http://localhost:8000/api/v1/ai-agents/enhanced-chat';
            if (message.toLowerCase().includes('test sms')) {
                endpoint = 'http://localhost:8000/api/v1/ai-agents/test-sms';
            }
            
            // Send request to appropriate endpoint
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentSession.token}`
                },
                body: JSON.stringify({
                    user_id: this.currentSession.user_id || 'demo_user',
                    message: message,
                    context: {
                        session_type: 'ai_agent_chat',
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayAgentResponse(data);
            } else {
                const errorData = await response.json();
                messageDiv.innerHTML = `<div class="error">❌ Error: ${errorData.detail || 'Failed to process request'}</div>`;
            }
        } catch (error) {
            console.error('Error sending agent request:', error);
            const messageDiv = document.querySelector('.response-message');
            messageDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
        }
    }

    displayAgentResponse(data) {
        const messageDiv = document.querySelector('.response-message');
        const detailsDiv = document.querySelector('.response-details');
        const actionItemsDiv = document.querySelector('.action-items');

        // Display main message - prioritize the main response
        if (data.response) {
            messageDiv.innerHTML = `<div class="success">🤖 AI Agent Response</div><div class="response-text">${data.response}</div>`;
        } else if (data.message) {
            // Handle SMS test response
            messageDiv.innerHTML = `<div class="success">📱 SMS Test Result</div><div class="response-text">${data.message}</div>`;
        } else {
            messageDiv.innerHTML = `<div class="error">❌ No response received</div>`;
        }

        // Display details
        let detailsHTML = '';
        
        // Display intent information
        if (data.intent) {
            detailsHTML += `
                <div class="detail-section">
                    <h5>🎯 Intent Analysis</h5>
                    <p>Primary Action: ${data.intent.primary_action || 'chat'}</p>
                    <p>Tools Requested: ${data.intent.tools_requested?.join(', ') || 'None'}</p>
                    <p>Therapy Related: ${data.intent.therapy_related ? 'Yes' : 'No'}</p>
                    <p>Urgency: ${data.intent.urgency_level || 'normal'}</p>
                </div>
            `;
        }

        // Only show tool actions if they're not just setup confirmations
        if (data.tool_actions && Object.keys(data.tool_actions).length > 0 && 
            !(data.intent && data.intent.primary_action === 'setup_sms' && data.user_profile_updated)) {
            detailsHTML += `
                <div class="detail-section">
                    <h5>🛠️ Tool Actions</h5>
                    <ul>
                        ${Object.entries(data.tool_actions).map(([action, result]) => {
                            let displayResult = result;
                            if (typeof result === 'object') {
                                if (result.error) {
                                    displayResult = `❌ ${result.error}`;
                                } else if (result.status === 'service_unavailable' || result.status === 'service_error') {
                                    displayResult = `❌ ${result.error || 'SMS service unavailable'}`;
                                } else {
                                    displayResult = JSON.stringify(result);
                                }
                            }
                            return `<li><strong>${action}:</strong> ${displayResult}</li>`;
                        }).join('')}
                    </ul>
                </div>
            `;
        }

        // Display profile update status
        if (data.user_profile_updated) {
            detailsHTML += `
                <div class="detail-section">
                    <h5>👤 Profile Updated</h5>
                    <p>✅ Your contact information has been saved for future use!</p>
                </div>
            `;
        }

        detailsDiv.innerHTML = detailsHTML;

        // Display action items (if any)
        if (data.action_items && data.action_items.length > 0) {
            let actionItemsHTML = '<h5>📋 Action Items</h5><ul>';
            data.action_items.forEach(item => {
                actionItemsHTML += `
                    <li class="action-item">
                        <span class="action-icon">${this.getActionIcon(item.type)}</span>
                        <div class="action-content">
                            <strong>${item.title}</strong>
                            <p>${item.description}</p>
                        </div>
                    </li>
                `;
            });
            actionItemsHTML += '</ul>';
            actionItemsDiv.innerHTML = actionItemsHTML;
        } else {
            actionItemsDiv.innerHTML = '';
        }
    }

    getActionIcon(type) {
        const icons = {
            'calendar_reminder': '📅',
            'therapy_preparation': '🧠',
            'email_sent': '📧',
            'notification_sent': '🔔',
            'crisis_support': '🚨',
            'mood_check': '💭',
            'achievement': '🎉',
            'therapy_reminder': '🩺',
            'daily_reminder': '🌅',
            'sms_sent': '📱'
        };
        return icons[type] || '📋';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ai-agents-demo')) {
        new AIAgentsDemo();
    }
}); 