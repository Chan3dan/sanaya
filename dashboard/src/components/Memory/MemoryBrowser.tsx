/**
 * Memory browser with search, filters, and manual memory creation.
 */
import { FormEvent, useEffect, useState } from 'react';
import { Plus, Search, Trash2 } from 'lucide-react';

interface MemoryItem {
  id: string;
  type: string;
  content: string;
  summary: string;
  importance: number;
  tags: string[];
}

const apiUrl = 'http://127.0.0.1:3001';

export function MemoryBrowser() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('all');
  const [content, setContent] = useState('');
  const [memories, setMemories] = useState<MemoryItem[]>([]);

  async function loadMemories(nextQuery = query, nextType = type) {
    const params = new URLSearchParams();
    if (nextQuery.trim()) params.set('q', nextQuery.trim());
    if (nextType !== 'all') params.set('type', nextType);
    const endpoint = nextQuery.trim() ? 'search' : '';
    const response = await fetch(`${apiUrl}/api/v1/memory/${endpoint}?${params.toString()}`);
    setMemories(await response.json());
  }

  useEffect(() => {
    void loadMemories('', 'all');
  }, []);

  async function addMemory(event: FormEvent) {
    event.preventDefault();
    if (!content.trim()) return;
    await fetch(`${apiUrl}/api/v1/memory`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ content: content.trim(), type: type === 'all' ? 'fact' : type, source: 'dashboard' })
    });
    setContent('');
    await loadMemories();
  }

  async function deleteMemory(id: string) {
    await fetch(`${apiUrl}/api/v1/memory/${id}`, { method: 'DELETE' });
    await loadMemories();
  }

  return (
    <section className="panel memory-panel">
      <div className="toolbar">
        <Search size={18} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} onKeyUp={() => void loadMemories()} placeholder="Search memory" />
        <select
          value={type}
          onChange={(event) => {
            setType(event.target.value);
            void loadMemories(query, event.target.value);
          }}
        >
          <option value="all">All</option>
          <option value="fact">Facts</option>
          <option value="preference">Preferences</option>
          <option value="event">Events</option>
        </select>
      </div>
      <form onSubmit={addMemory} className="composer">
        <input value={content} onChange={(event) => setContent(event.target.value)} placeholder="Add memory" />
        <button type="submit" aria-label="Add memory"><Plus size={18} /></button>
      </form>
      <div className="memory-list">
        {memories.length === 0 && <div className="empty">No memories stored yet.</div>}
        {memories.map((memory) => (
          <article className="message" key={memory.id}>
            <p>{memory.content || memory.summary}</p>
            <small>{memory.type} · importance {memory.importance.toFixed(1)}</small>
            <button type="button" aria-label={`Delete memory ${memory.id}`} onClick={() => void deleteMemory(memory.id)}><Trash2 size={16} /></button>
          </article>
        ))}
      </div>
    </section>
  );
}
