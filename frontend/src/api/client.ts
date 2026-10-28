import type { ConversionRequest, ConversionResult, ImageKind, ImagePreview } from '../types/conversion';

async function postImage<T>(path: string, payload: ConversionRequest, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The image request failed.');
  return data as T;
}

export const previewImage = (payload: ConversionRequest, signal: AbortSignal) =>
  postImage<ImagePreview>('/api/preview', payload, signal);

export const convertImage = (payload: ConversionRequest) =>
  postImage<ConversionResult>('/api/convert', payload);

export async function checkHealth(signal: AbortSignal): Promise<void> {
  const response = await fetch('/health', { signal });
  if (!response.ok || !(await response.json()).models_loaded) {
    throw new Error('Backend unavailable');
  }
}

export async function fetchSample(kind: ImageKind): Promise<File> {
  const response = await fetch(`/samples/${kind}.png`);
  if (!response.ok) throw new Error('Sample could not be loaded. Please upload an image.');
  return new File([await response.blob()], `sample_${kind}.png`, { type: 'image/png' });
}
