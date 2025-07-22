document.addEventListener('DOMContentLoaded', function() {
    // Make cards clickable
    function makeCardsClickable() {
        // Product cards
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            const link = card.querySelector('.btn-learn-more');
            if (link && !card.hasAttribute('data-clickable')) {
                card.setAttribute('data-clickable', 'true');
                
                // Create invisible overlay for card clicking
                const cardOverlay = document.createElement('div');
                cardOverlay.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 5;
                    cursor: pointer;
                `;
                
                cardOverlay.addEventListener('click', (e) => {
                    // Don't interfere with direct link clicks
                    if (e.target !== cardOverlay) return;
                    link.click();
                });
                
                card.appendChild(cardOverlay);
            }
        });

        // Feature cards with links
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            const link = card.querySelector('a');
            if (link && !card.hasAttribute('data-clickable')) {
                card.classList.add('clickable');
                card.setAttribute('data-clickable', 'true');
                
                card.addEventListener('click', (e) => {
                    // Don't interfere with direct link clicks
                    if (e.target.tagName === 'A') return;
                    link.click();
                });
            }
        });

        // Post cards
        const postCards = document.querySelectorAll('.post-card');
        postCards.forEach(card => {
            const link = card.querySelector('.btn-read-more, h3 a');
            if (link && !card.hasAttribute('data-clickable')) {
                card.setAttribute('data-clickable', 'true');
                
                card.addEventListener('click', (e) => {
                    // Don't interfere with direct link clicks
                    if (e.target.tagName === 'A') return;
                    link.click();
                });
            }
        });

        // About cards with links
        const aboutCards = document.querySelectorAll('.about-card');
        aboutCards.forEach(card => {
            const link = card.querySelector('a');
            if (link && !card.hasAttribute('data-clickable')) {
                card.classList.add('clickable');
                card.setAttribute('data-clickable', 'true');
                
                card.addEventListener('click', (e) => {
                    // Don't interfere with direct link clicks
                    if (e.target.tagName === 'A') return;
                    link.click();
                });
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

    // --- FIT-TO-CONTENT MENU DETECTION ---
    const headerBottom = document.querySelector('.header-bottom');
    const navDesktop = document.querySelector('.nav-desktop');
    const hamburger = document.querySelector('.hamburger');

    function updateMenuVisibility() {
        if (!headerBottom || !navDesktop || !hamburger) return;
        // Reset to measure
        navDesktop.style.display = '';
        hamburger.style.display = 'none';
        // Give browser a tick to layout
        setTimeout(() => {
            const navRect = navDesktop.getBoundingClientRect();
            const headerRect = headerBottom.getBoundingClientRect();
            if (navRect.right > headerRect.right - 10 || navRect.left < headerRect.left + 10) {
                // Menu overflows: show hamburger, hide nav
                navDesktop.style.display = 'none';
                hamburger.style.display = 'flex';
            } else {
                // Menu fits: show nav, hide hamburger
                navDesktop.style.display = '';
                hamburger.style.display = 'none';
            }
        }, 10);
    }
    window.addEventListener('resize', updateMenuVisibility);
    window.addEventListener('DOMContentLoaded', updateMenuVisibility);
    updateMenuVisibility();

    // --- END FIT-TO-CONTENT ---

    // Mobile navigation menu toggle
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.querySelector('.overlay') || document.createElement('div');
    if (!document.querySelector('.overlay')) {
        overlay.className = 'overlay';
        document.body.appendChild(overlay);
    }
    const mobileClose = document.querySelector('.mobile-close');

    function openMenu() {
        mobileMenu.classList.add('active');
        hamburger.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        mobileMenu.classList.remove('active');
        hamburger.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (hamburger && mobileMenu) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            if (mobileMenu.classList.contains('active')) {
                closeMenu();
            } else {
                openMenu();
            }
        });
    }
    if (mobileClose) {
        mobileClose.addEventListener('click', function(e) {
            e.stopPropagation();
            closeMenu();
        });
    }
    overlay.addEventListener('click', closeMenu);

    // Close menu when clicking outside (only if menu is open)
    document.addEventListener('click', function(e) {
        if (mobileMenu.classList.contains('active')) {
            if (!mobileMenu.contains(e.target) && !hamburger.contains(e.target)) {
                closeMenu();
            }
        }
    });

    // Close menu when clicking on mobile nav links
    const mobileLinks = document.querySelectorAll('.mobile-nav-links a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMenu();
            // Let default navigation happen (do not preventDefault)
        });
    });

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
    const mobileLinksDropdown = document.querySelectorAll('.mobile-nav-links .dropdown > a');
    mobileLinksDropdown.forEach(link => {
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