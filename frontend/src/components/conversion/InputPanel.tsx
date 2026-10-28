import { useRef } from 'react';
import type { CameraController } from '../../hooks/useCamera';
import type { ImageKind, InputTab } from '../../types/conversion';

interface Props {
  source: string | null;
  name: string;
  tab: InputTab;
  camera: CameraController;
  onTabChange: (tab: InputTab) => void;
  onFile: (file?: File) => void;
  onSample: (kind: ImageKind) => void;
  onStartCamera: () => void;
}

export function InputPanel({ source, name, tab, camera, onTabChange, onFile, onSample, onStartCamera }: Props) {
  const fileInput = useRef<HTMLInputElement>(null);
  const browse = () => fileInput.current?.click();
  return (
    <section className="panel">
      <div className="panel-heading">
        <h3><span>01</span> Your input</h3>
        <div className="tabs">
          {(['upload', 'camera'] as const).map(value => (
            <button key={value} aria-pressed={tab === value} className={tab === value ? 'selected' : ''} onClick={() => onTabChange(value)}>
              {value === 'upload' ? 'Upload' : 'Camera'}
            </button>
          ))}
        </div>
      </div>
      <div
        className={`image-stage ${!source && !camera.active ? 'empty-stage' : ''}`}
        onDragOver={event => event.preventDefault()}
        onDrop={event => { event.preventDefault(); if (tab === 'upload') onFile(event.dataTransfer.files[0]); }}
      >
        {camera.active ? (
          <video ref={camera.videoRef} autoPlay playsInline muted className="camera-video" />
        ) : source ? (
          <img src={source} alt="Original input" />
        ) : (
          <div className="empty-content">
            <span className="upload-symbol">{tab === 'upload' ? '↑' : '◎'}</span>
            <h4>{tab === 'upload' ? 'Start with a face.' : 'Step into the frame.'}</h4>
            <p>{tab === 'upload' ? 'Drop your photo or sketch here' : 'Capture a well-lit, front-facing photo'}</p>
            <button className="secondary" onClick={tab === 'upload' ? browse : onStartCamera}>
              {tab === 'upload' ? 'Browse files' : 'Enable camera'}
            </button>
            <small>{tab === 'upload' ? 'PNG, JPG, BMP, WebP · Up to 10 MB' : 'Your camera stays on your device'}</small>
          </div>
        )}
      </div>
      <input
        ref={fileInput} type="file" accept=".png,.jpg,.jpeg,.bmp,.webp"
        className="sr-only" aria-label="Upload a photo or sketch"
        onChange={event => { onFile(event.target.files?.[0]); event.target.value = ''; }}
      />
      <div className="input-footer">
        {source || camera.active ? (
          <>
            <span className="filename">{camera.active ? 'Live camera · preview mirrored' : name}</span>
            <button className="text-button" onClick={camera.active ? camera.capture : tab === 'camera' ? onStartCamera : browse}>
              {camera.active ? 'Capture photo' : tab === 'camera' ? 'Retake' : 'Replace image'}
            </button>
          </>
        ) : (
          <>
            <span>Need inspiration?</span>
            <button className="text-button" onClick={() => onSample('photo')}>Try a photo</button>
            <button className="text-button" onClick={() => onSample('sketch')}>Try a sketch</button>
          </>
        )}
      </div>
    </section>
  );
}
