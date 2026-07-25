// static/js/notifications.js
class NotificationSystem {
    constructor() {
        this.container = null;
        this.createContainer();
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            width: 100%;
        `;
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', duration = 5000) {
        const colors = {
            success: '#27AE60',
            error: '#E74C3C',
            warning: '#F39C12',
            info: '#3498DB'
        };
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="
                background: ${colors[type] || colors.info};
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                animation: slideInRight 0.5s ease;
                font-size: 14px;
            ">
                <span style="margin-right: 12px; font-size: 20px;">${icons[type] || 'ℹ️'}</span>
                <span style="flex: 1;">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    opacity: 0.7;
                    padding: 0 5px;
                ">✕</button>
            </div>
            <style>
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            </style>
        `;
        this.container.appendChild(notification.firstElementChild);
        setTimeout(() => {
            const el = this.container.lastElementChild;
            if (el) {
                el.querySelector('div').style.animation = 'slideOutRight 0.5s ease';
                setTimeout(() => el.remove(), 500);
            }
        }, duration);
    }
}

const notifications = new NotificationSystem();
window.notifications = notifications;
window.showNotification = function(message, type, duration) {
    notifications.show(message, type, duration);
};