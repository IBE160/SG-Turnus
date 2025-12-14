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
    // window.location.href = '/login';
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
  const headers = new Headers(rest.headers);

  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    } else {
      // Handle cases where token is required but not present (e.g., redirect to login)
      // For now, we'll proceed without the token, and the backend should reject if necessary
      console.warn("Attempted authenticated fetch without a token.");
    }
  }

  return fetch(input, {
    ...rest,
    headers,
  });
};
