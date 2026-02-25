document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Navbar
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = mobileMenu.querySelectorAll('a');

    const toggleMenu = () => {
        hamburger.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    };

    hamburger.addEventListener('click', toggleMenu);

    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (mobileMenu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // 3. Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const revealPoint = 100;

        revealElements.forEach(el => {
            const revealTop = el.getBoundingClientRect().top;
            if (revealTop < windowHeight - revealPoint) {
                el.classList.add('active');
            }
        });
    };

    // Initial check and scroll listener
    revealOnScroll();
    window.addEventListener('scroll', revealOnScroll);

    // 4. Abstract Heatmap Animation (Visual Touch)
    const heatmapGrid = document.querySelector('.grid-cells');
    if (heatmapGrid) {
        for (let i = 0; i < 48; i++) {
            const cell = document.createElement('div');
            // Randomly assign basic opacity to simulate data
            const randomVal = Math.random();
            let bgClass = '#222';
            
            if (randomVal > 0.8) {
                bgClass = 'var(--accent)';
                cell.style.boxShadow = '0 0 10px var(--accent-glow)';
            } else if (randomVal > 0.5) {
                bgClass = 'var(--accent-dark)';
            } else if (randomVal > 0.3) {
                bgClass = '#333';
            }
            
            cell.style.backgroundColor = bgClass;
            cell.style.borderRadius = '2px';
            cell.style.transition = 'background-color 2s ease';
            
            // Randomly animate cells
            setInterval(() => {
                if(Math.random() > 0.9) {
                    const temp = cell.style.backgroundColor;
                    cell.style.backgroundColor = 'var(--accent)';
                    setTimeout(() => cell.style.backgroundColor = temp, 1500);
                }
            }, 3000 + Math.random() * 5000);
            
            heatmapGrid.appendChild(cell);
        }
    }
});
