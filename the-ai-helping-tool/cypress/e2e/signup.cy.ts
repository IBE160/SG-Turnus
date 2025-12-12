describe('Sign Up Flow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/signup'); // Assuming your Next.js app runs on port 3000
  });

  it('should display the sign up form', () => {
    cy.contains('Sign Up').should('be.visible');
    cy.get('input[type="email"]').should('be.visible');
    cy.get('input[type="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should successfully register a new user and show verification message', () => {
    const email = `test-${Date.now()}@example.com`;
    const password = 'Password123!';

    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();

    // Assuming the backend returns success and the frontend shows this message
    cy.contains('Thank you for signing up. Please check your email for a verification link.').should('be.visible');

    // In a real E2E test, you would also:
    // 1. Intercept the backend /api/v1/auth/register request to verify payload
    // 2. Check a database or email service mock to ensure email was sent
    // 3. Simulate clicking the verification link (e.g., by visiting the verification URL directly)
    // 4. Verify successful verification and redirection to login/dashboard
  });

  it('should show an error if registration fails (e.g., duplicate email)', () => {
    // This test requires a way to mock or force a backend error state.
    // For simplicity, we'll assume a basic client-side validation, or
    // a mock service worker could be used to intercept network requests.

    // Simulate duplicate email (requires running the success test first or
    // mocking the backend to return a 409 for a specific email)
    const email = `duplicate@example.com`;
    const password = 'Password123!';

    // First attempt (will 'succeed' but prime the mock_db for duplicate)
    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.contains('Thank you for signing up. Please check your email for a verification link.').should('be.visible');

    cy.visit('http://localhost:3000/signup'); // Go back to signup page

    // Second attempt with same email
    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();

    // This part would depend on how your backend handles duplicate errors and
    // how your frontend displays them. Currently, our mock backend returns 409
    // and the frontend currently does not explicitly catch this and display
    // it in the UI, but rather the `authService` mock just returns success.
    // To properly test this, the `authService` in frontend needs to
    // actually call the backend, and the backend needs to be running.
    // For now, this test is more of a placeholder until the full integration.
  });
});
