<script lang="ts">
  import { onMount } from 'svelte';
  import { chatStore, type Message } from '../stores/chatStore';
  
  let messages: Message[] = [];
  let newMessage = '';
  let loading = false;
  let error = '';
  let chatContainer: HTMLElement;
  
  onMount(() => {
    const unsubscribe = chatStore.subscribe(state => {
      messages = state.messages;
      loading = state.loading;
      error = state.error;
      
      // Scroll to bottom when messages change
      setTimeout(() => {
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }, 0);
    });
    
    return unsubscribe;
  });
  
  async function sendMessage() {
    if (!newMessage.trim()) return;
    
    try {
      await chatStore.sendMessage(newMessage);
      newMessage = '';
    } catch (err) {
      console.error('Error sending message:', err);
      error = 'Failed to send message. Please try again.';
    }
  }
  
  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  }
  
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="container mx-auto px-4 h-full flex flex-col">
  <div class="flex-grow flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
    <!-- Chat Header -->
    <div class="bg-primary-600 text-white p-4 flex items-center">
      <div class="h-10 w-10 rounded-full bg-primary-700 flex items-center justify-center mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </div>
      <div>
        <h2 class="font-semibold">AI Assistant</h2>
        <p class="text-xs text-primary-100">Online</p>
      </div>
    </div>
    
    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 m-2 rounded">
        {error}
      </div>
    {/if}
    
    <!-- Chat Messages -->
    <div class="flex-grow p-4 overflow-y-auto bg-gray-50" bind:this={chatContainer}>
      {#if messages.length === 0}
        <div class="flex flex-col items-center justify-center h-full text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p class="text-lg mb-2">No messages yet</p>
          <p class="text-sm text-center max-w-md">
            Start a conversation with your AI assistant. You can ask about your emails, calendar, or any other questions you might have.
          </p>
        </div>
      {:else}
        <div class="space-y-4">
          {#each messages as message}
            <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
              <div class="max-w-3/4 {message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-white'} rounded-lg px-4 py-2 shadow">
                <div class="text-sm">{message.content}</div>
                <div class="text-xs mt-1 {message.role === 'user' ? 'text-primary-100' : 'text-gray-500'} text-right">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          {/each}
          
          {#if loading}
            <div class="flex justify-start">
              <div class="bg-white rounded-lg px-4 py-2 shadow">
                <div class="flex space-x-2">
                  <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Chat Input -->
    <div class="p-4 border-t border-gray-200">
      <div class="flex">
        <textarea 
          class="flex-grow px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          placeholder="Type your message..."
          rows="2"
          bind:value={newMessage}
          on:keydown={handleKeyDown}
          disabled={loading}
        ></textarea>
        <button 
          class="bg-primary-600 text-white px-4 rounded-r-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          on:click={sendMessage}
          disabled={loading || !newMessage.trim()}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </button>
      </div>
      <div class="text-xs text-gray-500 mt-2">
        Press Enter to send, Shift+Enter for a new line
      </div>
    </div>
  </div>
</div>
