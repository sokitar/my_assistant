<script lang="ts">
  import { currentView } from '../stores/navigationStore';
  
  // User prop
  export let user = null;
  
  // View titles
  const viewTitles = {
    dashboard: 'Dashboard',
    email: 'Email',
    calendar: 'Calendar',
    chat: 'AI Assistant'
  };
</script>

<header class="bg-white border-b border-gray-200 sticky top-0 z-10">
  <div class="flex items-center justify-between px-4 py-3 md:px-6">
    <!-- Mobile menu button -->
    <button type="button" class="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500">
      <span class="sr-only">Open main menu</span>
      <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
    
    <!-- Page title -->
    <h1 class="text-xl font-semibold text-gray-800">
      {viewTitles[$currentView] || 'Personal Assistant'}
    </h1>
    
    <!-- User menu -->
    <div class="flex items-center">
      <!-- Search -->
      <div class="hidden md:block mr-4">
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
          </div>
          <input type="text" class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm" placeholder="Search">
        </div>
      </div>
      
      <!-- Notifications -->
      <button type="button" class="p-2 rounded-full text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500">
        <span class="sr-only">View notifications</span>
        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      </button>
      
      <!-- Profile dropdown -->
      <div class="ml-3 relative">
        <div>
          <button type="button" class="flex items-center max-w-xs rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" id="user-menu-button" aria-expanded="false" aria-haspopup="true">
            <span class="sr-only">Open user menu</span>
            {#if user && user.avatar}
              <img class="h-8 w-8 rounded-full" src={user.avatar} alt={user.name}>
            {:else}
              <div class="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium">
                {#if user && user.name}
                  {user.name.charAt(0).toUpperCase()}
                {:else}
                  U
                {/if}
              </div>
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
</header>
