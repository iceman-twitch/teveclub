// Teveclub Bot - Frontend API Client

class TeveclubAPI {
    constructor() {
        this.baseURL = window.location.origin;
        this.csrfToken = this.getCSRFToken();
    }

    getCSRFToken() {
        // Try to get from cookie first
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        
        // If no cookie, try to get from input field
        if (!cookieValue) {
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                cookieValue = csrfInput.value;
            }
        }
        
        return cookieValue;
    }

    async request(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };

        // Only add CSRF token if we have one
        if (this.csrfToken) {
            options.headers['X-CSRFToken'] = this.csrfToken;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const text = await response.text();
            
            // Try to parse as JSON
            try {
                const result = JSON.parse(text);
                return result;
            } catch (parseError) {
                // If not JSON, return the text (likely an error page)
                console.error('Response is not JSON:', text);
                return {
                    success: false,
                    message: `Server error: Response is not JSON. Check Django console for errors.`
                };
            }
        } catch (error) {
            return {
                success: false,
                message: `Network error: ${error.message}`
            };
        }
    }

    async login(username, password) {
        return await this.request('/api/login/', 'POST', { username, password });
    }

    async feed() {
        return await this.request('/api/feed/', 'POST');
    }

    async learn() {
        return await this.request('/api/learn/', 'POST');
    }

    async guess() {
        return await this.request('/api/guess/', 'POST');
    }

    async logout() {
        return await this.request('/api/logout/', 'POST');
    }
}

// UI Controller
class TeveclubUI {
    constructor() {
        this.api = new TeveclubAPI();
        this.initElements();
        this.bindEvents();
    }

    initElements() {
        // Panels
        this.loginPanel = document.getElementById('login-panel');
        this.mainPanel = document.getElementById('main-panel');

        // Login form
        this.loginForm = document.getElementById('login-form');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.loginStatus = document.getElementById('login-status');

        // Action buttons
        this.feedBtn = document.getElementById('feed-btn');
        this.learnBtn = document.getElementById('learn-btn');
        this.guessBtn = document.getElementById('guess-btn');
        this.logoutBtn = document.getElementById('logout-btn');

        // Status
        this.mainStatus = document.getElementById('main-status');
        this.welcomeText = document.getElementById('welcome-text');
    }

    bindEvents() {
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.feedBtn.addEventListener('click', () => this.handleFeed());
        this.learnBtn.addEventListener('click', () => this.handleLearn());
        this.guessBtn.addEventListener('click', () => this.handleGuess());
        this.logoutBtn.addEventListener('click', () => this.handleLogout());
    }

    showStatus(element, message, type = 'info') {
        element.textContent = message;
        element.className = `status-message ${type}`;
        element.style.display = 'block';
    }

    hideStatus(element) {
        element.style.display = 'none';
    }

    updateMainStatus(message, append = false) {
        if (append) {
            const timestamp = new Date().toLocaleTimeString();
            this.mainStatus.textContent += `\n[${timestamp}] ${message}`;
        } else {
            this.mainStatus.textContent = message;
        }
        this.mainStatus.scrollTop = this.mainStatus.scrollHeight;
    }

    setButtonLoading(button, loading) {
        const spinner = button.querySelector('.spinner');
        const text = button.querySelector('.btn-text') || button.querySelector('.btn-label');
        
        if (loading) {
            button.disabled = true;
            if (spinner) spinner.style.display = 'inline-block';
            if (text) text.style.opacity = '0.5';
        } else {
            button.disabled = false;
            if (spinner) spinner.style.display = 'none';
            if (text) text.style.opacity = '1';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value.trim();

        if (!username || !password) {
            this.showStatus(this.loginStatus, '⚠️ Please fill in all fields', 'error');
            return;
        }

        const submitBtn = this.loginForm.querySelector('.btn-primary');
        this.setButtonLoading(submitBtn, true);
        this.showStatus(this.loginStatus, '🔄 Logging in...', 'info');

        const result = await this.api.login(username, password);

        this.setButtonLoading(submitBtn, false);

        if (result.success) {
            this.showStatus(this.loginStatus, '✅ Login successful!', 'success');
            this.welcomeText.textContent = `Welcome, ${username}! 🐪`;
            
            setTimeout(() => {
                this.loginPanel.style.display = 'none';
                this.mainPanel.style.display = 'block';
                this.updateMainStatus('✅ Logged in successfully. Ready to control your Teve!');
            }, 500);
        } else {
            this.showStatus(this.loginStatus, `❌ ${result.message}`, 'error');
        }
    }

    async handleFeed() {
        this.setButtonLoading(this.feedBtn, true);
        this.updateMainStatus('🍖 Starting feed process...', true);

        const result = await this.api.feed();

        this.setButtonLoading(this.feedBtn, false);

        if (result.success) {
            this.updateMainStatus(`✅ Feeding complete!\n${result.message}`, true);
        } else {
            this.updateMainStatus(`❌ Feed failed: ${result.message}`, true);
        }
    }

    async handleLearn() {
        this.setButtonLoading(this.learnBtn, true);
        this.updateMainStatus('📚 Starting learning session...', true);

        const result = await this.api.learn();

        this.setButtonLoading(this.learnBtn, false);

        if (result.success) {
            this.updateMainStatus(`✅ Learning complete!\n${result.message}`, true);
        } else {
            this.updateMainStatus(`❌ Learning failed: ${result.message}`, true);
        }
    }

    async handleGuess() {
        this.setButtonLoading(this.guessBtn, true);
        this.updateMainStatus('🎲 Starting guess game...', true);

        const result = await this.api.guess();

        this.setButtonLoading(this.guessBtn, false);

        if (result.success) {
            this.updateMainStatus(`✅ Guess game complete!\n${result.message}`, true);
        } else {
            this.updateMainStatus(`❌ Guess game failed: ${result.message}`, true);
        }
    }

    async handleLogout() {
        this.setButtonLoading(this.logoutBtn, true);
        this.updateMainStatus('🚪 Logging out...', true);

        const result = await this.api.logout();

        this.setButtonLoading(this.logoutBtn, false);

        if (result.success) {
            this.updateMainStatus('✅ Logged out successfully', true);
            
            setTimeout(() => {
                this.mainPanel.style.display = 'none';
                this.loginPanel.style.display = 'block';
                this.loginForm.reset();
                this.hideStatus(this.loginStatus);
                this.mainStatus.textContent = 'Ready';
            }, 500);
        } else {
            this.updateMainStatus(`❌ Logout failed: ${result.message}`, true);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TeveclubUI();
});
