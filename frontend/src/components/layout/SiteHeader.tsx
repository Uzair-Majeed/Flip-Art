import { useBackendHealth } from '../../hooks/useBackendHealth';
import { Brand } from './Brand';

export function SiteHeader() {
  const health = useBackendHealth();
  return (
    <header className="topbar">
      <a className="brand" href="#" aria-label="FlipArt home"><Brand /></a>
      <nav><a href="#workspace">Workspace</a><a href="#about">About the model</a></nav>
      <span className={`status ${health === 'Models ready' ? 'ready' : ''}`}><i />{health}</span>
    </header>
  );
}
