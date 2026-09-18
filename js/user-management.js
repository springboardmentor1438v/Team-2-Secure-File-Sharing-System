const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}

const usernameElement =
    document.getElementById("username");

const usersTable =
    document.getElementById("usersTable");

let allUsers = [];


// ==========================================
// LOAD PROFILE
// ==========================================

async function loadProfile() {

    try {

        const response = await fetch(
            `${API}/profile`,
            {
                headers: {
                    Authorization:
                        `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {

            localStorage.clear();

            window.location.href =
                "login.html";

            return;
        }

        const user =
            await response.json();

        if (user.role !== "ADMIN") {

            alert("Access Denied");

            window.location.href =
                "dashboard.html";

            return;
        }

        usernameElement.textContent =
            user.username;

    }

    catch (error) {

        console.error(
            "Profile error:",
            error
        );

        localStorage.clear();

        window.location.href =
            "login.html";

    }
}


// ==========================================
// LOAD USERS
// ==========================================

async function loadUsers() {

    try {

        const response = await fetch(
            `${API}/dashboard/all-users`,
            {
                headers: {
                    Authorization:
                        `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {

            alert(
                "Unable to load users."
            );

            return;
        }

        allUsers =
            await response.json();

        renderUsers(allUsers);

    }

    catch (error) {

        console.error(
            "Load users error:",
            error
        );

        alert(
            "Unable to connect to server."
        );

    }
}


// ==========================================
// DISPLAY USERS
// ==========================================

function renderUsers(users) {

    usersTable.innerHTML = "";

    if (!users || users.length === 0) {

        usersTable.innerHTML = `

            <tr>

                <td
                    colspan="5"
                    style="text-align:center;"
                >

                    No users found.

                </td>

            </tr>

        `;

        return;
    }


    users.forEach(user => {

        let roleBadge = "";

        if (user.role === "ADMIN") {

            roleBadge = `

                <span class="role-admin">

                    ADMIN

                </span>

            `;

        }

        else {

            roleBadge = `

                <span class="role-user">

                    USER

                </span>

            `;

        }


        usersTable.innerHTML += `

            <tr>

                <td>

                    ${user.id}

                </td>


                <td>

                    ${user.username}

                </td>


                <td>

                    ${user.email}

                </td>


                <td>

                    ${roleBadge}

                </td>


                <td>

                    <div class="user-actions">

                        <button
                            class="delete-user-btn"
                            onclick="deleteUser(${user.id}, '${escapeQuotes(user.username)}')"
                        >

                            <i class="fa-solid fa-trash"></i>

                            Delete

                        </button>

                    </div>

                </td>

            </tr>

        `;

    });

}


// ==========================================
// ESCAPE USERNAME
// ==========================================

function escapeQuotes(value) {

    return String(value)
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"');

}


// ==========================================
// DELETE USER
// ==========================================

async function deleteUser(
    userId,
    username
) {

    const confirmed = confirm(

        `Are you sure you want to delete user "${username}"?\n\n` +

        `This will permanently remove the user's account and related data.`

    );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `${API}/dashboard/delete-user/${userId}`,
                {
                    method: "DELETE",

                    headers: {

                        Authorization:
                            `Bearer ${token}`

                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to delete user."
            );

            return;

        }


        alert(
            data.message ||
            "User deleted successfully."
        );


        await loadUsers();

    }


    catch (error) {

        console.error(
            "Delete user error:",
            error
        );


        alert(
            "Unable to connect to server."
        );

    }

}


// ==========================================
// LOGOUT
// ==========================================

const logoutBtn =
    document.getElementById(
        "logoutBtn"
    );


if (logoutBtn) {

    logoutBtn.addEventListener(
        "click",
        event => {

            event.preventDefault();

            localStorage.clear();

            window.location.href =
                "login.html";

        }
    );

}


// ==========================================
// START
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await loadProfile();

        await loadUsers();

    }
);