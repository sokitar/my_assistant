declare module 'openai' {
  export default class OpenAI {
    constructor(options: { apiKey: string; dangerouslyAllowBrowser?: boolean });
    
    responses: {
      create(options: {
        model: string;
        instructions?: string;
        input: string;
        stream?: boolean;
      }): Promise<{ output_text: string }>;
    };
  }
}
