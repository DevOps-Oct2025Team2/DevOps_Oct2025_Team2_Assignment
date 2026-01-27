function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/api/login";
}
