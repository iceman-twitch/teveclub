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
        // Feed the pet multiple times until full (like original Python bot)
        let feedCount = 0;
        const maxAttempts = 10;
        
        while (feedCount < maxAttempts) {
            // Check if feeding is still needed
            const checkResult = await this.proxyRequest(
                `${this.teveclubBase}/myteve.pet`,
                'GET'
            );
            
            if (!checkResult.success) {
                return { success: false, message: '❌ Failed to check feeding status' };
            }
            
            // If no "Mehet!" button, pet is full
            if (!checkResult.html.includes('Mehet!')) {
                if (feedCount === 0) {
                    return { success: true, message: '✅ Pet is already full! No feeding needed.' };
                } else {
                    return { success: true, message: `✅ Pet fed ${feedCount} time(s) and is now full!` };
                }
            }
            
            // Feed the pet
            const feedResult = await this.proxyRequest(
                `${this.teveclubBase}/myteve.pet`,
                'POST',
                { 
                    kaja: '1',
                    pia: '1',
                    etet: 'Mehet!'
                }
            );
            
            if (!feedResult.success) {
                return { success: false, message: `❌ Feeding failed after ${feedCount} attempts` };
            }
            
            feedCount++;
            
            // Check if pet is satisfied
            if (feedResult.html && (feedResult.html.includes('elég jóllakott') || feedResult.html.includes('tele a hasa'))) {
                return { success: true, message: `✅ Pet fed ${feedCount} time(s) and is satisfied!` };
            }
            
            // Small delay between feeds
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        return { success: true, message: `✅ Fed ${feedCount} times (max attempts reached)` };
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
        // Play guess game - matches original bot
        const guessResult = await this.proxyRequest(
            `${this.teveclubBase}/egyszam.pet`,
            'POST',
            { 
                honnan: '403',
                tipp: 'Ez a tippem!'
            }
        );
        
        if (guessResult.success) {
            return { success: true, message: '✅ Guess game completed!' };
        } else {
            return { success: false, message: '❌ Guess game failed' };
        }
    }

    async setFood(foodId) {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/setfood.pet`,
            'POST',
            { kaja: foodId.toString() }
        );
        
        if (result.success && result.html) {
            return { success: true, message: '✅ Food selection updated!' };
        } else {
            return { success: false, message: '❌ Food selection failed' };
        }
    }

    async setDrink(drinkId) {
        const result = await this.proxyRequest(
            `${this.teveclubBase}/setdrink.pet`,
            'POST',
            { kaja: drinkId.toString() }
        );
        
        if (result.success && result.html) {
            return { success: true, message: '✅ Drink selection updated!' };
        } else {
            return { success: false, message: '❌ Drink selection failed' };
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

    async getCurrentFoodDrink() {
        try {
            const response = await fetch('/api/get-current-food-drink/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                credentials: 'same-origin'
            });
            
            const result = await response.json();
            console.log('getCurrentFoodDrink result:', result);
            
            if (result.success) {
                return result;
            } else {
                console.log('Failed to get current food/drink:', result.message);
                return { success: false };
            }
        } catch (error) {
            console.error('Error fetching current food/drink:', error);
            return { success: false };
        }
    }

    async getCurrentTrick() {
        try {
            const response = await fetch('/api/get-current-trick/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                credentials: 'same-origin'
            });
            
            const result = await response.json();
            console.log('getCurrentTrick result:', result);
            
            if (result.success) {
                return result;
            } else {
                console.log('Failed to get current trick:', result.message);
                return { success: false };
            }
        } catch (error) {
            console.error('Error fetching current trick:', error);
            return { success: false };
        }
    }

    getFoodItems() {
        return [
            { id: 0, name: 'széna', icon: '0.gif', cost: 0 },
            { id: 1, name: 'hamburger', icon: '1.gif', cost: 0 },
            { id: 9, name: 'csoki', icon: '9.gif', cost: 0 },
            { id: 10, name: 'gomba', icon: '10.gif', cost: 0 },
            { id: 12, name: 'szaloncukor', icon: '12.gif', cost: 0 }
        ];
    }

    getDrinkItems() {
        return [
            { id: 0, name: 'víz', icon: '0.gif', cost: 0 },
            { id: 1, name: 'kóla', icon: '1.gif', cost: 0 },
            { id: 8, name: 'pezsgő', icon: '8.gif', cost: 0 },
            { id: 9, name: 'banánturmix', icon: '9.gif', cost: 0 },
            { id: 21, name: 'Cherry Coke', icon: '21.gif', cost: 0 }
        ];
    }
}

// UI Controller
class TeveclubUI {
    constructor() {
        this.api = new TeveclubAPI();
        this.initElements();
        this.loadSavedCredentials();
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
        this.rememberUsername = document.getElementById('remember-username');
        this.rememberPassword = document.getElementById('remember-password');
        this.loginStatus = document.getElementById('login-status');

        // Action buttons
        this.feedBtn = document.getElementById('feed-btn');
        this.learnBtn = document.getElementById('learn-btn');
        this.guessBtn = document.getElementById('guess-btn');
        this.logoutBtn = document.getElementById('logout-btn');

        // Food/Drink dropdowns
        this.foodDropdown = document.getElementById('food-dropdown');
        this.drinkDropdown = document.getElementById('drink-dropdown');
        this.foodToggleBtn = document.getElementById('food-toggle-btn');
        this.drinkToggleBtn = document.getElementById('drink-toggle-btn');
        this.foodList = document.getElementById('food-list');
        this.drinkList = document.getElementById('drink-list');
        this.foodIcon = document.getElementById('food-icon');
        this.drinkIcon = document.getElementById('drink-icon');

        // Trick text
        this.trickText = document.getElementById('trick-text');

        // Set default icons
        if (this.foodIcon) {
            this.foodIcon.innerHTML = '<img src="/static/images/food/0.gif" style="width: 30px; height: 30px; object-fit: contain;" alt="food">';
        }
        if (this.drinkIcon) {
            this.drinkIcon.innerHTML = '<img src="/static/images/drink/0.gif" style="width: 30px; height: 30px; object-fit: contain;" alt="drink">';
        }

        // Status
        this.mainStatus = document.getElementById('main-status');
        this.welcomeText = document.getElementById('welcome-text');
    }

    loadSavedCredentials() {
        // Load saved username
        const savedUsername = localStorage.getItem('teveclub_username');
        const rememberUsernameChecked = localStorage.getItem('teveclub_remember_username') === 'true';
        
        if (savedUsername && rememberUsernameChecked) {
            this.usernameInput.value = savedUsername;
            this.rememberUsername.checked = true;
        }

        // Load saved password
        const savedPassword = localStorage.getItem('teveclub_password');
        const rememberPasswordChecked = localStorage.getItem('teveclub_remember_password') === 'true';
        
        if (savedPassword && rememberPasswordChecked) {
            this.passwordInput.value = savedPassword;
            this.rememberPassword.checked = true;
        }
    }

    saveCredentials(username, password) {
        // Save username if checkbox is checked
        if (this.rememberUsername.checked) {
            localStorage.setItem('teveclub_username', username);
            localStorage.setItem('teveclub_remember_username', 'true');
        } else {
            localStorage.removeItem('teveclub_username');
            localStorage.setItem('teveclub_remember_username', 'false');
        }

        // Save password if checkbox is checked
        if (this.rememberPassword.checked) {
            localStorage.setItem('teveclub_password', password);
            localStorage.setItem('teveclub_remember_password', 'true');
        } else {
            localStorage.removeItem('teveclub_password');
            localStorage.setItem('teveclub_remember_password', 'false');
        }
    }

    bindEvents() {
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Auto Mode button
        const autoModeBtn = document.getElementById('auto-mode-btn');
        if (autoModeBtn) {
            autoModeBtn.addEventListener('click', (e) => this.handleAutoMode(e));
        }
        
        this.feedBtn.addEventListener('click', () => {
            console.log('Feed button clicked!');
            this.handleFeed();
        });
        this.learnBtn.addEventListener('click', () => this.handleLearn());
        this.guessBtn.addEventListener('click', () => this.handleGuess());
        this.logoutBtn.addEventListener('click', () => this.handleLogout());

        // Food/Drink toggle - only if elements exist
        if (this.foodToggleBtn && this.drinkToggleBtn) {
            this.foodToggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Food toggle clicked');
                this.toggleDropdown('food');
            });
            this.drinkToggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drink toggle clicked');
                this.toggleDropdown('drink');
            });

            // Close dropdowns when clicking outside
            document.addEventListener('click', (e) => {
                if (!this.foodDropdown.contains(e.target) && !this.drinkDropdown.contains(e.target)) {
                    this.foodList.style.display = 'none';
                    this.drinkList.style.display = 'none';
                    this.foodDropdown.classList.remove('open');
                    this.drinkDropdown.classList.remove('open');
                }
            });

            // Initialize food/drink lists
            this.initializeFoodList();
            this.initializeDrinkList();
        }
    }

    toggleDropdown(type) {
        console.log('Toggle dropdown:', type);
        if (type === 'food') {
            const isOpen = this.foodList.style.display === 'block';
            console.log('Food dropdown isOpen:', isOpen);
            this.foodList.style.display = isOpen ? 'none' : 'block';
            this.drinkList.style.display = 'none';
            
            this.foodDropdown.classList.toggle('open', !isOpen);
            this.drinkDropdown.classList.remove('open');
        } else {
            const isOpen = this.drinkList.style.display === 'block';
            console.log('Drink dropdown isOpen:', isOpen);
            this.drinkList.style.display = isOpen ? 'none' : 'block';
            this.foodList.style.display = 'none';
            
            this.drinkDropdown.classList.toggle('open', !isOpen);
            this.foodDropdown.classList.remove('open');
        }
    }

    initializeFoodList() {
        const foods = this.api.getFoodItems();
        console.log('Initializing food list with', foods.length, 'items');
        this.foodList.innerHTML = foods.map(food => `
            <div class="food-item" data-id="${food.id}">
                <img src="/static/images/food/${food.icon}" 
                     alt="${food.name}" 
                     class="dropdown-item-icon"
                     onerror="this.style.display='none';">
                <span class="dropdown-item-name">${food.name}</span>
                ${food.cost > 0 ? `<span class="cost">(${food.cost} dt)</span>` : '<span class="free">Ingyenes!</span>'}
            </div>
        `).join('');

        this.foodList.querySelectorAll('.food-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const foodId = e.currentTarget.getAttribute('data-id');
                this.handleSetFood(parseInt(foodId));
            });
        });
        console.log('Food list initialized');
    }

    initializeDrinkList() {
        const drinks = this.api.getDrinkItems();
        this.drinkList.innerHTML = drinks.map(drink => `
            <div class="drink-item" data-id="${drink.id}">
                <img src="/static/images/drink/${drink.icon}" 
                     alt="${drink.name}"
                     class="dropdown-item-icon"
                     onerror="this.style.display='none';">
                <span class="dropdown-item-name">${drink.name}</span>
                ${drink.cost > 0 ? `<span class="cost">(${drink.cost} dt)</span>` : '<span class="free">Ingyenes!</span>'}
            </div>
        `).join('');

        this.drinkList.querySelectorAll('.drink-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const drinkId = e.currentTarget.getAttribute('data-id');
                this.handleSetDrink(parseInt(drinkId));
            });
        });
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

    async handleAutoMode(e) {
        e.preventDefault();
        
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value.trim();

        if (!username || !password) {
            this.showStatus(this.loginStatus, '⚠️ Please fill in all fields', 'error');
            return;
        }

        const autoModeBtn = document.getElementById('auto-mode-btn');
        this.setButtonLoading(autoModeBtn, true);
        this.showStatus(this.loginStatus, '⚡ Auto Mode: Logging in...', 'info');

        // Step 1: Login
        const loginResult = await this.api.login(username, password);
        
        if (!loginResult.success) {
            this.setButtonLoading(autoModeBtn, false);
            this.showStatus(this.loginStatus, `❌ Login failed: ${loginResult.message}`, 'error');
            return;
        }

        // Save credentials if remember me is checked
        this.saveCredentials(username, password);
        
        this.showStatus(this.loginStatus, '⚡ Auto Mode: Feeding...', 'info');

        // Step 2: Feed
        const feedResult = await this.api.feed();
        if (!feedResult.success) {
            this.showStatus(this.loginStatus, `⚠️ Feed warning: ${feedResult.message}`, 'warning');
        }

        this.showStatus(this.loginStatus, '⚡ Auto Mode: Learning...', 'info');

        // Step 3: Learn
        const learnResult = await this.api.learn();
        if (!learnResult.success) {
            this.showStatus(this.loginStatus, `⚠️ Learn warning: ${learnResult.message}`, 'warning');
        }

        this.showStatus(this.loginStatus, '⚡ Auto Mode: Guessing...', 'info');

        // Step 4: Guess
        const guessResult = await this.api.guess();
        if (!guessResult.success) {
            this.showStatus(this.loginStatus, `⚠️ Guess warning: ${guessResult.message}`, 'warning');
        }

        this.showStatus(this.loginStatus, '⚡ Auto Mode: Logging out...', 'info');

        // Step 5: Logout
        const logoutResult = await this.api.logout();

        this.setButtonLoading(autoModeBtn, false);

        if (logoutResult.success) {
            this.showStatus(this.loginStatus, '✅ Auto Mode completed successfully! All tasks done.', 'success');
        } else {
            this.showStatus(this.loginStatus, '⚠️ Auto Mode completed but logout failed', 'warning');
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
            // Save credentials if remember me is checked
            this.saveCredentials(username, password);
            
            this.showStatus(this.loginStatus, '✅ Login successful!', 'success');
            this.welcomeText.textContent = `Welcome, ${username}! 🐪`;
            
            // Fetch current food/drink and trick
            this.updateCurrentFoodDrink();
            this.updateCurrentTrick();
            
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
        console.log('handleFeed called');
        this.setButtonLoading(this.feedBtn, true);
        this.updateMainStatus('🍖 Starting feed process...', true);

        const result = await this.api.feed();
        console.log('Feed result:', result);

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

    async handleSetFood(foodId) {
        this.foodList.style.display = 'none';
        this.foodDropdown.classList.remove('open');
        this.updateMainStatus(`🍕 Setting food...`, true);

        const result = await this.api.setFood(foodId);

        if (result.success) {
            const food = this.api.getFoodItems().find(f => f.id === foodId);
            const foodName = food?.name || 'food';
            const foodIcon = food?.icon || '0.gif';
            
            // Update button icon immediately
            const foodIconElement = document.getElementById('food-icon');
            if (foodIconElement) {
                foodIconElement.innerHTML = `<img src="/static/images/food/${foodIcon}" style="width: 30px; height: 30px; object-fit: contain;" alt="${foodName}">`;
            }
            
            this.updateMainStatus(`✅ Food set to: ${foodName}`, true);
        } else {
            this.updateMainStatus(`❌ Food selection failed: ${result.message}`, true);
        }
    }

    async handleSetDrink(drinkId) {
        this.drinkList.style.display = 'none';
        this.drinkDropdown.classList.remove('open');
        this.updateMainStatus(`🥤 Setting drink...`, true);

        const result = await this.api.setDrink(drinkId);

        if (result.success) {
            const drink = this.api.getDrinkItems().find(d => d.id === drinkId);
            const drinkName = drink?.name || 'drink';
            const drinkIcon = drink?.icon || '0.gif';
            
            // Update button icon immediately
            const drinkIconElement = document.getElementById('drink-icon');
            if (drinkIconElement) {
                drinkIconElement.innerHTML = `<img src="/static/images/drink/${drinkIcon}" style="width: 30px; height: 30px; object-fit: contain;" alt="${drinkName}">`;
            }
            
            this.updateMainStatus(`✅ Drink set to: ${drinkName}`, true);
        } else {
            this.updateMainStatus(`❌ Drink selection failed: ${result.message}`, true);
        }
    }

    async updateCurrentFoodDrink() {
        console.log('Fetching current food/drink...');
        const result = await this.api.getCurrentFoodDrink();
        console.log('getCurrentFoodDrink result:', result);
        
        if (result.success && result.data) {
            const { foodIcon, drinkIcon } = result.data;
            
            // Update food button icon
            if (foodIcon) {
                const foodIconElement = document.getElementById('food-icon');
                console.log('Updating food icon to:', foodIcon);
                if (foodIconElement) {
                    const imgUrl = `/static/images/food/${foodIcon}`;
                    foodIconElement.innerHTML = `<img src="${imgUrl}" style="width: 30px; height: 30px; vertical-align: middle; object-fit: contain;" alt="current food">`;
                }
            }
            
            // Update drink button icon
            if (drinkIcon) {
                const drinkIconElement = document.getElementById('drink-icon');
                console.log('Updating drink icon to:', drinkIcon);
                if (drinkIconElement) {
                    const imgUrl = `/static/images/drink/${drinkIcon}`;
                    drinkIconElement.innerHTML = `<img src="${imgUrl}" style="width: 30px; height: 30px; vertical-align: middle; object-fit: contain;" alt="current drink">`;
                }
            }
        } else {
            console.log('Failed to get current food/drink');
        }
    }

    async updateCurrentTrick() {
        console.log('Fetching current trick...');
        const result = await this.api.getCurrentTrick();
        console.log('getCurrentTrick result:', result);
        
        if (result.success && result.trick) {
            if (this.trickText) {
                this.trickText.textContent = result.trick;
                this.trickText.style.display = 'block';
            }
        } else {
            console.log('Failed to get current trick');
            if (this.trickText) {
                this.trickText.style.display = 'none';
            }
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
