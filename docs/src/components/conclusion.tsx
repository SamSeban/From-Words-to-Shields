import React from 'react';

const ConclusionSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Discussion & Conclusions</h2>
      <div className="text-gray-700 leading-relaxed space-y-6">

        {/* ============================================ */}
        {/* SECTION: What Worked Well */}
        {/* ============================================ */}
        <div className="space-y-3">
          <p className='text-justify'>
            This work demonstrates that LLM-based agents can successfully construct and execute privacy-preserving pipelines from natural language requirements. Our system achieved an overall 69% success rate, comprising 59% first-attempt success plus an additional 10% recovered through the closed-loop retry mechanism, which rescued 24% of initially failed pipelines. Face detection with our YuNet-KCF-Kalman hybrid maintained continuous tracking with under 10% miss ratio, while the LLM-based keyword detection correctly identified and redacted sensitive phrases across diverse privacy intents. Crucially, the system translates complex privacy requirements into executable workflows in seconds, eliminating the weeks of engineering traditionally required to implement custom privacy pipelines.
          </p>
        </div>

        {/* ============================================ */}
        {/* SECTION: Limitations */}
        {/* ============================================ */}
        <div className="space-y-3">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Remaining Limitations</h3>
          
          <p className='text-justify'>
            Several technical limitations persist. The <code className="bg-gray-100 px-1 rounded">mute_keywords</code> tool exhibits high failure rates when multiple speakers talk simultaneously, as ASR transcription becomes unreliable in overlapping speech scenarios. The YuNet face detector struggles with poor video quality common in security camera footage and cannot reliably detect faces from behind or when heavily occluded.
          </p>

          <p className='text-justify'>
            Performance overhead remains a concern: the ~10.2s overhead compared to traditional pipelines (with 35% spent on LLM calls) makes the system unsuitable for latency-critical applications, though latency was measured on an average laptop and could improve significantly with better GPU/CPU hardware, making overall latency depend almost entirely on the LLM calls.
          </p>

          <p className='text-justify'>
            On the code generation side, LLM-generated tools have variable quality and may fail at execution time despite passing compilation. The system lacks formal verification beyond sandbox compliance checks, and generated tools may not anticipate edge cases that hand-coded implementations would handle. Additionally, the system cannot distinguish between individual faces, as it performs detection only, not recognition.
          </p>
        </div>

        {/* ============================================ */}
        {/* SECTION: Future Work */}
        {/* ============================================ */}
        <div className="space-y-3">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Future Directions</h3>
          
          <p className='text-justify'>
            On the performance front, implementing GPU acceleration for YuNet and Whisper inference would significantly reduce latency. Investigating smaller, distilled models for edge deployment (e.g., Whisper-tiny with fine-tuning) could enable on-device processing without cloud LLM calls, which can be critical for sensitive environments where we don't want to send data to the cloud. Adding speaker diarization would address the multi-person audio scenarios where the current system struggles.
          </p>

          <p className='text-justify'>
            For improved reliability, fine-tuning a specialized model for privacy tool generation could improve code quality. Additional verification approaches such as manual human checking (e.g., via Amazon Mechanical Turk) could train a verifier neural network to better predict tool success before deployment.
          </p>

          <p className='text-justify'>
            Expanding scope, the system could support arbitrary sensor data and process sensor fusion data from IoT environments, broadening applicability beyond audio-visual streams to comprehensive smart environment privacy protection.
          </p>
        </div>

        {/* ============================================ */}
        {/* SECTION: Broader Impact */}
        {/* ============================================ */}
        <div className="space-y-3">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Broader Impact</h3>
          
          <p className='text-justify'>
            This system enables non-technical users to enforce sophisticated privacy policies through natural language, substantially reducing the barrier to GDPR/CCPA compliance for small organizations and individuals who lack dedicated privacy engineering resources.
          </p>

          <p className='text-justify'>
            It also reduces the engineering burden, as organizations can implement privacy systems without dedicated ML teams. Dynamic tool generation eliminates the need to anticipate every privacy scenario upfront, while auditability features simplify compliance documentation and regulatory audits.
          </p>

          <p className='text-justify'>
            This work demonstrates a practical framework for deploying LLM agents in safety-critical infrastructure. The closed-loop verification approach provides a template for building trustworthy AI systems, and comprehensive logging establishes standards for AI decision traceability.
          </p>

          <p className='text-justify'>
            The system is particularly relevant for healthcare facilities, courtrooms, and workplaces where privacy requirements are stringent and context-dependent, enabling adaptive protection without custom engineering for each deployment.
          </p>
        </div>


      </div>
    </section>
  );
};

export default ConclusionSection;
