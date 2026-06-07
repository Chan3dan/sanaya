/**
 * Chat surface with streaming-ready message list and manual input.
 */
import { FormEvent, useState } from 'react';
import { Send } from 'lucide-react';
import { Socket } from 'socket.io-client';
import { useAppStore } from '../../store/useAppStore';
import { VoiceIndicator } from './VoiceIndicator';

export function ChatWindow({ socket }: { socket: Socket | null }) {
  const [text, setText] = useState('');
  const { messages, voiceStatus, addMessage } = useAppStore();

  function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    addMessage({ id: crypto.randomUUID(), role: 'user', content: trimmed, timestamp: new Date().toISOString() });
    socket?.emit('voice.manual_input', { text: trimmed });
    setText('');
  }

  return (
    <section className="chat">
      <VoiceIndicator status={voiceStatus} />
      <div className="messages">
        {messages.map((message) => (
          <article key={message.id} className={`message ${message.role}`}>
            <p>{message.content}</p>
            <small>{message.provider ?? message.role} · {new Date(message.timestamp).toLocaleTimeString()}</small>
          </article>
        ))}
      </div>
      <form onSubmit={submit} className="composer">
        <input value={text} onChange={(event) => setText(event.target.value)} placeholder="Message Sanaya" />
        <button type="submit" aria-label="Send"><Send size={18} /></button>
      </form>
    </section>
  );
}
