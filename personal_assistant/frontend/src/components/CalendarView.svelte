<script lang="ts">
  import { onMount } from 'svelte';
  import { calendarStore, type CalendarEvent } from '../stores/calendarStore';
  
  let events: CalendarEvent[] = [];
  let loading = true;
  let error = '';
  let currentView = 'month';
  let selectedDate = new Date();
  let selectedEvent: CalendarEvent | null = null;
  
  // New event form state
  let showEventForm = false;
  let newEvent = {
    summary: '',
    description: '',
    location: '',
    start: '',
    end: '',
    attendees: ''
  };
  
  onMount(async () => {
    try {
      await calendarStore.fetchEvents();
      
      const unsubscribe = calendarStore.subscribe(state => {
        events = state.events;
        loading = state.loading;
        error = state.error;
      });
      
      // Initialize form dates to today
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      newEvent.start = formatDateForInput(today);
      newEvent.end = formatDateForInput(tomorrow);
      
      return unsubscribe;
    } catch (err) {
      console.error('Error initializing calendar view:', err);
      error = 'Failed to load calendar events. Please try again.';
      loading = false;
    }
  });
  
  function formatDateForInput(date: Date): string {
    return date.toISOString().slice(0, 16);
  }
  
  function formatDateForDisplay(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function getMonthName(date: Date): string {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  }
  
  function getDaysInMonth(date: Date): Date[] {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Get the first day of the week for the first day of the month
    let startDay = new Date(firstDay);
    startDay.setDate(startDay.getDate() - startDay.getDay());
    
    // Get the last day of the week for the last day of the month
    let endDay = new Date(lastDay);
    if (endDay.getDay() < 6) {
      endDay.setDate(endDay.getDate() + (6 - endDay.getDay()));
    }
    
    const days: Date[] = [];
    let currentDay = new Date(startDay);
    
    while (currentDay <= endDay) {
      days.push(new Date(currentDay));
      currentDay.setDate(currentDay.getDate() + 1);
    }
    
    return days;
  }
  
  function getEventsForDay(date: Date): CalendarEvent[] {
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();
    
    return events.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate.getFullYear() === year && 
             eventDate.getMonth() === month && 
             eventDate.getDate() === day;
    });
  }
  
  function isToday(date: Date): boolean {
    const today = new Date();
    return date.getFullYear() === today.getFullYear() &&
           date.getMonth() === today.getMonth() &&
           date.getDate() === today.getDate();
  }
  
  function isCurrentMonth(date: Date): boolean {
    return date.getMonth() === selectedDate.getMonth();
  }
  
  function changeMonth(increment: number): void {
    const newDate = new Date(selectedDate);
    newDate.setMonth(newDate.getMonth() + increment);
    selectedDate = newDate;
  }
  
  function selectEvent(event: CalendarEvent): void {
    selectedEvent = event;
  }
  
  function closeSelectedEvent(): void {
    selectedEvent = null;
  }
  
  function toggleEventForm(): void {
    showEventForm = !showEventForm;
    if (!showEventForm) {
      resetEventForm();
    }
  }
  
  function resetEventForm(): void {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    newEvent = {
      summary: '',
      description: '',
      location: '',
      start: formatDateForInput(today),
      end: formatDateForInput(tomorrow),
      attendees: ''
    };
  }
  
  async function createEvent(): Promise<void> {
    if (!newEvent.summary || !newEvent.start || !newEvent.end) {
      error = 'Please fill out all required fields';
      return;
    }
    
    try {
      const attendeesList = newEvent.attendees
        ? newEvent.attendees.split(',').map(email => email.trim())
        : [];
      
      await calendarStore.createEvent({
        summary: newEvent.summary,
        description: newEvent.description,
        location: newEvent.location,
        start: new Date(newEvent.start).toISOString(),
        end: new Date(newEvent.end).toISOString(),
        attendees: attendeesList
      });
      
      resetEventForm();
      toggleEventForm();
      error = '';
    } catch (err) {
      console.error('Error creating event:', err);
      error = 'Failed to create event. Please try again.';
    }
  }
