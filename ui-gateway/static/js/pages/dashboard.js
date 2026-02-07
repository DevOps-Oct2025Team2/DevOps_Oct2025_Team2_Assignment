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
const refreshBtn = document.getElementById("refreshBtn");
if (refreshBtn) refreshBtn.addEventListener("click", loadDashboard);
const confirmModal = document.getElementById("confirmModal");
const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
console.log("confirmModal:", confirmModal);
console.log("cancelDeleteBtn:", cancelDeleteBtn);
console.log("confirmDeleteBtn:", confirmDeleteBtn);

let pendingDelete = null; // will hold { file, deleteBtn }

function openDeleteModal(file, deleteBtn) {
    console.log("openDeleteModal called for:", file.filename);
  pendingDelete = { file, deleteBtn };

  const modalSub = document.getElementById("modalSub");
  if (modalSub) modalSub.textContent = `Delete "${file.filename}"? This action cannot be undone.`;

  confirmModal?.classList.add("show");
  confirmModal?.setAttribute("aria-hidden", "false");
  cancelDeleteBtn?.focus();
}

function closeDeleteModal() {
  confirmModal?.classList.remove("show");
  confirmModal?.setAttribute("aria-hidden", "true");
  pendingDelete = null;
}

// Small helper: show a message to the user
function showMessage(text, isError = false) {
  if (!msgBox) return;

  msgBox.textContent = text;
  msgBox.classList.add("show");
  msgBox.classList.toggle("error", isError);
  msgBox.classList.toggle("success", !isError);
}

function formatBytes(bytes) {
  if (typeof bytes !== "number") return "";
  const units = ["B", "KB", "MB", "GB"];
  let n = bytes;
  let i = 0;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i++;
  }
  return `${n.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatDate(iso) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return d.toLocaleDateString();
}

function renderFiles(files) {
  if (!filesContainer) return;
  filesContainer.innerHTML = "";

  if (!files || files.length === 0) {
    filesContainer.className = "";
    const empty = document.createElement("div");
    empty.className = "empty";

    empty.innerHTML = `
        <div class="empty-icon" aria-hidden="true">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 16v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8.5 12.5L12 9l3.5 3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6 19h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        </div>
        <div class="empty-title">No files uploaded yet</div>
        <div class="empty-sub">
        Upload documents, images, or other files to store them securely in your isolated vault.
        </div>
    `;

    filesContainer.appendChild(empty);
    return;
  }

  filesContainer.className = "file-grid";

  for (const f of files) {
    const card = document.createElement("div");
    card.className = "file-card";

    const created = formatDate(f.created_at || f.uploaded_at || f.createdAt);

    card.innerHTML = `
        <div class="file-card-inner">
        <div class="file-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-6z"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 2v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>

        <div class="file-main">
            <div class="file-name" title="${f.filename}">${f.filename}</div>
            <div class="pills">
            <span class="pill">${formatBytes(f.size_bytes)}</span>
            ${created ? `<span class="pill">${created}</span>` : ``}
            </div>
        </div>

        <div class="file-actions">
            <button class="action-icon" title="Download" type="button" data-action="download">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 3v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M8 11l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4 21h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            </button>

            <button class="action-icon" title="Delete" type="button" data-action="delete">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M3 6h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M8 6V4h8v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            </button>
        </div>
        </div>

        <div class="file-footer">
        <span class="owner-dot" aria-hidden="true"></span>
        OWNER: ${(f.owner_username || f.owner || "YOU").toString().toUpperCase()}
        </div>
    `;

    // wire actions
    const downloadBtn = card.querySelector('[data-action="download"]');
    const deleteBtn = card.querySelector('[data-action="delete"]');

    downloadBtn.addEventListener("click", async () => {
        try {
        showMessage("Downloading...");
        downloadBtn.disabled = true;

        const { blob, filename } = await downloadFile(f.id);
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

    deleteBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openDeleteModal(f, deleteBtn);
    });

    filesContainer.appendChild(card);
  }
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
if (uploadBtn && fileInput) {
  uploadBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleUpload); // auto upload
}

cancelDeleteBtn?.addEventListener("click", closeDeleteModal);
    confirmModal?.addEventListener("click", (e) => {
        if (e.target === confirmModal) closeDeleteModal(); // click outside closes
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeDeleteModal();
});

confirmDeleteBtn?.addEventListener("click", async () => {
  if (!pendingDelete) return;

  const { file, deleteBtn } = pendingDelete;

  try {
    showMessage("Deleting...");
    confirmDeleteBtn.disabled = true;
    if (deleteBtn) deleteBtn.disabled = true;

    const res = await deleteFile(file.id);
    showMessage(res?.message || "File deleted successfully.");

    closeDeleteModal();
    await loadDashboard();
  } catch (err) {
    console.error(err);
    showMessage(err.message || "Delete failed.", true);
  } finally {
    confirmDeleteBtn.disabled = false;
    if (deleteBtn) deleteBtn.disabled = false;
  }
});
// Run on page load
loadDashboard();