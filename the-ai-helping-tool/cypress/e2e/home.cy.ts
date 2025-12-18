describe('Homepage and WebSocket Tester', () => {
  it('should load the homepage and display the WebSocket Tester', () => {
    cy.visit('http://localhost:3000'); // Assuming your Next.js app runs on port 3000

    cy.contains('Welcome to The AI Helping Tool').should('be.visible');
    cy.contains('WebSocket Tester').should('be.visible');
    cy.contains('Connection Status:').should('be.visible');
  });
});
