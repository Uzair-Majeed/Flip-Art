import type { ConversionMode } from '../../types/conversion';

const MODES = [
  { value: 'auto', label: 'Auto detect', description: 'Let the app choose', icon: '✧' },
  { value: 'photo', label: 'Picture to Sketch', description: 'Find the lines', icon: '✎' },
  { value: 'sketch', label: 'Sketch to Picture', description: 'Bring it to life', icon: '◉' },
] as const;

interface Props {
  mode: ConversionMode;
  onChange: (mode: ConversionMode) => void;
}

export function ModeSelector({ mode, onChange }: Props) {
  return (
    <div className="mode-bar" aria-label="Conversion mode">
      {MODES.map(({ value, label, description, icon }) => (
        <button key={value} className={`mode ${mode === value ? 'active' : ''}`} aria-pressed={mode === value} onClick={() => onChange(value)}>
          <span className="mode-icon">{icon}</span>
          <span><strong>{label}</strong><small>{description}</small></span>
          <span className="radio-dot" />
        </button>
      ))}
    </div>
  );
}
