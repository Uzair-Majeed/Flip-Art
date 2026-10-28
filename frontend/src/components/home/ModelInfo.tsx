export function ModelInfo() {
  return (
    <section id="about" className="about">
      <div>
        <span className="eyebrow">BEHIND THE TRANSFORMATION</span>
        <h2>Two worlds.<br />One learning cycle.</h2>
        <p>CycleGAN learns to translate between face photographs and pencil sketches without needing paired examples during training. FlipArt runs your trained ResNet-6 generators locally.</p>
        <p className="muted">The model generates at 128 × 128 pixels; results are enlarged for display. Sparse sketches may produce distorted faces. Detection confidence is a heuristic score, not measured accuracy.</p>
      </div>
      <div className="model-details">
        <div className="stats">
          <div><strong>11</strong><span>Training epochs</span></div>
          <div><strong>128²</strong><span>Native resolution</span></div>
          <div><strong>6</strong><span>Residual blocks</span></div>
        </div>
        <table>
          <caption>Reported model FID · Lower is better</caption>
          <thead><tr><th>Direction</th><th>Validation</th><th>Test</th></tr></thead>
          <tbody>
            <tr><td>Picture → Sketch</td><td>135.8</td><td>142.1</td></tr>
            <tr><td>Sketch → Picture</td><td>68.5</td><td>76.5</td></tr>
          </tbody>
        </table>
        <p className="dataset">Trained on the Person Face Sketches dataset.</p>
      </div>
    </section>
  );
}
