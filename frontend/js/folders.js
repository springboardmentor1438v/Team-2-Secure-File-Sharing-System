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

        const list = document.getElementById("foldersList");

        list.innerHTML = "";

        if (folders.length === 0) {

            list.innerHTML = `
                <div style="text-align:center;color:white;padding:30px;">
                    No folders found.
                </div>
            `;

            return;

        }

        folders.forEach(folder => {

            list.innerHTML += `

                <div class="folder-card">

                    <div class="folder-info">

                        <i class="fa-solid fa-folder"></i>

                        ${folder.folder_name}

                    </div>

                    <div class="actions">

                        <button
                        class="rename-btn"
                        onclick="renameFolder(${folder.id}, '${folder.folder_name}')">

                        Rename

                        </button>

                        <button
                        class="delete-btn"
                        onclick="deleteFolder(${folder.id})">

                        Delete

                        </button>

                    </div>

                </div>

            `;

        });

    }

    catch(err){

        console.log(err);

        alert("Server Error");

    }

}

// ---------------- CREATE ----------------

document
.getElementById("createBtn")
.addEventListener("click", createFolder);

async function createFolder(){

    const folderName =
        document.getElementById("folderName").value.trim();

    if(folderName===""){

        alert("Enter Folder Name");

        return;

    }

    try{

        const response = await fetch(

            `${API}/folders`,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json",

                    Authorization:`Bearer ${token}`

                },

                body:JSON.stringify({

                    folder_name:folderName

                })

            }

        );

        const data = await response.json();

        if(!response.ok){

            alert(data.detail);

            return;

        }

        alert(data.message || "Folder created successfully");

        document.getElementById("folderName").value="";

        loadFolders();

    }

    catch(err){

        console.log(err);

        alert("Server Error");

    }

}

// ---------------- RENAME ----------------

async function renameFolder(id, currentName){

    const newName = prompt(

        "Enter New Folder Name",

        currentName

    );

    if(!newName) return;

    try{

        const response = await fetch(

            `${API}/folders/${id}`,

            {

                method:"PUT",

                headers:{

                    "Content-Type":"application/json",

                    Authorization:`Bearer ${token}`

                },

                body:JSON.stringify({

                    folder_name:newName

                })

            }

        );

        const data = await response.json();

        if(!response.ok){

            alert(data.message || "Folder renamed successfully.");
            return;

        }

        alert(data.message || "Folder renamed successfully.");;

        loadFolders();

    }

    catch(err){

        console.log(err);

        alert("Server Error");

    }

}

// ---------------- DELETE ----------------

async function deleteFolder(id){

    if(!confirm("Delete this folder?")) return;

    try{

        const response = await fetch(

            `${API}/folders/${id}`,

            {

                method:"DELETE",

                headers:{

                    Authorization:`Bearer ${token}`

                }

            }

        );

        const data = await response.json();

        if(!response.ok){

            alert(data.detail);

            return;

        }

        alert(data.message);

        loadFolders();

    }

    catch(err){

        console.log(err);

        alert("Server Error");

    }

}

// ---------------- START ----------------

loadFolders();