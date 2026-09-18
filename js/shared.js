const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");
const sharedContainer = document.getElementById("sharedContainer");

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

        username.textContent = user.username;

    } catch {

        window.location.href = "login.html";

    }

}

async function loadSharedFiles() {

    sharedContainer.innerHTML = `
        <div class="empty-state">
            <h4>Loading shared files...</h4>
        </div>
    `;

    try {

        const response = await fetch(`${API}/shared-with-me`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const files = await response.json();

        if (!response.ok) {

            sharedContainer.innerHTML = `
                <div class="empty-state">
                    <h3>Unable to load shared files.</h3>
                </div>
            `;

            return;

        }

        if (files.length === 0) {

            sharedContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-folder-open"></i>
                    <h3>No files have been shared with you.</h3>
                </div>
            `;

            return;

        }

        sharedContainer.innerHTML = "";

        files.forEach(file => {

            const expiry = file.expiry_date
                ? new Date(file.expiry_date).toLocaleString()
                : "No Expiry";

            let buttonHTML = "";

            if (file.permission === "DOWNLOAD") {

                buttonHTML = `
                    <button
                        class="download-btn"
                        onclick="downloadShared(${file.share_id})">

                        <i class="fa-solid fa-download"></i>
                        Download

                    </button>
                `;

            } else {

                buttonHTML = `
                    <button
                        class="download-btn"
                        onclick="viewShared(${file.share_id})">

                        <i class="fa-solid fa-eye"></i>
                        View File

                    </button>
                `;

            }

            sharedContainer.innerHTML += `

                <div class="shared-card">

                    <div class="file-icon">
                        <i class="fa-solid fa-file"></i>
                    </div>

                    <div class="file-name">
                        ${file.filename}
                    </div>

                    <div class="file-info">
                        <strong>Owner :</strong> ${file.owner}
                    </div>

                    <div class="file-info">
                        <strong>Permission :</strong> ${file.permission}
                    </div>

                    <div class="file-info">
                        <strong>Expiry :</strong> ${expiry}
                    </div>

                    <div class="file-info">
                        <strong>Downloads :</strong>
                        ${file.download_count} / ${file.download_limit}
                    </div>

                    ${buttonHTML}

                </div>

            `;

        });

    } catch (error) {

        console.log(error);

        sharedContainer.innerHTML = `
            <div class="empty-state">
                <h3>Unable to connect to server.</h3>
            </div>
        `;

    }

}

function downloadShared(shareId) {

    fetch(`${API}/shared-download/${shareId}`, {

        headers: {
            Authorization: `Bearer ${token}`
        }

    })

    .then(response => {

        if (!response.ok) {

            return response.json().then(err => {

                alert(err.detail);

            });

        }

        return response.blob().then(blob => {

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");

            a.href = url;

            const disposition = response.headers.get("Content-Disposition");

            let filename = "download";

            if (disposition) {

                const match = disposition.match(/filename="(.+)"/);

                if (match) {

                    filename = match[1];

                }

            }

            a.download = filename;

            document.body.appendChild(a);

            a.click();

            a.remove();

            window.URL.revokeObjectURL(url);

        });

    });

}

async function viewShared(shareId) {

    const response = await fetch(`${API}/shared-view/${shareId}`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (!response.ok) {

        const err = await response.json();

        alert(err.detail);

        return;

    }

    const blob = await response.blob();

    const url = URL.createObjectURL(blob);

    window.open(url, "_blank");

}

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.clear();

    window.location.href = "login.html";

});

loadProfile();
loadSharedFiles();