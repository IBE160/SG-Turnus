// the-ai-helping-tool/cypress/e2e/summarize.cy.ts

describe('Summarize Page', () => {
  beforeEach(() => {
    // Intercept the summarization API call
    cy.intercept('POST', '/api/v1/study-materials/summarize', {
      statusCode: 200,
      body: { summary: 'This is a mocked summary for your text.' },
    }).as('postSummarize');

    // Visit the summarize page
    cy.visit('/summarize');
  });

  it('should display the title and input elements', () => {
    cy.contains('h1', 'Text Summarizer').should('be.visible');
    cy.get('textarea[placeholder="Paste your text here..."]').should('be.visible');
    cy.get('select#detailLevel').should('be.visible');
    cy.contains('button', 'Generate Summary').should('be.visible');
  });

  it('should allow user to input text and generate a summary', () => {
    const inputText = 'This is a test article that needs to be summarized. It contains several sentences and should produce a concise summary.';
    cy.get('textarea[placeholder="Paste your text here..."]').type(inputText);

    cy.get('select#detailLevel').select('normal'); // Ensure normal is selected

    cy.contains('button', 'Generate Summary').click();

    // Wait for the API call to complete
    cy.wait('@postSummarize').its('request.body').should('deep.equal', {
      text: inputText,
      detail_level: 'normal',
    });

    // Check if the summary is displayed
    cy.contains('h2', 'Summary').should('be.visible');
    cy.contains('p', 'This is a mocked summary for your text.').should('be.visible');
  });

  it('should display a brief summary when "Brief" detail level is selected', () => {
    const inputText = 'This is another test article for a brief summary. It should be even shorter.';
    cy.get('textarea[placeholder="Paste your text here..."]').type(inputText);

    cy.get('select#detailLevel').select('brief');

    cy.contains('button', 'Generate Summary').click();

    cy.wait('@postSummarize').its('request.body').should('deep.equal', {
      text: inputText,
      detail_level: 'brief',
    });

    cy.contains('h2', 'Summary').should('be.visible');
    cy.contains('p', 'This is a mocked summary for your text.').should('be.visible');
  });

  it('should show loading state during summarization', () => {
    cy.intercept('POST', '/api/v1/study-materials/summarize', (req) => {
      req.reply({
        delay: 500, // Simulate network delay
        body: { summary: 'Delayed summary.' },
      });
    }).as('postSummarizeDelayed');

    cy.get('textarea[placeholder="Paste your text here..."]').type('Text to summarize with delay.');
    cy.contains('button', 'Generate Summary').click();

    cy.contains('button', 'Summarizing...').should('be.visible').and('be.disabled');
    cy.wait('@postSummarizeDelayed');
    cy.contains('button', 'Generate Summary').should('be.visible').and('not.be.disabled');
    cy.contains('p', 'Delayed summary.').should('be.visible');
  });

  it('should display an error message if summarization fails', () => {
    cy.intercept('POST', '/api/v1/study-materials/summarize', {
      statusCode: 500,
      body: { detail: 'Internal Server Error' },
    }).as('postSummarizeError');

    cy.get('textarea[placeholder="Paste your text here..."]').type('Text that will cause an error.');
    cy.contains('button', 'Generate Summary').click();

    cy.wait('@postSummarizeError');
    cy.contains('p', 'Error: Internal Server Error').should('be.visible');
    cy.contains('h2', 'Summary').should('not.exist');
  });
});
