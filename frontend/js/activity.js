const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");
const logsTable = document.getElementById("logsTable");

// ---------------- PROFILE ----------------

async function loadProfile() {

    try {

        const response = await fetch(`${API}/profile`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {

            localStorage.clear();
            window.location.href = "login.html";
            return;

        }

        const user = await response.json();

        if (user.role !== "ADMIN") {

            alert("Access Denied");

            window.location.href = "dashboard.html";

            return;

        }

        username.textContent = user.username;

    } catch {

        window.location.href = "login.html";

    }

}

// ---------------- LOAD ACTIVITY ----------------

async function loadActivity() {

    try {

        const response = await fetch(`${API}/activity`, {

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        if (!response.ok) {

            alert("Unable to load activity logs.");

            return;

        }

        const logs = await response.json();

        logsTable.innerHTML = "";

        logs.forEach(log => {

            logsTable.innerHTML += `

            <tr>

                <td>${log.id}</td>

                <td>${log.user_id}</td>

                <td>${log.action}</td>

                <td>${log.resource_type}</td>

                <td>${log.description}</td>

                <td class="${log.status === "SUCCESS" ? "success" : "failed"}">

                    ${log.status}

                </td>

                <td>

                    ${new Date(log.created_at).toLocaleString()}

                </td>

            </tr>

            `;

        });

    } catch (err) {

        console.log(err);

        alert("Server connection failed.");

    }

}

// ---------------- LOGOUT ----------------

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.clear();

    window.location.href = "login.html";

});

// ---------------- START ----------------

loadProfile();

loadActivity();