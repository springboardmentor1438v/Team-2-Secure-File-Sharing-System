const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");
const filesTable = document.getElementById("filesTable");
const searchInput = document.getElementById("searchInput");

let allFiles = [];

/* ---------------- PROFILE ---------------- */

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

    } catch (err) {

        console.log(err);

        window.location.href = "login.html";

    }

}

/* ---------------- LOAD FILES ---------------- */

async function loadFiles() {

    try {

        const response = await fetch(`${API}/dashboard/all-files`, {

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        if (!response.ok) {

            alert("Unable to load files.");

            return;

        }

        allFiles = await response.json();

        renderFiles(allFiles);

    } catch (err) {

        console.log(err);

    }

}

/* ---------------- RENDER TABLE ---------------- */

function renderFiles(files) {

    filesTable.innerHTML = "";

    files.forEach(file => {

        filesTable.innerHTML += `

        <tr>

            <td>${file.id}</td>

            <td>${file.filename}</td>

            <td>${file.owner}</td>

            <td>${new Date(file.uploaded_at).toLocaleString()}</td>

            <td>

                <button
                    class="delete-btn"
                    onclick="deleteFile(${file.id})">

                    <i class="fa-solid fa-trash"></i>

                    Delete

                </button>

            </td>

        </tr>

        `;

    });

}

/* ---------------- SEARCH ---------------- */

searchInput.addEventListener("keyup", () => {

    const value = searchInput.value.toLowerCase();

    const filtered = allFiles.filter(file =>

        file.filename.toLowerCase().includes(value) ||

        file.owner.toLowerCase().includes(value)

    );

    renderFiles(filtered);

});

/* ---------------- DELETE ---------------- */

async function deleteFile(fileId) {

    const confirmDelete = confirm(
        "Are you sure you want to permanently delete this file?"
    );

    if (!confirmDelete) return;

    try {

        const response = await fetch(`${API}/dashboard/delete-file/${fileId}`, {

            method: "DELETE",

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        const data = await response.json();

        if (!response.ok) {

            alert(data.detail || "Unable to delete file.");

            return;

        }

        alert("File deleted successfully.");

        loadFiles();

    } catch (err) {

        console.log(err);

        alert("Server error.");

    }

}

/* ---------------- LOGOUT ---------------- */

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.clear();

    window.location.href = "login.html";

});

/* ---------------- START ---------------- */

loadProfile();

loadFiles();