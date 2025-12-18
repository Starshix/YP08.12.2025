// Мобильное меню
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileCatalogBtn = document.querySelector('.mobile-catalog-btn');
    const mobileCatalogContent = document.querySelector('.mobile-catalog-content');
    
    // Открыть мобильное меню
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    // Закрыть мобильное меню
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Закрыть при клике вне меню
    document.addEventListener('click', (e) => {
        if (!mobileMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Открыть/закрыть каталог в мобильном меню
    if (mobileCatalogBtn) {
        mobileCatalogBtn.addEventListener('click', () => {
            mobileCatalogContent.style.display = 
                mobileCatalogContent.style.display === 'block' ? 'none' : 'block';
        });
    }
    
    // Плавный скролл для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Закрыть мобильное меню если открыто
                mobileMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
});