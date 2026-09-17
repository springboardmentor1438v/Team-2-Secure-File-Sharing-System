const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");
const filesContainer = document.getElementById("filesContainer");

const searchInput = document.getElementById("searchInput");
const filterSelect = document.getElementById("filterSelect");
const sortSelect = document.getElementById("sortSelect");

let allFiles = [];
let currentUserId = null;
let shareModal = null;

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

        username.textContent = data.username;
        currentUserId = data.id;

    } catch (error) {
        console.error("Profile error:", error);
        localStorage.clear();
        window.location.href = "login.html";
    }
}

async function loadUsers() {

    const sharedWith = document.getElementById("sharedWith");

    if (!sharedWith) {
        console.error("sharedWith select not found");
        return;
    }

    sharedWith.innerHTML = `
        <option value="">Loading users...</option>
    `;

    try {

        const response = await fetch(`${API}/dashboard/all-users`, {

            method: "GET",

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        const data = await response.json();

        console.log("Users API status:", response.status);
        console.log("Users API data:", data);

        if (!response.ok) {

            sharedWith.innerHTML = `
                <option value="">
                    Unable to load users
                </option>
            `;

            return;
        }

        if (!Array.isArray(data)) {

            console.error("Users API did not return an array:", data);

            sharedWith.innerHTML = `
                <option value="">
                    Invalid user data
                </option>
            `;

            return;
        }

        sharedWith.innerHTML = `
            <option value="">
                Select a user
            </option>
        `;

        data.forEach(user => {

            if (!user.id || !user.username) {
                return;
            }

            if (
                currentUserId !== null &&
                Number(user.id) === Number(currentUserId)
            ) {
                return;
            }

            const option = document.createElement("option");

            option.value = user.id;

            option.textContent = user.username;

            sharedWith.appendChild(option);

        });

    } catch (error) {

        console.error("Unable to load users:", error);

        sharedWith.innerHTML = `
            <option value="">
                Unable to load users
            </option>
        `;

    }

}

async function loadFiles() {

    filesContainer.innerHTML = `
        <h4>Loading files...</h4>
    `;

    try {

        const response = await fetch(`${API}/files`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {

            alert("Unable to load files.");
            return;
        }

        allFiles = await response.json();

        console.log("Files loaded:", allFiles);

        if (!Array.isArray(allFiles)) {

            filesContainer.innerHTML = `
                <div class="text-center w-100 mt-5">
                    <h3>Unable to load files.</h3>
                </div>
            `;

            return;
        }

        if (allFiles.length === 0) {

            filesContainer.innerHTML = `
                <div class="text-center w-100 mt-5">
                    <h3>No files uploaded yet.</h3>
                </div>
            `;

            return;
        }

        applyFilters();

    } catch (error) {

        console.error(error);

        filesContainer.innerHTML = `
            <div class="text-center w-100 mt-5">
                <h3>Unable to load files.</h3>
            </div>
        `;
    }
}

function displayFiles(files) {

    filesContainer.innerHTML = "";

    if (!files || files.length === 0) {

        filesContainer.innerHTML = `
            <div class="text-center w-100 mt-5">
                <h3>No matching files found.</h3>
            </div>
        `;

        return;
    }

    files.forEach(file => {

        const filename =
            file.filename || "Unnamed file";

        const uploadDate =
            file.upload_date || "";

        filesContainer.innerHTML += `

        <div class="file-card">

            <div class="file-icon">
                <i class="fa-solid fa-file"></i>
            </div>

            <div class="file-name">
                ${filename}
            </div>

            <div class="file-info">
                ${uploadDate}
            </div>

            <div class="file-actions">

                <button
                    class="download-btn"
                    onclick="downloadFile(${file.id})"
                    title="Download">

                    <i class="fa-solid fa-download"></i>

                </button>

                <button
                    class="rename-btn"
                    onclick="renameFile(${file.id})"
                    title="Rename">

                    <i class="fa-solid fa-pen"></i>

                </button>

                <button
                    class="delete-btn"
                    onclick="deleteFile(${file.id})"
                    title="Delete">

                    <i class="fa-solid fa-trash"></i>

                </button>

                <button
                    class="share-btn"
                    onclick="shareFile(${file.id})"
                    title="Share">

                    <i class="fa-solid fa-share"></i>

                </button>

                <button
                    class="version-btn"
                    onclick="versions(${file.id})"
                    title="Versions">

                    <i class="fa-solid fa-clock-rotate-left"></i>

                    Versions

                </button>

            </div>

        </div>

        `;
    });
}

function searchFiles(files) {

    const keyword =
        searchInput.value
            .trim()
            .toLowerCase();

    if (!keyword) {
        return files;
    }

    return files.filter(file => {

        const filename =
            (file.filename || "").toLowerCase();

        return filename.includes(keyword);
    });
}

function filterFiles(files) {

    const type =
        filterSelect.value.toLowerCase();

    if (!type) {
        return files;
    }

    return files.filter(file => {

        const filename =
            (file.filename || "").toLowerCase();

        if (type === "pdf") {
            return filename.endsWith(".pdf");
        }

        if (type === "docx") {
            return filename.endsWith(".docx");
        }

        if (type === "jpg") {
            return /\.(jpg|jpeg|gif|webp)$/i.test(filename);
        }

        if (type === "png") {
            return filename.endsWith(".png");
        }

        if (type === "zip") {
            return /\.(zip|rar|7z)$/i.test(filename);
        }

        return true;
    });
}

function sortFiles(files) {

    const sortType =
        sortSelect.value;

    const sortedFiles =
        [...files];

    if (sortType === "name") {

        sortedFiles.sort((a, b) => {

            const nameA =
                (a.filename || "").toLowerCase();

            const nameB =
                (b.filename || "").toLowerCase();

            return nameA.localeCompare(nameB);
        });
    }

    else if (sortType === "date") {

        sortedFiles.sort((a, b) => {

            const dateA =
                new Date(
                    a.upload_date || 0
                ).getTime();

            const dateB =
                new Date(
                    b.upload_date || 0
                ).getTime();

            return dateB - dateA;
        });
    }

    else if (sortType === "size") {

        sortedFiles.sort((a, b) => {

            const sizeA =
                Number(a.size || 0);

            const sizeB =
                Number(b.size || 0);

            return sizeB - sizeA;
        });
    }

    return sortedFiles;
}

function applyFilters() {

    let result =
        [...allFiles];

    result =
        searchFiles(result);

    result =
        filterFiles(result);

    result =
        sortFiles(result);

    displayFiles(result);
}

if (searchInput) {
    searchInput.addEventListener(
        "input",
        applyFilters
    );
}

if (filterSelect) {
    filterSelect.addEventListener(
        "change",
        applyFilters
    );
}

if (sortSelect) {
    sortSelect.addEventListener(
        "change",
        applyFilters
    );
}

async function downloadFile(id) {

    try {

        const response =
            await fetch(
                `${API}/download/${id}`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {

            let data = {};

            try {
                data = await response.json();
            } catch {}

            alert(
                data.detail ||
                "Download failed."
            );

            return;
        }

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(blob);

        const a =
            document.createElement("a");

        a.href = url;
        a.download = "";

        document.body.appendChild(a);

        a.click();

        a.remove();

        window.URL.revokeObjectURL(url);

    } catch (error) {

        console.error(error);

        alert("Download failed.");
    }
}

async function renameFile(id) {

    const newName =
        prompt("Enter new filename");

    if (!newName) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API}/rename/${id}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json",

                        Authorization:
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        new_filename:
                            newName
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Rename failed."
            );

            return;
        }

        alert(
            data.message ||
            "File renamed successfully."
        );

        await loadFiles();

    } catch (error) {

        console.error(error);

        alert("Rename failed.");
    }
}

