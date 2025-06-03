document.addEventListener('DOMContentLoaded', function() {
    // Make cards clickable
    function makeCardsClickable() {
        // Product cards
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            const link = card.querySelector('.btn-learn-more');
            if (link && !card.querySelector('.card-link')) {
                const cardLink = document.createElement('a');
                cardLink.href = link.href;
                cardLink.className = 'card-link';
                cardLink.setAttribute('aria-label', 'View ' + (card.querySelector('h3')?.textContent || 'product'));
                card.appendChild(cardLink);
            }
        });

        // Feature cards with links
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            const link = card.querySelector('a');
            if (link && !card.querySelector('.card-link')) {
                card.classList.add('clickable');
                const cardLink = document.createElement('a');
                cardLink.href = link.href;
                cardLink.className = 'card-link';
                cardLink.setAttribute('aria-label', 'View ' + (card.querySelector('h3')?.textContent || 'feature'));
                card.appendChild(cardLink);
            }
        });

        // Post cards
        const postCards = document.querySelectorAll('.post-card');
        postCards.forEach(card => {
            const link = card.querySelector('.btn-read-more, .post-content h2 a');
            if (link && !card.querySelector('.card-link')) {
                const cardLink = document.createElement('a');
                cardLink.href = link.href;
                cardLink.className = 'card-link';
                cardLink.setAttribute('aria-label', 'Read ' + (card.querySelector('h2')?.textContent || 'post'));
                card.appendChild(cardLink);
            }
        });

        // About cards with links
        const aboutCards = document.querySelectorAll('.about-card');
        aboutCards.forEach(card => {
            const link = card.querySelector('a');
            if (link && !card.querySelector('.card-link')) {
                card.classList.add('clickable');
                const cardLink = document.createElement('a');
                cardLink.href = link.href;
                cardLink.className = 'card-link';
                cardLink.setAttribute('aria-label', 'View ' + (card.querySelector('h3')?.textContent || 'information'));
                card.appendChild(cardLink);
            }
        });
    }

    // Initialize card functionality
    makeCardsClickable();

    // Header scroll behavior for mobile
    let lastScrollTop = 0;
    const header = document.querySelector('header');
    
    function handleScroll() {
        if (window.innerWidth <= 768) { // Only on mobile
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down & past 100px
                header.classList.add('hide-on-scroll');
            } else {
                // Scrolling up
                header.classList.remove('hide-on-scroll');
            }
            
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        } else {
            // Remove class on desktop
            header.classList.remove('hide-on-scroll');
        }
    }
    
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleScroll);

    // Mobile navigation menu toggle
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);
    const mobileClose = document.querySelector('.mobile-close');

    if (hamburger && mobileMenu) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        });

        function closeMenu() {
            mobileMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        mobileClose.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && !hamburger.contains(e.target)) {
                closeMenu();
            }
        });
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }

    // Dropdown functionality for mobile
    const mobileLinks = document.querySelectorAll('.mobile-nav-links .dropdown > a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdownContent = this.nextElementSibling;
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            } else {
                dropdownContent.style.display = 'block';
            }
        });
    });
});