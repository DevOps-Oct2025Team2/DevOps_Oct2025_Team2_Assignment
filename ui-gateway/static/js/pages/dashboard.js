// ui-gateway/static/js/pages/dashboard.js
import { getDashboardFiles, uploadFile, deleteFile, downloadFile } from "../api/fileApi.js";

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

    filesContainer.innerHTML = "";

    // Empty state (AC-DASH-04)
    if (!files || files.length === 0) {
        const p = document.createElement("p");
        p.textContent = "No files uploaded yet. Upload one to get started.";
        filesContainer.appendChild(p);
        return;
    }

    const ul = document.createElement("ul");

    for (const f of files) {
        const li = document.createElement("li");
        li.style.marginBottom = "10px";

        const info = document.createElement("span");
        info.textContent = `${f.filename} (${f.size_bytes} bytes) - ${f.content_type}`;
        li.appendChild(info);

        // --- Download button ---
        const downloadBtn = document.createElement("button");
        downloadBtn.textContent = "Download";
        downloadBtn.style.marginLeft = "10px";
        downloadBtn.addEventListener("click", async () => {
        try {
            showMessage("Downloading...");
            downloadBtn.disabled = true;

            const { blob, filename } = await downloadFile(f.id);

            // Trigger browser download
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename || f.filename || "download";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);

            showMessage("Download started.");
        } catch (err) {
            console.error(err);
            showMessage(err.message || "Download failed.", true);
        } finally {
            downloadBtn.disabled = false;
        }
        });
        li.appendChild(downloadBtn);

        // --- Delete button ---
        const delBtn = document.createElement("button");
        delBtn.textContent = "Delete";
        delBtn.style.marginLeft = "6px";
        delBtn.addEventListener("click", async () => {
        const ok = confirm(`Delete "${f.filename}"? This cannot be undone.`);
        if (!ok) return;

        try {
            showMessage("Deleting...");
            delBtn.disabled = true;

            const res = await deleteFile(f.id);
            showMessage(res?.message || "File deleted successfully.");

            // Refresh list so file disappears (AC-FILE-03)
            await loadDashboard();
        } catch (err) {
            console.error(err);
            showMessage(err.message || "Delete failed.", true);
        } finally {
            delBtn.disabled = false;
        }
        });
        li.appendChild(delBtn);

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
