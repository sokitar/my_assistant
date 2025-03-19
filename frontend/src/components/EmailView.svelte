<script lang="ts">
  import { onMount } from 'svelte';
  import { emailStore, type Email } from '../stores/emailStore';
  
  let emails: Email[] = [];
  let selectedEmail: Email | null = null;
  let loading = true;
  let error = '';
  
  // Compose email state
  let showComposeForm = false;
  let to = '';
  let subject = '';
  let body = '';
  let sendingEmail = false;
  
  // Filter state
  let filter = 'inbox';
  
  onMount(async () => {
    try {
      await emailStore.fetchEmails();
      
      const unsubscribe = emailStore.subscribe(state => {
        emails = state.emails;
        loading = state.loading;
        error = state.error;
      });
      
      return unsubscribe;
    } catch (err) {
      console.error('Error initializing email view:', err);
      error = 'Failed to load emails. Please try again.';
      loading = false;
    }
  });
  
  function selectEmail(email: Email) {
    selectedEmail = email;
    if (!email.read) {
      emailStore.markAsRead(email.id);
    }
  }
  
  function closeSelectedEmail() {
    selectedEmail = null;
  }
  
  function toggleComposeForm() {
    showComposeForm = !showComposeForm;
    if (!showComposeForm) {
      resetComposeForm();
    }
  }
  
  function resetComposeForm() {
    to = '';
    subject = '';
    body = '';
  }
  
  async function sendEmail() {
    if (!to || !subject || !body) {
      error = 'Please fill out all fields';
      return;
    }
    
    try {
      sendingEmail = true;
      await emailStore.sendEmail(to, subject, body);
      resetComposeForm();
      toggleComposeForm();
      error = '';
    } catch (err) {
      console.error('Error sending email:', err);
      error = 'Failed to send email. Please try again.';
    } finally {
      sendingEmail = false;
    }
  }
  
  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function getFilteredEmails() {
    switch (filter) {
      case 'inbox':
        return emails.filter(email => !email.sent);
      case 'sent':
        return emails.filter(email => email.sent);
      case 'unread':
        return emails.filter(email => !email.read && !email.sent);
      default:
        return emails;
    }
  }
</script>

<div class="container mx-auto px-4 h-full">
  <div class="flex flex-col h-full">
    <!-- Email Header -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex space-x-2">
        <button 
          class="px-3 py-1 rounded-md {filter === 'inbox' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => filter = 'inbox'}>
          Inbox
        </button>
        <button 
          class="px-3 py-1 rounded-md {filter === 'sent' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => filter = 'sent'}>
          Sent
        </button>
        <button 
          class="px-3 py-1 rounded-md {filter === 'unread' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}"
          on:click={() => filter = 'unread'}>
          Unread
        </button>
      </div>
      <button 
        class="btn-primary btn"
        on:click={toggleComposeForm}>
        {showComposeForm ? 'Cancel' : 'Compose Email'}
      </button>
    </div>
    
    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {error}
      </div>
    {/if}
    
    {#if showComposeForm}
      <!-- Compose Email Form -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Compose Email</h2>
        <form on:submit|preventDefault={sendEmail} class="space-y-4">
          <div>
            <label for="to" class="block text-sm font-medium text-gray-700 mb-1">To:</label>
            <input 
              type="email" 
              id="to" 
              bind:value={to} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="recipient@example.com"
              required
            />
          </div>
          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">Subject:</label>
            <input 
              type="text" 
              id="subject" 
              bind:value={subject} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Email subject"
              required
            />
          </div>
          <div>
            <label for="body" class="block text-sm font-medium text-gray-700 mb-1">Message:</label>
            <textarea 
              id="body" 
              bind:value={body} 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 h-32"
              placeholder="Write your message here..."
              required
            ></textarea>
          </div>
          <div class="flex justify-end">
            <button 
              type="button" 
              class="btn-secondary btn mr-2"
              on:click={toggleComposeForm}>
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn-primary btn"
              disabled={sendingEmail}>
              {sendingEmail ? 'Sending...' : 'Send Email'}
            </button>
          </div>
        </form>
      </div>
    {/if}
    
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    {:else if selectedEmail}
      <!-- Email Detail View -->
      <div class="bg-white rounded-lg shadow-md p-6 flex-grow overflow-auto">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h2 class="text-xl font-semibold">{selectedEmail.subject}</h2>
            <div class="mt-2 flex items-center text-sm text-gray-600">
              <span class="font-medium">{selectedEmail.from}</span>
              <span class="mx-2">•</span>
              <span>{formatDate(selectedEmail.date)}</span>
            </div>
            {#if selectedEmail.to}
              <div class="mt-1 text-sm text-gray-600">
                To: {selectedEmail.to}
              </div>
            {/if}
          </div>
          <button 
            class="text-gray-400 hover:text-gray-600"
            on:click={closeSelectedEmail}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="border-t border-gray-200 pt-4 mt-4">
          <div class="prose max-w-none">
            <p>{selectedEmail.body}</p>
          </div>
        </div>
        <div class="mt-6 flex space-x-2">
          <button class="btn-primary btn">
            Reply
          </button>
          <button class="btn-secondary btn">
            Forward
          </button>
        </div>
      </div>
    {:else}
      <!-- Email List -->
      <div class="bg-white rounded-lg shadow-md flex-grow overflow-auto">
        {#if getFilteredEmails().length === 0}
          <div class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <p class="text-lg">No emails found</p>
          </div>
        {:else}
          <ul class="divide-y divide-gray-200">
            {#each getFilteredEmails() as email}
              <li 
                class="px-6 py-4 hover:bg-gray-50 cursor-pointer {!email.read && !email.sent ? 'bg-blue-50' : ''}"
                on:click={() => selectEmail(email)}>
                <div class="flex justify-between items-start">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {email.sent ? `To: ${email.to}` : `From: ${email.from}`}
                    </p>
                    <p class="text-sm {!email.read && !email.sent ? 'font-semibold' : 'font-normal'} text-gray-900 mt-1">
                      {email.subject}
                    </p>
                    <p class="text-sm text-gray-500 truncate mt-1">
                      {email.body.substring(0, 100)}...
                    </p>
                  </div>
                  <div class="ml-4 flex-shrink-0">
                    <p class="text-xs text-gray-500">{formatDate(email.date)}</p>
                    {#if !email.read && !email.sent}
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                        New
                      </span>
                    {/if}
                  </div>
                </div>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    {/if}
  </div>
</div>
