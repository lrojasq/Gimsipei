// Login Page JavaScript - Password Toggle Functionality

document.addEventListener('DOMContentLoaded', function() {
    openPassword();
});

function openPassword() {
    let iconPassword = document.querySelector('.fa-lock');
    let inputPassword = document.getElementById('password');
    let isTypePassword = true;
    
    if (!iconPassword || !inputPassword) return false;
    
    iconPassword.addEventListener('click', () => {
        if (isTypePassword) {
            inputPassword.setAttribute('type', 'text');
            iconPassword.classList.remove('fa-lock');
            iconPassword.classList.add('fa-lock-open');
            isTypePassword = false;
        } else {
            inputPassword.setAttribute('type', 'password');
            iconPassword.classList.remove('fa-lock-open');
            iconPassword.classList.add('fa-lock');
            isTypePassword = true;
        }
    });
}

