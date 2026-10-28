export function Hero() {
  return (
    <section className="intro">
      <div>
        <p className="eyebrow">A LITTLE SCIENCE. A DIFFERENT PERSPECTIVE.</p>
        <h1>From face to sketch.<br />And back again<span className="orange">.</span></h1>
        <p className="lede">Explore two sides of the same face with CycleGAN.<br />Your images, transformed locally.</p>
      </div>
      <div className="hero-pair" aria-label="Example face photo and sketch">
        <figure><img src="/samples/photo.png" alt="Sample face photo" /><figcaption>THE PHOTOGRAPH</figcaption></figure>
        <span className="swap">↔</span>
        <figure className="sketch-card"><img src="/samples/sketch.png" alt="Sample face sketch" /><figcaption>THE SKETCH</figcaption></figure>
      </div>
    </section>
  );
}
