import React from 'react';
import { FileText } from 'lucide-react';

const SlidesDemoSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Slides & Demo</h2>
      
      {/* Implements the desired two-column layout */}
      <div className="grid grid-cols-2 gap-8">
        
        {/* === LEFT COLUMN: Slides Content === */}
        <div className="space-y-4"> 
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Presentation Slides</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-center">
              <FileText className="w-5 h-5 text-indigo-600 mr-2 shrink-0" />
              <a 
                href="./midterm_presentation.pdf" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-800 hover:underline truncate"
              >
                Midterm Presentation Slides (PDF)
              </a>
            </div>
            <div className="flex items-center justify-center">
              <FileText className="w-5 h-5 text-indigo-600 mr-2 shrink-0" />
              <a 
                href="./final_presentation_group12.pdf" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-800 hover:underline truncate"
              >
                Final Presentation Slides (PDF)
              </a>
            </div>
          </div>
        </div>

        {/* === RIGHT COLUMN: Demo Content === 
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Demo</h3>
          <div className="flex items-center justify-center">
            <Video className="w-5 h-5 text-indigo-600 mr-2 shrink-0" />
            <a 
              href="https://youtube.com/your-demo-video" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-indigo-600 hover:text-indigo-800 hover:underline"
            >
              Watch Project Demo
            </a>
          </div>
        </div>
        */}
      </div>
    </section>
  );
};

export default SlidesDemoSection;