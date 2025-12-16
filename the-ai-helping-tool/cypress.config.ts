import { defineConfig } from "cypress";
import axios from 'axios';

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', {
        async getUserVerificationStatus(email: string) {
          try {
            const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'; // Adjust as per your backend URL
            const response = await axios.get(`${backendUrl}/api/v1/test/user-verification-status/${email}`);
            return response.data.is_verified;
          } catch (error) {
            console.error(`Error fetching user verification status for ${email}:`, error);
            return null;
          }
        },
      });
      return config;
    },
  },
});
