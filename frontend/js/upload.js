const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

// ---------------- LOAD FOLDERS ----------------

async function loadFolders() {

    try {

        const response = await fetch(`${API}/folders`, {

            headers: {
                Authorization: `Bearer ${token}`
            }

        });

        if (!response.ok) {

            alert("Unable to load folders.");

            return;

        }

        const folders = await response.json();

        const select = document.getElementById("folderSelect");

        select.innerHTML = "";

        if (folders.length === 0) {

            select.innerHTML =
                `<option value="">No folders available</option>`;

            return;

        }

        folders.forEach(folder => {

            select.innerHTML += `

                <option value="${folder.id}">
                    ${folder.folder_name}
                </option>

            `;

        });

    }

    catch (err) {

        console.log(err);

        alert("Unable to connect to server.");

    }

}

// ---------------- UPLOAD FILE ----------------

document
.getElementById("uploadForm")
.addEventListener("submit", uploadFile);

async function uploadFile(e) {

    e.preventDefault();

    const folder_id =
        document.getElementById("folderSelect").value;

    const file =
        document.getElementById("fileInput").files[0];

    if (!folder_id) {

        alert("Please select a folder.");

        return;

    }

    if (!file) {

        alert("Please select a file.");

        return;

    }

    const formData = new FormData();

    formData.append("file", file);

    const progressBar =
        document.getElementById("progressBar");

    const progressText =
        document.getElementById("progressText");

    progressBar.style.width = "30%";

    progressText.innerHTML = "Uploading...";

    try {

        const response = await fetch(

            `${API}/upload?folder_id=${folder_id}`,

            {

                method: "POST",

                headers: {

                    Authorization: `Bearer ${token}`

                },

                body: formData

            }

        );

        const data = await response.json();

        if (!response.ok) {

            progressBar.style.width = "0%";

            progressText.innerHTML = "Upload Failed";

            alert(data.detail);

            return;

        }

        progressBar.style.width = "100%";

        progressText.innerHTML = "Upload Successful";

        alert(data.message);

        document.getElementById("uploadForm").reset();

        setTimeout(() => {

            window.location.href = "files.html";

        }, 1000);

    }

    catch (err) {

        console.log(err);

        progressBar.style.width = "0%";

        progressText.innerHTML = "Upload Failed";

        alert("Server Error");

    }

}

// ---------------- START ----------------

loadFolders();