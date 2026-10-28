import type { ConversionMode, ConversionOptions, ImagePreview } from '../../types/conversion';

interface Props {
  mode: ConversionMode;
  preview: ImagePreview | null;
  options: ConversionOptions;
  busy: boolean;
  preparing: boolean;
  canConvert: boolean;
  onChange: (update: Partial<ConversionOptions>) => void;
  onConvert: () => void;
}

export function ConversionSettings({ mode, preview, options, busy, preparing, canConvert, onChange, onConvert }: Props) {
  const toSketch = preview ? preview.direction === 'photo->sketch' : mode !== 'sketch';
  const cleanupDisabled = mode === 'photo' || (mode === 'auto' && preview?.detected_type === 'photo');
  return (
    <div className="settings">
      <div>
        <p className="settings-label">FINE-TUNE YOUR CONVERSION</p>
        <div className="checks">
          <label><input type="checkbox" checked={options.face_crop} disabled={!toSketch} onChange={event => onChange({ face_crop: event.target.checked })} /> Face crop</label>
          <label><input type="checkbox" checked={options.grayscale_sketch} disabled={!toSketch} onChange={event => onChange({ grayscale_sketch: event.target.checked })} /> Grayscale sketch</label>
          <label><input type="checkbox" checked={options.enhance_contrast} disabled={!toSketch} onChange={event => onChange({ enhance_contrast: event.target.checked })} /> Enhance contrast</label>
          <label><input type="checkbox" checked={options.clean_sketch} disabled={cleanupDisabled} onChange={event => onChange({ clean_sketch: event.target.checked })} /> Clean up sketch</label>
        </div>
      </div>
      <button className="primary" disabled={!canConvert || preparing || busy} onClick={onConvert}>
        {busy ? 'Converting…' : preparing ? 'Preparing input…' : 'Convert image'} <span>↗</span>
      </button>
    </div>
  );
}
