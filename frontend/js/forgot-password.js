const API = "http://127.0.0.1:8000";

document
.getElementById("forgotForm")
.addEventListener("submit", async function (e) {

    e.preventDefault();

    const email = document.getElementById("email").value;

    if (email === "") {
        alert("Enter Email");
        return;
    }

    try {

        const response = await fetch(`${API}/verify-email`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email
            })

        });

        const data = await response.json();

        if (!response.ok) {

            alert(data.detail);
            return;

        }

        window.location.href = `reset-password.html?email=${email}`;

    }

    catch (err) {

        console.log(err);
        alert("Server Error");

    }

});