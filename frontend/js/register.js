const registerForm = document.getElementById("registerForm");
const registerAlert = document.getElementById("registerAlert");

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    registerAlert.classList.add("d-none");

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!username || !email || !password || !confirmPassword) {
        showError("Please fill all fields.");
        return;
    }

    if (password.length < 8) {
        showError("Password must be at least 8 characters.");
        return;
    }

    if (password !== confirmPassword) {
        showError("Passwords do not match.");
        return;
    }

    try {

        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {

            registerAlert.className = "alert alert-success";
            registerAlert.textContent = "Account created successfully! Redirecting to login...";
            registerAlert.classList.remove("d-none");

            setTimeout(() => {
                window.location.href = "login.html";
            }, 2000);

        } else {

            showError(data.detail || "Registration failed.");

        }

    } catch (error) {

        showError("Unable to connect to the server.");

    }

});

function showError(message) {

    registerAlert.className = "alert alert-danger";
    registerAlert.textContent = message;
    registerAlert.classList.remove("d-none");

}