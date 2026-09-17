const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");
const usersTable = document.getElementById("usersTable");
const searchInput = document.getElementById("searchInput");

let allUsers = [];

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

        const data = await response.json();

        if (data.role !== "ADMIN") {

            alert("Access Denied");

            window.location.href = "dashboard.html";

            return;

        }

        username.textContent = data.username;

    }

    catch (err) {

        console.log(err);

        window.location.href = "login.html";

    }

}

// ---------------- LOAD USERS ----------------

async function loadUsers() {

    try {

        const response = await fetch(`${API}/dashboard/all-users`, {

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        if (!response.ok) {

            alert("Unable to load users.");

            return;

        }

        allUsers = await response.json();

        renderUsers(allUsers);

    }

    catch (err) {

        console.log(err);

    }

}

// ---------------- RENDER USERS ----------------

function renderUsers(users) {

    usersTable.innerHTML = "";

    users.forEach(user => {

        usersTable.innerHTML += `

        <tr>

            <td>${user.id}</td>

            <td>${user.username}</td>

            <td>${user.email}</td>

            <td>${user.role}</td>

            <td>

                <button
                    class="btn btn-primary btn-sm"
                    onclick="changeRole(${user.id}, '${user.role}')">

                    Change Role

                </button>

            </td>

        </tr>

        `;

    });

}

// ---------------- CHANGE ROLE ----------------

async function changeRole(userId, currentRole) {

    const newRole = currentRole === "ADMIN"
        ? "USER"
        : "ADMIN";

    const confirmChange = confirm(
        `Change this user's role to ${newRole}?`
    );

    if (!confirmChange) return;

    try {

        const response = await fetch(

            `${API}/dashboard/change-role/${userId}`,

            {

                method: "PUT",

                headers: {

                    "Content-Type": "application/json",

                    Authorization: `Bearer ${token}`

                },

                body: JSON.stringify({

                    role: newRole

                })

            }

        );

        const data = await response.json();

        if (!response.ok) {

            alert(data.detail);

            return;

        }

        alert("Role updated successfully.");

        loadUsers();

    }

    catch (err) {

        console.log(err);

        alert("Server error.");

    }

}

// ---------------- SEARCH ----------------

searchInput.addEventListener("keyup", () => {

    const value = searchInput.value.toLowerCase();

    const filtered = allUsers.filter(user =>

        user.username.toLowerCase().includes(value) ||

        user.email.toLowerCase().includes(value)

    );

    renderUsers(filtered);

});

// ---------------- LOGOUT ----------------

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.clear();

    window.location.href = "login.html";

});

// ---------------- START ----------------

loadProfile();

loadUsers();