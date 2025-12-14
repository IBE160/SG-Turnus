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

  it('should successfully register a new user and complete email verification', () => {
    // Generate a unique email for this test run
    const email = `test-${Date.now()}@example.com`;
    const password = 'Password123!';

    // Intercept the registration request
    cy.intercept('POST', '/api/v1/auth/register').as('registerUser');
    // Intercept the email verification request
    cy.intercept('POST', '/api/v1/auth/verify-email').as('verifyEmail');

    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();

    // Verify frontend message
    cy.contains('Thank you for signing up. Please check your email for a verification link.').should('be.visible');

    // Wait for the registration request to complete and inspect it
    cy.wait('@registerUser').then((interception) => {
      expect(interception.request.body.email).to.equal(email);
      expect(interception.request.body.password).to.equal(password);
      expect(interception.response.statusCode).to.equal(201);
      
      // Extract verification link from the backend's email service log (this would be ideal but hard in E2E)
      // For now, we assume the link structure and simulate clicking it.
      // In a real scenario, you'd have a test utility to fetch the actual verification token/link.
      const verificationToken = 'mock_verification_token'; // Backend currently uses a mock UUID, we'll use a consistent one for test
      const verificationLink = `http://localhost:3000/verify-email?email=${email}&token=${verificationToken}`;
      
      cy.visit(verificationLink); // Simulate user clicking the link
      
      // We should see a success message on the verification page (assuming such a page exists)
      cy.contains('Email verified successfully.').should('be.visible');
      
      // Now, assert that the verify-email endpoint was called
      cy.wait('@verifyEmail').then((verifyInterception) => {
        expect(verifyInterception.request.body.email).to.equal(email);
        expect(verifyInterception.request.body.token).to.equal(verificationToken);
        expect(verifyInterception.response.statusCode).to.equal(200);
      });
    });
  });

  it('should show an error if registration fails (e.g., duplicate email)', () => {
    // Intercept the registration request to mock a duplicate user error
    cy.intercept('POST', '/api/v1/auth/register', {
      statusCode: 409,
      body: { detail: 'User with this email already exists' },
    }).as('duplicateRegister');

    const email = `duplicate-test-${Date.now()}@example.com`;
    const password = 'Password123!';

    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();

    cy.wait('@duplicateRegister'); // Wait for the mocked request
    cy.contains('User with this email already exists').should('be.visible');
  });

  it('should show client-side password validation errors', () => {
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('short');
    cy.get('button[type="submit"]').click(); // Click to trigger validation

    cy.contains('Password must be at least 8 characters long.').should('be.visible');

    cy.get('input[type="password"]').clear().type('password123'); // Missing uppercase
    cy.contains('Password must contain at least one uppercase letter.').should('be.visible');

    cy.get('input[type="password"]').clear().type('PASSWORD123'); // Missing lowercase
    cy.contains('Password must contain at least one lowercase letter.').should('be.visible');

    cy.get('input[type="password"]').clear().type('Password'); // Missing number
    cy.contains('Password must contain at least one number.').should('be.visible');

    cy.get('input[type="password"]').clear().type('Password123'); // Missing special character
    cy.contains('Password must contain at least one special character').should('be.visible');

    // With a valid password, the error should disappear
    cy.get('input[type="password"]').clear().type('Password123!');
    cy.contains('Password must be at least 8 characters long.').should('not.exist');
    cy.contains('Password must contain at least one uppercase letter.').should('not.exist');
    cy.contains('Password must contain at least one lowercase letter.').should('not.exist');
    cy.contains('Password must contain at least one number.').should('not.exist');
    cy.contains('Password must contain at least one special character').should('not.exist');
  });
});
