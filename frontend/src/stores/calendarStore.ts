import { writable } from 'svelte/store';

export interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  location?: string;
  start: string;
  end: string;
  color?: string;
}

interface CalendarStore {
  events: CalendarEvent[];
  loading: boolean;
  error: string | null;
  selectedEvent: CalendarEvent | null;
}

const initialState: CalendarStore = {
  events: [],
  loading: false,
  error: null,
  selectedEvent: null
};

function createCalendarStore() {
  const { subscribe, set, update } = writable<CalendarStore>(initialState);

  return {
    subscribe,
    fetchEvents: async (startDate?: string, endDate?: string) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        let url = '/api/calendar/events';
        if (startDate && endDate) {
          url += `?start=${startDate}&end=${endDate}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Failed to fetch calendar events');
        }
        
        const events = await response.json();
        update(state => ({ ...state, events, loading: false }));
      } catch (error) {
        console.error('Error fetching calendar events:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
      }
    },
    selectEvent: (id: string) => {
      update(state => {
        const selectedEvent = state.events.find(event => event.id === id) || null;
        return { ...state, selectedEvent };
      });
    },
    createEvent: async (event: Omit<CalendarEvent, 'id'>) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch('/api/calendar/events', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(event)
        });
        
        if (!response.ok) {
          throw new Error('Failed to create event');
        }
        
        const newEvent = await response.json();
        
        update(state => ({ 
          ...state, 
          events: [...state.events, newEvent],
          loading: false 
        }));
        
        return true;
      } catch (error) {
        console.error('Error creating event:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
        return false;
      }
    },
    updateEvent: async (id: string, eventData: Partial<Omit<CalendarEvent, 'id'>>) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch(`/api/calendar/events/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(eventData)
        });
        
        if (!response.ok) {
          throw new Error('Failed to update event');
        }
        
        const updatedEvent = await response.json();
        
        update(state => ({
          ...state,
          events: state.events.map(event => 
            event.id === id ? updatedEvent : event
          ),
          selectedEvent: state.selectedEvent?.id === id 
            ? updatedEvent 
            : state.selectedEvent,
          loading: false
        }));
        
        return true;
      } catch (error) {
        console.error('Error updating event:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
        return false;
      }
    },
    deleteEvent: async (id: string) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const response = await fetch(`/api/calendar/events/${id}`, {
          method: 'DELETE'
        });
        
        if (!response.ok) {
          throw new Error('Failed to delete event');
        }
        
        update(state => ({
          ...state,
          events: state.events.filter(event => event.id !== id),
          selectedEvent: state.selectedEvent?.id === id 
            ? null 
            : state.selectedEvent,
          loading: false
        }));
        
        return true;
      } catch (error) {
        console.error('Error deleting event:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }));
        return false;
      }
    },
    reset: () => set(initialState)
  };
}

export const calendarStore = createCalendarStore();
