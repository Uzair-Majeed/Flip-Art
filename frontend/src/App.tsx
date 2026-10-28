import { ConversionWorkspace } from './components/conversion/ConversionWorkspace';
import { Hero } from './components/home/Hero';
import { ModelInfo } from './components/home/ModelInfo';
import { SiteFooter } from './components/layout/SiteFooter';
import { SiteHeader } from './components/layout/SiteHeader';

export default function App() {
  return (
    <>
      <SiteHeader />
      <main>
        <Hero />
        <ConversionWorkspace />
        <ModelInfo />
      </main>
      <SiteFooter />
    </>
  );
}
