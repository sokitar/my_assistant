# Personal Assistant Frontend

A modern, responsive frontend for the Personal Assistant application built with Svelte and Tailwind CSS.

## Features

- **Beautiful UI**: Modern interface built with Tailwind CSS
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **TypeScript Support**: Type-safe code for better developer experience
- **Component-Based Architecture**: Modular components for maintainability
- **State Management**: Svelte stores for efficient state management
- **API Integration**: Seamless integration with the FastAPI backend

## Project Structure

```
frontend/
├── src/              # Source code
│   ├── components/   # Reusable UI components
│   │   ├── Dashboard.svelte    # Dashboard view
│   │   ├── EmailView.svelte    # Email management view
│   │   ├── CalendarView.svelte # Calendar management view
│   │   ├── ChatView.svelte     # AI chat interface
│   │   ├── Header.svelte       # Application header
│   │   └── Sidebar.svelte      # Navigation sidebar
│   ├── services/     # API service integrations
│   │   ├── userService.ts      # User profile service
│   │   └── openaiService.ts    # OpenAI API integration
│   ├── stores/       # Svelte stores for state management
│   │   ├── navigationStore.ts  # Navigation state
│   │   ├── emailStore.ts       # Email data and operations
│   │   ├── calendarStore.ts    # Calendar events and operations
│   │   └── chatStore.ts        # Chat messages and AI interactions
│   ├── types/        # TypeScript type definitions
│   ├── App.svelte    # Main application component
│   └── main.ts       # Application entry point
├── public/           # Static assets
├── package.json      # Frontend dependencies
├── tsconfig.json     # TypeScript configuration
├── vite.config.ts    # Vite configuration
├── postcss.config.js # PostCSS configuration
└── tailwind.config.js # Tailwind CSS configuration
```

## Setup Instructions

### Prerequisites

- Node.js (v14 or later)
- npm or yarn
- Backend API running (see main project README)

### Installation

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Create a `.env` file in the frontend directory with the following variables:
   ```
   VITE_API_URL=http://localhost:8000
   ```

### Development

Run the development server:
```bash
npm run dev
# or
yarn dev
```

This will start the development server at http://localhost:5173.

### Building for Production

Build the frontend for production:
```bash
npm run build
# or
yarn build
```

The built files will be in the `dist` directory, which can be served by the FastAPI backend.

## Development Guidelines

### Svelte Best Practices

- **Separation of concerns**: Keep components small and focused
- **Consistent naming**: Use descriptive names for components and variables
- **Code organization**: Group related functionality together
- **Comments**: Add comments to explain complex logic

### State Management

- Use Svelte's reactive statements for local component state
- Use Svelte stores for global state management
- Follow the pattern established in the stores directory

### Styling

- Use Tailwind CSS utility classes for styling
- Follow the color scheme defined in `tailwind.config.js`
- Use the global button classes defined in `App.svelte`

### API Integration

- All API calls should go through the service layer
- Handle loading states and errors consistently
- Use try/catch blocks for error handling

## Testing

Run the test suite:
```bash
npm run test
# or
yarn test
```

## Contributing

1. Follow the code style and organization of the project
2. Write clear, descriptive commit messages
3. Add appropriate comments to your code
4. Test your changes thoroughly before submitting
