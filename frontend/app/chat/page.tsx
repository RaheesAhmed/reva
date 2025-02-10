'use client';

import { useState, useEffect } from 'react';
import Chat, { Message } from '@/components/Chat';
import ToolSelector from '@/components/ToolSelector';

import { Button } from "@/components/ui/button";
import { Menu, MessageSquare, Settings2, Plus, Trash2, AlertCircle } from "lucide-react";
import { cn } from '@/lib/utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface ChatHistory {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isToolsOpen, setIsToolsOpen] = useState(true);
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | undefined>();

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('chat_history');
    if (savedHistory) {
      const history = JSON.parse(savedHistory);
      setChatHistory(history);
      // Set the most recent chat as current if exists
      if (history.length > 0) {
        setCurrentChatId(history[0].id);
      }
    }
  }, []);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem('chat_history', JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  const createNewChat = () => {
    const newChat: ChatHistory = {
      id: Date.now().toString(),
      title: 'New Chat',
      lastMessage: '',
      timestamp: new Date(),
    };
    setChatHistory(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
  };

  const updateChatHistory = (message: Message) => {
    if (!currentChatId) return;

    setChatHistory(prev => prev.map(chat => {
      if (chat.id === currentChatId) {
        // Update chat title based on first user message if it's "New Chat"
        const title = chat.title === 'New Chat' && message.role === 'user' 
          ? message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
          : chat.title;

        return {
          ...chat,
          title,
          lastMessage: message.content,
          timestamp: message.timestamp,
        };
      }
      return chat;
    }));
  };

  const deleteChat = (chatId: string, event?: React.MouseEvent) => {
    if (event) {
      event.stopPropagation();
    }
    setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId) {
      const remainingChats = chatHistory.filter(chat => chat.id !== chatId);
      setCurrentChatId(remainingChats.length > 0 ? remainingChats[0].id : undefined);
    }
    if (chatHistory.length === 1) {
      localStorage.removeItem('chat_history');
    }
  };

  const deleteAllChats = () => {
    setChatHistory([]);
    setCurrentChatId(undefined);
    localStorage.removeItem('chat_history');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Overlay for mobile when sidebar or tools are open */}
      {(isSidebarOpen || isToolsOpen) && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 md:hidden"
          onClick={() => {
            setIsSidebarOpen(false);
            setIsToolsOpen(false);
          }}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed md:relative z-40 w-[280px] md:w-80 border-r",
        "transition-all duration-300 ease-in-out shadow-lg h-full",
        "bg-background",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-full flex-col">
          <div className="border-b p-4 bg-background">
            <Button 
              onClick={createNewChat}
              className="w-full justify-center space-x-2 bg-primary hover:bg-primary/20 text-white font-medium"
              variant="ghost"
            >
              <Plus className="h-5 w-5" />
              <span>New Chat</span>
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                onClick={() => setCurrentChatId(chat.id)}
                className={cn(
                  "flex items-center space-x-3 px-4 py-3 rounded-xl cursor-pointer group bg-background",
                  "hover:bg-secondary/80 transition-all duration-200",
                  currentChatId === chat.id 
                    ? "bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20" 
                    : "hover:translate-x-1"
                )}
              >
                <MessageSquare className={cn(
                  "h-5 w-5 shrink-0",
                  currentChatId === chat.id ? "text-primary" : "text-muted-foreground"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate text-sm">{chat.title}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {chat.lastMessage || "No messages yet"}
                  </div>
                </div>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-all duration-200"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive transition-colors" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete chat</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete this chat? This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => deleteChat(chat.id)}>
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            ))}
          </div>
          <div className="border-t p-4 bg-background">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-muted-foreground hover:text-destructive transition-colors"
                  disabled={chatHistory.length === 0}
                >
                  <Trash2 className="mr-2 h-5 w-5" />
                  Clear All Chats
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Clear all chats</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete all chats? This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={deleteAllChats}>
                    Delete All
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-background relative">
        <header className="border-b shadow-sm z-20 relative bg-background">
          <div className="flex h-14 md:h-16 items-center gap-4 px-4 md:px-6">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hover:bg-primary/10 md:flex"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex-1 font-semibold text-base md:text-lg truncate">
              {currentChatId 
                ? chatHistory.find(chat => chat.id === currentChatId)?.title || "New Chat"
                : "Select or create a chat"}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsToolsOpen(!isToolsOpen)}
              className={cn(
                "hover:bg-primary/10",
                isToolsOpen && "text-primary bg-primary/10"
              )}
            >
              <Settings2 className="h-5 w-5" />
            </Button>
           
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden relative">
          <div className="flex-1 relative flex flex-col bg-background z-10">
            {currentChatId ? (
              <Chat
                selectedTools={selectedTools}
                chatId={currentChatId}
                onUpdateHistory={updateChatHistory}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground p-4">
                <div className="text-center space-y-6 animate-in fade-in-50 scale-95">
                  <div className="rounded-full bg-primary/10 p-3 w-fit mx-auto">
                    <MessageSquare className="h-6 md:h-8 w-6 md:w-8 text-primary" />
                  </div>
                  <div>
                    <div className="text-lg md:text-xl font-semibold text-foreground mb-2">No chat selected</div>
                    <div className="text-sm max-w-sm mx-auto text-muted-foreground">
                      Create a new chat or select an existing one to start your conversation
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Tools Panel */}
          <div className={cn(
            "fixed md:relative right-0 top-[3.5rem] md:top-0 z-40 w-[280px] md:w-80 border-l",
            "transition-all duration-300 ease-in-out flex flex-col",
            "h-[calc(100vh-3.5rem)] md:h-full",
            "bg-background shadow-lg",
            isToolsOpen ? "translate-x-0" : "translate-x-full"
          )}>
            <div className="p-4 md:p-6 border-b bg-background">
              <h2 className="font-semibold text-lg text-foreground flex items-center gap-2">
                <Settings2 className="h-5 w-5 text-muted-foreground" />
                Available Tools
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar bg-background">
              <div className="p-4 md:p-6 pt-4">
                <ToolSelector
                  selectedTools={selectedTools}
                  onToolsChange={setSelectedTools}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
