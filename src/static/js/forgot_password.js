// Forgot Password JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('forgotPasswordForm');
    const submitBtn = document.getElementById('submitBtn');
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('new_password');
    const toggleIcon = document.getElementById('toggleIcon');

    // Toggle password visibility
    togglePassword.addEventListener('click', function() {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
    });

    // Form validation and submission
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            // Show loading state
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Actualizando...';
        }
        form.classList.add('was-validated');
    });

    // Real-time validation
    const inputs = form.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Check for success message and add delay before redirect
    const successAlert = document.querySelector('.alert-success');
    if (successAlert) {
        // Disable form to prevent multiple submissions
        const form = document.getElementById('forgotPasswordForm');
        const inputs = form.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = true;
        });
        
        // Show countdown in the alert
        let countdown = 3;
        const originalMessage = successAlert.textContent.trim();
        
        const updateCountdown = () => {
            successAlert.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                ${originalMessage}
                <br><small class="mt-2 d-block">
                    <i class="fas fa-clock me-1"></i>
                    Redirigiendo en ${countdown} segundos...
                </small>
            `;
            countdown--;
        };
        
        // Update countdown every second
        const countdownInterval = setInterval(() => {
            updateCountdown();
            if (countdown < 0) {
                clearInterval(countdownInterval);
                // Add a smooth fade out effect
                successAlert.style.transition = 'opacity 0.5s ease-out';
                successAlert.style.opacity = '0';
                
                // Redirect after fade out
                setTimeout(() => {
                    window.location.href = successAlert.getAttribute('data-redirect') || '/auth/login';
                }, 500);
            }
        }, 1000);
        
        // Initial countdown update
        updateCountdown();
    }
});