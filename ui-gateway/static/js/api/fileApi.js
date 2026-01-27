// Assumption: If access_token exists in localStorage, assume userId = 1
// Later replace this with real JWT decoding / login integration.

// Base URL for file_service in local dev mode. If later run docker-compose and map ports, change this One line
const FILE_SERVICE_BASE = "http://localhost:5002";

// Temporary helper to get user id, in real auth need to decode JWT
function getUserIdForDev(){
    return 1; // assum logged in user is ID 1
}

// Helpers: build headers for file_service request
// Backend expects X-User-Id for auth simulation

function buildAuthHeaders(extraHeaders = {}){
    const token = localStorage.getItem("access_token");

    // UI already redirects to /login if no token (authGuard.js)
    // but we still guard in case this module is used elsewhere
    if (!token){
        throw new Error("Unauthorised: no access token found.");
    }

    return{
        "X-User-Id": String(getUserIdForDev()),
        ...extraHeaders,
    };
}

// GEt /dashboard
export async function getDashboardFiles(){
    const resp = await fetch(`${FILE_SERVICE_BASE}/dashboard`, {
        method: "GET",
        headers: buildAuthHeaders(),
    });

    // Handle auth error consistently
    if (resp.status === 401){
        throw new Error("Unauthorised (401). Please login again.");
    }

    if (!resp.ok){
        // Try read backend error message
        let msg = `Failed to fetch dashboard files (HTTP ${resp.status})`;
        try{
            const body = await resp.json();
            if (body?.error) msg = body.error;
        } catch(_){}
        throw new Error(msg);
    }

    return await resp.json();
}

// POST /dashboard/upload
export async function uploadFile(file){
    if (!file){
        throw new Error("No file selected.");
    }

    const formData = new FormData();
    formData.append("file", file); // filed name is "file"

    const resp = await fetch(`${FILE_SERVICE_BASE}/dashboard/upload`, {
        method: "POST",
        headers: buildAuthHeaders(), // Note: Do NOT set Content-Type manually for FormData
        body: formData,
    });

    if (!resp.ok){
        let msg = `Upload failed (HTTP ${resp.status})`;
        try{
            const body = await resp.json();
            if (body?.error) msg = body.error;
        }catch (_){}
        throw new Error (msg);
    }

    return resp.json();
}