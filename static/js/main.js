// static/js/main.js

// Auto-hide alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});

// Cart quantity update
function updateQuantity(productId, action) {
    fetch(`/cart/${action}/${productId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Price range filter
function updatePrice() {
    const range = document.getElementById('priceRange');
    const value = document.getElementById('priceValue');
    if (range && value) {
        value.textContent = range.value + ' €';
    }
}

// Confirm delete
function confirmDelete() {
    return confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.');
}

// Search with debounce
let searchTimeout;

function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            const form = searchInput.closest('form');
            if (form) {
                form.submit();
            }
        }
    }, 500);
}

// Scroll to top button
window.addEventListener('scroll', function() {
    const button = document.getElementById('scrollToTop');
    if (button) {
        if (window.pageYOffset > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    }
});

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}