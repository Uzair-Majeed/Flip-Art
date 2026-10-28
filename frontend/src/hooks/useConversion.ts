import { useEffect, useMemo, useState } from 'react';
import { convertImage, fetchSample, previewImage } from '../api/client';
import type { ConversionMode, ConversionOptions, ConversionResult, ImageKind, ImagePreview } from '../types/conversion';
import { readImageFile } from '../utils/images';

const DEFAULT_OPTIONS: ConversionOptions = {
  face_crop: true,
  grayscale_sketch: true,
  enhance_contrast: false,
  clean_sketch: false,
};

export function useConversion() {
  const [source, setSource] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [mode, setMode] = useState<ConversionMode>('auto');
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [preview, setPreview] = useState<ImagePreview | null>(null);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [preparing, setPreparing] = useState(false);
  const [error, setError] = useState('');
  const payload = useMemo(() => source ? { image: source, mode, ...options } : null, [source, mode, options]);

  useEffect(() => {
    setResult(null);
    setPreview(null);
    if (!payload) {
      setPreparing(false);
      return;
    }
    const controller = new AbortController();
    setPreparing(true);
    setError('');
    const timer = setTimeout(async () => {
      try {
        const data = await previewImage(payload, controller.signal);
        if (!controller.signal.aborted) setPreview(data);
      } catch (error) {
        if (!controller.signal.aborted) setError(error instanceof Error ? error.message : 'Preview failed.');
      } finally {
        if (!controller.signal.aborted) setPreparing(false);
      }
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [payload]);

  function setImage(image: string, filename: string) {
    setSource(image);
    setName(filename);
    setError('');
  }

  function reset() {
    setSource(null);
    setName('');
    setPreview(null);
    setResult(null);
    setError('');
    setPreparing(false);
  }

  async function loadFile(file?: File): Promise<boolean> {
    if (!file || busy) return false;
    setError('');
    try {
      setImage(await readImageFile(file), file.name);
      return true;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not read this file.');
      return false;
    }
  }

  async function loadSample(kind: ImageKind): Promise<boolean> {
    try {
      if (!await loadFile(await fetchSample(kind))) return false;
      setMode(kind);
      return true;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not load the sample.');
      return false;
    }
  }

  async function convert() {
    if (!payload || !preview || preparing || busy) return;
    setBusy(true);
    setError('');
    try {
      setResult(await convertImage(payload));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not connect to Flask.');
    } finally {
      setBusy(false);
    }
  }

  function updateOptions(update: Partial<ConversionOptions>) {
    setOptions(current => ({ ...current, ...update }));
  }

  return {
    source, name, mode, options, preview, result, busy, preparing, error,
    setMode, setError, setImage, updateOptions, loadFile, loadSample, convert, reset,
  };
}
