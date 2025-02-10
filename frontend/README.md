# CRE AI Assistant Frontend

Modern Next.js frontend for the Commercial Real Estate AI Assistant, built with TypeScript, Tailwind CSS, and shadcn/ui.

## Technical Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Context + Hooks
- **API Client**: Custom Fetch wrapper
- **Markdown**: React Markdown with syntax highlighting
- **Forms**: React Hook Form
- **Validation**: Zod
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/
│   ├── admin/
│   │   ├── documents/
│   │   │   ├── page.tsx
│   │   │   └── upload.tsx
│   │   └── layout.tsx
│   ├── chat/
│   │   └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── chat/
│   │   ├── chat-input.tsx
│   │   ├── chat-message.tsx
│   │   └── chat-window.tsx
│   ├── documents/
│   │   ├── document-list.tsx
│   │   ├── document-upload.tsx
│   │   └── document-item.tsx
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── ui/
│       └── [shadcn components]
├── lib/
│   ├── api/
│   │   ├── client.ts
│   │   └── types.ts
│   ├── hooks/
│   │   ├── use-chat.ts
│   │   └── use-documents.ts
│   └── utils/
│       ├── format.ts
│       └── validation.ts
├── styles/
│   └── globals.css
├── types/
│   └── index.d.ts
└── public/
    └── assets/
```

## Setup & Development

1. Install dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Set up environment variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (if needed)
NEXT_PUBLIC_SUPABASE_URL=your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

3. Run development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Features

### Chat Interface

- Real-time chat with AI assistant
- Markdown support with syntax highlighting
- Code block copying
- Message history
- Tool selection
- Typing indicators
- Error handling

### Document Management

- Drag and drop file upload
- Progress tracking
- File type validation
- Size limits
- Status updates
- Deletion confirmation
- List view with sorting

### Admin Dashboard

- Document statistics
- Processing status
- Error monitoring
- Batch operations

## Component Usage

### Chat Components

```tsx
// Chat window with messages
<ChatWindow
  messages={messages}
  isLoading={isLoading}
  onRetry={handleRetry}
/>

// Chat input with tools
<ChatInput
  onSubmit={handleSubmit}
  tools={availableTools}
  disabled={isLoading}
/>

// Individual chat message
<ChatMessage
  message={message}
  isAI={message.role === 'assistant'}
  timestamp={message.timestamp}
/>
```

### Document Components

```tsx
// Document upload zone
<DocumentUpload
  onUpload={handleUpload}
  maxSize={10 * 1024 * 1024} // 10MB
  acceptedTypes={['pdf', 'docx', 'txt']}
/>

// Document list with actions
<DocumentList
  documents={documents}
  onDelete={handleDelete}
  onRefresh={handleRefresh}
  isLoading={isLoading}
/>

// Individual document item
<DocumentItem
  document={document}
  onDelete={() => handleDelete(document.id)}
  showStatus
/>
```

## API Integration

### Setup

```typescript
// lib/api/client.ts
export class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL!;
  }

  async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error("API request failed");
    }

    return response.json();
  }
}
```

### Usage

```typescript
// lib/hooks/use-chat.ts
export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (content: string) => {
    setIsLoading(true);
    try {
      const response = await api.chat.send({ message: content });
      setMessages((prev) => [...prev, response]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage };
}
```

## State Management

```typescript
// Context for chat state
export const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const value = {
    messages,
    isLoading,
    sendMessage: async (content: string) => {
      // Implementation
    },
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
```

## Styling

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {...},
        secondary: {...},
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

### Component Styling

```tsx
// Using clsx/cn utility for conditional classes
const buttonClasses = cn(
  "px-4 py-2 rounded-md",
  "bg-primary hover:bg-primary-dark",
  "text-white font-medium",
  {
    "opacity-50 cursor-not-allowed": disabled,
  }
);
```

## Testing

```bash
# Run tests
npm test
# or
yarn test
# or
pnpm test
```

### Component Testing

```typescript
// components/chat/chat-input.test.tsx
import { render, fireEvent } from "@testing-library/react";
import { ChatInput } from "./chat-input";

describe("ChatInput", () => {
  it("submits message on enter", () => {
    const onSubmit = jest.fn();
    const { getByRole } = render(<ChatInput onSubmit={onSubmit} />);

    const input = getByRole("textbox");
    fireEvent.change(input, { target: { value: "test message" } });
    fireEvent.keyPress(input, { key: "Enter", code: 13, charCode: 13 });

    expect(onSubmit).toHaveBeenCalledWith("test message");
  });
});
```

## Build & Deployment

```bash
# Build for production
npm run build
# or
yarn build
# or
pnpm build

# Start production server
npm start
# or
yarn start
# or
pnpm start
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

## Performance Optimization

1. Image Optimization

   - Use Next.js Image component
   - Proper sizing and formats
   - Lazy loading

2. Code Splitting

   - Dynamic imports
   - Route-based splitting
   - Component lazy loading

3. Caching
   - API response caching
   - Static page generation
   - Revalidation strategies

## Accessibility

1. Semantic HTML
2. ARIA labels
3. Keyboard navigation
4. Color contrast
5. Screen reader support

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request
