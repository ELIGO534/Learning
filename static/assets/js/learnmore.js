document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sponsorshipForm");
    const contactInput = document.getElementById("contact");
    let submittedNumbers = new Set(); // Store submitted numbers

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload

        let contactNumber = contactInput.value.trim();

        // Check if the contact number is exactly 10 digits
        if (!/^\d{10}$/.test(contactNumber)) {
            showCustomAlert("Please enter a valid 10-digit phone number!", false);
            return;
        }

        // Check if the number has already been used
        if (submittedNumbers.has(contactNumber)) {
            showCustomAlert("This phone number has already submitted the form!", false);
            return;
        }

        let formData = new FormData(this);

        fetch("/survey/submit/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                submittedNumbers.add(contactNumber); // Store the submitted number
                showCustomAlert("Form submitted successfully!", true);
                form.reset();
                setTimeout(() => window.location.href = "/home", 2000);
            } else {
                showCustomAlert(data.message, false);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});

// Function to show a custom-styled alert box
function showCustomAlert(message, success) {
    let alertBox = document.createElement("div");
    alertBox.classList.add("custom-alert");

    if (success) {
        alertBox.classList.add("success");
    } else {
        alertBox.classList.add("error");
    }

    alertBox.innerHTML = `
        <div class="alert-content">
            <p>${message}</p>
            <button onclick="closeCustomAlert()">OK</button>
        </div>
    `;

    document.body.appendChild(alertBox);
}

// Function to close the custom alert box
function closeCustomAlert() {
    let alertBox = document.querySelector(".custom-alert");
    if (alertBox) {
        alertBox.remove();
    }
}

// Function to get CSRF token from cookies
function getCSRFToken() {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        let [name, value] = cookie.split("=");
        if (name === "csrftoken") return value;
    }
    return "";
}
