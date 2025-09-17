// Función para mostrar/ocultar contraseñas
function setupPasswordToggle(passwordId, toggleId) {
    const toggleButton = document.querySelector(toggleId);
    const passwordInput = document.querySelector(passwordId);

    if (toggleButton && passwordInput) {
        toggleButton.addEventListener('click', function (e) {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
}

// Función para validación de formularios
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Función para cerrar alertas automáticamente
function setupAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
}

// Inicializar todas las funciones cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    setupFormValidation();
    setupAutoCloseAlerts();

    // Setup password toggles if they exist
    setupPasswordToggle('#password', '#togglePassword');
    setupPasswordToggle('#confirm_password', '#toggleConfirmPassword');
});


// Función para manejar el dropdown
document.querySelectorAll(".grado").forEach((grado) => {
    grado.addEventListener("click", () => {
        const materias = grado.nextElementSibling;
        const icono = grado.querySelector("i");

        materias.classList.toggle("active");
        icono.classList.toggle("rotate");
    });
});

if (document.getElementById('hamburger')) {
    document.getElementById('hamburger').addEventListener('click', function () {
        document.getElementById('mobileNav').classList.toggle('active');

        // Animación para el menú hamburguesa (opcional)
        this.classList.toggle('open');
    });
}


let menu = document.querySelectorAll('.mobile-nav li a')
if (menu) {
    menu.forEach(item => {
        item.addEventListener('click', () => {
            document.getElementById('mobileNav').classList.remove('active');
            document.getElementById('hamburger').classList.remove('open');
        });
    });
}


