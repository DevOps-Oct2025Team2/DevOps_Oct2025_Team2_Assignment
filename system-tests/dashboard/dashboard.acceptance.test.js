const axios = require("axios");
const FormData = require("form-data");

// Allow extra time for setup hooks that create users and upload files.
jest.setTimeout(30000);

const AUTH_BASE = "http://127.0.0.1:5000/api";
const FILE_BASE = "http://127.0.0.1:5002";

async function login(username, password) {
  const res = await axios.post(`${AUTH_BASE}/login`, { username, password });
  return res.data.access_token;
}

async function adminToken() {
  return login("admin", "admin123");
}

async function createUser(adminTok, username, password) {
  await axios.post(
    `${AUTH_BASE}/admin/users`,
    { username, password, role: "user" },
    { headers: { Authorization: `Bearer ${adminTok}` } }
  );

  const list = await axios.get(`${AUTH_BASE}/admin/users`, {
    headers: { Authorization: `Bearer ${adminTok}` }
  });

  const found = list.data.find((u) => u.username === username);
  if (!found) {
    throw new Error("Created user not found in admin list");
  }
  return found;
}

async function deleteUser(adminTok, userId) {
  await axios.delete(`${AUTH_BASE}/admin/users/${userId}`, {
    headers: { Authorization: `Bearer ${adminTok}` }
  });
}

async function uploadTextFile(userTok, filename, content) {
  const form = new FormData();
  form.append("file", Buffer.from(content, "utf-8"), {
    filename,
    contentType: "text/plain"
  });

  const res = await axios.post(`${FILE_BASE}/dashboard/upload`, form, {
    headers: {
      Authorization: `Bearer ${userTok}`,
      ...form.getHeaders()
    }
  });

  return res.data.file;
}

// Dashboard acceptance tests

