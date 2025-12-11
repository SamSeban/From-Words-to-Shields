import './App.css'
import Navbar from './components/navbar';
import TeamPage from './components/team';
import AbstractSection, { TableOfContents } from './components/abstract';
import SlidesDemoSection from './components/slidesDemo';
import IntroductionSection from './components/introduction';
import RelatedWorkSection from './components/related_work';
import TechnicalApproachSection from './components/technicalApproach';
import InteractiveDemo from './components/interactiveDemo';
import ResultsSection from './components/results';
import ConclusionSection from './components/conclusion';
import ReferencesSection from './components/references';
import SupplementarySection from './components/supplementary';


function App() {

  // const [currentPage, setCurrentPage] = useState<Page>('home');

  // const renderPage = () => {
  //   switch (currentPage) {
  //     case 'team':
  //       return <TeamPage />;
  //     case 'documents':
  //       return <DocumentsPage />;
  //     case 'home':
  //     default:
  //       return <HomePage />;
  //   }
  // };


return (
  <div className="min-h-screen flex flex-col font-sans bg-gray-50">
    <Navbar />
    <TableOfContents />
    <main className="grow  mx-auto p-4 sm:p-6 lg:p-8">
      <div id="team">
        <TeamPage />
      </div>
      <AbstractSection />
      <div id="interactive-demo">
        <InteractiveDemo />
      </div>
      <div id="slides-demo">
        <SlidesDemoSection />
      </div>
      <div id="introduction">
        <IntroductionSection />
      </div>
      <div id="related-work">
        <RelatedWorkSection />
      </div>
      <div id="technical-approach">
        <TechnicalApproachSection />
      </div>
      <div id="results">
        <ResultsSection />
      </div>
      <div id="conclusion">
        <ConclusionSection />
      </div>
      <div id="references">
        <ReferencesSection />
      </div>
      <div id="supplementary">
        <SupplementarySection />
      </div>
    </main>
  </div>
)
}

export default App
