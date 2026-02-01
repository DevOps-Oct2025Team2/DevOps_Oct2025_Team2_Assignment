const token = localStorage.getItem("access_token");

if (!token) {
  alert("Unauthorized");
  window.location.href = "/api/login";
}

function loadUsers() {
  fetch("http://localhost:5000/api/admin/users", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
    .then(res => {
      if (!res.ok) throw new Error("Failed to fetch users");
      return res.json();
    })
    .then(users => {
      const table = document.getElementById("usersTable");
      table.innerHTML = "";

      users
        .filter(u => u.role === "user") 
        .forEach(user => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${user.username}</td>
            <td>
              <button class="danger-btn" onclick="deleteUser(${user.id})">
                Delete
              </button>
            </td>
          `;
          table.appendChild(row);
        });
    })
    .catch(err => {
      console.error(err);
      alert("Error loading users");
    });
}

function addUser() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    alert("Username and password are required");
    return;
  }

  if (username.length < 3) {
    alert("Username must be at least 3 characters");
    return;
  }

 // Strong password rule
  const strongPasswordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

  if (!strongPasswordRegex.test(password)) {
    alert(
      "Password must be at least 8 characters and include:\n" +
      "- Uppercase letter\n" +
      "- Lowercase letter\n" +
      "- Number\n" +
      "- Special character"
    );
    return;
  }

  fetch("http://localhost:5000/api/admin/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      username,
      password
    })
  })
    .then(res => {
      if (!res.ok) throw new Error("Failed to create user");
      return res.json();
    })
    .then(() => {
      document.getElementById("username").value = "";
      document.getElementById("password").value = "";
      loadUsers(); // refresh table
    })
    .catch(err => {
      console.error(err);
      alert("Error creating user");
    });
}

function deleteUser(id) {
  if (!confirm("Are you sure you want to delete this user?")) return;

  fetch(`http://localhost:5000/api/admin/users/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
    .then(res => {
      if (!res.ok) throw new Error("Delete failed");
      loadUsers();
    })
    .catch(err => {
      console.error(err);
      alert("Error deleting user");
    });
}

loadUsers();

