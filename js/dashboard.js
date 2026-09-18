const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");


// =====================================================
// AUTH CHECK
// =====================================================

if (!token) {
    window.location.href = "login.html";
}


// =====================================================
// COMMON HEADERS
// =====================================================

const headers = {
    "Authorization": `Bearer ${token}`
};


// =====================================================
// ELEMENTS
// =====================================================

const usernameElement =
    document.getElementById("username");

const totalFilesElement =
    document.getElementById("totalFiles");

const storageUsageElement =
    document.getElementById("storageUsage");

const sharedFilesElement =
    document.getElementById("sharedFiles");

const recentActivityElement =
    document.getElementById("recentActivity");

const mostDownloadedElement =
    document.getElementById("mostDownloaded");

const logoutBtn =
    document.getElementById("logoutBtn");


// =====================================================
// LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");

    window.location.href = "login.html";
}


if (logoutBtn) {

    logoutBtn.addEventListener("click", function (event) {

        event.preventDefault();

        logout();

    });

}


// =====================================================
// LOAD PROFILE
// =====================================================

async function loadProfile() {

    try {

        const response = await fetch(
            `${API}/profile`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            logout();

            return;

        }


        const user = await response.json();


        if (usernameElement) {

            usernameElement.textContent =
                user.username || "User";

        }

    }

    catch (error) {

        console.error(
            "Profile loading error:",
            error
        );

    }

}


// =====================================================
// LOAD TOTAL FILES
// =====================================================

async function loadTotalFiles() {

    if (!totalFilesElement) {
        return;
    }


    totalFilesElement.textContent = "Loading...";


    try {

        const response = await fetch(
            `${API}/dashboard/total-files`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load total files"
            );

        }


        const data =
            await response.json();


        const total =
            data.total_files ??
            data.total ??
            0;


        totalFilesElement.textContent =
            total;

    }

    catch (error) {

        console.error(
            "Total files error:",
            error
        );

        totalFilesElement.textContent =
            "--";

    }

}


// =====================================================
// LOAD STORAGE USAGE
// =====================================================

async function loadStorageUsage() {

    if (!storageUsageElement) {
        return;
    }


    storageUsageElement.textContent =
        "Loading...";


    try {

        const response = await fetch(
            `${API}/dashboard/storage-usage`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load storage usage"
            );

        }


        const data =
            await response.json();


        storageUsageElement.textContent =
            data.storage_used ?? "0";

    }

    catch (error) {

        console.error(
            "Storage usage error:",
            error
        );

        storageUsageElement.textContent =
            "--";

    }

}


// =====================================================
// LOAD SHARED FILES
// =====================================================

async function loadSharedFiles() {

    if (!sharedFilesElement) {
        return;
    }


    sharedFilesElement.textContent =
        "Loading...";


    try {

        const response = await fetch(
            `${API}/dashboard/shared-files-count`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load shared files"
            );

        }


        const data =
            await response.json();


        const count =
            data.shared_files ??
            data.count ??
            0;


        sharedFilesElement.textContent =
            count;

    }

    catch (error) {

        console.error(
            "Shared files error:",
            error
        );

        sharedFilesElement.textContent =
            "--";

    }

}


async function loadSharedWithMe() {

    try {

        const response = await fetch(
            `${API}/dashboard/shared-with-me-count`,
            {
                headers
            }
        );

        if (!response.ok) {

            document.getElementById("sharedWithMe").textContent = "--";

            return;
        }

        const data = await response.json();

        document.getElementById("sharedWithMe").textContent =
            data.shared_with_me ?? 0;

    } catch (error) {

        console.error(error);

        document.getElementById("sharedWithMe").textContent = "--";

    }

}

// =====================================================
// LOAD RECENT ACTIVITY
// =====================================================

async function loadRecentActivity() {

    if (!recentActivityElement) {
        return;
    }


    recentActivityElement.innerHTML =
        "<p>Loading activity...</p>";


    try {

        const response = await fetch(
            `${API}/dashboard/recent-activity`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load recent activity"
            );

        }


        const activities =
            await response.json();


        recentActivityElement.innerHTML =
            "";


        if (
            !Array.isArray(activities) ||
            activities.length === 0
        ) {

            recentActivityElement.innerHTML = `
                <p>No recent activity.</p>
            `;

            return;

        }


        activities.forEach(activity => {

            const item =
                document.createElement("div");

            item.className =
                "activity-item";


            const action =
                document.createElement("strong");

            action.textContent =
                activity.action || "Activity";


            const description =
                document.createElement("small");

            description.textContent =
                activity.description || "";


            item.appendChild(action);

            item.appendChild(
                document.createElement("br")
            );

            item.appendChild(description);


            recentActivityElement.appendChild(
                item
            );

        });

    }

    catch (error) {

        console.error(
            "Recent activity error:",
            error
        );


        recentActivityElement.innerHTML = `
            <p>Unable to load activity.</p>
        `;

    }

}


// =====================================================
// LOAD MOST DOWNLOADED FILES
// =====================================================

async function loadMostDownloaded() {

    if (!mostDownloadedElement) {
        return;
    }


    mostDownloadedElement.innerHTML =
        "<p>Loading...</p>";


    try {

        const response = await fetch(
            `${API}/dashboard/most-downloaded-files`,
            {
                headers: headers
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load most downloaded files"
            );

        }


        const files =
            await response.json();


        mostDownloadedElement.innerHTML =
            "";


        if (
            !Array.isArray(files) ||
            files.length === 0
        ) {

            mostDownloadedElement.innerHTML = `
                <p>No downloads yet.</p>
            `;

            return;

        }


        files.forEach(file => {

            const item =
                document.createElement("div");

            item.className =
                "activity-item";


            const filename =
                document.createElement("strong");

            filename.textContent =
                file.filename || "Unknown file";


            const downloads =
                document.createElement("small");

            downloads.textContent =
                `⬇ ${file.downloads ?? 0} Downloads`;


            item.appendChild(filename);

            item.appendChild(
                document.createElement("br")
            );

            item.appendChild(downloads);


            mostDownloadedElement.appendChild(
                item
            );

        });

    }

    catch (error) {

        console.error(
            "Most downloaded error:",
            error
        );


        mostDownloadedElement.innerHTML = `
            <p>Unable to load data.</p>
        `;

    }

}


// =====================================================
// LOAD DASHBOARD
// =====================================================

async function loadDashboard() {

    await loadProfile();

    await Promise.all([

        loadTotalFiles(),

        loadStorageUsage(),

        loadSharedFiles(),

        loadSharedWithMe(),

        loadRecentActivity(),

        loadMostDownloaded()

    ]);

}

async function loadSharedWithMe() {

    try {

        const response = await fetch(
            `${API}/shared-with-me`,
            {
                headers: headers
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load shared files");
        }

        const files = await response.json();

        document.getElementById("sharedWithMe").textContent =
            Array.isArray(files) ? files.length : 0;

    } catch (error) {

        console.error(error);

        document.getElementById("sharedWithMe").textContent = "--";

    }
}

async function loadSharedByMe() {

    try {

        const response = await fetch(
            `${API}/my-shares`,
            {
                headers: headers
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load my shares");
        }

        const shares = await response.json();

        document.getElementById("sharedByMe").textContent =
            Array.isArray(shares) ? shares.length : 0;

    } catch (error) {

        console.error(error);

        document.getElementById("sharedByMe").textContent = "--";

    }
}


// =====================================================
// START DASHBOARD
// =====================================================

loadDashboard();