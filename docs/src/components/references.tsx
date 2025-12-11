import React from 'react';

const ReferencesSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">References</h2>
      <div className="text-gray-700 leading-relaxed space-y-4 text-left">
        <ol className="list-decimal list-inside space-y-3">
          <li>
            <span className="font-medium">[Jin22]</span> Jin, H., et al. "Peekaboo: A Hub-Based Approach to Enable Transparency in Data Processing within Smart Homes."
            <a href="https://arxiv.org/pdf/2204.04540" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline ml-1">
              arXiv:2204.04540
            </a>
          </li>
          <li>
            <span className="font-medium">[Li24]</span> Li, W., et al. "1-2-3 Check: Contextual Integrity-Aware Multi-Agent Privacy Reasoning."
            <a href="https://arxiv.org/pdf/2508.07667" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline ml-1">
              arXiv:2508.07667
            </a>
          </li>
          <li>
            <span className="font-medium">[Iravantchi23]</span> Iravantchi, Y., et al. "PrivacyLens: On-Device PII Removal from RGB Images Using Thermal Sensing."
            <a href="https://petsymposium.org/popets/2024/popets-2024-0146.pdf" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline ml-1">
              PETS 2024
            </a>
          </li>
          <li>
            <span className="font-medium">[Zhou21]</span> Zhou, J., et al. "Privacy-sensitive Objects Pixelation for Live Video Streaming."
            <a href="https://arxiv.org/pdf/2101.00604" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline ml-1">
              arXiv:2101.00604
            </a>
          </li>
          <li>
            <span className="font-medium">[Zhang25]</span> Zhang, S., et al. "Evaluating the Efficacy of Large Language Models for Generating
            Fine-Grained Visual Privacy Policies in Homes."
            <a href="https://arxiv.org/pdf/2508.00321" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline ml-1">
              arXiv:2508.00321
            </a>
          </li>
        </ol>
      </div>
    </section>
  );
};

export default ReferencesSection;