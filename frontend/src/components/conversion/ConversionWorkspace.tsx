import { useState } from 'react';
import { useCamera } from '../../hooks/useCamera';
import { useConversion } from '../../hooks/useConversion';
import type { ImageKind, InputTab } from '../../types/conversion';
import { ConversionSettings } from './ConversionSettings';
import { InputPanel } from './InputPanel';
import { InputPreview } from './InputPreview';
import { ModeSelector } from './ModeSelector';
import { OutputPanel } from './OutputPanel';

export function ConversionWorkspace() {
  const conversion = useConversion();
  const camera = useCamera({ onCapture: conversion.setImage, onError: conversion.setError });
  const [tab, setTab] = useState<InputTab>('upload');

  async function upload(file?: File) {
    if (await conversion.loadFile(file)) camera.stop();
  }

  async function sample(kind: ImageKind) {
    if (await conversion.loadSample(kind)) {
      camera.stop();
      setTab('upload');
    }
  }

  async function startCamera() {
    if (await camera.start()) conversion.reset();
  }

  function changeTab(value: InputTab) {
    setTab(value);
    if (value === 'upload') camera.stop();
  }

  function reset() {
    camera.stop();
    conversion.reset();
  }

  return (
    <section id="workspace" className="workspace">
      <div className="workspace-heading">
        <div><span className="eyebrow">YOUR CREATIVE WORKSPACE</span><h2>Make the switch.</h2></div>
        <span className="local-note">● Local processing · No cloud uploads</span>
      </div>
      <fieldset className="work-controls" disabled={conversion.busy}>
        <legend className="sr-only">Conversion settings</legend>
        <ModeSelector mode={conversion.mode} onChange={conversion.setMode} />
        <div className="panels">
          <InputPanel
            source={conversion.source} name={conversion.name} tab={tab} camera={camera}
            onTabChange={changeTab} onFile={upload} onSample={sample} onStartCamera={startCamera}
          />
          <OutputPanel result={conversion.result} busy={conversion.busy} />
        </div>
        <ConversionSettings
          mode={conversion.mode} preview={conversion.preview} options={conversion.options}
          busy={conversion.busy} preparing={conversion.preparing}
          canConvert={Boolean(conversion.source && conversion.preview)}
          onChange={conversion.updateOptions} onConvert={conversion.convert}
        />
      </fieldset>
      {conversion.error && <div role="alert" className="error">{conversion.error}</div>}
      {conversion.preview && <InputPreview preview={conversion.preview} busy={conversion.busy} onReset={reset} />}
      <p className="workspace-note">Best with tightly framed faces. Sketch cleanup can reduce noise, but cannot restore missing facial details.</p>
    </section>
  );
}