</script>

<div class="container mx-auto px-4 h-full">
  <div class="flex flex-col h-full">
    <!-- Calendar Header -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex space-x-2">
        <button 
          class="px-3 py-1 rounded-md {currentView === 'month' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => currentView = 'month'}>
          Month
        </button>
        <button 
          class="px-3 py-1 rounded-md {currentView === 'week' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => currentView = 'week'}>
          Week
        </button>
        <button 
          class="px-3 py-1 rounded-md {currentView === 'day' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => currentView = 'day'}>
          Day
        </button>
      </div>
      <button 
        class="btn-primary btn"
        on:click={toggleEventForm}>
        {showEventForm ? 'Cancel' : 'New Event'}
      </button>
    </div>
    
    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {error}
      </div>
    {/if}
    
    {#if showEventForm}
      <!-- New Event Form -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Create New Event</h2>
        <form on:submit|preventDefault={createEvent} class="space-y-4">
          <div>
            <label for="summary" class="block text-sm font-medium text-gray-700 mb-1">Title: <span class="text-red-500">*</span></label>
            <input 
              type="text" 
              id="summary" 
              bind:value={newEvent.summary} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Event title"
              required
            />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="start" class="block text-sm font-medium text-gray-700 mb-1">Start: <span class="text-red-500">*</span></label>
              <input 
                type="datetime-local" 
                id="start" 
                bind:value={newEvent.start} 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label for="end" class="block text-sm font-medium text-gray-700 mb-1">End: <span class="text-red-500">*</span></label>
              <input 
                type="datetime-local" 
                id="end" 
                bind:value={newEvent.end} 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
          </div>
          <div>
            <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Location:</label>
            <input 
              type="text" 
              id="location" 
              bind:value={newEvent.location} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Event location"
            />
          </div>
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description:</label>
            <textarea 
              id="description" 
              bind:value={newEvent.description} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 h-24"
              placeholder="Event description"
            ></textarea>
          </div>
          <div>
            <label for="attendees" class="block text-sm font-medium text-gray-700 mb-1">Attendees (comma separated):</label>
            <input 
              type="text" 
              id="attendees" 
              bind:value={newEvent.attendees} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="email1@example.com, email2@example.com"
            />
          </div>
          <div class="flex justify-end">
            <button 
              type="button" 
              class="btn-secondary btn mr-2"
              on:click={toggleEventForm}>
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn-primary btn">
              Create Event
            </button>
          </div>
        </form>
      </div>
    {/if}
    
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    {:else if selectedEvent}
      <!-- Event Detail View -->
      <div class="bg-white rounded-lg shadow-md p-6 flex-grow overflow-auto">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h2 class="text-xl font-semibold">{selectedEvent.summary}</h2>
            <div class="mt-2 flex items-center text-sm text-gray-600">
              <span>{formatDateForDisplay(selectedEvent.start)}</span>
              <span class="mx-2">to</span>
              <span>{formatDateForDisplay(selectedEvent.end)}</span>
            </div>
            {#if selectedEvent.location}
              <div class="mt-2 text-sm text-gray-600 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                {selectedEvent.location}
              </div>
            {/if}
          </div>
          <button 
            class="text-gray-400 hover:text-gray-600"
            on:click={closeSelectedEvent}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        {#if selectedEvent.description}
          <div class="border-t border-gray-200 pt-4 mt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">Description</h3>
            <div class="prose max-w-none text-gray-600">
              <p>{selectedEvent.description}</p>
            </div>
          </div>
        {/if}
        {#if selectedEvent.attendees && selectedEvent.attendees.length > 0}
          <div class="border-t border-gray-200 pt-4 mt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">Attendees</h3>
            <ul class="space-y-1">
              {#each selectedEvent.attendees as attendee}
                <li class="text-sm text-gray-600">{attendee}</li>
              {/each}
            </ul>
          </div>
        {/if}
        <div class="mt-6 flex space-x-2">
          <button class="btn-primary btn">
            Edit
          </button>
          <button class="btn-secondary btn">
            Delete
          </button>
        </div>
      </div>
    {:else if currentView === 'month'}
      <!-- Month View -->
      <div class="bg-white rounded-lg shadow-md flex-grow overflow-auto">
        <div class="p-4 flex justify-between items-center border-b border-gray-200">
          <button 
            class="p-1 rounded-full hover:bg-gray-100"
            on:click={() => changeMonth(-1)}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-xl font-semibold">{getMonthName(selectedDate)}</h2>
          <button 
            class="p-1 rounded-full hover:bg-gray-100"
            on:click={() => changeMonth(1)}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-7 text-center py-2 border-b border-gray-200">
          {#each ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as day}
            <div class="text-sm font-medium text-gray-500">{day}</div>
          {/each}
        </div>
        <div class="grid grid-cols-7 auto-rows-fr divide-x divide-y divide-gray-200">
          {#each getDaysInMonth(selectedDate) as day}
            <div 
              class="min-h-[100px] p-2 {isCurrentMonth(day) ? 'bg-white' : 'bg-gray-50'} {isToday(day) ? 'bg-blue-50' : ''}"
              on:click={() => currentView = 'day'}>
              <div class="flex justify-between items-center mb-1">
                <span class="{isToday(day) ? 'bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : 'text-gray-700'} text-sm">
                  {day.getDate()}
                </span>
                {#if getEventsForDay(day).length > 0}
                  <span class="text-xs bg-gray-200 rounded-full px-2 py-0.5">
                    {getEventsForDay(day).length}
                  </span>
                {/if}
              </div>
              <div class="space-y-1 overflow-y-auto max-h-[80px]">
                {#each getEventsForDay(day) as event}
                  <div 
                    class="text-xs p-1 rounded truncate cursor-pointer bg-primary-100 text-primary-800 hover:bg-primary-200"
                    on:click|stopPropagation={() => selectEvent(event)}>
                    {event.summary}
                  </div>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {:else if currentView === 'week'}
      <!-- Week View (simplified) -->
      <div class="bg-white rounded-lg shadow-md flex-grow overflow-auto p-4">
        <h3 class="text-lg font-medium mb-4">Week View</h3>
        <p class="text-gray-500">Week view implementation would display a detailed week calendar here.</p>
        <div class="mt-4 space-y-2">
          <h4 class="font-medium">This Week's Events:</h4>
          {#if events.length === 0}
            <p class="text-gray-500 italic">No events this week</p>
          {:else}
            <ul class="space-y-2">
              {#each events.slice(0, 5) as event}
                <li 
                  class="p-3 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer"
                  on:click={() => selectEvent(event)}>
                  <div class="font-medium">{event.summary}</div>
                  <div class="text-sm text-gray-600 mt-1">{formatDateForDisplay(event.start)}</div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    {:else if currentView === 'day'}
      <!-- Day View (simplified) -->
      <div class="bg-white rounded-lg shadow-md flex-grow overflow-auto p-4">
        <h3 class="text-lg font-medium mb-4">Day View</h3>
        <p class="text-gray-500">Day view implementation would display a detailed day schedule here.</p>
        <div class="mt-4 space-y-2">
          <h4 class="font-medium">Today's Events:</h4>
          {#if events.length === 0}
            <p class="text-gray-500 italic">No events today</p>
          {:else}
            <ul class="space-y-2">
              {#each events.slice(0, 5) as event}
                <li 
                  class="p-3 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer"
                  on:click={() => selectEvent(event)}>
                  <div class="font-medium">{event.summary}</div>
                  <div class="text-sm text-gray-600 mt-1">{formatDateForDisplay(event.start)}</div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>
