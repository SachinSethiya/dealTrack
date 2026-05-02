// CSRF Token Helper Functions
document.addEventListener('DOMContentLoaded', function() {
    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to setup AJAX CSRF token
    function setupCSRF() {
        const csrftoken = getCookie('csrftoken');
        
        // Set up AJAX requests with CSRF token
        if (typeof window.$ !== 'undefined') {
            // jQuery support
            window.$.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }
        
        // Native fetch support
        if (typeof window.fetch !== 'undefined') {
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                if (options.method && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(options.method.toUpperCase())) {
                    options.headers = {
                        ...options.headers,
                        'X-CSRFToken': csrftoken
                    };
                }
                return originalFetch(url, options);
            };
        }
        
        // Debug: Log CSRF token status
        console.log('CSRF Token Status:', {
            hasToken: !!csrftoken,
            tokenLength: csrftoken ? csrftoken.length : 0,
            cookieExists: document.cookie.includes('csrftoken')
        });
    }

    // Setup CSRF protection
    setupCSRF();

    // Add form submission debugging
    const forms = document.querySelectorAll('form[method="post"]');
    forms.forEach(function(form, index) {
        form.addEventListener('submit', function(e) {
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]');
            console.log(`Form ${index + 1} submission:`, {
                hasCsrfToken: !!csrfToken,
                csrfTokenValue: csrfToken ? csrfToken.value.substring(0, 10) + '...' : 'none',
                action: form.action,
                method: form.method
            });
        });
    });

    // Auto-refresh CSRF token if it's missing
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.warn('CSRF token is missing. This might cause form submission failures.');
        
        // Try to get a new CSRF token
        fetch('/get-csrf-token/', {
            method: 'GET',
            credentials: 'same-origin'
        }).then(response => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Failed to get CSRF token');
        }).then(html => {
            // Extract CSRF token from response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const token = doc.querySelector('input[name="csrfmiddlewaretoken"]');
            if (token) {
                console.log('New CSRF token obtained');
            }
        }).catch(error => {
            console.error('Could not refresh CSRF token:', error);
        });
    }
});
