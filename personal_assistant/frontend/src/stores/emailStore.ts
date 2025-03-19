import { writable } from 'svelte/store';

export interface Email {
  id: string;
  from: string;
  to: string;
  subject: string;
  body: string;
  date: string;
  read: boolean;
  important: boolean;
}

interface EmailStore {
  emails: Email[];
  loading: boolean;
  error: string | null;
  selectedEmail: Email | null;
}

const initialState: EmailStore = {
  emails: [],
  loading: false,
  error: null,
  selectedEmail: null
};

function createEmailStore() {
  const { subscribe, set, update } = writable<EmailStore>(initialState);

  return {
    subscribe,
    fetchEmails: async () => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch('/api/emails');
        if (!response.ok) {
          throw new Error('Failed to fetch emails');
        }
        const emails = await response.json();
        update(state => ({ ...state, emails, loading: false }));
      } catch (error) {
        console.error('Error fetching emails:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
      }
    },
    selectEmail: (id: string) => {
      update(state => {
        const selectedEmail = state.emails.find(email => email.id === id) || null;
        return { ...state, selectedEmail };
      });
    },
    sendEmail: async (email: Omit<Email, 'id' | 'date' | 'read' | 'important'>) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch('/api/emails', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(email)
        });
        
        if (!response.ok) {
          throw new Error('Failed to send email');
        }
        
        // Refresh emails after sending
        const emailsResponse = await fetch('/api/emails');
        const emails = await emailsResponse.json();
        
        update(state => ({ ...state, emails, loading: false }));
        return true;
      } catch (error) {
        console.error('Error sending email:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
        return false;
      }
    },
    markAsRead: async (id: string) => {
      try {
        const response = await fetch(`/api/emails/${id}/read`, {
          method: 'PUT'
        });
        
        if (!response.ok) {
          throw new Error('Failed to mark email as read');
        }
        
        update(state => ({
          ...state,
          emails: state.emails.map(email => 
            email.id === id ? { ...email, read: true } : email
          ),
          selectedEmail: state.selectedEmail?.id === id 
            ? { ...state.selectedEmail, read: true } 
            : state.selectedEmail
        }));
      } catch (error) {
        console.error('Error marking email as read:', error);
      }
    },
    reset: () => set(initialState)
  };
}

export const emailStore = createEmailStore();
