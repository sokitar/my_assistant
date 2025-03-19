import { writable } from 'svelte/store';

// Define the possible views in the application
export type View = 'dashboard' | 'email' | 'calendar' | 'chat';

// Create a writable store with 'dashboard' as the default view
export const currentView = writable<View>('dashboard');
