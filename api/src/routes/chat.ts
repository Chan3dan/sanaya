/**
 * Chat history and message queue routes.
 */
import { randomUUID } from 'node:crypto';
import { Router } from 'express';
import type Redis from 'ioredis';

const coreUrl = process.env.SANAYA_CORE_URL ?? 'http://127.0.0.1:8000';

async function sendCoreResponse(response: Response, res: { status: (code: number) => { json: (body: unknown) => void } }): Promise<void> {
  const text = await response.text();
  try {
    res.status(response.status).json(JSON.parse(text));
  } catch {
    res.status(response.status).json({ error: text || response.statusText });
  }
}

export default function chatRouter(publisher: Redis): Router {
  const router = Router();
  router.get('/history', async (req, res) => {
    const sessionId = encodeURIComponent(String(req.query.session_id ?? 'default'));
    const response = await fetch(`${coreUrl}/chat/history?session_id=${sessionId}`);
    await sendCoreResponse(response, res);
  });
  router.post('/message', async (req, res) => {
    const messageId = randomUUID();
    const text = String(req.body.text ?? '').trim();
    if (!text) {
      res.status(400).json({ error: 'Message text is required.' });
      return;
    }

    await publisher.publish('voice.manual_input', JSON.stringify({ message_id: messageId, text }));

    try {
      const response = await fetch(`${coreUrl}/chat/message`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ text, session_id: req.body.session_id ?? 'default' })
      });
      await sendCoreResponse(response, res);
    } catch (error) {
      res.status(502).json({ error: error instanceof Error ? error.message : 'Core chat request failed.' });
    }
  });
  router.delete('/history', async (req, res) => {
    const sessionId = encodeURIComponent(String(req.query.session_id ?? 'default'));
    const response = await fetch(`${coreUrl}/chat/history?session_id=${sessionId}`, { method: 'DELETE' });
    await sendCoreResponse(response, res);
  });
  return router;
}
