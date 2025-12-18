// cypress/support/commands.ts
Cypress.Commands.add('login', (email, password) => {
  cy.request('POST', '/api/auth/login', { email, password })
    .its('body')
    .then((body) => {
      window.localStorage.setItem('token', body.access_token);
    });
});
