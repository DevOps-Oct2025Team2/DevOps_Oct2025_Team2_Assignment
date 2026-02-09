async function logout() {
  const token = localStorage.getItem("access_token");

  try {
    await fetch("http://127.0.0.1:5000/api/logout", {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
  } catch (error) {
    console.error("Logout error:", error);
  } finally {
    localStorage.removeItem("access_token");
    window.location.href = "/api/login";
  }
}
