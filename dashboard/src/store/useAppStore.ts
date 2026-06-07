/**
 * Zustand store for Sanaya dashboard state.
 */
import { create } from 'zustand';

export type VoiceStatus = 'idle' | 'listening' | 'transcribing' | 'speaking';

export interface ConversationTurn {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  provider?: string;
  timestamp: string;
}

interface AppState {
  messages: ConversationTurn[];
  voiceStatus: VoiceStatus;
  isConnected: boolean;
  activeModule: string;
  addMessage: (message: ConversationTurn) => void;
  setVoiceStatus: (status: VoiceStatus) => void;
  setConnected: (connected: boolean) => void;
  setActiveModule: (module: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  voiceStatus: 'idle',
  isConnected: false,
  activeModule: 'Chat',
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setVoiceStatus: (voiceStatus) => set({ voiceStatus }),
  setConnected: (isConnected) => set({ isConnected }),
  setActiveModule: (activeModule) => set({ activeModule })
}));
