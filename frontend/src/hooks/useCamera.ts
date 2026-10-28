import { useCallback, useEffect, useRef, useState } from 'react';

interface CameraOptions {
  onCapture: (image: string, name: string) => void;
  onError: (message: string) => void;
}

export function useCamera({ onCapture, onError }: CameraOptions) {
  const [active, setActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const requestId = useRef(0);

  const stop = useCallback(() => {
    requestId.current++;
    stream.current?.getTracks().forEach(track => track.stop());
    stream.current = null;
    setActive(false);
  }, []);

  useEffect(() => () => {
    requestId.current++;
    stream.current?.getTracks().forEach(track => track.stop());
  }, []);

  useEffect(() => {
    if (videoRef.current && stream.current) videoRef.current.srcObject = stream.current;
  }, [active]);

  async function start(): Promise<boolean> {
    onError('');
    const id = ++requestId.current;
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera access needs localhost or HTTPS.');
      const media = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      if (id !== requestId.current) {
        media.getTracks().forEach(track => track.stop());
        return false;
      }
      stream.current?.getTracks().forEach(track => track.stop());
      stream.current = media;
      setActive(true);
      return true;
    } catch (error) {
      onError(error instanceof DOMException && error.name === 'NotAllowedError'
        ? 'Camera permission denied. Allow access in your browser, or upload an image.'
        : 'Could not start the camera. Check that it is connected and not being used elsewhere.');
      return false;
    }
  }

  function capture() {
    if (!videoRef.current?.videoWidth) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d')!.drawImage(videoRef.current, 0, 0);
    onCapture(canvas.toDataURL('image/png'), 'Camera capture');
    stop();
  }

  return { active, videoRef, start, stop, capture };
}

export type CameraController = ReturnType<typeof useCamera>;
