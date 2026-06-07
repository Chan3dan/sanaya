/**
 * Chat history and message queue routes.
 */
import { randomUUID } from 'node:crypto';
import { Router } from 'express';
import type Redis from 'ioredis';

interface OllamaGenerateResponse {
  response?: string;
}

export default function chatRouter(publisher: Redis): Router {
  const router = Router();
  router.get('/history', (_req, res) => res.json([]));
  router.post('/message', async (req, res) => {
    const messageId = randomUUID();
    const text = String(req.body.text ?? '').trim();
    if (!text) {
      res.status(400).json({ error: 'Message text is required.' });
      return;
    }

    await publisher.publish('voice.manual_input', JSON.stringify({ message_id: messageId, text }));

    const ollamaBaseUrl = process.env.OLLAMA_BASE_URL ?? 'http://127.0.0.1:11434';
    const model = process.env.OLLAMA_CHAT_MODEL ?? 'qwen2.5:0.5b';
    try {
      const response = await fetch(`${ollamaBaseUrl}/api/generate`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          model,
          prompt: text,
          stream: false
        })
      });

      if (!response.ok) {
        res.status(502).json({ error: `Ollama returned ${response.status}` });
        return;
      }

      const data = (await response.json()) as OllamaGenerateResponse;
      const content = data.response?.trim() || 'Sanaya did not return a response.';
      await publisher.publish('ai.response.done', JSON.stringify({ message_id: messageId, provider: 'ollama', model, content }));
      res.json({ message_id: messageId, provider: 'ollama', model, content });
    } catch (error) {
      res.status(502).json({ error: error instanceof Error ? error.message : 'Ollama request failed.' });
    }
  });
  router.delete('/history', (_req, res) => res.json({ deleted: true }));
  return router;
}
