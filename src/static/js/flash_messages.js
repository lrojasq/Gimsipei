// Flash Messages Auto-Dismiss
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach((message, index) => {
        // Auto-dismiss after 5 seconds (staggered by 100ms per message)
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => {
                message.remove();
            }, 300); // Match CSS animation duration
        }, 5000 + (index * 100));
    });
});

