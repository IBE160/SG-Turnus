describe('SEO Elements on Landing Page', () => {
  beforeEach(() => {
    cy.visit('/'); // Assuming the landing page is at the root URL
  });

  it('should have the correct title tag', () => {
    cy.title().should('eq', 'The AI Helping Tool');
  });

  it('should have a descriptive meta description', () => {
    cy.get('head meta[name="description"]')
      .should('have.attr', 'content', 'An AI-powered tool to help you learn and study more effectively.');
  });

  it('should have a main heading (h1)', () => {
    cy.get('h1').should('contain', 'Welcome to The AI Helping Tool');
  });

  it('should have a subheading (h2)', () => {
    cy.get('h2').should('contain', 'Your Smart Companion for Learning and Productivity');
  });
});