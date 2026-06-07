/**
 * Express and Socket.IO gateway bridging dashboard clients to Redis events.
 */
import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import helmet from 'helmet';
import Redis from 'ioredis';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { createServer } from 'node:http';
import { Server } from 'socket.io';
import winston from 'winston';
import chatRouter from './routes/chat';
import memoryRouter from './routes/memory';
import settingsRouter from './routes/settings';
import { registerSocketEvents } from './socket/events';

dotenv.config({ path: '../.env' });

const logger = winston.createLogger({
  level: process.env.SANAYA_LOG_LEVEL?.toLowerCase() ?? 'info',
  transports: [new winston.transports.Console()]
});

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, { cors: { origin: '*' } });
const port = Number(process.env.SANAYA_API_PORT ?? 3001);
const redisUrl = process.env.REDIS_URL ?? 'redis://localhost:6379';
const publisher = new Redis(redisUrl);
const subscriber = new Redis(redisUrl);

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));
app.use(rateLimit({ windowMs: 60_000, limit: 120 }));
app.use('/api/v1/chat', chatRouter(publisher));
app.use('/api/v1/memory', memoryRouter());
app.use('/api/v1', settingsRouter());

registerSocketEvents(io, publisher);

const channels = [
  'ai.token',
  'ai.response.done',
  'voice.status',
  'automation.task.complete',
  'memory.stored',
  'wake_word.detected',
  'module.health'
];

subscriber.subscribe(...channels).catch((error) => logger.error('redis.subscribe.failed', error));
subscriber.on('message', (channel, message) => {
  try {
    io.emit(channel, JSON.parse(message));
  } catch (error) {
    logger.warn(`Invalid event payload on ${channel}: ${String(error)}`);
  }
});

httpServer.listen(port, () => logger.info(`Sanaya API listening on ${port}`));
