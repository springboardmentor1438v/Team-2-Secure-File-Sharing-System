const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const username = document.getElementById("username");

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

    } catch (err) {

        console.log(err);
        window.location.href = "login.html";

    }

}

async function loadStatistics() {

    try {

        const headers = {
            Authorization: `Bearer ${token}`
        };

        const [
            users,
            files,
            shares,
            active
        ] = await Promise.all([

            fetch(`${API}/dashboard/total-users`, { headers }),
            fetch(`${API}/dashboard/admin/total-files`, { headers }),
            fetch(`${API}/dashboard/admin/total-shares`, { headers }),
            fetch(`${API}/dashboard/admin/active-shares`, { headers })

        ]);

        const usersData = await users.json();
        const filesData = await files.json();
        const sharesData = await shares.json();
        const activeData = await active.json();

        document.getElementById("totalUsers").textContent =
            usersData.total_users;

        document.getElementById("totalFiles").textContent =
            filesData.total_files;

        document.getElementById("totalShares").textContent =
            sharesData.total_shares;

        document.getElementById("activeShares").textContent =
            activeData.active_shares;

    } catch (err) {

        console.log(err);

        alert("Unable to load dashboard statistics.");

    }

}

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.clear();

    window.location.href = "login.html";

});

loadProfile();

loadStatistics();