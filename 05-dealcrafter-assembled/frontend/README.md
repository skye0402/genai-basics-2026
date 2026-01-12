# DealCrafter Frontend

React-based chat interface for the DealCrafter financial research assistant.

## Features

- **Streaming Chat**: Real-time SSE streaming responses from the AI agent
- **UI5 Fiori Design**: SAP Fiori-style components via UI5 Web Components
- **Document Upload**: Upload PDF/DOCX files for RAG-based Q&A
- **Dark/Light Mode**: Theme toggle with system preference detection
- **Chat History**: Persistent session management with sidebar navigation
- **Responsive Layout**: Mobile-friendly design

## Prerequisites

- Node.js 20+
- pnpm (preferred package manager)

## Installation

```bash
pnpm install
```

## Development

Start the development server:

```bash
pnpm dev
```

The frontend runs on http://localhost:5173 by default.

## Build

Create a production build:

```bash
pnpm build
```

## Configuration

The frontend connects to the backend at `http://localhost:8000` by default.

To change this, set the `VITE_API_URL` environment variable:

```bash
VITE_API_URL=http://your-backend:8000 pnpm dev
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ChatInput.tsx       # Message input with attachments
│   │   ├── ChatMessage.tsx     # Message display
│   │   ├── ChatWindow.tsx      # Main chat container
│   │   ├── Sidebar.tsx         # Chat history sidebar
│   │   └── ...
│   ├── contexts/         # React contexts
│   │   ├── ChatContext.tsx     # Chat state management
│   │   └── ThemeContext.tsx    # Theme management
│   ├── services/         # API services
│   │   ├── api.ts              # Backend API calls
│   │   └── chatHistory.ts      # Session management
│   ├── types/            # TypeScript types
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── index.html            # HTML template
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Key Dependencies

- **React 18** - UI framework
- **@ui5/webcomponents-react** - SAP Fiori components
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety

## Browser Timezone

The frontend automatically detects the user's browser timezone and sends it with each chat request. This allows the AI agent to greet users appropriately based on their local time.
