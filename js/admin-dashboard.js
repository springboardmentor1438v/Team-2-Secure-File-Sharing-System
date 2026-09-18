const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");


// =====================================================
// AUTHENTICATION
// =====================================================

if (!token) {
    window.location.href = "login.html";
}

const headers = {
    "Authorization": `Bearer ${token}`
};


// =====================================================
// LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");

    window.location.href = "login.html";
}


const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener("click", function (event) {

        event.preventDefault();

        logout();

    });

}


// =====================================================
// LOAD ADMIN PROFILE
// =====================================================

async function loadProfile() {

    try {

        const response = await fetch(
            `${API}/profile`,
            {
                headers
            }
        );

        if (!response.ok) {

            logout();

            return;
        }

        const user = await response.json();

        const username =
            document.getElementById("username");

        if (username) {

            username.textContent =
                user.username || "Admin";

        }

    }

    catch (error) {

        console.error(
            "Profile error:",
            error
        );

    }

}


// =====================================================
// TOTAL USERS
// =====================================================

async function loadTotalUsers() {

    const element =
        document.getElementById("totalUsers");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/total-users`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to load total users"
            );

        }

        element.textContent =
            data.total_users ?? 0;

    }

    catch (error) {

        console.error(
            "Total users error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// TOTAL FILES - ALL USERS
// =====================================================

async function loadTotalFiles() {

    const element =
        document.getElementById("totalFiles");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/admin/total-files`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to load total files"
            );

        }

        element.textContent =
            data.total_files ?? 0;

    }

    catch (error) {

        console.error(
            "Total files error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// STORAGE USAGE - ALL USERS
// =====================================================

async function loadStorageUsage() {

    const element =
        document.getElementById("storageUsage");

    if (!element) return;

    try {

        /*
         * This endpoint should return:
         *
         * {
         *     "storage_used": "2.5 MB",
         *     "total_bytes": 2621440
         * }
         *
         * for ALL users.
         */

        const response = await fetch(
            `${API}/dashboard/admin/storage-usage`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load storage usage"
            );

        }

        element.textContent =
            data.storage_used ?? "0 Bytes";

    }

    catch (error) {

        console.error(
            "Storage usage error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// TOTAL SHARES - ALL USERS
// =====================================================

async function loadTotalShares() {

    const element =
        document.getElementById("totalShares");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/admin/total-shares`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load total shares"
            );

        }

        element.textContent =
            data.total_shares ?? 0;

    }

    catch (error) {

        console.error(
            "Total shares error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// ACTIVE SHARES - ALL USERS
// =====================================================

async function loadActiveShares() {

    const element =
        document.getElementById("activeShares");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/admin/active-shares`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load active shares"
            );

        }

        element.textContent =
            data.active_shares ?? 0;

    }

    catch (error) {

        console.error(
            "Active shares error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// EXPIRED SHARES - ALL USERS
// =====================================================

async function loadExpiredShares() {

    const element =
        document.getElementById("expiredShares");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/expired-shares`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load expired shares"
            );

        }

        /*
         * Current backend returns an array
         * of expired Share objects.
         *
         * Therefore we display its length.
         */

        if (Array.isArray(data)) {

            element.textContent =
                data.length;

        }

        else {

            element.textContent =
                data.expired_shares ??
                data.count ??
                0;

        }

    }

    catch (error) {

        console.error(
            "Expired shares error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// DOWNLOAD ACTIVITY - ALL USERS
// =====================================================

async function loadDownloadActivity() {

    const element =
        document.getElementById("downloadActivity");

    if (!element) return;

    try {

        /*
         * This endpoint should return:
         *
         * {
         *     "download_activity": 10
         * }
         *
         * for ALL users.
         */

        const response = await fetch(
            `${API}/dashboard/admin/download-activity`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load download activity"
            );

        }

        element.textContent =
            data.download_activity ??
            data.downloads ??
            data.count ??
            0;

    }

    catch (error) {

        console.error(
            "Download activity error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// FAILED LOGIN ATTEMPTS - ALL USERS
// =====================================================

async function loadFailedLogins() {

    const element =
        document.getElementById("failedLogins");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/failed-logins`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load failed login attempts"
            );

        }

        /*
         * Current backend returns an array
         * of ActivityLog records.
         */

        if (Array.isArray(data)) {

            element.textContent =
                data.length;

        }

        else {

            element.textContent =
                data.failed_logins ??
                data.count ??
                0;

        }

    }

    catch (error) {

        console.error(
            "Failed login error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// SECURITY EVENTS - ALL USERS
// =====================================================

async function loadSecurityEvents() {

    const element =
        document.getElementById("securityEvents");

    if (!element) return;

    try {

        const response = await fetch(
            `${API}/dashboard/security-events`,
            {
                headers
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load security events"
            );

        }

        /*
         * Current backend returns an array
         * of ActivityLog records.
         */

        if (Array.isArray(data)) {

            element.textContent =
                data.length;

        }

        else {

            element.textContent =
                data.security_events ??
                data.count ??
                0;

        }

    }

    catch (error) {

        console.error(
            "Security events error:",
            error
        );

        element.textContent = "--";

    }

}


// =====================================================
// LOAD EVERYTHING
// =====================================================

async function loadAdminDashboard() {

    await Promise.all([

        loadProfile(),

        loadTotalUsers(),

        loadTotalFiles(),

        loadStorageUsage(),

        loadTotalShares(),

        loadActiveShares(),

        loadExpiredShares(),

        loadDownloadActivity(),

        loadFailedLogins(),

        loadSecurityEvents()

    ]);

}

async function loadStorageUsage() {

    try {

        const response = await fetch(
            `${API}/dashboard/admin/storage-usage`,
            {
                headers
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load storage usage");
        }

        const data = await response.json();

        document.getElementById("storageUsage").textContent =
            data.storage_used ?? "--";

    } catch (error) {

        console.error("Storage usage error:", error);

        document.getElementById("storageUsage").textContent = "--";

    }
}

async function loadDownloadActivity() {

    try {

        const response = await fetch(
            `${API}/dashboard/admin/download-activity`,
            {
                headers
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load download activity");
        }

        const data = await response.json();

        document.getElementById("downloadActivity").textContent =
            data.download_activity ?? data.total_downloads ?? "--";

    } catch (error) {

        console.error("Download activity error:", error);

        document.getElementById("downloadActivity").textContent = "--";

    }
}


// =====================================================
// START DASHBOARD
// =====================================================

loadAdminDashboard();