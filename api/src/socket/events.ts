/**
 * Socket.IO event bridge for client-originated Sanaya events.
 */
import type Redis from 'ioredis';
import type { Server } from 'socket.io';

export function registerSocketEvents(io: Server, publisher: Redis): void {
  io.on('connection', (socket) => {
    socket.emit('module.health', { module: 'api', status: 'ok' });

    socket.on('voice.manual_input', async (payload) => {
      await publisher.publish('voice.manual_input', JSON.stringify(payload));
    });
    socket.on('conversation.clear', async () => {
      await publisher.publish('conversation.clear', JSON.stringify({}));
    });
    socket.on('task.cancel', async (payload) => {
      await publisher.publish('task.cancel', JSON.stringify(payload));
    });
  });
}
