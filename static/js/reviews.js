class ReviewManager {
    constructor(productId) {
        this.productId = productId;
        this.currentPage = 1;
        this.hasMore = true;
        this.container = document.getElementById('reviews-container');
        this.statsContainer = document.getElementById('reviews-stats');
        this.loadMoreBtn = document.getElementById('load-more-container');
        
        this.init();
    }
    
    init() {
        this.loadReviews();
        
        document.getElementById('load-more-reviews')?.addEventListener('click', () => {
            this.loadReviews();
        });
        
        document.addEventListener('click', (e) => {
            if (e.target.closest('.vote-btn')) {
                this.handleVote(e);
            }
        });
    }
    
    async loadReviews() {
        try {
            const response = await fetch(`/reviews/product/${this.productId}/?page=${this.currentPage}`);
            const data = await response.json();
            
            if (this.currentPage === 1) {
                this.container.innerHTML = data.html;
                this.updateStats(data.stats);
            } else {
                this.container.insertAdjacentHTML('beforeend', data.html);
            }
            
            this.hasMore = data.has_next;
            this.currentPage++;
            
            this.loadMoreBtn.style.display = this.hasMore ? 'block' : 'none';
        } catch (error) {
            console.error('Error loading reviews:', error);
            this.container.innerHTML = `
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Ошибка при загрузке отзывов
                </div>
            `;
        }
    }
    
    async handleVote(event) {
        event.preventDefault();
        
        const btn = event.target.closest('.vote-btn');
        const reviewId = btn.dataset.reviewId;
        const voteType = btn.dataset.voteType;
        
        try {
            const formData = new FormData();
            formData.append('vote', voteType);
            
            const response = await fetch(`/reviews/vote/${reviewId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                const reviewElement = document.getElementById(`review-${reviewId}`);
                const likesSpan = reviewElement.querySelector('.likes-count');
                const dislikesSpan = reviewElement.querySelector('.dislikes-count');
                
                if (likesSpan) likesSpan.textContent = data.likes;
                if (dislikesSpan) dislikesSpan.textContent = data.dislikes;
                
                const likeBtn = reviewElement.querySelector('.vote-btn[data-vote-type="like"]');
                const dislikeBtn = reviewElement.querySelector('.vote-btn[data-vote-type="dislike"]');
                
                if (likeBtn) likeBtn.classList.toggle('active', data.user_vote === 'like');
                if (dislikeBtn) dislikeBtn.classList.toggle('active', data.user_vote === 'dislike');
            }
        } catch (error) {
            console.error('Error voting:', error);
        }
    }
    
    updateStats(stats) {
        document.getElementById('reviews-count').textContent = stats.total_reviews;
        
        this.statsContainer.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-4">
                    <div class="d-flex align-items-center">
                        <div class="display-4 fw-bold me-3">${stats.avg_rating}</div>
                        <div>
                            <div class="text-warning fs-4">
                                ${'★'.repeat(Math.round(stats.avg_rating))}${'☆'.repeat(5 - Math.round(stats.avg_rating))}
                            </div>
                            <small class="text-muted">${stats.total_reviews} отзывов</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    ${stats.distribution.map(r => `
                        <div class="d-flex align-items-center mb-2">
                            <span class="me-2" style="min-width: 30px;">${r.stars}★</span>
                            <div class="progress flex-grow-1" style="height: 8px;">
                                <div class="progress-bar bg-warning" style="width: ${r.percent}%"></div>
                            </div>
                            <span class="ms-2 small">${r.count}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('reviews-container');
    if (container) {
        new ReviewManager(container.dataset.productId);
    }
});