describe("AC-DASH-01 — Authorized Access to User Dashboard", () => {
  it("should allow authenticated non-admin user to access /dashboard", async () => {
    const token = await login("user1", "user123");
    const res = await axios.get(`${FILE_BASE}/dashboard`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    expect(res.status).toBe(200);
    expect(res.data).toBeDefined();
    expect(Array.isArray(res.data.files)).toBe(true);
  });
});

describe("AC-DASH-02 — Unauthenticated Access to User Dashboard", () => {
  it("should deny access to /dashboard when unauthenticated", async () => {
    try {
      await axios.get(`${FILE_BASE}/dashboard`);
      throw new Error("Expected unauthorized access to be denied");
    } catch (error) {
      expect(error.response.status).toBe(401);
    }
  });
});

describe("AC-DASH-03 — User Data Isolation (Server-Enforced)", () => {
  let adminTok;
  let userA;
  let userB;
  let tokenA;
  let tokenB;
  const fileAName = `dashA-${Date.now()}.txt`;
  const fileBName = `dashB-${Date.now()}.txt`;

  beforeAll(async () => {
    adminTok = await adminToken();
    userA = await createUser(adminTok, `usera_${Date.now()}`, "user123");
    userB = await createUser(adminTok, `userb_${Date.now()}`, "user123");

    tokenA = await login(userA.username, "user123");
    tokenB = await login(userB.username, "user123");

    await uploadTextFile(tokenA, fileAName, "A-content");
    await uploadTextFile(tokenB, fileBName, "B-content");
  });

  afterAll(async () => {
    await deleteUser(adminTok, userA.id);
    await deleteUser(adminTok, userB.id);
  });

  it("should only return files owned by the authenticated user", async () => {
    const resA = await axios.get(`${FILE_BASE}/dashboard`, {
      headers: { Authorization: `Bearer ${tokenA}` }
    });

    const filenamesA = resA.data.files.map((f) => f.filename);
    expect(filenamesA).toContain(fileAName);
    expect(filenamesA).not.toContain(fileBName);
  });
});

describe("AC-DASH-04 — Empty State Handling", () => {
  let adminTok;
  let emptyUser;
  let emptyToken;

  beforeAll(async () => {
    adminTok = await adminToken();
    emptyUser = await createUser(adminTok, `empty_${Date.now()}`, "user123");
    emptyToken = await login(emptyUser.username, "user123");
  });

  afterAll(async () => {
    await deleteUser(adminTok, emptyUser.id);
  });

  it("should return an empty file list for a user with no uploads", async () => {
    const res = await axios.get(`${FILE_BASE}/dashboard`, {
      headers: { Authorization: `Bearer ${emptyToken}` }
    });

    expect(res.status).toBe(200);
    expect(Array.isArray(res.data.files)).toBe(true);
    expect(res.data.files.length).toBe(0);
  });
});

// Admin acceptance tests

describe("AC-ADMIN-01 — Create User Account", () => {
  it("should allow admin to create a new user", async () => {
    const adminTok = await adminToken();
    const username = `admin_create_${Date.now()}`;

    const user = await createUser(adminTok, username, "user123");
    expect(user.username).toBe(username);

    await deleteUser(adminTok, user.id);
  });
});

describe("AC-ADMIN-02 — Delete User Account", () => {
  it("should allow admin to delete an existing user", async () => {
    const adminTok = await adminToken();
    const username = `admin_delete_${Date.now()}`;

    const user = await createUser(adminTok, username, "user123");
    await deleteUser(adminTok, user.id);

    // Verify user no longer appears in admin list
    const list = await axios.get(`${AUTH_BASE}/admin/users`, {
      headers: { Authorization: `Bearer ${adminTok}` }
    });
    const stillThere = list.data.find((u) => u.username === username);
    expect(stillThere).toBeUndefined();

    // Deleted user should not be able to log in
    try {
      await login(username, "user123");
      throw new Error("Deleted user should not authenticate");
    } catch (error) {
      expect(error.response.status).toBe(401);
    }
  });
});

describe("AC-ADMIN-03 — Admin Actions Restricted to Admin Users", () => {
  let userTok;

  beforeAll(async () => {
    userTok = await login("user1", "user123");
  });

  it("should deny non-admin user from creating accounts", async () => {
    try {
      await axios.post(
        `${AUTH_BASE}/admin/users`,
        { username: `noadmin_${Date.now()}`, password: "user123", role: "user" },
        { headers: { Authorization: `Bearer ${userTok}` } }
      );
      throw new Error("Non-admin should not create users");
    } catch (error) {
      expect(error.response.status).toBe(403);
    }
  });

  it("should deny non-admin user from deleting accounts", async () => {
    try {
      await axios.delete(`${AUTH_BASE}/admin/users/1`, {
        headers: { Authorization: `Bearer ${userTok}` }
      });
      throw new Error("Non-admin should not delete users");
    } catch (error) {
      expect(error.response.status).toBe(403);
    }
  });
});

// File management acceptance tests

describe("AC-FILE-01 — Upload File", () => {
  it("should upload a valid file and show it in dashboard", async () => {
    const token = await login("user1", "user123");
    const filename = `upload_${Date.now()}.txt`;

    const file = await uploadTextFile(token, filename, "hello world");
    expect(file.filename).toBe(filename);

    const res = await axios.get(`${FILE_BASE}/dashboard`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const filenames = res.data.files.map((f) => f.filename);
    expect(filenames).toContain(filename);
  });
});

describe("AC-FILE-02 — File Upload Validation Enforcement", () => {
  it("should reject invalid file types", async () => {
    const token = await login("user1", "user123");
    const form = new FormData();
    form.append("file", Buffer.from("{}", "utf-8"), {
      filename: `bad_${Date.now()}.json`,
      contentType: "application/json"
    });

    try {
      await axios.post(`${FILE_BASE}/dashboard/upload`, form, {
        headers: {
          Authorization: `Bearer ${token}`,
          ...form.getHeaders()
        }
      });
      throw new Error("Invalid upload should be rejected");
    } catch (error) {
      expect(error.response.status).toBe(400);
    }
  });
});

describe("AC-FILE-03 — Download Own File", () => {
  it("should allow a user to download their own file", async () => {
    const token = await login("user1", "user123");
    const filename = `download_${Date.now()}.txt`;
    const content = "download-content";

    const file = await uploadTextFile(token, filename, content);

    const res = await axios.get(`${FILE_BASE}/dashboard/download/${file.id}`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: "arraybuffer"
    });

    expect(res.status).toBe(200);
    const body = Buffer.from(res.data).toString("utf-8");
    expect(body).toBe(content);
  });
});

describe("AC-FILE-04 — Delete Own File", () => {
  it("should allow a user to delete their own file", async () => {
    const token = await login("user1", "user123");
    const filename = `delete_${Date.now()}.txt`;

    const file = await uploadTextFile(token, filename, "to-delete");

    const delRes = await axios.post(`${FILE_BASE}/dashboard/delete/${file.id}`, null, {
      headers: { Authorization: `Bearer ${token}` }
    });
    expect(delRes.status).toBe(200);

    try {
      await axios.get(`${FILE_BASE}/dashboard/download/${file.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      throw new Error("Deleted file should not be downloadable");
    } catch (error) {
      expect([403, 404]).toContain(error.response.status);
    }
  });
});

describe("AC-FILE-05 — Prevent Access to Other Users’ Files", () => {
  let adminTok;
  let userA;
  let userB;
  let tokenA;
  let tokenB;
  let foreignFile;

  beforeAll(async () => {
    adminTok = await adminToken();
    userA = await createUser(adminTok, `owner_${Date.now()}`, "user123");
    userB = await createUser(adminTok, `intruder_${Date.now()}`, "user123");

    tokenA = await login(userA.username, "user123");
    tokenB = await login(userB.username, "user123");

    foreignFile = await uploadTextFile(tokenA, `owner_${Date.now()}.txt`, "secret");
  });

  afterAll(async () => {
    await deleteUser(adminTok, userA.id);
    await deleteUser(adminTok, userB.id);
  });

  it("should deny access to files owned by another user", async () => {
    try {
      await axios.get(`${FILE_BASE}/dashboard/download/${foreignFile.id}`, {
        headers: { Authorization: `Bearer ${tokenB}` }
      });
      throw new Error("Cross-user file access should be denied");
    } catch (error) {
      expect([403, 404]).toContain(error.response.status);
    }
  });
});
