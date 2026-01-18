const axios = require("axios");

// Test case for successful login ( AC-LOGIN-01 )
describe("AC-LOGIN-01 — Successful Login", () => {
  it("should authenticate user and return JWT token and role", async () => {
    const response = await axios.post(
      "http://127.0.0.1:5000/api/login", // auth-service port
      {
        username: "user1",
        password: "user123"
      }
    );

    // HTTP success
    expect(response.status).toBe(200);

    // Token checks
    expect(response.data).toBeDefined();
    expect(response.data.access_token).toBeDefined();
    expect(response.data.token_type).toBe("Bearer");

    // Role-based logic
    expect(["admin", "user"]).toContain(response.data.role);
  });
});
