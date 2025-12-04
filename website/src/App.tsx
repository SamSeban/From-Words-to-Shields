import './App.css'
import Navbar from './components/navbar';
import TeamPage from './components/team';
import AbstractSection from './components/abstract';
import SlidesDemoSection from './components/slidesDemo';
import IntroductionSection from './components/introduction';
import RelatedWorkSection from './components/related_work';

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
    <main className="grow  mx-auto p-4 sm:p-6 lg:p-8">
      <TeamPage />
      <AbstractSection />
      <SlidesDemoSection />
      <IntroductionSection />
      <RelatedWorkSection />
    </main>
  </div>
)
}

export default App
