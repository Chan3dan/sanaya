/**
 * Sanaya dashboard application shell.
 */
import { useEffect, useMemo } from 'react';
import { Brain, Database, HeartPulse, MessageSquare, Plug, Settings } from 'lucide-react';
import { io } from 'socket.io-client';
import { ChatWindow } from './components/Chat/ChatWindow';
import { MemoryBrowser } from './components/Memory/MemoryBrowser';
import { StatusBar } from './components/SystemHealth/StatusBar';
import { useAppStore } from './store/useAppStore';
import './styles.css';

const nav = [
  ['Chat', MessageSquare],
  ['Memory', Database],
  ['Plugins', Plug],
  ['Settings', Settings],
  ['Health', HeartPulse]
] as const;

const apiUrl = 'http://127.0.0.1:3001';

export default function App() {
  const socket = useMemo(() => io(apiUrl, { autoConnect: true, transports: ['websocket'] }), []);
  const { activeModule, isConnected, setActiveModule, setConnected, setVoiceStatus } = useAppStore();

  useEffect(() => {
    socket.connect();
    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));
    socket.on('voice.status', (payload: { state: 'idle' | 'listening' | 'transcribing' | 'speaking' }) => setVoiceStatus(payload.state));
    return () => {
      socket.disconnect();
    };
  }, [socket, setConnected, setVoiceStatus]);

  return (
    <main className="app">
      <aside>
        <div className="brand"><Brain size={24} /> Sanaya</div>
        {nav.map(([name, Icon]) => (
          <button className={activeModule === name ? 'active' : ''} key={name} onClick={() => setActiveModule(name)}>
            <Icon size={18} />
            <span>{name}</span>
          </button>
        ))}
      </aside>
      <div className="workspace">
        <header>
          <h1>{activeModule}</h1>
          <span className={isConnected ? 'connected' : 'disconnected'}>{isConnected ? 'connected' : 'offline'}</span>
        </header>
        {activeModule === 'Chat' && <ChatWindow />}
        {activeModule === 'Memory' && <MemoryBrowser />}
        {activeModule === 'Health' && <StatusBar connected={isConnected} />}
        {!['Chat', 'Memory', 'Health'].includes(activeModule) && <section className="panel"><div className="empty">{activeModule} controls are ready for Phase 1 wiring.</div></section>}
      </div>
    </main>
  );
}
