document.getElementById('sponsorshipForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Collect form data
    const formData = {
        email: document.getElementById('email').value,
        firstName: document.getElementById('first-name').value,
        lastName: document.getElementById('last-name').value,
        company: document.getElementById('company').value,
        country: document.getElementById('country').value
    };

    // Send data to backend (You can replace with your Django backend)
    fetch('/submit-sponsorship', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => alert('Thank you for your submission!'))
    .catch(error => console.error('Error:', error));
});

function redirectToHome() {
    window.location.href = "/home";
}
