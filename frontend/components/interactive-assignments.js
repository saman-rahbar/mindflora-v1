// Interactive Assignments Component
class InteractiveAssignments {
    constructor() {
        console.log('InteractiveAssignments constructor called');
        this.container = null;
        this.assignments = [];
        this.currentAssignment = null;
        this.categories = {
            'homework': { icon: 'fas fa-book', color: '#007AFF' },
            'exercise': { icon: 'fas fa-dumbbell', color: '#00B894' },
            'meditation': { icon: 'fas fa-om', color: '#6C5CE7' },
            'journaling': { icon: 'fas fa-pen', color: '#FF6B6B' },
            'social': { icon: 'fas fa-users', color: '#FD79A8' },
            'self-care': { icon: 'fas fa-heart', color: '#FFD93D' }
        };
    }

    async init(containerId) {
        console.log('InteractiveAssignments init called with containerId:', containerId);
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Interactive assignments container not found:', containerId);
            return;
        }
        console.log('Container found:', this.container);

        console.log('Loading assignments data...');
        await this.loadAssignments();
        console.log('Assignments loaded:', this.assignments.length, 'assignments');
        
        console.log('Rendering assignments...');
        this.render();
        console.log('Setting up event listeners...');
        this.setupEventListeners();
        console.log('InteractiveAssignments initialization complete');
    }

    async refreshAssignments() {
        console.log('refreshAssignments: Force refreshing assignments');
        await this.loadAssignments();
        this.render();
        console.log('refreshAssignments: Refresh complete');
    }

    async loadAssignments() {
        try {
            console.log('loadAssignments: Starting to load assignments');
            
            // Check for current assignment from therapy session
            const currentAssignment = localStorage.getItem('currentAssignment');
            let assignments = [];
            
            console.log('loadAssignments: Current assignment from localStorage:', currentAssignment);
            
            if (currentAssignment) {
                try {
                    const parsedAssignment = JSON.parse(currentAssignment);
                    assignments.push(parsedAssignment);
                    console.log('loadAssignments: Added assignment from localStorage:', parsedAssignment);
                    
                    // Mark this as the active assignment
                    parsedAssignment.isActive = true;
                    this.currentAssignment = parsedAssignment;
                } catch (parseError) {
                    console.error('loadAssignments: Error parsing localStorage assignment:', parseError);
                }
            }
            
            console.log('loadAssignments: Making API call to therapy/assignments');
            const response = await apiCall('therapy/assignments');
            console.log('loadAssignments: API response:', response);
            
            if (response && response.data) {
                // Merge with API assignments, avoiding duplicates
                const apiAssignments = response.data.filter(apiAssignment => 
                    !assignments.some(existing => existing.id === apiAssignment.id)
                );
                this.assignments = [...assignments, ...apiAssignments];
                console.log('loadAssignments: Merged assignments with API data:', this.assignments);
            } else {
                // If no current assignment and API fails, use mock data
                if (assignments.length === 0) {
                    console.log('loadAssignments: No assignments found, using mock data');
                    this.assignments = [
                        {
                            id: "1",
                            title: "Daily Mood Check-in",
                            description: "Take 5 minutes to reflect on your mood and write down 3 things you're grateful for.",
                            category: "homework",
                            status: "active",
                            estimated_duration: 15,
                            deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
                            progress: 0,
                            instructions: "Find a quiet place, take deep breaths, and reflect on your day.",
                            materials: ["Journal", "Quiet space"],
                            progress_questions: [
                                "How are you feeling about this assignment?",
                                "What challenges did you encounter?",
                                "What insights did you gain?",
                                "How can you apply this learning?"
                            ]
                        }
                    ];
                } else {
                    this.assignments = assignments;
                    console.log('loadAssignments: Using localStorage assignments only:', this.assignments);
                }
            }
        } catch (error) {
            console.error('Error loading assignments:', error);
            // Use mock data as fallback
            this.assignments = [
                {
                    id: "1",
                    title: "Daily Mood Check-in",
                    description: "Take 5 minutes to reflect on your mood and write down 3 things you're grateful for.",
                    category: "homework",
                    status: "active",
                    estimated_duration: 15,
                    deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
                    progress: 0,
                    instructions: "Find a quiet place, take deep breaths, and reflect on your day.",
                    materials: ["Journal", "Quiet space"],
                    progress_questions: [
                        "How are you feeling about this assignment?",
                        "What challenges did you encounter?",
                        "What insights did you gain?",
                        "How can you apply this learning?"
                    ]
                }
            ];
        }
    }

    render() {
        console.log('render: Starting to render assignments component');
        console.log('render: Container:', this.container);
        console.log('render: Assignments to render:', this.assignments);
        
        if (!this.container) {
            console.error('render: Container is null, cannot render');
            return;
        }
        
        try {
            this.container.innerHTML = `
            <div class="interactive-assignments">
                <div class="assignments-header">
                    <h2><i class="fas fa-tasks"></i> Your Assignments</h2>
                    <div class="assignments-stats">
                        <div class="stat-item">
                            <span class="stat-number">${this.getActiveCount()}</span>
                            <span class="stat-label">Active</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.getCompletedCount()}</span>
                            <span class="stat-label">Completed</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.calculateCompletionRate()}%</span>
                            <span class="stat-label">Success Rate</span>
                        </div>
                    </div>
                </div>

                <!-- Assignment Categories -->
                <div class="assignment-categories">
                    <button class="category-btn active" data-category="all">
                        <i class="fas fa-th"></i> All
                    </button>
                    ${Object.entries(this.categories).map(([category, info]) => `
                        <button class="category-btn" data-category="${category}">
                            <i class="${info.icon}"></i> ${category.charAt(0).toUpperCase() + category.slice(1)}
                        </button>
                    `).join('')}
                </div>

                <!-- Assignments Grid -->
                <div class="assignments-grid">
                    ${this.renderAssignments()}
                </div>

                <!-- Assignment Detail Modal -->
                <div id="assignment-modal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3 id="modal-title"></h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div id="modal-content"></div>
                        </div>
                    </div>
                </div>

                <!-- Progress Tracking -->
                <div class="progress-tracking">
                    <h3><i class="fas fa-chart-line"></i> Progress Overview</h3>
                    <div class="progress-cards">
                        ${this.renderProgressCards()}
                    </div>
                </div>
            </div>
        `;
            console.log('render: Successfully rendered assignments component');
        } catch (error) {
            console.error('render: Error rendering assignments:', error);
            this.container.innerHTML = `
                <div class="interactive-assignments">
                    <div class="assignments-header">
                        <h2><i class="fas fa-tasks"></i> Your Assignments</h2>
                    </div>
                    <div style="padding: 40px; text-align: center;">
                        <p>Error rendering assignments: ${error.message}</p>
                        <button onclick="window.interactiveAssignments.render()">Try Again</button>
                    </div>
                </div>
            `;
        }
    }

    renderAssignments() {
        if (this.assignments.length === 0) {
            return `
                <div class="empty-assignments">
                    <i class="fas fa-clipboard-list"></i>
                    <h3>No assignments yet</h3>
                    <p>Start a therapy session to receive personalized assignments!</p>
                    <button class="btn btn-primary" onclick="interactiveAssignments.startTherapySession()">
                        <i class="fas fa-comments"></i> Start Therapy Session
                    </button>
                </div>
            `;
        }

        return this.assignments.map(assignment => `
            <div class="assignment-card ${assignment.status}" 
                 data-category="${assignment.category || 'general'}"
                 onclick="interactiveAssignments.openAssignment('${assignment.id}')">
                <div class="assignment-header">
                    <div class="assignment-icon" style="color: ${this.categories[assignment.category]?.color || '#6C757D'}">
                        <i class="${this.categories[assignment.category]?.icon || 'fas fa-star'}"></i>
                    </div>
                    <div class="assignment-status">
                        <span class="status-badge ${assignment.status}">${assignment.status}</span>
                    </div>
                </div>
                <div class="assignment-content">
                    <h4>
                        ${assignment.title}
                        ${assignment.isActive ? '<span class="therapy-badge"><i class="fas fa-heart"></i> Therapy</span>' : ''}
                    </h4>
                    <p>${assignment.description}</p>
                    <div class="assignment-meta">
                        <span class="assignment-category">${assignment.category || 'General'}</span>
                        <span class="assignment-duration">${assignment.estimated_duration || '15 min'}</span>
                    </div>
                    ${assignment.deadline ? `
                        <div class="assignment-deadline">
                            <i class="fas fa-calendar"></i>
                            <span>Due: ${this.formatDate(assignment.deadline)}</span>
                        </div>
                    ` : ''}
                    ${assignment.progress ? `
                        <div class="assignment-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${assignment.progress}%"></div>
                            </div>
                            <span class="progress-text">${assignment.progress}% complete</span>
                        </div>
                    ` : ''}
                </div>
                <div class="assignment-actions">
                    <button class="btn-start" data-assignment-id="${assignment.id}">
                        <i class="fas fa-play"></i> Start
                    </button>
                    <button class="btn-view" data-assignment-id="${assignment.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderProgressCards() {
        const categoryProgress = {};
        
        this.assignments.forEach(assignment => {
            const category = assignment.category || 'general';
            if (!categoryProgress[category]) {
                categoryProgress[category] = { total: 0, completed: 0, active: 0 };
            }
            categoryProgress[category].total++;
            if (assignment.status === 'completed') {
                categoryProgress[category].completed++;
            } else if (assignment.status === 'active') {
                categoryProgress[category].active++;
            }
        });

        return Object.entries(categoryProgress).map(([category, progress]) => {
            const percentage = Math.round((progress.completed / progress.total) * 100);
            const categoryInfo = this.categories[category] || { icon: 'fas fa-star', color: '#6C757D' };
            
            return `
                <div class="progress-card">
                    <div class="progress-icon" style="color: ${categoryInfo.color}">
                        <i class="${categoryInfo.icon}"></i>
                    </div>
                    <div class="progress-info">
                        <h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>
                        <div class="progress-stats">
                            <span>${progress.completed}/${progress.total}</span>
                            <span class="progress-percentage">${percentage}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    setupEventListeners() {
        // Category filter buttons
        const categoryButtons = document.querySelectorAll('.category-btn');
        categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.filterByCategory(button.dataset.category);
                
                // Update active button
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });

        // Assignment action buttons
        const startButtons = document.querySelectorAll('.btn-start');
        startButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const assignmentId = button.getAttribute('data-assignment-id');
                this.startAssignment(assignmentId);
            });
        });

        const viewButtons = document.querySelectorAll('.btn-view');
        viewButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const assignmentId = button.getAttribute('data-assignment-id');
                const assignment = this.assignments.find(a => a.id === assignmentId);
                if (assignment) {
                    this.showAssignmentModal(assignment);
                }
            });
        });

        // Modal close button
        const modalClose = document.querySelector('.modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                this.hideAssignmentModal();
            });
        }

        // Close modal when clicking outside
        const modal = document.getElementById('assignment-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideAssignmentModal();
                }
            });
        }
    }

    filterByCategory(category) {
        const assignmentCards = document.querySelectorAll('.assignment-card');
        
        assignmentCards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    openAssignment(assignmentId) {
        const assignment = this.assignments.find(a => a.id === assignmentId);
        if (!assignment) return;

        this.currentAssignment = assignment;
        this.showAssignmentModal(assignment);
    }

    showAssignmentModal(assignment) {
        const modal = document.getElementById('assignment-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');

        modalTitle.textContent = assignment.title;
        modalContent.innerHTML = `
            <div class="assignment-detail">
                <div class="detail-header">
                    <div class="detail-icon" style="color: ${this.categories[assignment.category]?.color || '#6C757D'}">
                        <i class="${this.categories[assignment.category]?.icon || 'fas fa-star'}"></i>
                    </div>
                    <div class="detail-info">
                        <h4>${assignment.title}</h4>
                        <p>${assignment.description}</p>
                    </div>
                </div>
                
                <div class="detail-stats">
                    <div class="stat-item">
                        <span class="stat-label">Category</span>
                        <span class="stat-value">${assignment.category || 'General'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Duration</span>
                        <span class="stat-value">${assignment.estimated_duration || '15 min'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Status</span>
                        <span class="stat-value ${assignment.status}">${assignment.status}</span>
                    </div>
                    ${assignment.deadline ? `
                        <div class="stat-item">
                            <span class="stat-label">Deadline</span>
                            <span class="stat-value">${this.formatDate(assignment.deadline)}</span>
                        </div>
                    ` : ''}
                </div>

                ${assignment.instructions ? `
                    <div class="detail-instructions">
                        <h5>Instructions</h5>
                        <div class="instructions-content">
                            ${assignment.instructions}
                        </div>
                    </div>
                ` : ''}

                ${assignment.materials ? `
                    <div class="detail-materials">
                        <h5>Materials Needed</h5>
                        <ul>
                            ${assignment.materials.map(material => `
                                <li><i class="fas fa-check"></i> ${material}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                <div class="assignment-actions">
                    <button class="btn btn-primary" onclick="interactiveAssignments.startAssignment('${assignment.id}')">
                        <i class="fas fa-play"></i> Start Assignment
                    </button>
                    <button class="btn btn-secondary" onclick="interactiveAssignments.markComplete('${assignment.id}')">
                        <i class="fas fa-check"></i> Mark Complete
                    </button>
                    <button class="btn btn-outline" onclick="interactiveAssignments.logProgress('${assignment.id}')">
                        <i class="fas fa-edit"></i> Log Progress
                    </button>
                </div>
            </div>
        `;

        modal.style.display = 'block';
    }

    hideAssignmentModal() {
        const modal = document.getElementById('assignment-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async startAssignment(assignmentId) {
        const assignment = this.assignments.find(a => a.id === assignmentId);
        if (!assignment) return;

        // Update assignment status
        assignment.status = 'active';
        assignment.started_at = new Date();

        // Save to backend
        await this.updateAssignment(assignment);

        // Show assignment workspace
        this.showAssignmentWorkspace(assignment);
    }

    showAssignmentWorkspace(assignment) {
        const workspaceHTML = `
            <div class="assignment-workspace-modern">
                <!-- Header with clear task info -->
                <div class="workspace-header-modern">
                    <div class="task-info">
                        <div class="task-category">
                            <span class="category-badge ${assignment.category}">${assignment.category.toUpperCase()}</span>
                        </div>
                        <h2 class="task-title">${assignment.title}</h2>
                        <p class="task-description">${assignment.description}</p>
                        <div class="task-meta">
                            <span class="estimated-time">
                                <i class="fas fa-clock"></i> ${assignment.estimated_duration} minutes
                            </span>
                            <span class="deadline">
                                <i class="fas fa-calendar"></i> Due: ${new Date(assignment.deadline).toLocaleDateString()}
                            </span>
                        </div>
                    </div>
                    <button class="close-btn" onclick="interactiveAssignments.closeWorkspace()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <!-- Step-by-step guide -->
                <div class="assignment-steps">
                    <div class="step-indicator">
                        <div class="step active" data-step="1">
                            <div class="step-number">1</div>
                            <div class="step-label">Prepare</div>
                        </div>
                        <div class="step" data-step="2">
                            <div class="step-number">2</div>
                            <div class="step-label">Practice</div>
                        </div>
                        <div class="step" data-step="3">
                            <div class="step-number">3</div>
                            <div class="step-label">Reflect</div>
                        </div>
                        <div class="step" data-step="4">
                            <div class="step-number">4</div>
                            <div class="step-label">Complete</div>
                        </div>
                    </div>

                    <!-- Step 1: Preparation -->
                    <div class="step-content active" id="step-1">
                        <div class="step-card">
                            <h3><i class="fas fa-lightbulb"></i> Let's Get Started!</h3>
                            <div class="instructions">
                                <h4>Your Task:</h4>
                                <p class="task-instructions">${assignment.instructions || assignment.description}</p>
                                
                                <h4>What You'll Need:</h4>
                                <ul class="materials-list">
                                    ${(assignment.materials || ['A quiet space', 'Your phone/computer']).map(material => 
                                        `<li><i class="fas fa-check-circle"></i> ${material}</li>`
                                    ).join('')}
                                </ul>
                                
                                <div class="preparation-checklist">
                                    <h4>Before You Begin:</h4>
                                    <label class="checkbox-item">
                                        <input type="checkbox" id="prep-space"> 
                                        <span class="checkmark"></span>
                                        I have a quiet, comfortable space
                                    </label>
                                    <label class="checkbox-item">
                                        <input type="checkbox" id="prep-materials"> 
                                        <span class="checkmark"></span>
                                        I have all the materials I need
                                    </label>
                                    <label class="checkbox-item">
                                        <input type="checkbox" id="prep-mindset"> 
                                        <span class="checkmark"></span>
                                        I'm ready to focus and engage
                                    </label>
                                </div>
                            </div>
                            <button class="next-step-btn" onclick="interactiveAssignments.nextStep(2)" disabled>
                                <i class="fas fa-arrow-right"></i> Start Practice
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: Practice -->
                    <div class="step-content" id="step-2">
                        <div class="step-card">
                            <h3><i class="fas fa-play-circle"></i> Time to Practice</h3>
                            
                            <div class="timer-section">
                                <div class="timer-display-modern">
                                    <div class="time-circle">
                                        <span class="time-text">
                                            <span id="timer-minutes">00</span>:<span id="timer-seconds">00</span>
                                        </span>
                                        <div class="time-label">minutes</div>
                                    </div>
                                </div>
                                
                                <div class="timer-controls-modern">
                                    <button id="start-timer" class="timer-btn primary">
                                        <i class="fas fa-play"></i> Start
                                    </button>
                                    <button id="pause-timer" class="timer-btn secondary" disabled>
                                        <i class="fas fa-pause"></i> Pause
                                    </button>
                                    <button id="reset-timer" class="timer-btn outline">
                                        <i class="fas fa-redo"></i> Reset
                                    </button>
                                </div>
                            </div>

                            <div class="practice-notes">
                                <h4><i class="fas fa-pen"></i> Practice Notes</h4>
                                <p class="helper-text">Jot down your thoughts, feelings, or observations as you go...</p>
                                <textarea id="assignment-notes" placeholder="What am I noticing? How am I feeling? What thoughts are coming up?"></textarea>
                            </div>

                            <button class="next-step-btn" onclick="interactiveAssignments.nextStep(3)">
                                <i class="fas fa-arrow-right"></i> Move to Reflection
                            </button>
                        </div>
                    </div>

                    <!-- Step 3: Reflection -->
                    <div class="step-content" id="step-3">
                        <div class="step-card">
                            <h3><i class="fas fa-heart"></i> Time to Reflect</h3>
                            <p class="step-description">Take a moment to process your experience and capture your insights.</p>
                            
                            <div class="reflection-questions">
                                ${this.renderReflectionQuestions(assignment)}
                            </div>

                            <button class="next-step-btn" onclick="interactiveAssignments.nextStep(4)">
                                <i class="fas fa-arrow-right"></i> Finish Up
                            </button>
                        </div>
                    </div>

                    <!-- Step 4: Completion -->
                    <div class="step-content" id="step-4">
                        <div class="step-card">
                            <h3><i class="fas fa-trophy"></i> You're Almost Done!</h3>
                            <p class="step-description">Review your work and mark this assignment as complete.</p>
                            
                            <div class="completion-summary">
                                <div class="summary-item">
                                    <i class="fas fa-clock"></i>
                                    <span>Time Spent: <span id="final-time">--</span></span>
                                </div>
                                <div class="summary-item">
                                    <i class="fas fa-edit"></i>
                                    <span>Notes Written: <span id="notes-count">0</span> characters</span>
                                </div>
                                <div class="summary-item">
                                    <i class="fas fa-check-circle"></i>
                                    <span>Reflections: <span id="reflections-count">0</span>/4 completed</span>
                                </div>
                            </div>

                            <div class="completion-actions">
                                <button class="complete-btn" data-assignment-id="${assignment.id}">
                                    <i class="fas fa-check"></i> Complete Assignment
                                </button>
                                <button class="save-btn" data-assignment-id="${assignment.id}">
                                    <i class="fas fa-save"></i> Save for Later
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Replace main content with workspace
        this.container.innerHTML = workspaceHTML;
        this.setupModernWorkspaceEventListeners();
    }

    renderReflectionQuestions(assignment) {
        const questions = assignment.progress_questions || [
            'How are you feeling about this assignment?',
            'What challenges did you encounter?',
            'What insights did you gain?',
            'How can you apply this learning?'
        ];

        return questions.map((question, index) => `
            <div class="reflection-question">
                <div class="question-header">
                    <h5><i class="fas fa-question-circle"></i> ${question}</h5>
                </div>
                <textarea 
                    id="answer-${index}" 
                    placeholder="Take your time to reflect and share your thoughts..."
                    class="reflection-textarea"
                ></textarea>
            </div>
        `).join('');
    }

    renderProgressQuestions(assignment) {
        const questions = assignment.progress_questions || [
            'How are you feeling about this assignment?',
            'What challenges did you encounter?',
            'What insights did you gain?',
            'How can you apply this learning?'
        ];

        return questions.map((question, index) => `
            <div class="progress-question">
                <label>${question}</label>
                <textarea id="answer-${index}" placeholder="Your answer..."></textarea>
            </div>
        `).join('');
    }

    setupModernWorkspaceEventListeners() {
        // Setup preparation checklist
        this.setupPreparationChecklist();
        
        // Setup timer functionality
        this.setupTimerFunctionality();
        
        // Setup progress tracking
        this.setupProgressTracking();
        
        // Setup completion buttons
        this.setupCompletionButtons();
    }

    setupCompletionButtons() {
        // Complete Assignment button
        const completeBtn = document.querySelector('.complete-btn');
        if (completeBtn) {
            completeBtn.addEventListener('click', async () => {
                const assignmentId = completeBtn.getAttribute('data-assignment-id');
                console.log('Complete button clicked for assignment:', assignmentId);
                
                // Add visual feedback
                completeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Completing...';
                completeBtn.disabled = true;
                
                try {
                    await this.completeAssignment(assignmentId);
                } catch (error) {
                    console.error('Error completing assignment:', error);
                    completeBtn.innerHTML = '<i class="fas fa-check"></i> Complete Assignment';
                    completeBtn.disabled = false;
                }
            });
        } else {
            console.warn('Complete button not found');
        }
        
        // Save for Later button
        const saveBtn = document.querySelector('.save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                const assignmentId = saveBtn.getAttribute('data-assignment-id');
                console.log('Save button clicked for assignment:', assignmentId);
                
                // Add visual feedback
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                saveBtn.disabled = true;
                
                try {
                    await this.saveProgress(assignmentId);
                    saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved!';
                    setTimeout(() => {
                        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save for Later';
                        saveBtn.disabled = false;
                    }, 2000);
                } catch (error) {
                    console.error('Error saving progress:', error);
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Save for Later';
                    saveBtn.disabled = false;
                }
            });
        } else {
            console.warn('Save button not found');
        }
    }

    setupPreparationChecklist() {
        const checkboxes = document.querySelectorAll('.preparation-checklist input[type="checkbox"]');
        const nextBtn = document.querySelector('.next-step-btn[onclick*="nextStep(2)"]');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                if (nextBtn) {
                    nextBtn.disabled = !allChecked;
                    if (allChecked) {
                        nextBtn.classList.add('ready');
                    } else {
                        nextBtn.classList.remove('ready');
                    }
                }
            });
        });
    }

    nextStep(stepNumber) {
        // Hide all step contents
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Hide all step indicators
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show target step
        const targetStep = document.getElementById(`step-${stepNumber}`);
        const targetIndicator = document.querySelector(`[data-step="${stepNumber}"]`);
        
        if (targetStep) targetStep.classList.add('active');
        if (targetIndicator) targetIndicator.classList.add('active');
        
        // Mark previous steps as completed
        for (let i = 1; i < stepNumber; i++) {
            const prevStep = document.querySelector(`[data-step="${i}"]`);
            if (prevStep) prevStep.classList.add('completed');
        }
        
        // Update progress tracking if moving to final step
        if (stepNumber === 4) {
            this.updateCompletionSummary();
        }
    }

    updateCompletionSummary() {
        // Update time spent
        const timeDisplay = document.querySelector('#final-time');
        const minutes = document.querySelector('#timer-minutes').textContent;
        const seconds = document.querySelector('#timer-seconds').textContent;
        if (timeDisplay) {
            timeDisplay.textContent = `${minutes}:${seconds}`;
        }
        
        // Update notes count
        const notesTextarea = document.querySelector('#assignment-notes');
        const notesCount = document.querySelector('#notes-count');
        if (notesTextarea && notesCount) {
            notesCount.textContent = notesTextarea.value.length;
        }
        
        // Update reflections count
        const reflectionTextareas = document.querySelectorAll('.reflection-textarea');
        const reflectionsCount = document.querySelector('#reflections-count');
        if (reflectionsCount) {
            const completed = Array.from(reflectionTextareas).filter(textarea => textarea.value.trim().length > 0).length;
            reflectionsCount.textContent = completed;
        }
    }

    setupProgressTracking() {
        // Track notes changes
        document.addEventListener('input', (e) => {
            if (e.target.id === 'assignment-notes') {
                const notesCount = document.querySelector('#notes-count');
                if (notesCount) {
                    notesCount.textContent = e.target.value.length;
                }
            }
            
            if (e.target.classList.contains('reflection-textarea')) {
                const reflectionTextareas = document.querySelectorAll('.reflection-textarea');
                const reflectionsCount = document.querySelector('#reflections-count');
                if (reflectionsCount) {
                    const completed = Array.from(reflectionTextareas).filter(textarea => textarea.value.trim().length > 0).length;
                    reflectionsCount.textContent = completed;
                }
            }
        });
    }

    setupTimerFunctionality() {
        // Timer functionality
        let timerInterval;
        let timeElapsed = 0;
        let isRunning = false;

        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const resetBtn = document.getElementById('reset-timer');

        if (startBtn) {
            startBtn.addEventListener('click', () => {
                if (!isRunning) {
                    isRunning = true;
                    startBtn.disabled = true;
                    pauseBtn.disabled = false;
                    
                    timerInterval = setInterval(() => {
                        timeElapsed++;
                        this.updateTimerDisplay(timeElapsed);
                    }, 1000);
                }
            });
        }

        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (isRunning) {
                    isRunning = false;
                    startBtn.disabled = false;
                    pauseBtn.disabled = true;
                    clearInterval(timerInterval);
                }
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                timeElapsed = 0;
                isRunning = false;
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                clearInterval(timerInterval);
                this.updateTimerDisplay(0);
            });
        }
    }

    updateTimerDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        document.getElementById('timer-minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('timer-seconds').textContent = remainingSeconds.toString().padStart(2, '0');
    }

    async completeAssignment(assignmentId) {
        const assignment = this.assignments.find(a => a.id === assignmentId);
        if (!assignment) return;

        // Get notes and progress
        const notes = document.getElementById('assignment-notes')?.value || '';
        const answers = [];
        for (let i = 0; i < 4; i++) {
            const answer = document.getElementById(`answer-${i}`)?.value || '';
            answers.push(answer);
        }

        // Update assignment
        assignment.status = 'completed';
        assignment.completed_at = new Date();
        assignment.notes = notes;
        assignment.progress_answers = answers;
        assignment.progress = 100;

        // Save to backend
        await this.updateAssignment(assignment);

        // Show completion message
        this.showCompletionMessage(assignment);

        // Return to assignments view
        setTimeout(() => {
            this.render();
        }, 3000);
    }

    showCompletionMessage(assignment) {
        this.container.innerHTML = `
            <div class="completion-message">
                <div class="completion-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <h3>Assignment Completed!</h3>
                <p>Great job completing "${assignment.title}"!</p>
                <div class="completion-stats">
                    <div class="stat">
                        <span class="stat-number">+50</span>
                        <span class="stat-label">XP Earned</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">1</span>
                        <span class="stat-label">Achievement Unlocked</span>
                    </div>
                </div>
                <button class="btn btn-primary back-to-assignments-btn">
                    <i class="fas fa-arrow-left"></i> Back to Assignments
                </button>
            </div>
        `;
        
        // Add event listener for back button
        const backBtn = this.container.querySelector('.back-to-assignments-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.render();
            });
        }
    }

    async saveProgress(assignmentId) {
        const assignment = this.assignments.find(a => a.id === assignmentId);
        if (!assignment) return;

        const notes = document.getElementById('assignment-notes')?.value || '';
        assignment.notes = notes;
        assignment.progress = Math.min(assignment.progress + 25, 100);

        await this.updateAssignment(assignment);

        this.showMessage('Progress saved successfully!', 'success');
    }

    async updateAssignment(assignment) {
        try {
            console.log('Updating assignment:', assignment);
            
            // Try to update via API
            const response = await apiCall(`/therapy/assignments/${assignment.id}`, {
                method: 'PUT',
                body: JSON.stringify(assignment)
            });
            
            console.log('Assignment update response:', response);
            
            // Also update localStorage if this was the current assignment
            const currentAssignment = localStorage.getItem('currentAssignment');
            if (currentAssignment) {
                const parsed = JSON.parse(currentAssignment);
                if (parsed.id === assignment.id) {
                    localStorage.setItem('currentAssignment', JSON.stringify(assignment));
                    console.log('Updated assignment in localStorage');
                }
            }
            
        } catch (error) {
            console.error('Error updating assignment via API:', error);
            
            // Fallback: update localStorage only
            const currentAssignment = localStorage.getItem('currentAssignment');
            if (currentAssignment) {
                const parsed = JSON.parse(currentAssignment);
                if (parsed.id === assignment.id) {
                    localStorage.setItem('currentAssignment', JSON.stringify(assignment));
                    console.log('Updated assignment in localStorage as fallback');
                }
            }
        }
    }

    getActiveCount() {
        return this.assignments.filter(a => a.status === 'active').length;
    }

    getCompletedCount() {
        return this.assignments.filter(a => a.status === 'completed').length;
    }

    calculateCompletionRate() {
        if (this.assignments.length === 0) return 0;
        const completed = this.getCompletedCount();
        return Math.round((completed / this.assignments.length) * 100);
    }

    formatDate(dateString) {
        if (!dateString) return 'No deadline';
        const date = new Date(dateString);
        return date.toLocaleDateString();
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

    startTherapySession() {
        // Navigate to therapy session
        window.location.hash = '#therapy';
    }
}

// Initialize the interactive assignments
const interactiveAssignments = new InteractiveAssignments(); 