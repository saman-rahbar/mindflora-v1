// Achievement Gallery Component
class AchievementGallery {
    constructor() {
        this.container = null;
        this.achievements = [];
        this.categories = {
            'therapy': { icon: 'fas fa-comments', color: '#007AFF' },
            'journaling': { icon: 'fas fa-book-open', color: '#FF6B6B' },
            'streak': { icon: 'fas fa-fire', color: '#FFD93D' },
            'milestone': { icon: 'fas fa-trophy', color: '#6C5CE7' },
            'wellness': { icon: 'fas fa-heart', color: '#00B894' },
            'community': { icon: 'fas fa-users', color: '#FD79A8' }
        };
    }

    async init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Achievement gallery container not found');
            return;
        }

        await this.loadAchievements();
        this.render();
        this.setupEventListeners();
    }

    async loadAchievements() {
        try {
            const response = await apiCall('gamification/achievements');
            this.achievements = response.data || [];
        } catch (error) {
            console.error('Error loading achievements:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="achievement-gallery">
                <div class="gallery-header">
                    <h2><i class="fas fa-trophy"></i> Achievement Gallery</h2>
                    <div class="gallery-stats">
                        <div class="stat-item">
                            <span class="stat-number">${this.getUnlockedCount()}</span>
                            <span class="stat-label">Unlocked</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.achievements.length}</span>
                            <span class="stat-label">Total</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.calculateCompletionRate()}%</span>
                            <span class="stat-label">Completion</span>
                        </div>
                    </div>
                </div>

                <!-- Achievement Categories -->
                <div class="achievement-categories">
                    <button class="category-btn active" data-category="all">
                        <i class="fas fa-th"></i> All
                    </button>
                    ${Object.entries(this.categories).map(([category, info]) => `
                        <button class="category-btn" data-category="${category}">
                            <i class="${info.icon}"></i> ${category.charAt(0).toUpperCase() + category.slice(1)}
                        </button>
                    `).join('')}
                </div>

                <!-- Achievement Grid -->
                <div class="achievement-grid">
                    ${this.renderAchievements()}
                </div>

                <!-- Achievement Details Modal -->
                <div id="achievement-modal" class="modal">
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

                <!-- Progress Summary -->
                <div class="achievement-progress">
                    <h3><i class="fas fa-chart-pie"></i> Progress Summary</h3>
                    <div class="progress-cards">
                        ${this.renderProgressCards()}
                    </div>
                </div>
            </div>
        `;
    }

    renderAchievements() {
        return this.achievements.map(achievement => `
            <div class="achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}" 
                 data-category="${achievement.category || 'general'}"
                 onclick="achievementGallery.showAchievementDetails('${achievement.id}')">
                <div class="achievement-icon">
                    <i class="${achievement.icon || 'fas fa-star'}"></i>
                    ${achievement.unlocked ? '<div class="unlock-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="achievement-info">
                    <h4>${achievement.name}</h4>
                    <p>${achievement.description}</p>
                    <div class="achievement-meta">
                        <span class="achievement-category">${achievement.category || 'General'}</span>
                        <span class="achievement-xp">+${achievement.xp_earned || 0} XP</span>
                    </div>
                    ${achievement.unlocked ? 
                        `<div class="unlock-date">Unlocked ${this.formatDate(achievement.unlocked_at)}</div>` :
                        `<div class="progress-bar">
                            <div class="progress-fill" style="width: ${achievement.progress || 0}%"></div>
                        </div>`
                    }
                </div>
            </div>
        `).join('');
    }

    renderProgressCards() {
        const categoryProgress = {};
        
        this.achievements.forEach(achievement => {
            const category = achievement.category || 'general';
            if (!categoryProgress[category]) {
                categoryProgress[category] = { total: 0, unlocked: 0 };
            }
            categoryProgress[category].total++;
            if (achievement.unlocked) {
                categoryProgress[category].unlocked++;
            }
        });

        return Object.entries(categoryProgress).map(([category, progress]) => {
            const percentage = Math.round((progress.unlocked / progress.total) * 100);
            const categoryInfo = this.categories[category] || { icon: 'fas fa-star', color: '#6C757D' };
            
            return `
                <div class="progress-card">
                    <div class="progress-icon" style="color: ${categoryInfo.color}">
                        <i class="${categoryInfo.icon}"></i>
                    </div>
                    <div class="progress-info">
                        <h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>
                        <div class="progress-stats">
                            <span>${progress.unlocked}/${progress.total}</span>
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

        // Modal close button
        const modalClose = document.querySelector('.modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                this.hideAchievementDetails();
            });
        }

        // Close modal when clicking outside
        const modal = document.getElementById('achievement-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideAchievementDetails();
                }
            });
        }
    }

    filterByCategory(category) {
        const achievementCards = document.querySelectorAll('.achievement-card');
        
        achievementCards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    showAchievementDetails(achievementId) {
        const achievement = this.achievements.find(a => a.id === achievementId);
        if (!achievement) return;

        const modal = document.getElementById('achievement-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');

        modalTitle.textContent = achievement.name;
        modalContent.innerHTML = `
            <div class="achievement-detail">
                <div class="detail-header">
                    <div class="detail-icon">
                        <i class="${achievement.icon || 'fas fa-star'}"></i>
                    </div>
                    <div class="detail-info">
                        <h4>${achievement.name}</h4>
                        <p>${achievement.description}</p>
                    </div>
                </div>
                
                <div class="detail-stats">
                    <div class="stat-item">
                        <span class="stat-label">Category</span>
                        <span class="stat-value">${achievement.category || 'General'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">XP Earned</span>
                        <span class="stat-value">+${achievement.xp_earned || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Status</span>
                        <span class="stat-value ${achievement.unlocked ? 'unlocked' : 'locked'}">
                            ${achievement.unlocked ? 'Unlocked' : 'Locked'}
                        </span>
                    </div>
                    ${achievement.unlocked ? `
                        <div class="stat-item">
                            <span class="stat-label">Unlocked</span>
                            <span class="stat-value">${this.formatDate(achievement.unlocked_at)}</span>
                        </div>
                    ` : ''}
                </div>

                ${achievement.criteria ? `
                    <div class="detail-criteria">
                        <h5>Requirements</h5>
                        <ul>
                            ${achievement.criteria.map(criterion => `
                                <li class="${criterion.completed ? 'completed' : ''}">
                                    <i class="fas fa-${criterion.completed ? 'check' : 'circle'}"></i>
                                    ${criterion.description}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${achievement.rewards ? `
                    <div class="detail-rewards">
                        <h5>Rewards</h5>
                        <div class="rewards-list">
                            ${achievement.rewards.map(reward => `
                                <div class="reward-item">
                                    <i class="${reward.icon || 'fas fa-gift'}"></i>
                                    <span>${reward.description}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        modal.style.display = 'block';
    }

    hideAchievementDetails() {
        const modal = document.getElementById('achievement-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    getUnlockedCount() {
        return this.achievements.filter(a => a.unlocked).length;
    }

    calculateCompletionRate() {
        if (this.achievements.length === 0) return 0;
        return Math.round((this.getUnlockedCount() / this.achievements.length) * 100);
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
}

// Initialize the achievement gallery
const achievementGallery = new AchievementGallery(); 