/**
 * Chat surface with streaming-ready message list and manual input.
 */
import { FormEvent, useState } from 'react';
import { Send } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { VoiceIndicator } from './VoiceIndicator';

interface ChatResponse {
  content: string;
  provider: string;
}

const apiUrl = 'http://127.0.0.1:3001';

export function ChatWindow() {
  const [text, setText] = useState('');
  const [isSending, setSending] = useState(false);
  const { messages, voiceStatus, addMessage } = useAppStore();

  async function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isSending) return;
    addMessage({ id: crypto.randomUUID(), role: 'user', content: trimmed, timestamp: new Date().toISOString() });
    setText('');
    setSending(true);
    try {
      const response = await fetch(`${apiUrl}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ text: trimmed })
      });
      if (!response.ok) {
        throw new Error(`Chat request failed with ${response.status}`);
      }
      const data = (await response.json()) as ChatResponse;
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.content,
        provider: data.provider,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      addMessage({
        id: crypto.randomUUID(),
        role: 'system',
        content: error instanceof Error ? error.message : 'Chat request failed.',
        timestamp: new Date().toISOString()
      });
    } finally {
      setSending(false);
    }
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
        <input value={text} onChange={(event) => setText(event.target.value)} placeholder="Message Sanaya" disabled={isSending} />
        <button type="submit" aria-label="Send" disabled={isSending}><Send size={18} /></button>
      </form>
    </section>
  );
}
