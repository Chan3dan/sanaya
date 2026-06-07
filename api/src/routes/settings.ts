/**
 * Settings, provider, and health routes.
 */
import { Router } from 'express';

export default function settingsRouter(): Router {
  const router = Router();
  router.get('/settings', (_req, res) => res.json({ ai: { default_provider: 'ollama' }, privacy: { mode: false } }));
  router.patch('/settings', (req, res) => res.json(req.body));
  router.get('/health', (_req, res) => res.json({ status: 'ok', redis: 'unknown', modules: [] }));
  router.get('/providers', (_req, res) => res.json([{ name: 'ollama', status: 'configured', local: true }]));
  return router;
}
