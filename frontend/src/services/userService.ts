/**
 * Service for handling user-related API calls
 */
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences?: Record<string, any>;
}

/**
 * Fetches the current user's profile
 * @returns Promise with user profile data
 */
export async function fetchUserProfile(): Promise<UserProfile> {
  const response = await fetch('/api/user/profile');
  
  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }
  
  return await response.json();
}

/**
 * Updates the user's profile
 * @param profileData - Partial user profile data to update
 * @returns Promise with updated user profile
 */
export async function updateUserProfile(profileData: Partial<UserProfile>): Promise<UserProfile> {
  const response = await fetch('/api/user/profile', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(profileData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to update user profile');
  }
  
  return await response.json();
}

/**
 * Updates user preferences
 * @param preferences - User preferences to update
 * @returns Promise with success status
 */
export async function updateUserPreferences(preferences: Record<string, any>): Promise<boolean> {
  const response = await fetch('/api/user/preferences', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(preferences)
  });
  
  return response.ok;
}
