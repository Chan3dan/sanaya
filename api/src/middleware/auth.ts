/**
 * JWT middleware for Phase 1 single-user API protection.
 */
import type { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthenticatedRequest extends Request {
  user?: string | jwt.JwtPayload;
}

export function auth(req: AuthenticatedRequest, res: Response, next: NextFunction): void {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Missing bearer token' });
    return;
  }
  try {
    req.user = jwt.verify(header.slice(7), process.env.JWT_SECRET ?? 'change-this-to-a-random-64-char-string');
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}
