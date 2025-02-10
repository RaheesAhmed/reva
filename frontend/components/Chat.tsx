import { useState, useRef, useEffect, CSSProperties } from 'react';
import { apiClient } from '@/lib/api-client';
import { Send, Bot, User } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import ReactMarkdown from 'react-markdown';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { cn } from '@/lib/utils';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatProps {
  selectedTools: string[];
  chatId?: string;
  onUpdateHistory: (message: Message) => void;
}

export default function Chat({ selectedTools, chatId, onUpdateHistory }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history from localStorage when chatId changes
  useEffect(() => {
    if (chatId) {
      const savedMessages = localStorage.getItem(`chat_${chatId}`);
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      } else {
        setMessages([]);
      }
    }
  }, [chatId]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (chatId && messages.length > 0) {
      localStorage.setItem(`chat_${chatId}`, JSON.stringify(messages));
    }
  }, [messages, chatId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    const newUserMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: userMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    onUpdateHistory(newUserMessage);

    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage = {
      id: assistantMessageId,
      role: 'assistant' as const,
      content: '',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const stream = await apiClient.chat(userMessage, selectedTools);
      const reader = stream.getReader();
      const decoder = new TextDecoder('utf-8');
      let fullResponse = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // Convert the stream value to string safely
        const chunk = typeof value === 'string' ? value : decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(5).trim();
            
            if (data === '[DONE]') {
              break;
            } else if (data.startsWith('ERROR:')) {
              throw new Error(data.slice(6).trim());
            } else {
              // Clean the response and handle line breaks
              const cleanedData = data
                .replace(/\[object Object\]/g, '')
                .replace(/,+/g, ',')
                .trim();
              
              // Ensure proper spacing between words
              fullResponse = fullResponse 
                ? `${fullResponse}${cleanedData.startsWith(' ') ? '' : ' '}${cleanedData}` 
                : cleanedData;

              // Format the response with proper line breaks and markdown
              const formattedResponse = fullResponse
                .replace(/\n\s*\n/g, '\n\n')  // Fix multiple newlines
                .replace(/([.!?])\s+/g, '$1\n')  // Add newline after sentences
                .replace(/###\s*/g, '\n### ')  // Format headers
                .replace(/##\s*/g, '\n## ')
                .replace(/#\s*/g, '\n# ')
                .replace(/\*\*([^*]+)\*\*/g, '**$1**')  // Preserve bold
                .trim();
              
              setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: formattedResponse }
                  : msg
              ));
            }
          }
        }
      }

      const finalResponse = fullResponse
        .replace(/\n\s*\n/g, '\n\n')
        .replace(/([.!?])\s+/g, '$1\n')
        .replace(/###\s*/g, '\n### ')
        .replace(/##\s*/g, '\n## ')
        .replace(/#\s*/g, '\n# ')
        .replace(/\*\*([^*]+)\*\*/g, '**$1**')
        .trim();

      // Update history with the final formatted response
      onUpdateHistory({
        ...assistantMessage,
        content: finalResponse,
      });

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: assistantMessageId,
        role: 'assistant' as const,
        content: 'Sorry, an error occurred. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => prev.map(msg =>
        msg.id === assistantMessageId ? errorMessage : msg
      ));
      onUpdateHistory(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background/95 chat-container">
      <ScrollArea className="flex-1 px-4 md:px-6 custom-scrollbar">
        <div className="max-w-4xl mx-auto space-y-6 md:space-y-8 py-6 md:py-8">
          {messages.map((message, index) => {
            // Skip rendering if this is an empty assistant message and we're loading
            if (message.role === 'assistant' && 
                !message.content && 
                isLoading && 
                index === messages.length - 1) {
              return (
                <div key={message.id} className="flex items-start gap-4 pl-4 animate-in fade-in-50">
                  <div className="flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-full bg-primary/10 text-primary ring-1 ring-primary/20">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="glass-panel rounded-lg p-4">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            return (
              <div
                key={message.id}
                className={cn(
                  "group relative flex items-start gap-4 message-bubble",
                  message.role === 'assistant' && "bg-card/50 rounded-lg p-4 md:p-6 glass-panel",
                  message.role === 'user' && "pl-4"
                )}
              >
                <div className={cn(
                  "flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-full",
                  message.role === 'assistant' 
                    ? "bg-primary/10 text-primary ring-1 ring-primary/20" 
                    : "bg-secondary text-secondary-foreground"
                )}>
                  {message.role === 'assistant' ? (
                    <Bot className="h-5 w-5" />
                  ) : (
                    <User className="h-5 w-5" />
                  )}
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="font-semibold text-sm">
                      {message.role === 'user' ? 'You' : 'Assistant'}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkBreaks]}
                      components={{
                        p: ({node, ...props}) => (
                          <p className="my-0.5 last:mb-0" {...props} />
                        ),
                        strong: ({node, ...props}) => (
                          <strong className="font-semibold text-foreground" {...props} />
                        ),
                        h1: ({node, ...props}) => (
                          <h1 className="text-base font-semibold mt-1.5 mb-0.5 first:mt-0" {...props} />
                        ),
                        h2: ({node, ...props}) => (
                          <h2 className="text-base font-semibold mt-1.5 mb-0.5 first:mt-0" {...props} />
                        ),
                        h3: ({node, ...props}) => (
                          <h3 className="text-base font-semibold mt-1.5 mb-0.5 first:mt-0" {...props} />
                        ),
                        ul: ({node, ...props}) => (
                          <ul className="my-0.5 pl-4" {...props} />
                        ),
                        ol: ({node, ...props}) => (
                          <ol className="my-0.5 pl-4" {...props} />
                        ),
                        li: ({node, ...props}) => (
                          <li className="my-0.5 pl-0.5" {...props} />
                        ),
                        code: ({node, inline, className, children, ...props}) => {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{ margin: '0.5rem 0', padding: '0.75rem', borderRadius: '0.375rem' }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code
                              className="bg-secondary text-secondary-foreground rounded px-1.5 py-0.5 text-[0.875em]"
                              {...props}
                            >
                              {children}
                            </code>
                          );
                        }
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
      
      <form 
        onSubmit={handleSubmit}
        className=""
      >
        <div className="max-w-4xl mx-auto p-4 md:p-6 ">
          <div className="relative flex items-center">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              
              className="min-h-[60px] w-full resize-none bg-card pr-20 text-base rounded-xl border-secondary/50 focus:border-primary/50 focus:ring-primary/50"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <div className="absolute right-0 top-1/2 -translate-y-1/2 pr-4">
              <Button 
                type="submit" 
                size="icon"
                disabled={isLoading || !input.trim()}
                className={cn(
                  "h-10 w-10 rounded-full bg-primary text-primary-foreground shadow-lg",
                  "hover:bg-primary/90 hover:shadow-md transition-all duration-200",
                  "active:scale-95",
                  isLoading && "opacity-50 cursor-not-allowed"
                )}
              >
                <Send className="h-5 w-5" />
                <span className="sr-only">Send message</span>
              </Button>
            </div>
          </div>
          <div className="mt-2 text-xs text-muted-foreground flex items-center gap-2 flex-wrap justify-center">
            <span>Press</span>
            <kbd className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs font-medium">Enter</kbd>
            <span>to send,</span>
            <kbd className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs font-medium">Shift + Enter</kbd>
            <span>for new line</span>
          </div>
        </div>
      </form>
    </div>
  );
}