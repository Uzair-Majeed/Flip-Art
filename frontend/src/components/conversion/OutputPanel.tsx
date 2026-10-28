import type { ConversionResult } from '../../types/conversion';
import { pngDataUrl } from '../../utils/images';

interface Props {
  result: ConversionResult | null;
  busy: boolean;
}

export function OutputPanel({ result, busy }: Props) {
  const outputKind = result?.direction === 'photo->sketch' ? 'sketch' : 'photo';
  return (
    <section className="panel result-panel">
      <div className="panel-heading">
        <h3><span>02</span> The transformation</h3>
        <span className="pill">{result ? `${result.inference_ms} ms` : '128 × 128 model'}</span>
      </div>
      <div className={`image-stage ${!result ? 'output-empty' : ''}`} aria-live="polite">
        {result ? <img src={pngDataUrl(result.output_image)} alt={`Generated face ${outputKind}`} /> : (
          <div className="empty-content">
            <span className={busy ? 'spinner' : 'result-symbol'}>{busy ? '' : '✧'}</span>
            <h4>{busy ? 'A new perspective is forming…' : 'A new perspective awaits.'}</h4>
            <p>{busy ? 'Running your image through the trained model' : 'Your generated image will appear here'}</p>
          </div>
        )}
      </div>
      <div className="input-footer">
        <span>{result ? 'Generated locally · Displayed at 512 × 512' : 'Two generators. One creative experiment.'}</span>
        {result && <a className="text-button" href={pngDataUrl(result.output_image)} download={`flipart-${outputKind}.png`}>Download PNG ↓</a>}
      </div>
    </section>
  );
}
