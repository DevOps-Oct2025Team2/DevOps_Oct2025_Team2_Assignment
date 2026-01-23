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

loadUsers();

