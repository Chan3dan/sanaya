/**
 * Chat history and message queue routes.
 */
import { randomUUID } from 'node:crypto';
import { Router } from 'express';
import type Redis from 'ioredis';

export default function chatRouter(publisher: Redis): Router {
  const router = Router();
  router.get('/history', (_req, res) => res.json([]));
  router.post('/message', async (req, res) => {
    const messageId = randomUUID();
    await publisher.publish('voice.manual_input', JSON.stringify({ message_id: messageId, text: req.body.text ?? '' }));
    res.json({ queued: true, message_id: messageId });
  });
  router.delete('/history', (_req, res) => res.json({ deleted: true }));
  return router;
}
