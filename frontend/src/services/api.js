/**
 * This file handles all communication with our backend API.
 * Think of it as the messenger between the frontend and backend.
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Sends your calculation request to the backend and gets the results.
 * 
 * @param {Object} data - What you want to calculate
 * @param {number} data.principal - Starting amount
 * @param {number} data.rate - Interest rate as a percentage
 * @param {number} data.time - Number of years
 * @returns {Promise<Object>} Your calculated interest amounts
 * @throws {Error} If something goes wrong (like backend is down)
 */
export const calculateInterest = async (data) => {
  try {
    const response = await fetch(`${API_URL}/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || 
        errorData.detail || 
        `Server error: ${response.status}`
      );
    }

    const result = await response.json();
    return result;
  } catch (error) {
    if (error.message.includes('Failed to fetch')) {
      throw new Error(
        'Unable to connect to server. Please ensure the backend is running.'
      );
    }
    throw error;
  }
};

/**
 * Pings the backend to see if it's alive and well.
 * 
 * @returns {Promise<Object>} Health status info
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    throw new Error('Unable to connect to backend');
  }
};

/**
 * Asks the backend to check if the Google Sheet is set up correctly.
 * 
 * @returns {Promise<Object>} Whether everything looks good or not
 */
export const verifySheet = async () => {
  try {
    const response = await fetch(`${API_URL}/verify`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Verification failed');
    }
    return await response.json();
  } catch (error) {
    throw error;
  }
};
