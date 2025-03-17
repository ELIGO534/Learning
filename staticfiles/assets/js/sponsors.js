// Function to animate numbers from 0 to target value
function animateCounter(id, target) {
    let count = 0;
    const speed = Math.ceil(target / 100); // Speed factor
    const updateCounter = () => {
        count += speed;
        if (count > target) count = target;
        document.getElementById(id).innerText = count;
        if (count < target) {
            requestAnimationFrame(updateCounter);
        }
    };
    updateCounter();
}

// Run when page loads
window.onload = () => {
    animateCounter("companies-count", 15);
    animateCounter("courses-count", 60);
    animateCounter("students-count", 1000);
};
document.addEventListener("DOMContentLoaded", function () {
    let track = document.querySelector(".partner-track");
    let slides = document.querySelectorAll(".partner-slide");
    let index = 0;
    let totalSlides = slides.length;

    function showSlide() {
        let offset = -index * 100 + "%";
        track.style.transform = "translateX(" + offset + ")";
        index = (index + 1) % totalSlides;
    }

    // Auto-slide every 2 seconds
    setInterval(showSlide, 2000);
});
