/**
 * Memory browser with search and filters.
 */
import { Search } from 'lucide-react';

export function MemoryBrowser() {
  return (
    <section className="panel">
      <div className="toolbar">
        <Search size={18} />
        <input placeholder="Search memory" />
        <select defaultValue="all">
          <option value="all">All</option>
          <option value="fact">Facts</option>
          <option value="preference">Preferences</option>
          <option value="event">Events</option>
        </select>
      </div>
      <div className="empty">No memories stored yet.</div>
    </section>
  );
}
