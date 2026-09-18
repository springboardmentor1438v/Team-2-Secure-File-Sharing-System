const loginForm = document.getElementById("loginForm");
const loginAlert = document.getElementById("loginAlert");
const loginBtn = document.getElementById("loginBtn");
const loginText = document.getElementById("loginText");
const loginSpinner = document.getElementById("loginSpinner");

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

togglePassword.addEventListener("click", () => {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        togglePassword.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';

    } else {

        passwordInput.type = "password";
        togglePassword.innerHTML = '<i class="fa-solid fa-eye"></i>';

    }

});

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    loginAlert.className = "alert alert-danger d-none";

    const username = document.getElementById("username").value.trim();
    const password = passwordInput.value;

    if (!username || !password) {

        showError("Please enter email and password.");
        return;

    }

    loginBtn.disabled = true;
    loginText.classList.add("d-none");
    loginSpinner.classList.remove("d-none");

    try {

        const formData = new URLSearchParams();

        formData.append("grant_type", "password");
        formData.append("username", username);
        formData.append("password", password);
        formData.append("scope", "");
        formData.append("client_id", "");
        formData.append("client_secret", "");

        const response = await fetch("http://127.0.0.1:8000/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },

            body: formData.toString()

        });

        const data = await response.json();

        if (response.ok) {

            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("token_type", data.token_type);

    // Get logged-in user profile
            const profileResponse = await fetch("http://127.0.0.1:8000/profile", {
                 headers: {
                    Authorization: `Bearer ${data.access_token}`
        }
    });

            const profile = await profileResponse.json();

            if (profile.role === "ADMIN") {

              window.location.href = "admin-dashboard.html";

    } 
            else {

               window.location.href = "dashboard.html";

    }

}
        else {

            showError(data.detail || "Invalid Email or Password.");

        }

    } catch (error) {

        console.error(error);
        showError("Unable to connect to server.");

    }

    loginBtn.disabled = false;
    loginText.classList.remove("d-none");
    loginSpinner.classList.add("d-none");

});

function showError(message) {

    loginAlert.textContent = message;
    loginAlert.className = "alert alert-danger";
}