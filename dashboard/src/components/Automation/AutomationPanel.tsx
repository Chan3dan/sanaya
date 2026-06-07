/**
 * Manual Phase 1 automation command runner.
 */
import { FormEvent, useEffect, useState } from 'react';
import { Play } from 'lucide-react';

interface Plugin {
  name: string;
  description: string;
}

interface TaskResult {
  id: string;
  plugin: string;
  status: string;
  result?: { message?: string };
  error?: string;
}

const apiUrl = 'http://127.0.0.1:3001';

export function AutomationPanel() {
  const [command, setCommand] = useState('Hey Sanaya, open calculator');
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [result, setResult] = useState<TaskResult | null>(null);
  const [isRunning, setRunning] = useState(false);

  useEffect(() => {
    fetch(`${apiUrl}/api/v1/automation/plugins`)
      .then((response) => response.json())
      .then(setPlugins)
      .catch(() => setPlugins([]));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!command.trim() || isRunning) return;
    setRunning(true);
    try {
      const response = await fetch(`${apiUrl}/api/v1/automation/voice/manual`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ command })
      });
      setResult(await response.json());
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="panel automation-panel">
      <form onSubmit={submit} className="composer">
        <input value={command} onChange={(event) => setCommand(event.target.value)} disabled={isRunning} />
        <button type="submit" aria-label="Run command" disabled={isRunning}><Play size={18} /></button>
      </form>
      <div className="status-grid">
        {plugins.map((plugin) => (
          <div className="status-item" key={plugin.name}>
            <span>{plugin.name}</span>
            <b className="ok">loaded</b>
          </div>
        ))}
      </div>
      {result && (
        <article className={`message ${result.status === 'failed' ? 'system' : 'assistant'}`}>
          <p>{result.result?.message ?? result.error ?? result.status}</p>
          <small>{result.plugin} · {result.status}</small>
        </article>
      )}
    </section>
  );
}
