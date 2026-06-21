document.addEventListener('DOMContentLoaded', () => {
    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile Hamburger Menu
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    // Native Scroll Reveal Micro-Animations (Intersection Observer)
    const revealOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, revealOptions);

    const revealElements = document.querySelectorAll('.gsap-reveal'); // reusing the class name for simplicity
    revealElements.forEach(el => {
        // Prepare the element for CSS transition
        el.classList.add('reveal-prep');
        revealObserver.observe(el);
    });
});

// Simple Toast Notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // basic inline styles for the toast
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: type === 'success' ? '#4a9d6e' : '#d94f4f',
        color: '#fff',
        padding: '12px 24px',
        borderRadius: '8px',
        zIndex: 9999,
        opacity: 0,
        transition: 'opacity 0.3s'
    });

    document.body.appendChild(toast);
    
    // animate in
    requestAnimationFrame(() => {
        toast.style.opacity = 1;
    });

    // remove after 3s
    setTimeout(() => {
        toast.style.opacity = 0;
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
