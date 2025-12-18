import { API_BASE_URL } from './api';

export type Permissions = 'view' | 'edit';

export const generateShareLink = async (
  token: string,
  studyMaterialId: number,
  permissions: Permissions
): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/sharing/generate-link`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      study_material_id: studyMaterialId,
      permissions,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate share link.');
  }

  const data = await response.json();
  return data.share_token;
};

export const shareWithUser = async (
  token: string,
  studyMaterialId: number,
  email: string,
  permissions: Permissions
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/sharing/share-with-user`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      study_material_id: studyMaterialId,
      target_user_email: email,
      permissions,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to share with user.');
  }
};

export const getSharedMaterial = async (shareToken: string, token?: string): Promise<any> => {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/sharing/shared/${shareToken}`, {
        method: 'GET',
        headers,
    });

    if (!response.ok) {
        throw new Error('Failed to retrieve shared material.');
    }

    return response.json();
};