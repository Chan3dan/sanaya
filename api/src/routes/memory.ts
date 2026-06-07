/**
 * Memory REST routes proxied to Sanaya core.
 */
import { Router } from 'express';

const coreUrl = process.env.SANAYA_CORE_URL ?? 'http://127.0.0.1:8000';

async function sendCoreResponse(response: Response, res: { status: (code: number) => { json: (body: unknown) => void } }): Promise<void> {
  const text = await response.text();
  try {
    res.status(response.status).json(JSON.parse(text));
  } catch {
    res.status(response.status).json({ error: text || response.statusText });
  }
}

export default function memoryRouter(): Router {
  const router = Router();
  router.get('/', async (req, res) => {
    const query = new URLSearchParams();
    if (req.query.type) query.set('type', String(req.query.type));
    const response = await fetch(`${coreUrl}/memory?${query.toString()}`);
    await sendCoreResponse(response, res);
  });
  router.post('/', async (req, res) => {
    const response = await fetch(`${coreUrl}/memory`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    await sendCoreResponse(response, res);
  });
  router.get('/search', async (req, res) => {
    const query = new URLSearchParams();
    if (req.query.q) query.set('q', String(req.query.q));
    if (req.query.type) query.set('type', String(req.query.type));
    const response = await fetch(`${coreUrl}/memory/search?${query.toString()}`);
    await sendCoreResponse(response, res);
  });
  router.patch('/:id', async (req, res) => {
    const response = await fetch(`${coreUrl}/memory/${encodeURIComponent(req.params.id)}`, {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    await sendCoreResponse(response, res);
  });
  router.delete('/:id', async (req, res) => {
    const response = await fetch(`${coreUrl}/memory/${encodeURIComponent(req.params.id)}`, { method: 'DELETE' });
    await sendCoreResponse(response, res);
  });
  return router;
}
