<script lang="ts">
  import { onMount } from 'svelte';
  import Sidebar from './components/Sidebar.svelte';
  import Header from './components/Header.svelte';
  import Dashboard from './components/Dashboard.svelte';
  import EmailView from './components/EmailView.svelte';
  import CalendarView from './components/CalendarView.svelte';
  import ChatView from './components/ChatView.svelte';
  import { currentView } from './stores/navigationStore';
  import { fetchUserProfile } from './services/userService';
  
  let loading = true;
  let user = null;
  
  onMount(async () => {
    try {
      user = await fetchUserProfile();
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      loading = false;
    }
  });
</script>

<div class="flex h-screen bg-gray-100">
  <Sidebar />
  
  <div class="flex flex-col flex-1 overflow-hidden">
    <Header {user} />
    
    <main class="flex-1 overflow-y-auto p-4 md:p-6">
      {#if loading}
        <div class="flex justify-center items-center h-full">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      {:else}
        {#if $currentView === 'dashboard'}
          <Dashboard />
        {:else if $currentView === 'email'}
          <EmailView />
        {:else if $currentView === 'calendar'}
          <CalendarView />
        {:else if $currentView === 'chat'}
          <ChatView />
        {/if}
      {/if}
    </main>
  </div>
</div>