async function deleteFile(id) {

    if (!confirm("Delete this file?")) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API}/delete/${id}`,
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
                "Delete failed."
            );

            return;
        }

        alert(
            data.message ||
            "File deleted successfully."
        );

        await loadFiles();

    } catch (error) {

        console.error(error);

        alert("Delete failed.");
    }
}

function shareFile(id) {

    const shareFileId =
        document.getElementById("shareFileId");

    const sharedWith =
        document.getElementById("sharedWith");

    const permission =
        document.getElementById("permission");

    const expiryDate =
        document.getElementById("expiryDate");

    const downloadLimit =
        document.getElementById("downloadLimit");

    if (shareFileId) {
        shareFileId.value = id;
    }

    if (sharedWith) {
        sharedWith.value = "";
    }

    if (permission) {
        permission.value = "VIEW";
    }

    if (expiryDate) {
        expiryDate.value = "";
    }

    if (downloadLimit) {
        downloadLimit.value = 5;
    }

    if (shareModal) {
        shareModal.show();
    }
}

async function versions(id) {

    try {

        const response =
            await fetch(
                `${API}/versions/${id}`,
                {
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
                "Unable to load versions."
            );

            return;
        }

        if (!data.length) {

            alert("No versions found.");

            return;
        }

        let message =
            "📂 File Versions\n\n";

        data.forEach(version => {

            message +=
`Version : ${version.version}
File : ${version.stored_filename}
Uploaded : ${version.uploaded_at}

`;
        });

        alert(message);

    } catch (error) {

        console.error(error);

        alert(
            "Unable to load versions."
        );
    }
}

async function shareSelectedFile() {

    const file_id =
        Number(
            document.getElementById(
                "shareFileId"
            ).value
        );

    const shared_with =
        Number(
            document.getElementById(
                "sharedWith"
            ).value
        );

    const permission =
        document.getElementById(
            "permission"
        ).value;

    const expiry_date =
        document.getElementById(
            "expiryDate"
        ).value || null;

    const download_limit =
        Number(
            document.getElementById(
                "downloadLimit"
            ).value
        );

    if (!file_id) {

        alert("Invalid file.");

        return;
    }

    if (!shared_with) {

        alert("Please select a recipient.");

        return;
    }

    try {

        const response =
            await fetch(
                `${API}/share`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        Authorization:
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({

                        file_id,

                        shared_with,

                        permission,

                        expiry_date,

                        download_limit

                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to share file."
            );

            return;
        }

        if (shareModal) {
            shareModal.hide();
        }

        alert(
            data.message ||
            "File shared successfully."
        );

    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );
    }
}

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const modalElement =
            document.getElementById(
                "shareModal"
            );

        if (
            modalElement &&
            typeof bootstrap !== "undefined"
        ) {

            shareModal =
                new bootstrap.Modal(
                    modalElement
                );
        }

        await loadProfile();

        await loadUsers();

        await loadFiles();

        const shareNowButton =
            document.getElementById(
                "shareNow"
            );

        if (shareNowButton) {

            shareNowButton.addEventListener(
                "click",
                shareSelectedFile
            );
        }

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
    }
);