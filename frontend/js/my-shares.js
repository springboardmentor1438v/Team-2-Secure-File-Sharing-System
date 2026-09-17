const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");


// --------------------------------------------------
// AUTH CHECK
// --------------------------------------------------

if (!token) {

    window.location.href = "login.html";

}


// --------------------------------------------------
// ELEMENTS
// --------------------------------------------------

const username =
    document.getElementById("username");

const sharesContainer =
    document.getElementById("sharesContainer");


// --------------------------------------------------
// COMMON HEADERS
// --------------------------------------------------

const headers = {

    "Authorization": `Bearer ${token}`

};


// --------------------------------------------------
// LOAD PROFILE
// --------------------------------------------------

async function loadProfile() {

    try {

        const response = await fetch(
            `${API}/profile`,
            {
                headers: headers
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


        username.textContent =
            user.username;


    } catch (error) {

        console.error(
            "Profile error:",
            error
        );

        window.location.href =
            "login.html";

    }

}


// --------------------------------------------------
// LOAD MY SHARED FILES
// --------------------------------------------------

async function loadShares() {

    sharesContainer.innerHTML = `
        <h3>Loading...</h3>
    `;


    try {

        const response = await fetch(
            `${API}/my-shares`,
            {
                headers: headers
            }
        );


        const shares =
            await response.json();


        if (!response.ok) {

            sharesContainer.innerHTML = `
                <h3>
                    Unable to load shared files.
                </h3>
            `;

            return;

        }


        // No shares

        if (!shares.length) {

            sharesContainer.innerHTML = `

                <div class="text-center w-100">

                    <h3>
                        No shared files found.
                    </h3>

                </div>

            `;

            return;

        }


        sharesContainer.innerHTML = "";


        // --------------------------------------------------
        // DISPLAY EACH SHARE
        // --------------------------------------------------

        shares.forEach(share => {


            // Expiry

            const expiry =
                share.expiry_date
                    ? new Date(
                        share.expiry_date
                    ).toLocaleString()
                    : "No Expiry";


            // Status

            const status =
                share.is_revoked

                    ? `
                        <span class="status-revoked">
                            REVOKED
                        </span>
                      `

                    : `
                        <span class="status-active">
                            ACTIVE
                        </span>
                      `;


            // Download limit

            const downloadLimit =
                share.download_limit > 0
                    ? share.download_limit
                    : "Unlimited";


            // --------------------------------------------------
            // CARD
            // --------------------------------------------------

            sharesContainer.innerHTML += `

                <div class="share-card">


                    <h5>
                        ${share.filename}
                    </h5>


                    <p>
                        <strong>
                            Shared With:
                        </strong>

                        ${share.shared_with}
                    </p>


                    <p>
                        <strong>
                            Permission:
                        </strong>

                        ${share.permission}
                    </p>


                    <p>
                        <strong>
                            Expiry:
                        </strong>

                        ${expiry}
                    </p>


                    <p>
                        <strong>
                            Downloads:
                        </strong>

                        ${share.download_count}
                        /
                        ${downloadLimit}
                    </p>


                    <p>
                        <strong>
                            Status:
                        </strong>

                        ${status}
                    </p>


                    <div class="share-actions">


                        <!-- EDIT -->

                        <button
                            class="edit-btn"
                            onclick='openEditModal(${JSON.stringify(share)})'
                            ${share.is_revoked ? "disabled" : ""}>

                            <i class="fa-solid fa-pen-to-square"></i>

                            ${
                                share.is_revoked
                                    ? "Cannot Edit"
                                    : "Edit Share"
                            }

                        </button>


                        <!-- REVOKE -->

                        <button
                            class="revoke-btn"
                            onclick="revokeShare(${share.share_id})"
                            ${share.is_revoked ? "disabled" : ""}>

                            <i class="fa-solid fa-ban"></i>

                            ${
                                share.is_revoked
                                    ? "Already Revoked"
                                    : "Revoke Share"
                            }

                        </button>


                    </div>


                </div>

            `;

        });


    } catch (error) {

        console.error(
            "Load shares error:",
            error
        );


        sharesContainer.innerHTML = `

            <h3>
                Unable to connect to server.
            </h3>

        `;

    }

}


// --------------------------------------------------
// OPEN EDIT MODAL
// --------------------------------------------------

function openEditModal(share) {


    // Don't allow revoked shares

    if (share.is_revoked) {

        alert(
            "Revoked shares cannot be edited."
        );

        return;

    }


    // Share ID

    document.getElementById(
        "editShareId"
    ).value = share.share_id;


    // Permission

    document.getElementById(
        "editPermission"
    ).value = share.permission;


    // Download limit

    document.getElementById(
        "editDownloadLimit"
    ).value =
        share.download_limit ?? 0;


    // Expiry

    const expiryInput =
        document.getElementById(
            "editExpiry"
        );


    if (share.expiry_date) {

        const date =
            new Date(
                share.expiry_date
            );


        // Convert to datetime-local format

        const year =
            date.getFullYear();


        const month =
            String(
                date.getMonth() + 1
            ).padStart(2, "0");


        const day =
            String(
                date.getDate()
            ).padStart(2, "0");


        const hours =
            String(
                date.getHours()
            ).padStart(2, "0");


        const minutes =
            String(
                date.getMinutes()
            ).padStart(2, "0");


        expiryInput.value =
            `${year}-${month}-${day}T${hours}:${minutes}`;

    } else {

        expiryInput.value = "";

    }


    // Open Bootstrap modal

    const modalElement =
        document.getElementById(
            "editShareModal"
        );


    const modal =
        new bootstrap.Modal(
            modalElement
        );


    modal.show();

}


// --------------------------------------------------
// SAVE EDITED SHARE
// --------------------------------------------------

async function saveShareChanges() {


    const shareId =
        document.getElementById(
            "editShareId"
        ).value;


    const permission =
        document.getElementById(
            "editPermission"
        ).value;


    const expiryInput =
        document.getElementById(
            "editExpiry"
        ).value;


    const downloadLimit =
        parseInt(
            document.getElementById(
                "editDownloadLimit"
            ).value
        );


    // --------------------------------------------------
    // VALIDATION
    // --------------------------------------------------

    if (!shareId) {

        alert(
            "Share ID is missing."
        );

        return;

    }


    if (
        permission !== "VIEW" &&
        permission !== "DOWNLOAD"
    ) {

        alert(
            "Invalid permission."
        );

        return;

    }


    if (
        isNaN(downloadLimit) ||
        downloadLimit < 0
    ) {

        alert(
            "Download limit cannot be negative."
        );

        return;

    }


    // --------------------------------------------------
    // EXPIRY DATE
    // --------------------------------------------------

    let expiryDate = null;


    if (expiryInput) {

        expiryDate =
            new Date(
                expiryInput
            ).toISOString();

    }


    // --------------------------------------------------
    // REQUEST BODY
    // --------------------------------------------------

    const requestBody = {

        permission:
            permission,

        expiry_date:
            expiryDate,

        download_limit:
            downloadLimit

    };


    console.log(
        "Updating share:",
        requestBody
    );


    try {


        const response =
            await fetch(
                `${API}/edit-share/${shareId}`,
                {

                    method: "PUT",

                    headers: {

                        "Authorization":
                            `Bearer ${token}`,

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            requestBody
                        )

                }
            );


        const data =
            await response.json();


        // --------------------------------------------------
        // SUCCESS
        // --------------------------------------------------

        if (response.ok) {


            alert(
                data.message ||
                "Share updated successfully"
            );


            // Close modal

            const modalElement =
                document.getElementById(
                    "editShareModal"
                );


            const modal =
                bootstrap.Modal.getInstance(
                    modalElement
                );


            if (modal) {

                modal.hide();

            }


            // Reload shares

            await loadShares();


        }

        // --------------------------------------------------
        // ERROR
        // --------------------------------------------------

        else {

            alert(
                data.detail ||
                "Unable to update share."
            );

        }


    } catch (error) {

        console.error(
            "Edit share error:",
            error
        );


        alert(
            "Unable to connect to server."
        );

    }

}


// --------------------------------------------------
// REVOKE SHARE
// --------------------------------------------------

async function revokeShare(shareId) {


    const confirmRevoke =
        confirm(
            "Are you sure you want to revoke this share?"
        );


    if (!confirmRevoke) {

        return;

    }


    try {


        const response =
            await fetch(
                `${API}/revoke/${shareId}`,
                {

                    method: "PUT",

                    headers: headers

                }
            );


        const data =
            await response.json();


        if (response.ok) {


            alert(
                data.message ||
                "Share revoked successfully."
            );


            await loadShares();


        } else {


            alert(
                data.detail ||
                "Unable to revoke share."
            );

        }


    } catch (error) {

        console.error(
            "Revoke error:",
            error
        );


        alert(
            "Unable to connect to server."
        );

    }

}


// --------------------------------------------------
// LOGOUT
// --------------------------------------------------

document
    .getElementById("logoutBtn")
    .addEventListener(
        "click",
        function(event) {

            event.preventDefault();


            localStorage.clear();


            window.location.href =
                "login.html";

        }
    );


// --------------------------------------------------
// START
// --------------------------------------------------

loadProfile();

loadShares();