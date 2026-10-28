import type { ImagePreview } from '../../types/conversion';
import { pngDataUrl } from '../../utils/images';

interface Props {
  preview: ImagePreview;
  busy: boolean;
  onReset: () => void;
}

export function InputPreview({ preview, busy, onReset }: Props) {
  return (
    <div className="preview-strip">
      <img src={pngDataUrl(preview.input_preview)} alt="Exact prepared model input" />
      <div>
        <strong>{preview.cleanup_applied ? 'Cleaned sketch preview' : 'Model input preview'}</strong>
        <p>Detected: {preview.detected_type === 'photo' ? 'real photo' : 'sketch'} · {Math.round(preview.detection_confidence * 100)}% heuristic confidence{preview.manual_override ? ' · Manual direction selected' : ''}</p>
        <p>{preview.direction === 'photo->sketch' ? 'Picture → Sketch' : 'Sketch → Picture'} · {preview.cleanup_applied ? 'Cleanup on' : 'Cleanup off'} · 128 × 128 input</p>
        {preview.face_found === false && <p className="warning">No face detected, used center crop.</p>}
      </div>
      <button className="text-button" disabled={busy} onClick={onReset}>Convert another ↗</button>
    </div>
  );
}
