// static/js/main.js

/* ============ DOCUMENT READY ============ */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    autoDismissAlerts();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add active class to nav items
    setActiveNavItem();
    
    // Product image hover zoom
    initializeProductZoom();
    
    // Cart quantity animations
    initializeCartAnimations();
    
    // Scroll to top button
    initializeScrollToTop();
    
    // Price range filter
    initializePriceRange();
});

/* ============ AUTO DISMISS ALERTS ============ */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            } else {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 500);
            }
        }, 5000);
    });
}

/* ============ TOOLTIPS ============ */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* ============ ACTIVE NAV ITEM ============ */
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.includes(href)) {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

/* ============ PRODUCT ZOOM ============ */
function initializeProductZoom() {
    const productImages = document.querySelectorAll('.product-zoom');
    
    productImages.forEach(function(img) {
        img.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width * 100;
            const y = (e.clientY - rect.top) / rect.height * 100;
            this.style.transformOrigin = `${x}% ${y}%`;
            this.style.transform = 'scale(1.5)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

/* ============ CART ANIMATIONS ============ */
function initializeCartAnimations() {
    const cartButtons = document.querySelectorAll('.cart-btn');
    
    cartButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            this.classList.add('animate__animated', 'animate__bounceIn');
            setTimeout(function() {
                btn.classList.remove('animate__animated', 'animate__bounceIn');
            }, 1000);
        });
    });
}

/* ============ SCROLL TO TOP ============ */
function initializeScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scrollToTop';
    scrollBtn.className = 'btn btn-primary rounded-circle position-fixed';
    scrollBtn.style.cssText = `
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        display: none;
        z-index: 999;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    `;
    scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'flex';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/* ============ PRICE RANGE ============ */
function initializePriceRange() {
    const rangeInput = document.getElementById('priceRange');
    const priceDisplay = document.getElementById('priceValue');
    
    if (rangeInput && priceDisplay) {
        rangeInput.addEventListener('input', function() {
            priceDisplay.textContent = this.value + ' €';
        });
    }
}

/* ============ CONFIRM DELETE ============ */
function confirmDelete(message) {
    const defaultMessage = 'Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.';
    return confirm(message || defaultMessage);
}

// Attacher la fonction à l'objet window pour l'utiliser dans les templates
window.confirmDelete = confirmDelete;

/* ============ SEARCH WITH DEBOUNCE ============ */
function debounceSearch(callback, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => callback.apply(this, args), delay);
    };
}

/* ============ FORM VALIDATION ============ */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/* ============ CART QUANTITY UPDATE ============ */
function updateCartQuantity(productId, action) {
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
        } else {
            alert(data.message || 'Une erreur est survenue.');
        }
    })
    .catch(error => console.error('Error:', error));
}

/* ============ ADD TO CART AJAX ============ */
function addToCartAjax(productId) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Chargement...';
    }
    
    fetch(`/cart/add/${productId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour le badge du panier
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = data.total_items;
                badge.classList.remove('d-none');
            }
            
            // Afficher une notification
            showToast('Produit ajouté au panier !', 'success');
            
            // Animation du bouton
            if (button) {
                button.classList.add('btn-success');
                button.innerHTML = '<i class="bi bi-check-circle"></i> Ajouté !';
                setTimeout(() => {
                    button.classList.remove('btn-success');
                    button.innerHTML = '<i class="bi bi-cart-plus"></i> Ajouter au panier';
                    button.disabled = false;
                }, 2000);
            }
        } else {
            showToast(data.message || 'Une erreur est survenue.', 'danger');
            if (button) {
                button.disabled = false;
                button.innerHTML = '<i class="bi bi-cart-plus"></i> Ajouter au panier';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Une erreur est survenue.', 'danger');
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-cart-plus"></i> Ajouter au panier';
        }
    });
}

/* ============ TOAST NOTIFICATIONS ============ */
function showToast(message, type) {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.role = 'alert';
    toast.ariaLive = 'assertive';
    toast.ariaAtomic = 'true';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'x-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.querySelector('.toast-container').appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

/* ============ IMAGE PREVIEW ============ */
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

/* ============ PASSWORD STRENGTH ============ */
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    return strength;
}

/* ============ PRODUCT FILTER ============ */
function applyFilters() {
    const form = document.getElementById('filterForm');
    if (form) {
        form.submit();
    }
}

/* ============ SORT PRODUCTS ============ */
function sortProducts(value) {
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('sort', value);
    window.location.href = currentUrl.toString();
}

/* ============ PRINT RECEIPT ============ */
function printReceipt() {
    window.print();
}

/* ============ DOWNLOAD RECEIPT ============ */
function downloadReceipt(orderId) {
    window.location.href = `/orders/download-receipt/${orderId}/`;
}

/* ============ EXPOSE FUNCTIONS TO GLOBAL SCOPE ============ */
window.updateCartQuantity = updateCartQuantity;
window.addToCartAjax = addToCartAjax;
window.showToast = showToast;
window.previewImage = previewImage;
window.applyFilters = applyFilters;
window.sortProducts = sortProducts;
window.printReceipt = printReceipt;
window.downloadReceipt = downloadReceipt;
window.validateForm = validateForm;
window.confirmDelete = confirmDelete;