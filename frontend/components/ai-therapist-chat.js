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
                        <button class="btn-icon" onclick="aiTherapistChat.exportSession()">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn-icon" onclick="aiTherapistChat.startNewSession()">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>

                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages">
                        ${this.renderWelcomeMessage()}
                        ${this.renderMessages()}
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
                            <button class="quick-action-btn" onclick="aiTherapistChat.sendQuickMessage('I\'m feeling anxious today')">
                                😰 Feeling Anxious
                            </button>
                            <button class="quick-action-btn" onclick="aiTherapistChat.sendQuickMessage('I need help with stress management')">
                                😤 Stress Management
                            </button>
                            <button class="quick-action-btn" onclick="aiTherapistChat.sendQuickMessage('I want to work on my goals')">
                                🎯 Goal Setting
                            </button>
                            <button class="quick-action-btn" onclick="aiTherapistChat.sendQuickMessage('I need someone to talk to')">
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

                <!-- Session Summary Modal -->
                <div id="session-modal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Session Summary</h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="session-summary">
                                <div class="summary-section">
                                    <h4>Session Overview</h4>
                                    <p>Duration: ${this.getSessionDuration()}</p>
                                    <p>Messages: ${this.currentSession.messages.length}</p>
                                    <p>Action Items: ${this.actionItems.length}</p>
                                </div>
                                <div class="summary-section">
                                    <h4>Key Topics Discussed</h4>
                                    <div class="topics-list">
                                        ${this.currentSession.topics.map(topic => `
                                            <span class="topic-tag">${topic}</span>
                                        `).join('')}
                                    </div>
                                </div>
                                <div class="summary-section">
                                    <h4>Next Steps</h4>
                                    <div class="next-steps">
                                        ${this.actionItems.map(item => `
                                            <div class="step-item">
                                                <i class="fas fa-check-circle"></i>
                                                <span>${item.description}</span>
                                                ${item.deadline ? `<span class="deadline">Due: ${item.deadline}</span>` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.scrollToBottom();
    }

    renderWelcomeMessage() {
        return `
            <div class="message therapist-message">
                <div class="message-avatar">
                    <i class="fas fa-user-md"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">${this.therapistPersonality.name}</span>
                        <span class="message-time">${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div class="message-text">
                        <p>Hello! I'm ${this.therapistPersonality.name}, your AI therapist. I'm here to support you on your mental health journey.</p>
                        <p>How are you feeling today? You can share anything that's on your mind, and I'll help you work through it together.</p>
                        <p>Remember, this is a safe space for you to express yourself openly.</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderMessages() {
        return this.currentSession.messages.map(message => `
            <div class="message ${message.sender}-message">
                <div class="message-avatar">
                    <i class="fas fa-${message.sender === 'therapist' ? 'user-md' : 'user'}"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">${message.sender === 'therapist' ? this.therapistPersonality.name : 'You'}</span>
                        <span class="message-time">${new Date(message.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div class="message-text">
                        ${message.content}
                    </div>
                    ${message.actionItems ? this.renderMessageActionItems(message.actionItems) : ''}
                </div>
            </div>
        `).join('');
    }

    renderMessageActionItems(actionItems) {
        if (!actionItems || actionItems.length === 0) return '';
        
        return `
            <div class="action-items-extracted">
                <h5><i class="fas fa-lightbulb"></i> Suggested Actions:</h5>
                <div class="action-items-grid">
                    ${actionItems.map(item => `
                        <div class="action-item-card" onclick="aiTherapistChat.addActionItem('${item.description}', '${item.deadline || ''}')">
                            <div class="action-icon">
                                <i class="fas fa-${item.icon || 'task'}"></i>
                            </div>
                            <div class="action-content">
                                <h6>${item.title}</h6>
                                <p>${item.description}</p>
                                ${item.deadline ? `<span class="deadline">Due: ${item.deadline}</span>` : ''}
                            </div>
                            <button class="add-action-btn">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderActionItems() {
        if (this.actionItems.length === 0) {
            return `
                <div class="empty-action-items">
                    <i class="fas fa-clipboard-list"></i>
                    <p>No action items yet. Start a conversation to get personalized recommendations!</p>
                </div>
            `;
        }

        return this.actionItems.map((item, index) => `
            <div class="action-item ${item.completed ? 'completed' : ''}" data-index="${index}">
                <div class="action-checkbox">
                    <input type="checkbox" 
                           id="action-${index}" 
                           ${item.completed ? 'checked' : ''}
                           onchange="aiTherapistChat.toggleActionItem(${index})">
                    <label for="action-${index}"></label>
                </div>
                <div class="action-content">
                    <h6>${item.title}</h6>
                    <p>${item.description}</p>
                    ${item.deadline ? `<span class="deadline">Due: ${item.deadline}</span>` : ''}
                </div>
                <div class="action-actions">
                    <button class="btn-icon" onclick="aiTherapistChat.editActionItem(${index})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="aiTherapistChat.deleteActionItem(${index})">
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
            if (response.actionItems) {
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
            const response = await apiCall('therapy/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: userMessage,
                    session_id: this.currentSession.id,
                    therapist_personality: this.therapistPersonality,
                    conversation_history: this.currentSession.messages.slice(-5) // Last 5 messages for context
                })
            });

            if (response && response.content) {
                return {
                    content: response.content,
                    actionItems: response.action_items || []
                };
            } else {
                // Fallback response with personalized content
                const fallbackResponses = [
                    "I understand how you're feeling. Let's work through this together. What specific aspect would you like to focus on?",
                    "Thank you for sharing that with me. I'm here to listen and support you. How can I help you today?",
                    "I appreciate you opening up to me. Let's explore this together. What would be most helpful for you right now?",
                    "I hear you, and I want you to know that your feelings are valid. Let's work on this step by step."
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
        } catch (error) {
            console.error('Error getting therapist response:', error);
            return {
                content: "I'm here to listen and help. Could you tell me more about what's on your mind?",
                actionItems: [
                    {
                        title: "Daily Check-in",
                        description: "Practice daily self-reflection",
                        deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
                    }
                ]
            };
        }
    }

    addMessage(sender, content, actionItems = null) {
        const message = {
            sender,
            content,
            timestamp: new Date(),
            actionItems
        };

        this.currentSession.messages.push(message);
        this.messages.push(message);

        // Extract topics from user messages
        if (sender === 'user') {
            this.extractTopics(content);
        }

        this.render();
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
        this.isTyping = true;
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message therapist-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-md"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${this.therapistPersonality.name}</span>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
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
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    getSessionDuration() {
        const duration = new Date() - this.currentSession.startTime;
        const minutes = Math.floor(duration / 60000);
        return `${minutes} minutes`;
    }

    exportSession() {
        const sessionData = {
            session: this.currentSession,
            actionItems: this.actionItems,
            exportDate: new Date()
        };

        const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `therapy-session-${this.currentSession.id}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    startNewSession() {
        // Save current session if it has content
        if (this.currentSession && this.currentSession.messages.length > 0) {
            this.saveSession();
        }

        this.startNewSession();
        this.actionItems = [];
        this.render();
    }

    async saveSession() {
        try {
            await apiCall('therapy/sessions', {
                method: 'POST',
                body: JSON.stringify(this.currentSession)
            });
        } catch (error) {
            console.error('Error saving session:', error);
        }
    }
}

// Initialize the AI therapist chat
const aiTherapistChat = new AITherapistChat(); 