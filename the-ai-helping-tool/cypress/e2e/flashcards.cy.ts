// the-ai-helping-tool/cypress/e2e/flashcards.cy.ts

describe('Flashcards Page', () => {
  beforeEach(() => {
    // Intercept the flashcard API call
    cy.intercept('POST', '/api/v1/study-materials/flashcards', {
      statusCode: 200,
      body: {
        flashcards: [
          { question: 'What is Cypress?', answer: 'A frontend testing tool.' },
          { question: 'What is an intercept?', answer: 'Cypress command to mock network requests.' },
        ],
      },
    }).as('postFlashcards');

    // Visit the flashcards page
    cy.visit('/flashcards');
  });

  it('should display the title and input elements', () => {
    cy.contains('h1', 'Flashcard Generator').should('be.visible');
    cy.get('textarea[placeholder="Paste your study material here..."]').should('be.visible');
    cy.contains('button', 'Generate Flashcards').should('be.visible');
  });

  it('should allow user to input text and generate flashcards', () => {
    const inputText = 'Cypress is a great tool for testing web applications. It allows you to intercept network requests.';
    cy.get('textarea[placeholder="Paste your study material here..."]').type(inputText);

    cy.contains('button', 'Generate Flashcards').click();

    // Wait for the API call to complete
    cy.wait('@postFlashcards').its('request.body').should('deep.equal', {
      text: inputText,
    });

    // Check if the flashcards are displayed
    cy.contains('h2', 'Generated Flashcards').should('be.visible');
    cy.contains('p', 'What is Cypress?').should('be.visible');
    cy.contains('p', 'A frontend testing tool.').should('be.visible');
    cy.contains('p', 'What is an intercept?').should('be.visible');
    cy.contains('p', 'Cypress command to mock network requests.').should('be.visible');
  });

  it('should show loading state during flashcard generation', () => {
    cy.intercept('POST', '/api/v1/study-materials/flashcards', (req) => {
      req.reply({
        delay: 500, // Simulate network delay
        body: {
          flashcards: [{ question: 'Delayed Q', answer: 'Delayed A' }],
        },
      });
    }).as('postFlashcardsDelayed');

    cy.get('textarea[placeholder="Paste your study material here..."]').type('Text to generate flashcards with delay.');
    cy.contains('button', 'Generate Flashcards').click();

    cy.contains('button', 'Generating Flashcards...').should('be.visible').and('be.disabled');
    cy.wait('@postFlashcardsDelayed');
    cy.contains('button', 'Generate Flashcards').should('be.visible').and('not.be.disabled');
    cy.contains('p', 'Delayed Q').should('be.visible');
  });

  it('should display an error message if flashcard generation fails', () => {
    cy.intercept('POST', '/api/v1/study-materials/flashcards', {
      statusCode: 500,
      body: { detail: 'Internal Server Error' },
    }).as('postFlashcardsError');

    cy.get('textarea[placeholder="Paste your study material here..."]').type('Text that will cause an error.');
    cy.contains('button', 'Generate Flashcards').click();

    cy.wait('@postFlashcardsError');
    cy.contains('p', 'Error: Internal Server Error').should('be.visible');
    cy.contains('h2', 'Generated Flashcards').should('not.exist');
  });
});
