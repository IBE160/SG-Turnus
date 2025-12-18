import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// --- Frontend Interfaces corresponding to Backend Schemas ---

export enum Permissions {
  VIEW_ONLY = "view_only",
  EDIT = "edit",
}

export interface ShareCreateRequest {
  study_material_id: number;
  shared_with_email?: string;
  permissions?: Permissions;
  expires_at?: string; // ISO 8601 string
}

export interface SharedMaterialResponse {
  id: number;
  study_material_id: number;
  file_name: string;
  s3_key: string;
  shared_by_user_id: number;
  shared_with_user_id?: number;
  share_token?: string;
  permissions: Permissions;
  created_at: string; // ISO 8601 string
  expires_at?: string; // ISO 8601 string
}

export interface SharedLinkResponse {
  share_token: string;
  full_share_url: string;
  permissions: Permissions;
  expires_at?: string; // ISO 8601 string
}

// --- API Service Functions ---

const sharingService = {
  /**
   * Creates a new share entry for a study material.
   * Can be a direct share with a user or generate a shareable link.
   */
  createShare: async (shareData: ShareCreateRequest, token: string): Promise<SharedMaterialResponse> => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/sharing/share`,
        shareData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating share:', error);
      throw error;
    }
  },

  /**
   * Allows access to a shared material via a public share token.
   * No authentication required for this endpoint.
   */
  getSharedMaterialByToken: async (shareToken: string): Promise<SharedMaterialResponse> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/sharing/material/${shareToken}`);
      return response.data;
    } catch (error) {
      console.error('Error getting shared material by token:', error);
      throw error;
    }
  },

  /**
   * Retrieves a list of study materials shared by the current user.
   */
  getMyShares: async (token: string): Promise<SharedMaterialResponse[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/sharing/my-shares`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error getting my shares:', error);
      throw error;
    }
  },

  /**
   * Retrieves a list of study materials shared with the current user.
   */
  getSharedWithMe: async (token: string): Promise<SharedMaterialResponse[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/sharing/shared-with-me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error getting shared with me materials:', error);
      throw error;
    }
  },

  /**
   * Revokes a specific share.
   */
  revokeShare: async (shareId: number, token: string): Promise<void> => {
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/sharing/${shareId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Error revoking share:', error);
      throw error;
    }
  },
};

export default sharingService;
