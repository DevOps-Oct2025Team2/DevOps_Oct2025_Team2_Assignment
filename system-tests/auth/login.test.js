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

// Test case for failed login ( AC-LOGIN-02 )
describe("AC-LOGIN-02 — Failed Login (Invalid Credentials)", () => {
  it("should reject authentication and not issue any token", async () => {
    try {
      await axios.post(
        "http://127.0.0.1:5000/api/login", // auth-service port
        {
          username: "user1",
          password: "wrongpassword"
        }
      );

      // If request succeeds, this is a FAIL
      throw new Error("Authentication should have failed but succeeded");

    } catch (error) {
      // Axios throws for non-2xx responses
      const response = error.response;

      // HTTP failure expected
      expect(response.status).toBe(401); // or 400 depending on backend design

      // No token should be issued
      expect(response.data.access_token).toBeUndefined();

      // Error message should be present
      expect(response.data).toBeDefined();
      expect(response.data.message || response.data.error).toBeDefined();
    }
  });
});

// Test case for input validation ( AC-LOGIN-03 )
describe("AC-LOGIN-03 — Input Validation", () => {

  it("should reject login when username and password are empty", async () => {
    try {
      await axios.post(
        "http://127.0.0.1:5000/api/login",
        {
          username: "",
          password: ""
        }
      );

      // If backend accepts this, it's a FAIL
      throw new Error("Login should not proceed with empty credentials");

    } catch (error) {
      const response = error.response;

      // Expect validation failure
      expect(response.status).toBe(400); 
      // Ensure no token is issued
      expect(response.data.access_token).toBeUndefined();

      // Validation error message should be present
      expect(response.data.message || response.data.error).toBeDefined();
    }
  });

  it("should reject login when inputs do not meet format constraints", async () => {
    try {
      await axios.post(
        "http://127.0.0.1:5000/api/login",
        {
          username: "!!@@##",
          password: "123"
        }
      );

      throw new Error("Login should not proceed with invalid input format");

    } catch (error) {
      const response = error.response;

      expect(response.status).toBe(401);
      expect(response.data.access_token).toBeUndefined();
      expect(response.data.message || response.data.error).toBeDefined();
    }
  });

});

// Test case for unauthenticated access to protected routes ( AC-AUTH-01 )
describe("AC-LOGIN-04 — Unauthenticated Access to Protected Routes", () => {

  it("should deny access to /api/profile when user is unauthenticated", async () => {
    try {
      await axios.get(
        "http://127.0.0.1:5000/api/profile"
      );

      throw new Error("Access to /api/profile should be denied for unauthenticated users");

    } catch (error) {
      const response = error.response;

      // Access must be denied
      expect([401, 403]).toContain(response.status);

      // No protected data should be returned
      expect(response.data).toBeDefined();
    }
  });

  it("should deny access to /api/admin when user is unauthenticated", async () => {
    try {
      await axios.get(
        "http://127.0.0.1:5000/api/admin"
      );

      throw new Error("Access to /api/admin should be denied for unauthenticated users");

    } catch (error) {
      const response = error.response;

      // Access must be denied
      expect([401, 403]).toContain(response.status);

      // No protected data should be returned
      expect(response.data).toBeDefined();
    }
  });

});

// Test case for unauthorized access by authenticated non-admin user ( AC-AUTH-02 )
describe("AC-LOGIN-05 — Unauthorized Access by Authenticated Non-Admin User", () => {

  let userToken;

  // Step 1: Login as non-admin user
  beforeAll(async () => {
    const loginResponse = await axios.post(
      "http://127.0.0.1:5000/api/login",
      {
        username: "user1",      // non-admin user
        password: "user123"
      }
    );

    userToken = loginResponse.data.access_token;
  });

  it("should deny access to /admin for authenticated non-admin user", async () => {
    try {
      await axios.get(
        "http://127.0.0.1:5000/api/admin",
        {
          headers: {
            Authorization: `Bearer ${userToken}`
          }
        }
      );

      throw new Error("Non-admin user should not be able to access /admin");

    } catch (error) {
      const response = error.response;

      // Must be forbidden
      expect(response.status).toBe(403);

      // No admin content should be returned
      expect(response.data).toBeDefined();
    }
  });

});
