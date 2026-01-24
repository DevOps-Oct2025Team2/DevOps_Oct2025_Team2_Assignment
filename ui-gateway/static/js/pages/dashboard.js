// ui-gateway/static/js/pages/dashboard.js
import { getDashboardFiles, uploadFile } from "../api/fileApi.js";

/**
 * Dashboard page controller
 * Responsibilities:
 *  - fetch and render dashboard files
 *  - handle upload button click
 *  - show messages (success/error)
 */

// ---- DOM elements ----
const filesContainer = document.getElementById("files");
const msgBox = document.getElementById("msg");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");

// Small helper: show a message to the user
function showMessage(text, isError = false) {
    if (!msgBox) return;
    msgBox.textContent = text;
    msgBox.style.padding = "8px";
    msgBox.style.margin = "8px 0";
    msgBox.style.border = "1px solid #ccc";
    msgBox.style.borderRadius = "6px";
    msgBox.style.background = isError ? "#ffe6e6" : "#e6ffed";
}

// Render file list or empty state
function renderFiles(files) {
    if (!filesContainer) return;

    // Clear existing content
    filesContainer.innerHTML = "";

    // Empty state (AC-DASH-04)
    if (!files || files.length === 0) {
        const p = document.createElement("p");
        p.textContent = "No files uploaded yet. Upload one to get started.";
        filesContainer.appendChild(p);
        return;
    }

    // Simple list view
    const ul = document.createElement("ul");
    for (const f of files) {
        const li = document.createElement("li");

        // Basic formatting for size (bytes)
        li.textContent = `${f.filename} (${f.size_bytes} bytes) - ${f.content_type}`;

        ul.appendChild(li);
    }
    filesContainer.appendChild(ul);
}

// Fetch dashboard files and render them
async function loadDashboard() {
    try {
        showMessage("Loading files...");
        const data = await getDashboardFiles();

        // Your backend returns { files: [...] }
        renderFiles(data.files);
        showMessage("Loaded.");
    } catch (err) {
        console.error(err);
        showMessage(err.message || "Failed to load dashboard.", true);
    }
}

// Handle upload click
async function handleUpload() {
    try {
        const file = fileInput?.files?.[0];

        if (!file) {
        showMessage("Please select a file first.", true);
        return;
        }

        uploadBtn.disabled = true;
        showMessage("Uploading...");

        await uploadFile(file);

        showMessage("Upload successful!");
        fileInput.value = ""; // clear input

        // Refresh file list so new file appears (AC-FILE-01)
        await loadDashboard();
    } catch (err) {
        console.error(err);
        showMessage(err.message || "Upload failed.", true);
    } finally {
        uploadBtn.disabled = false;
    }
}

// Wire up events
if (uploadBtn) {
    uploadBtn.addEventListener("click", handleUpload);
}

// Run on page load
loadDashboard();
