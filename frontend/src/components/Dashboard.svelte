<script lang="ts">
  import { onMount } from 'svelte';
  import { emailStore, type Email } from '../stores/emailStore';
  import { calendarStore, type CalendarEvent } from '../stores/calendarStore';
  
  let recentEmails: Email[] = [];
  let upcomingEvents: CalendarEvent[] = [];
  let loading = true;
  
  onMount(async () => {
    try {
      // Fetch data for the dashboard
      await Promise.all([
        emailStore.fetchEmails(),
        calendarStore.fetchEvents()
      ]);
      
      // Get recent emails from the store
      const unsubscribeEmails = emailStore.subscribe(state => {
        recentEmails = state.emails
          .filter(email => !email.read)
          .slice(0, 5);
      });
      
      // Get upcoming events from the store
      const unsubscribeEvents = calendarStore.subscribe(state => {
        const now = new Date();
        upcomingEvents = state.events
          .filter(event => new Date(event.start) > now)
          .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
          .slice(0, 5);
      });
      
      loading = false;
      
      return () => {
        unsubscribeEmails();
        unsubscribeEvents();
      };
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      loading = false;
    }
  });
  
  // Format date for display
  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="container mx-auto px-4">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Welcome to Your Personal Assistant</h1>
    <p class="text-gray-600 mt-2">Stay organized with your emails, calendar, and AI assistance</p>
  </div>
  
  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Quick Actions -->
      <div class="card bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="grid grid-cols-2 gap-4">
          <button class="btn-primary btn flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            Compose Email
          </button>
          <button class="btn-secondary btn flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            New Event
          </button>
          <button class="btn bg-green-600 text-white hover:bg-green-700 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            Chat with AI
          </button>
          <button class="btn bg-amber-500 text-white hover:bg-amber-600 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            Search
          </button>
        </div>
      </div>
      
      <!-- AI Suggestions -->
      <div class="card bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">AI Suggestions</h2>
        <ul class="space-y-3">
          <li class="flex items-start">
            <div class="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="text-gray-700">Respond to 3 unread emails from your team</p>
          </li>
          <li class="flex items-start">
            <div class="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="text-gray-700">Prepare for your meeting with Marketing at 2 PM</p>
          </li>
          <li class="flex items-start">
            <div class="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <p class="text-gray-700">Follow up on the project proposal you sent yesterday</p>
          </li>
        </ul>
      </div>
      
      <!-- Unread Emails -->
      <div class="card bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Unread Emails</h2>
        {#if recentEmails.length === 0}
          <p class="text-gray-500 italic">No unread emails</p>
        {:else}
          <ul class="divide-y divide-gray-200">
            {#each recentEmails as email}
              <li class="py-3">
                <div class="flex items-center justify-between">
                  <p class="font-medium text-gray-900">{email.from}</p>
                  <span class="text-xs text-gray-500">{formatDate(email.date)}</span>
                </div>
                <p class="text-sm text-gray-900 font-medium mt-1">{email.subject}</p>
                <p class="text-sm text-gray-500 truncate mt-1">{email.body.substring(0, 100)}...</p>
              </li>
            {/each}
          </ul>
        {/if}
        <div class="mt-4">
          <a href="#" class="text-primary-600 hover:text-primary-800 text-sm font-medium flex items-center">
            View all emails
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </a>
        </div>
      </div>
      
      <!-- Upcoming Events -->
      <div class="card bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Upcoming Events</h2>
        {#if upcomingEvents.length === 0}
          <p class="text-gray-500 italic">No upcoming events</p>
        {:else}
          <ul class="divide-y divide-gray-200">
            {#each upcomingEvents as event}
              <li class="py-3">
                <div class="flex items-center justify-between">
                  <p class="font-medium text-gray-900">{event.summary}</p>
                  <span class="text-xs text-gray-500">{formatDate(event.start)}</span>
                </div>
                {#if event.location}
                  <p class="text-sm text-gray-500 mt-1 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {event.location}
                  </p>
                {/if}
                {#if event.description}
                  <p class="text-sm text-gray-500 truncate mt-1">{event.description.substring(0, 100)}...</p>
                {/if}
              </li>
            {/each}
          </ul>
        {/if}
        <div class="mt-4">
          <a href="#" class="text-primary-600 hover:text-primary-800 text-sm font-medium flex items-center">
            View calendar
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </a>
        </div>
      </div>
    </div>
  {/if}
</div>
