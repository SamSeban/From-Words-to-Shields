import React from 'react';

const RelatedWorkSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Related Work</h2>
      <div className="text-gray-700 leading-relaxed space-y-6">
        
        <p  className='text-justify'>
          Our work builds upon and extends several lines of research in privacy enforcement, agent-based systems, 
          and multimodal processing. Below we provide a comparative overview of key related systems and highlight 
          the gaps our approach addresses.
        </p>

        {/* Comparison Table */}
        <div className="overflow-x-auto">
          
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">System/Approach</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Privacy Enforcement</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Adaptability</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Verification</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Developer Effort</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Key Limitation</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border border-gray-300 px-4 py-2 font-medium">Peekaboo [Jin22]</td>
                <td className="border border-gray-300 px-4 py-2">Enforced by a structured, developer-written Manifest and fixed local operators.</td>
                <td className="border border-gray-300 px-4 py-2">Low (Static). Limited to a fixed set of operators; cannot handle novel or custom logic.</td>
                <td className="border border-gray-300 px-4 py-2">Auditable Manifest. Transparency is from a human-readable, deterministic policy (manifest).</td>
                <td className="border border-gray-300 px-4 py-2">High. Developers must learn the API and write a new, unique manifest for every app.</td>
                <td className="border border-gray-300 px-4 py-2">Static Inflexibility. Cannot dynamically adapt or generate new privacy enforcement logic.</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="border border-gray-300 px-4 py-2 font-medium">1-2-3 Check [Li24]</td>
                <td className="border border-gray-300 px-4 py-2">Multi-agent system decomposes privacy reasoning to adhere to Contextual Integrity (CI) norms.</td>
                <td className="border border-gray-300 px-4 py-2">Moderate. Adapts by classifying and enforcing rules based on the dynamic context (who, what, where) of the input.</td>
                <td className="border border-gray-300 px-4 py-2">Checker Agent. A dedicated agent validates output against CI norms, substantially reducing information leakage.</td>
                <td className="border border-gray-300 px-4 py-2">Moderate. Effort for Agent Orchestration and defining the specialized roles, prompts, and CI norms.</td>
                <td className="border border-gray-300 px-4 py-2">Scope Limitation. Focuses only on contextual leakage in text/audio summarization (no multimodal data sanitization).</td>
            </tr>
              <tr>
              <td className="border border-gray-300 px-4 py-2 font-medium">PrivacyLens [Iravantchi23]</td>
              <td className="border border-gray-300 px-4 py-2">On-device PII removal from RGB images, primarily using thermal sensing for robust person detection. No audio/speech support.</td>
              <td className="border border-gray-300 px-4 py-2">Low (Hardware-Bound). Limited to a fixed library of sanitization modes. Cannot support custom, dynamic policies (e.g., "blur just kids' faces").</td>
              <td className="border border-gray-300 px-4 py-2">Sensor Reliability. Verification relies on the thermal sensor reliably detecting the person to trigger pre-defined PII removal. No post-execution policy check.</td>
              <td className="border border-gray-300 px-4 py-2">High. Requires custom hardware (thermal sensor, GPU on-device) and low-level system integration/development.</td>
              <td className="border border-gray-300 px-4 py-2">Lack of Policy Nuance & Modality. Cannot interpret complex policies or handle audio/speech data. Limited to visual input.</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="border border-gray-300 px-4 py-2 font-medium">Privacy-sensitive Objects Pixelation for Live Video Streaming</td>
                <td className="border border-gray-300 px-4 py-2">Real-time video sanitization on edge devices using pre-defined object removal operators.</td>
                <td className="border border-gray-300 px-4 py-2">Low. Supports only pre-specified objects and operator chains.</td>
                <td className="border border-gray-300 px-4 py-2">Operator Checks. No semantic verification; relies on correct computer vision (CV) detection.</td>
                <td className="border border-gray-300 px-4 py-2">High. Adding a new privacy rule requires adding new CV detectors or rules.</td>
                <td className="border border-gray-300 px-4 py-2">Operator Rigidity. Cannot interpret custom language policies or generate new tools.</td>
              </tr>

            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-600 italic mb-2">Table 2: Comparison of privacy enforcement approaches</p>

        {/* Individual Work Discussions */}
        <div className="space-y-4 mt-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Peekaboo: Hub-Based Privacy Enforcement [Jin22]</h3>
            <p  className='text-justify'>
              <strong>What they did:</strong> Jin et al. proposed Peekaboo, a trusted in-home hub that mediates smart home 
              sensor data through developer-specified processing pipelines defined in manifests. The system provides strong 
              architectural guarantees and complete transparency.
            </p>
            <p className="mt-2">
              <strong>Relation to our work:</strong> We adopt Peekaboo's hub-based architecture and manifest-driven approach 
              as our foundation, inheriting its strong trust model.
            </p>
            <p className="mt-2">
              <strong>Gap addressed:</strong> While Peekaboo requires manual pipeline construction and code changes for new 
              privacy rules, our system uses LLM agents to automatically generate and adapt pipelines from natural language 
              requirements.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Multi-Agent LLM Reasoning for Privacy [Li24]</h3>
            <p  className='text-justify'>
              <strong>What they did:</strong> Li et al. demonstrated using LLMs as multi-agent reasoning frameworks to 
              interpret complex privacy policies in natural language and decompose them into executable sub-tasks.
            </p>
            <p className="mt-2">
              <strong>Relation to our work:</strong> We leverage similar LLM-based planning and reasoning capabilities for 
              policy interpretation and pipeline construction.
            </p>
            <p className="mt-2">
              <strong>Gap addressed:</strong> Their approach lacks robust verification mechanisms and auditability. We add 
              a closed-loop verification system with automated recovery and comprehensive audit logs to ensure correctness 
              and trustworthiness.
            </p>
          </div>

          <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400">
            <p className="text-sm text-gray-700">
              <strong>Note:</strong> Additional related works to be added: tool generation frameworks, sandboxing approaches, 
              multimodal processing systems, differential privacy techniques, etc.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};

export default RelatedWorkSection;