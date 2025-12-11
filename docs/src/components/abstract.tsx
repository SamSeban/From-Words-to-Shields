import React, { useEffect, useState } from 'react';

const sections = [
  { id: 'abstract', label: 'Abstract' },
  { id: 'interactive-demo', label: 'Interactive Demo' },
  { id: 'slides-demo', label: 'Slides & Demo' },
  { id: 'introduction', label: 'Introduction' },
  { id: 'related-work', label: 'Related Work' },
  { id: 'technical-approach', label: 'Technical Approach' },
  { id: 'results', label: 'Evaluation & Results' },
  { id: 'conclusion', label: 'Discussion & Conclusions' },
  { id: 'references', label: 'References' },
  { id: 'supplementary', label: 'Supplementary Material' },
];

export const TableOfContents: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>('abstract');
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  useEffect(() => {
    const observers: IntersectionObserver[] = [];

    sections.forEach(({ id }) => {
      const element = document.getElementById(id);
      if (element) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                setActiveSection(id);
              }
            });
          },
          {
            rootMargin: '-20% 0px -60% 0px',
            threshold: 0,
          }
        );
        observer.observe(element);
        observers.push(observer);
      }
    });

    return () => {
      observers.forEach((observer) => observer.disconnect());
    };
  }, []);

  return (
    <nav className="hidden lg:block fixed left-4 top-1/2 -translate-y-1/2 z-50">
      {isCollapsed ? (
        <div
          onClick={() => setIsCollapsed(false)}
          className="bg-white/80 backdrop-blur-sm rounded-md shadow-sm p-1.5 border border-gray-200 hover:bg-white hover:shadow transition-all duration-200 cursor-pointer"
          aria-label="Open table of contents"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      ) : (
        <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-4 border border-gray-100">
          <div className="flex items-center justify-between mb-3">
          <div
              onClick={() => setIsCollapsed(true)}
              className="rounded hover:bg-gray-100 transition-colors duration-200 cursor-pointer"
              aria-label="Close table of contents"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-700 hover:text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </div>
            <h3 className="text-sm font-bold text-indigo-700 uppercase tracking-wider">Contents</h3>
<div></div>
          </div>
          <ul className="space-y-1">
            {sections.map((section) => (
              <li key={section.id}>
                <a
                  href={`#${section.id}`}
                  className={`block py-1.5 px-3 rounded-lg text-sm transition-all duration-200 ${
                    activeSection === section.id
                      ? 'bg-indigo-100 text-indigo-700 font-semibold border-l-2 border-indigo-600'
                      : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'
                  }`}
                >
                  {section.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </nav>
  );
};

const AbstractSection: React.FC = () => {
  return (
    <section id="abstract" className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Abstract</h2>
      <div className="text-gray-700 leading-relaxed">
        <p className="text-justify">
          Modern smart environments pose significant privacy risks as raw sensor data from cameras and microphones 
          is often transmitted directly to third-party cloud services without user control. Existing solutions like 
          Peekaboo enforce local preprocessing but struggle to scale due to their reliance on manually crafted, 
          pre-specified operator pipelines. Our project explores how Large Language Model (LLM)-based agents can 
          autonomously construct, execute, and refine privacy-preserving pipelines for audio, video, and tabular data 
          by translating natural language requirements into executable data-sanitization workflows in real time. 
          Our system achieved an overall 69% success rate, comprising 59% first-attempt success plus an additional 10% recovered through the closed-loop retry mechanism, which rescued 24% of initially failed pipelines. Face detection with our YuNet-KCF-Kalman hybrid maintained continuous tracking with under 10% miss ratio, while the LLM-based keyword detection correctly identified and redacted sensitive phrases across diverse privacy intents. Crucially, the system translates complex privacy requirements into executable workflows in seconds, eliminating the weeks of engineering traditionally required to implement custom privacy pipelines.
          This work demonstrates the feasibility of user-driven privacy enforcement and provides insights into the 
          safe integration of agentic AI into privacy infrastructure, making compliance with dynamic regulations 
          like GDPR more manageable while significantly reducing engineering overhead.
        </p>
      </div>
    </section>
  );
};

export default AbstractSection;
