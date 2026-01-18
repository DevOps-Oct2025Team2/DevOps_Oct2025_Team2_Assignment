document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const errorText = document.getElementById("error");


  if (!form) {
    console.error("Login form not found (check form id)");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorText.textContent = "";

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
      errorText.textContent = "Username and password are required";
      return;
    }

    if (username.length < 3 || password.length < 6) {
      errorText.textContent = "Invalid username or password format";
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        errorText.textContent = data.message || "Login failed";
        return;
      }


      localStorage.setItem("access_token", data.access_token);

      if (data.role === "admin") {
        window.location.href = "/admin";
      } else {
        window.location.href = "/dashboard";
      }

    } catch (error) {
      console.error("Login error:", error);
      errorText.textContent = "Server error. Please try again.";
    }
  });
});


