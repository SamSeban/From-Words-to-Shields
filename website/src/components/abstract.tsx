import React from 'react';

const AbstractSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Abstract</h2>
      <div className="text-gray-700 leading-relaxed">
        <p className="text-justify">
          Modern smart environments pose significant privacy risks as raw sensor data from cameras and microphones 
          is often transmitted directly to third-party cloud services without user control. Existing solutions like 
          Peekaboo enforce local preprocessing but struggle to scale due to their reliance on manually crafted, 
          pre-specified operator pipelines. Our project explores how Large Language Model (LLM)-based agents can 
          autonomously construct, execute, and refine privacy-preserving pipelines for audio, video, and tabular data 
          by translating natural language requirements into executable data-sanitization workflows in real time. 
          <strong className="text-red-600"> [TODO: ADD KEY RESULTS HERE] </strong> 
          This work demonstrates the feasibility of user-driven privacy enforcement and provides insights into the 
          safe integration of agentic AI into privacy infrastructure, making compliance with dynamic regulations 
          like GDPR more manageable while significantly reducing engineering overhead.
        </p>
      </div>
    </section>
  );
};

export default AbstractSection;