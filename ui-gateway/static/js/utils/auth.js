export function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

export function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  if (!token) return {};
  return {
    "Authorization": "Bearer " + token
  };
}
