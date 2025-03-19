// Using dynamic import to avoid TypeScript errors with the OpenAI SDK
// This is a workaround for the module resolution issue
type OpenAIClient = any; // We'll use any type temporarily until we can properly import OpenAI

/**
 * Service for handling OpenAI API interactions
 */
class OpenAIService {
  private client: OpenAIClient | null = null;

  /**
   * Initializes the OpenAI client
   * Note: In production, API keys should be handled server-side
   */
  async initialize(apiKey: string): Promise<void> {
    try {
      // Dynamically import OpenAI to avoid TypeScript errors
      const { default: OpenAI } = await import('openai');
      
      this.client = new OpenAI({
        apiKey,
        dangerouslyAllowBrowser: true // Only for development - in production, use server-side API calls
      });
    } catch (error) {
      console.error('Failed to initialize OpenAI client:', error);
      throw new Error('Failed to initialize OpenAI client');
    }
  }

  /**
   * Checks if the client is initialized
   */
  isInitialized(): boolean {
    return this.client !== null;
  }

  /**
   * Sends a message to the OpenAI API and returns the response
   * @param input - User input message
   * @param instructions - System instructions for the AI
   * @returns Promise with the AI response
   */
  async sendMessage(input: string, instructions: string = 'You are a helpful assistant'): Promise<string> {
    if (!this.client) {
      throw new Error('OpenAI client not initialized');
    }

    try {
      const response = await this.client.responses.create({
        model: 'gpt-4o',
        instructions,
        input,
      });

      return response.output_text;
    } catch (error) {
      console.error('Error calling OpenAI API:', error);
      throw error;
    }
  }

  /**
   * Creates a streaming response from OpenAI
   * @param input - User input message
   * @param instructions - System instructions for the AI
   * @returns Promise with a stream of responses
   */
  async streamMessage(input: string, instructions: string = 'You are a helpful assistant'): Promise<ReadableStream> {
    if (!this.client) {
      throw new Error('OpenAI client not initialized');
    }

    try {
      const stream = await this.client.responses.create({
        model: 'gpt-4o',
        instructions,
        input,
        stream: true,
      });

      return stream as unknown as ReadableStream;
    } catch (error) {
      console.error('Error streaming from OpenAI API:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const openaiService = new OpenAIService();
