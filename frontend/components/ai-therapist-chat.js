// AI Therapist Chat Component
class AITherapistChat {
    constructor() {
        this.container = null;
        this.messages = [];
        this.currentSession = null;
        this.actionItems = [];
        this.isTyping = false;
        this.therapistPersonality = {
            name: "Dr. Sarah",
            style: "compassionate",
            approach: "evidence-based",
            specialties: ["CBT", "Mindfulness", "Stress Management"]
        };
    }

    async init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('AI therapist chat container not found');
            return;
        }

        this.startNewSession();
        this.render();
        this.setupEventListeners();
    }

    startNewSession() {
        this.currentSession = {
            id: Date.now(),
            startTime: new Date(),
            messages: [],
            actionItems: [],
            mood: null,
            topics: []
        };
    }

    render() {
        this.container.innerHTML = `
            <div class="ai-therapist-chat">
                <div class="chat-header">
                    <div class="therapist-info">
                        <div class="therapist-avatar">
                            <i class="fas fa-user-md"></i>
                        </div>
                        <div class="therapist-details">
                            <h3>${this.therapistPersonality.name}</h3>
                            <p>AI Therapist • ${this.therapistPersonality.specialties.join(', ')}</p>
                            <div class="session-status">
                                <span class="status-indicator online"></span>
                                <span>Online - Ready to help</span>
                            </div>
                        </div>
                    </div>
                    <div class="chat-controls">
                        <select id="therapy-type-selector" class="therapy-selector">
                            <option value="cbt">🧠 CBT</option>
                            <option value="logotherapy">🎯 Logotherapy</option>
                            <option value="act">🌱 ACT</option>
                            <option value="dbt">⚖️ DBT</option>
                            <option value="somotherapy">💆 Somotherapy</option>
                            <option value="positive_psychology">✨ Positive Psychology</option>
                        </select>
                        <button class="btn-icon" id="export-session-btn">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn-icon" id="new-session-btn">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>

                <div class="chat-container">
                                    <div class="chat-messages" id="chat-messages">
                    ${this.messages.length === 0 ? this.renderWelcomeMessage() : this.renderMessages()}
                </div>

                    <div class="chat-input-section">
                        <div class="input-container">
                            <textarea 
                                id="chat-input" 
                                placeholder="Share what's on your mind..."
                                rows="3"
                            ></textarea>
                            <button id="send-message" class="send-btn" disabled>
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <div class="quick-actions">
                            <button class="quick-action-btn" data-message="I'm feeling anxious today">
                                😰 Feeling Anxious
                            </button>
                            <button class="quick-action-btn" data-message="I need help with stress management">
                                😤 Stress Management
                            </button>
                            <button class="quick-action-btn" data-message="I want to work on my goals">
                                🎯 Goal Setting
                            </button>
                            <button class="quick-action-btn" data-message="I need someone to talk to">
                                💬 Just Talk
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Action Items Panel -->
                <div class="action-items-panel">
                    <div class="panel-header">
                        <h4><i class="fas fa-tasks"></i> Action Items</h4>
                        <span class="item-count">${this.actionItems.length} items</span>
                    </div>
                    <div class="action-items-list" id="action-items-list">
                        ${this.renderActionItems()}
                    </div>
                </div>
            </div>
        `;
    }

    renderWelcomeMessage() {
        return `
            <div class="message therapist">
                <div class="message-avatar">
                    <i class="fas fa-user-md"></i>
                </div>
                <div class="message-content">
                    Hello! I'm ${this.therapistPersonality.name}, your AI therapist. I'm here to listen, support, and help you work through whatever you're experiencing. How can I help you today?
                </div>
            </div>
        `;
    }

    renderMessages() {
        return this.messages.map(message => `
            <div class="message ${message.sender}">
                <div class="message-avatar">
                    <i class="fas fa-${message.sender === 'user' ? 'user' : 'user-md'}"></i>
                </div>
                <div class="message-content">
                    ${message.content}
                    ${message.actionItems ? this.renderMessageActionItems(message.actionItems) : ''}
                </div>
            </div>
        `).join('');
    }

    renderMessageActionItems(actionItems) {
        if (!actionItems || actionItems.length === 0) return '';
        
        return `
            <div class="action-items" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                <h5 style="margin: 0 0 8px 0; font-size: 12px; color: #007AFF;">Action Items:</h5>
                ${actionItems.map(item => `
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 12px;">
                        <i class="fas fa-lightbulb" style="color: #FFD93D;"></i>
                        <span>${item.title || item.description}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderActionItems() {
        if (this.actionItems.length === 0) {
            return '<p style="text-align: center; color: #86868b; font-style: italic;">No action items yet. Start a conversation to generate some!</p>';
        }

        return this.actionItems.map((item, index) => `
            <div class="action-item ${item.completed ? 'completed' : ''}">
                <div class="action-item-checkbox" onclick="window.aiTherapistChat.toggleActionItem(${index})"></div>
                <div class="action-item-content">
                    <div class="action-item-title">${item.title}</div>
                    <div class="action-item-description">${item.description}</div>
                </div>
                <div class="action-item-actions">
                    <button class="btn-edit" onclick="window.aiTherapistChat.editActionItem(${index})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-delete" onclick="window.aiTherapistChat.deleteActionItem(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-message');

        if (input) {
            input.addEventListener('input', () => {
                sendBtn.disabled = !input.value.trim();
            });

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Add event listeners for quick action buttons
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendQuickMessage(message);
            });
        });

        // Add event listeners for control buttons
        const exportBtn = document.getElementById('export-session-btn');
        const newSessionBtn = document.getElementById('new-session-btn');

        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportSession();
            });
        }

        if (newSessionBtn) {
            newSessionBtn.addEventListener('click', () => {
                this.resetSession();
            });
        }

        // Therapy type selector
        const therapySelector = document.getElementById('therapy-type-selector');
        if (therapySelector) {
            therapySelector.addEventListener('change', (e) => {
                this.currentSession.therapyType = e.target.value;
                console.log('Therapy type changed to:', e.target.value);
            });
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';
        document.getElementById('send-message').disabled = true;

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to AI therapist
            const response = await this.getTherapistResponse(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add therapist response
            this.addMessage('therapist', response.content, response.actionItems);
            
            // Extract and add action items
            if (response.actionItems && response.actionItems.length > 0) {
                response.actionItems.forEach(item => {
                    this.addActionItem(item.description, item.deadline, item.title);
                });
            }

        } catch (error) {
            console.error('Error getting therapist response:', error);
            this.hideTypingIndicator();
            this.addMessage('therapist', 'I apologize, but I\'m having trouble processing your message right now. Please try again in a moment.');
        }
    }

    sendQuickMessage(message) {
        const input = document.getElementById('chat-input');
        input.value = message;
        input.focus();
        document.getElementById('send-message').disabled = false;
    }

    async getTherapistResponse(userMessage) {
        try {
            // Get user context for personalization
            const userContext = this.getUserContext();
            
            const response = await apiCall('/ai-chat/send-message', {
                method: 'POST',
                body: JSON.stringify({
                    message: userMessage,
                    session_id: this.currentSession?.id,
                    therapy_type: this.currentSession?.therapyType || 'cbt',
                    user_context: userContext
                })
            });
            
            if (response && response.response) {
                // Update session with new data
                if (response.session_id) {
                    this.currentSession.id = response.session_id;
                }
                
                return {
                    content: response.response,
                    actionItems: response.action_items || []
                };
            } else {
                throw new Error('Invalid response from AI service');
            }
        } catch (error) {
            console.error('Error getting therapist response:', error);
            
            // Fallback response if API fails
            const fallbackResponses = [
                "I hear you, and I want you to know that your feelings are valid. What you're experiencing is a common human experience, and it's okay to feel this way.",
                "That sounds really challenging. I can sense the weight of what you're carrying. Remember, you don't have to face this alone.",
                "I appreciate you sharing this with me. It takes courage to be vulnerable. Let's work together to find some clarity."
            ];
            
            return {
                content: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
                actionItems: [
                    {
                        title: "Reflection Exercise",
                        description: "Take 5 minutes to reflect on what we discussed",
                        deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
                    }
                ]
            };
        }
    }

    getUserContext() {
        // Get user info from localStorage or API
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        return {
            name: userInfo.first_name || 'User',
            age: userInfo.age || null,
            education_level: userInfo.education_level || null,
            therapy_preference: userInfo.therapy_preference || 'cbt'
        };
    }

    addMessage(sender, content, actionItems = null) {
        const message = {
            sender,
            content,
            timestamp: new Date(),
            actionItems: actionItems || []
        };

        this.currentSession.messages.push(message);
        this.messages.push(message);

        // Extract topics from user messages
        if (sender === 'user') {
            this.extractTopics(content);
        }

        this.render();
        this.scrollToBottom();
    }

    extractTopics(message) {
        const topics = ['anxiety', 'stress', 'depression', 'goals', 'relationships', 'work', 'family', 'health'];
        const messageLower = message.toLowerCase();
        
        topics.forEach(topic => {
            if (messageLower.includes(topic) && !this.currentSession.topics.includes(topic)) {
                this.currentSession.topics.push(topic);
            }
        });
    }

    addActionItem(description, deadline = null, title = null) {
        const actionItem = {
            id: Date.now(),
            title: title || 'Action Item',
            description,
            deadline,
            completed: false,
            created_at: new Date(),
            session_id: this.currentSession.id
        };

        this.actionItems.push(actionItem);
        this.currentSession.actionItems.push(actionItem);

        // Save to backend
        this.saveActionItem(actionItem);

        this.render();
    }

    async saveActionItem(actionItem) {
        try {
            await apiCall('therapy/action-items', {
                method: 'POST',
                body: JSON.stringify(actionItem)
            });
        } catch (error) {
            console.error('Error saving action item:', error);
        }
    }

    toggleActionItem(index) {
        this.actionItems[index].completed = !this.actionItems[index].completed;
        this.render();
        
        // Update in backend
        this.updateActionItem(this.actionItems[index]);
    }

    editActionItem(index) {
        const item = this.actionItems[index];
        const newTitle = prompt('Edit action item title:', item.title);
        const newDescription = prompt('Edit action item description:', item.description);
        const newDeadline = prompt('Edit deadline (YYYY-MM-DD):', item.deadline);

        if (newTitle && newDescription) {
            item.title = newTitle;
            item.description = newDescription;
            item.deadline = newDeadline;
            this.render();
            this.updateActionItem(item);
        }
    }

    deleteActionItem(index) {
        if (confirm('Are you sure you want to delete this action item?')) {
            const item = this.actionItems[index];
            this.actionItems.splice(index, 1);
            this.render();
            this.deleteActionItemFromBackend(item.id);
        }
    }

    async updateActionItem(actionItem) {
        try {
            await apiCall(`therapy/action-items/${actionItem.id}`, {
                method: 'PUT',
                body: JSON.stringify(actionItem)
            });
        } catch (error) {
            console.error('Error updating action item:', error);
        }
    }

    async deleteActionItemFromBackend(itemId) {
        try {
            await apiCall(`therapy/action-items/${itemId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Error deleting action item:', error);
        }
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message therapist typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-md"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    getSessionDuration() {
        return Math.round((new Date() - this.currentSession.startTime) / 1000);
    }

    exportSession() {
        const sessionData = {
            session: this.currentSession,
            messages: this.messages,
            actionItems: this.actionItems,
            duration: this.getSessionDuration()
        };

        const dataStr = JSON.stringify(sessionData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `therapy-session-${this.currentSession.id}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    resetSession() {
        this.messages = [];
        this.actionItems = [];
        this.currentSession = {
            id: Date.now(),
            startTime: new Date(),
            messages: [],
            actionItems: [],
            mood: null,
            topics: []
        };
        this.render();
    }

    async saveSession() {
        try {
            await apiCall('therapy/sessions', {
                method: 'POST',
                body: JSON.stringify({
                    session: this.currentSession,
                    messages: this.messages,
                    actionItems: this.actionItems
                })
            });
        } catch (error) {
            console.error('Error saving session:', error);
        }
    }
}

// Initialize the AI therapist chat
const aiTherapistChat = new AITherapistChat(); 