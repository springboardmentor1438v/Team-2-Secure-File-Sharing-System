const API = "http://127.0.0.1:8000";

// Get email from URL
const params = new URLSearchParams(window.location.search);
const email = params.get("email");

// Redirect if email is missing
if (!email) {
    alert("Invalid reset password request.");
    window.location.href = "forgot-password.html";
}

// Form Submit
document
    .getElementById("resetForm")
    .addEventListener("submit", function (e) {

        e.preventDefault();

        resetPassword();

    });

// ---------------- RESET PASSWORD ----------------

async function resetPassword() {

    const password = document.getElementById("password").value.trim();

    const confirmPassword = document.getElementById("confirmPassword").value.trim();

    if (password === "" || confirmPassword === "") {

        alert("Please fill all fields.");
        return;

    }

    if (password.length < 6) {

        alert("Password must be at least 6 characters.");
        return;

    }

    if (password !== confirmPassword) {

        alert("Passwords do not match.");
        return;

    }

    try {

        const response = await fetch(`${API}/reset-password`, {

            method: "PUT",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                email: email,

                password: password

            })

        });

        const data = await response.json();

        if (!response.ok) {

            alert(data.detail || "Password reset failed.");

            return;

        }

        alert("Password updated successfully!");

        window.location.href = "login.html";

    }

    catch (err) {

        console.error(err);

        alert("Unable to connect to server.");

    }

}