/**
 * Automation plugin routes proxied to Sanaya core.
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

export default function automationRouter(): Router {
  const router = Router();
  router.get('/plugins', async (_req, res) => {
    const response = await fetch(`${coreUrl}/automation/plugins`);
    await sendCoreResponse(response, res);
  });
  router.post('/run', async (req, res) => {
    const response = await fetch(`${coreUrl}/automation/run`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    await sendCoreResponse(response, res);
  });
  router.post('/voice/manual', async (req, res) => {
    const response = await fetch(`${coreUrl}/voice/manual`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    await sendCoreResponse(response, res);
  });
  return router;
}
