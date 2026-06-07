/**
 * System health strip for Sanaya modules.
 */
import { Activity, Cpu, Database, Radio } from 'lucide-react';

export function StatusBar({ connected }: { connected: boolean }) {
  const modules = [
    ['Voice', Radio],
    ['AI', Activity],
    ['Memory', Database],
    ['Automation', Cpu]
  ] as const;
  return (
    <section className="status-grid">
      {modules.map(([name, Icon]) => (
        <div className="status-item" key={name}>
          <Icon size={18} />
          <span>{name}</span>
          <b className={connected ? 'ok' : 'warn'}>{connected ? 'ready' : 'offline'}</b>
        </div>
      ))}
    </section>
  );
}
