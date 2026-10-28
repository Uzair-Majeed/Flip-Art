import { useEffect, useState } from 'react';
import { checkHealth } from '../api/client';
import type { BackendStatus } from '../types/conversion';

export function useBackendHealth(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>('Connecting');

  useEffect(() => {
    const controller = new AbortController();
    checkHealth(controller.signal)
      .then(() => { if (!controller.signal.aborted) setStatus('Models ready'); })
      .catch(() => { if (!controller.signal.aborted) setStatus('Backend unavailable'); });
    return () => controller.abort();
  }, []);

  return status;
}
