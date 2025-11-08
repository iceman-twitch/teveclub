// Teveclub Bot - Frontend API Client
// Uses Django proxy to communicate with teveclub.hu

class TeveclubAPI {
    constructor() {
        this.proxyURL = '/api/proxy/';
        this.teveclubBase = 'https://teveclub.hu';
        this.csrfToken = this.getCSRFToken();
    }

    getCSRFToken() {
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
        return cookieValue;
    }

    async proxyRequest(url, method = 'GET', data = null) {
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                url: url,
                method: method,
                data: data
            })
        };

        try {
            const response = await fetch(this.proxyURL, options);
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Proxy request error:', error);
            return {
                success: false,
                message: `Network error: ${error.message}`
            };
        }
    }

    async login(username, password) {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/`,
            'POST',
            {
                tevenev: username,
                pass: password,
                x: '38',
                y: '42',
                login: 'Gyere!'
            }
        );
        
        console.log('Login result:', result);
        console.log('Response contains success marker:', result.html && result.html.includes('Teve Legyen Veled'));
        
        if (result.success && result.html && result.html.includes('Teve Legyen Veled')) {
            return { success: true, message: 'Login successful' };
        } else if (result.html && result.html.includes('Sikertelen')) {
            return { success: false, message: 'Invalid username or password' };
        } else if (!result.success) {
            return { success: false, message: result.message || 'Login failed' };
        } else {
            return { success: false, message: 'Invalid credentials or unexpected response' };
        }
    }

    async feed() {
        // Check if feeding is available
        const checkResult = await this.proxyRequest(`${this.teveclubBase}/myteve.pet`, 'GET');
        
        if (!checkResult.success) {
            return { success: false, message: 'Failed to check feeding status' };
        }
        
        if (!checkResult.html.includes('Mehet!')) {
            return { success: true, message: '✅ Pet is already well-fed! No feeding needed.' };
        }
        
        // Perform feeding
        const feedResult = await this.proxyRequest(
            `${this.teveclubBase}/myteve.pet`,
            'POST',
            { eat: '1' }
        );
        
        if (feedResult.success) {
            return { success: true, message: '✅ Pet fed successfully!' };
        } else {
            return { success: false, message: '❌ Feeding failed' };
        }
    }

    async learn() {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/tanit.pet`,
            'GET'
        );
        
        if (result.success && result.html) {
            if (result.html.includes('sikeresen megtanult')) {
                return { success: true, message: '✅ Learning successful!' };
            } else {
                return { success: false, message: 'No more tricks to learn' };
            }
        } else {
            return { success: false, message: '❌ Learning failed' };
        }
    }

    async guess() {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/egyszam.pet`,
            'GET'
        );
        
        if (result.success) {
            return { success: true, message: '✅ Guess game completed!' };
        } else {
            return { success: false, message: '❌ Guess game failed' };
        }
    }

    async logout() {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/`,
            'POST',
            { logout: '1' }
        );
        
        return { success: true, message: 'Logged out successfully' };
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
