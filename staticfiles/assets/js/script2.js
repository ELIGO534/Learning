document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            // Remove active class from all cards
            cards.forEach(c => c.classList.remove('active'));
            // Add active class to the hovered card
            this.classList.add('active');
        });
    });
});