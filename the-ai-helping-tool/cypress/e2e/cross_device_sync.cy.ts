// the-ai-helping-tool/cypress/e2e/cross_device_sync.cy.ts

describe('Cross-Device Synchronization', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'Password123!'); 
    // Clear the database or specific user data before each test if possible,
    // to ensure a clean state. This typically involves a backend call.
    // cy.task('db:clearUserStudyMaterials', 'test@example.com'); // Example custom task
  });

  it('should reflect study material creation and updates across different client instances via polling', () => {
    // Scenario: User A makes a change, User B (same user, different "device"/tab) sees the update.

    // 1. Visit the dashboard in the first tab/instance
    cy.visit('/dashboard');
    cy.get('[data-testid="study-material-list"]').as('firstClientList');
    cy.get('input[type="file"]').as('firstClientFileInput');
    cy.get('button:contains("Upload Material")').as('firstClientUploadButton');

    // 2. Create a study material in the first client
    const fileName = `test_doc_${Date.now()}.txt`; // Unique filename for each test run
    cy.get('@firstClientFileInput').selectFile({
        contents: Cypress.Buffer.from('This is some test content for creation.'),
        fileName: fileName,
        mimeType: 'text/plain',
        lastModified: Date.now(),
    }, { force: true });
    cy.get('@firstClientUploadButton').click();
    cy.contains('File uploaded successfully!').should('be.visible');

    // Verify the material appears in the first client's list
    cy.get('@firstClientList').contains(fileName).should('exist');

    // 3. Open a second tab/instance (simulated by another visit in Cypress)
    cy.visit('/dashboard');
    cy.get('[data-testid="study-material-list"]').as('secondClientList');

    // Wait for the second client to poll and display the new material
    // Polling interval is 5 seconds. We should wait slightly longer to ensure poll occurs.
    cy.wait(5500); 
    cy.get('@secondClientList').contains(fileName).should('exist');

    // 4. Update the study material from the first client instance's UI (rename)
    const newFileName = `renamed_doc_${Date.now()}.txt`;
    cy.get('@firstClientList')
      .contains(fileName)
      .parents('[data-testid^="study-material-item-"]')
      .find('button[aria-label="edit"]')
      .click();

    cy.get('@firstClientList')
      .contains(fileName)
      .parents('[data-testid^="study-material-item-"]')
      .find('input[type="text"]')
      .clear()
      .type(newFileName);

    cy.get('@firstClientList')
      .contains(fileName)
      .parents('[data-testid^="study-material-item-"]')
      .find('button[aria-label="save"]')
      .click();

    cy.get('@firstClientList').contains(newFileName).should('exist');
    cy.get('@firstClientList').contains(fileName).should('not.exist');

    // 5. Verify the update is reflected in the second client instance after polling interval
    cy.wait(5500); 
    cy.get('@secondClientList').contains(newFileName).should('exist');
    cy.get('@secondClientList').contains(fileName).should('not.exist');
  });
});
