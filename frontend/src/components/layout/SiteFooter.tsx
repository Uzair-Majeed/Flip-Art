import { Brand } from './Brand';

export function SiteFooter() {
  return (
    <footer>
      <span className="brand"><Brand /></span>
      <span>
        A CycleGAN exploration · Built to run locally<br />
        Built by Uzair Majeed &amp; Faez Ahmed
      </span>
    </footer>
  );
}
