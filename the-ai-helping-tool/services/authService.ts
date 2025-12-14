export const registerUser = async (email: string, password: string) => {
  console.log('Registering user with', { email, password });
  const response = await fetch('/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Registration failed');
  }
  return response.json();
};

export const loginUser = async (email: string, password: string) => {
  console.log('Logging in user with', { email });
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Login failed');
  }
  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
  }
  return data;
};

export const getToken = (): string | null => {
  return typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
};

export const logoutUser = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    // Optionally redirect to login page after logout
    window.location.href = '/login';
  }
};

const REFRESH_TOKEN_URL = '/api/v1/auth/refresh'; // Assuming this endpoint exists

const refreshToken = async (): Promise<string | null> => {
  try {
    const response = await fetch(REFRESH_TOKEN_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    }
    return null;
  } catch (error) {
    console.error('Error refreshing token:', error);
    // Redirect to login if refresh fails
    logoutUser();
    return null;
  }
};

interface AuthenticatedFetchOptions extends RequestInit {
  includeAuth?: boolean;
}

export const authenticatedFetch = async (
  input: RequestInfo | URL,
  options: AuthenticatedFetchOptions = {}
): Promise<Response> => {
  const { includeAuth = true, ...rest } = options;
  let headers = new Headers(rest.headers);

  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    } else {
      console.warn("Attempted authenticated fetch without a token.");
      // If no token is present, we cannot proceed with an authenticated request
      // and should ideally redirect to login or throw an error.
      // For now, let's just make sure headers are set up correctly for the first attempt.
    }
  }

  // First attempt
  let response = await fetch(input, { ...rest, headers });

  if (response.status === 401 && includeAuth) {
    console.log("Token expired or unauthorized, attempting to refresh...");
    const newToken = await refreshToken();
    if (newToken) {
      console.log("Token refreshed successfully, retrying original request.");
      headers = new Headers(rest.headers); // Recreate headers to ensure no stale Authorization header
      headers.set('Authorization', `Bearer ${newToken}`);
      response = await fetch(input, { ...rest, headers }); // Retry with new token
    } else {
      console.error("Failed to refresh token, redirecting to login.");
      // refreshToken already calls logoutUser which redirects, so no need to do it again here.
    }
  }

  return response;
};
