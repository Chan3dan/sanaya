/**
 * Memory REST routes for Phase 1 dashboard use.
 */
import { Router } from 'express';

export default function memoryRouter(): Router {
  const router = Router();
  router.get('/', (_req, res) => res.json([]));
  router.post('/', (req, res) => res.status(202).json({ queued: true, ...req.body }));
  router.patch('/:id', (req, res) => res.json({ id: req.params.id, ...req.body }));
  router.delete('/:id', (req, res) => res.json({ deleted: true, id: req.params.id }));
  router.get('/search', (_req, res) => res.json([]));
  return router;
}
