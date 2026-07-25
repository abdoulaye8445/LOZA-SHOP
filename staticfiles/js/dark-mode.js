// static/js/dark-mode.js
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'dark-mode-toggle';
    toggleBtn.innerHTML = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
    document.body.appendChild(toggleBtn);
    
    toggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'true');
            this.innerHTML = '☀️';
        } else {
            localStorage.setItem('darkMode', 'false');
            this.innerHTML = '🌙';
        }
    });
});