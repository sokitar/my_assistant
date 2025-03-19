import { writable } from 'svelte/store';
import OpenAI from 'openai';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatStore {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

const initialState: ChatStore = {
  messages: [],
  loading: false,
  error: null
};

function createChatStore() {
  const { subscribe, set, update } = writable<ChatStore>(initialState);

  return {
    subscribe,
    fetchMessages: async () => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch('/api/chat/messages');
        if (!response.ok) {
          throw new Error('Failed to fetch messages');
        }
        const messages = await response.json();
        update(state => ({ ...state, messages, loading: false }));
      } catch (error) {
        console.error('Error fetching messages:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
      }
    },
    sendMessage: async (content: string) => {
      // Generate a unique ID for the message
      const messageId = crypto.randomUUID();
      const timestamp = new Date().toISOString();
      
      // Add user message to the store immediately
      const userMessage: Message = {
        id: messageId,
        role: 'user',
        content,
        timestamp
      };
      
      update(state => ({
        ...state,
        messages: [...state.messages, userMessage],
        loading: true,
        error: null
      }));
      
      try {
        // Send message to the backend
        const response = await fetch('/api/chat/messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ content })
        });
        
        if (!response.ok) {
          throw new Error('Failed to send message');
        }
        
        // Get the assistant's response
        const assistantResponse = await response.json();
        
        // Add assistant message to the store
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: assistantResponse.content,
          timestamp: new Date().toISOString()
        };
        
        update(state => ({
          ...state,
          messages: [...state.messages, assistantMessage],
          loading: false
        }));
        
        return true;
      } catch (error) {
        console.error('Error sending message:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
        return false;
      }
    },
    clearMessages: () => {
      update(state => ({ ...state, messages: [], error: null }));
    },
    reset: () => set(initialState)
  };
}

export const chatStore = createChatStore();
