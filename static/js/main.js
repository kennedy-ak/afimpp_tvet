// ========================================
// Main JavaScript File for AfIMMP TVTC
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // Navbar Scroll Effect
    // ========================================
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
    });
    
    // ========================================
    // Scroll to Top Button
    // ========================================
    const scrollToTopBtn = createScrollToTopButton();
    
    function createScrollToTopButton() {
        const btn = document.createElement('div');
        btn.className = 'scroll-to-top';
        btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        document.body.appendChild(btn);
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                btn.classList.add('show');
            } else {
                btn.classList.remove('show');
            }
        });
        
        btn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        return btn;
    }
    
    // ========================================
    // Auto-dismiss Alerts
    // ========================================
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Auto dismiss after 5 seconds
    });
    
    // ========================================
    // Form Validation Enhancement
    // ========================================
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // ========================================
    // Password Strength Indicator
    // ========================================
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(function(field) {
        if (field.name === 'password1' || field.name === 'password') {
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength mt-2';
            strengthIndicator.innerHTML = '<small class="text-muted">Password strength: <span class="strength-text">-</span></small>';
            field.parentElement.appendChild(strengthIndicator);
            
            field.addEventListener('input', function() {
                const strength = calculatePasswordStrength(field.value);
                updatePasswordStrength(strengthIndicator, strength);
            });
        }
    });
    
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        if (strength <= 2) return 'weak';
        if (strength <= 4) return 'medium';
        return 'strong';
    }
    
    function updatePasswordStrength(indicator, strength) {
        const strengthText = indicator.querySelector('.strength-text');
        
        if (strength === 'weak') {
            strengthText.textContent = 'Weak';
            strengthText.className = 'strength-text text-danger';
        } else if (strength === 'medium') {
            strengthText.textContent = 'Medium';
            strengthText.className = 'strength-text text-warning';
        } else {
            strengthText.textContent = 'Strong';
            strengthText.className = 'strength-text text-success';
        }
    }
    
    // ========================================
    // Confirm Password Match
    // ========================================
    const password1 = document.querySelector('input[name="password1"]');
    const password2 = document.querySelector('input[name="password2"]');
    
    if (password1 && password2) {
        password2.addEventListener('input', function() {
            if (password2.value !== password1.value) {
                password2.setCustomValidity('Passwords do not match');
            } else {
                password2.setCustomValidity('');
            }
        });
    }
    
    // ========================================
    // Payment Method Toggle
    // ========================================
    const paymentMethodSelect = document.getElementById('id_payment_method');
    
    if (paymentMethodSelect) {
        paymentMethodSelect.addEventListener('change', function() {
            togglePaymentFields(this.value);
        });
        
        // Trigger on page load
        togglePaymentFields(paymentMethodSelect.value);
    }
    
    function togglePaymentFields(method) {
        const mobileMoneyFields = document.getElementById('mobileMoneyFields');
        const cardFields = document.getElementById('cardFields');
        const bankTransferFields = document.getElementById('bankTransferFields');
        
        if (mobileMoneyFields) mobileMoneyFields.style.display = 'none';
        if (cardFields) cardFields.style.display = 'none';
        if (bankTransferFields) bankTransferFields.style.display = 'none';
        
        if (method === 'mobile_money' && mobileMoneyFields) {
            mobileMoneyFields.style.display = 'block';
        } else if (method === 'card' && cardFields) {
            cardFields.style.display = 'block';
        } else if (method === 'bank_transfer' && bankTransferFields) {
            bankTransferFields.style.display = 'block';
        }
    }
    
    // ========================================
    // Card Number Formatting
    // ========================================
    const cardNumberInput = document.getElementById('card_number');
    
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });
    }
    
    // ========================================
    // Card Expiry Formatting
    // ========================================
    const cardExpiryInput = document.getElementById('card_expiry');
    
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
    
    // ========================================
    // Phone Number Formatting
    // ========================================
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"], input[name="mobile_number"]');
    
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value;
        });
    });
    
    // ========================================
    // Image Preview
    // ========================================
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    let preview = input.parentElement.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-2';
                        input.parentElement.appendChild(preview);
                    }
                    preview.innerHTML = `<img src="${event.target.result}" class="img-thumbnail" style="max-width: 200px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // ========================================
    // Search Form Enhancement
    // ========================================
    const searchForms = document.querySelectorAll('form[role="search"], .search-form');
    
    searchForms.forEach(function(form) {
        const searchInput = form.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                // You can add live search functionality here
                console.log('Search query:', searchInput.value);
            }, 500));
        }
    });
    
    // ========================================
    // Debounce Function
    // ========================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // ========================================
    // Tooltip Initialization
    // ========================================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ========================================
    // Popover Initialization
    // ========================================
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // ========================================
    // Lazy Loading Images
    // ========================================
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(function(img) {
        imageObserver.observe(img);
    });
    
    // ========================================
    // Smooth Scroll for Anchor Links
    // ========================================
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ========================================
    // Loading Spinner on Form Submit
    // ========================================
    const allForms = document.querySelectorAll('form');
    
    allForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable button after 10 seconds as a fallback
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 10000);
            }
        });
    });
    
    // ========================================
    // Confirmation Dialogs
    // ========================================
    const confirmLinks = document.querySelectorAll('[data-confirm]');
    
    confirmLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const message = link.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // ========================================
    // Character Counter for Textareas
    // ========================================
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted small text-end mt-1';
        counter.textContent = `0 / ${maxLength}`;
        textarea.parentElement.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength} / ${maxLength}`;
            
            if (currentLength >= maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    });
    
    // ========================================
    // Print Functionality
    // ========================================
    const printButtons = document.querySelectorAll('[data-print]');
    
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });
    
    // ========================================
    // Copy to Clipboard
    // ========================================
    const copyButtons = document.querySelectorAll('[data-copy]');
    
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = button.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Show success message
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                setTimeout(function() {
                    button.innerHTML = originalText;
                }, 2000);
            });
        });
    });
    
    // ========================================
    // Console Welcome Message
    // ========================================
    console.log('%cWelcome to AfIMMP TVTC!', 'color: #0d6efd; font-size: 20px; font-weight: bold;');
    console.log('%cBuilt with Django & Bootstrap', 'color: #6c757d; font-size: 14px;');
    
});

// ========================================
// Service Worker Registration (Optional)
// ========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/static/sw.js');
    });
}