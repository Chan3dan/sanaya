/**
 * Animated voice state indicator.
 */
import { Mic } from 'lucide-react';
import type { VoiceStatus } from '../../store/useAppStore';

export function VoiceIndicator({ status }: { status: VoiceStatus }) {
  const active = status !== 'idle';
  return (
    <div className="voice-indicator">
      <Mic size={18} />
      <span>{status}</span>
      <div className={`bars ${active ? 'active' : ''}`}>
        <i />
        <i />
        <i />
      </div>
    </div>
  );
}
