import React from 'react';

const IntroductionSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-gray-50 rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Introduction</h2>
      <div className="text-gray-700 leading-relaxed space-y-6">
        
        {/* 1.1 Motivation & Objective */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Motivation & Objective</h3>
          <p className='text-justify'>
            Smart environments are increasingly filled with cameras and microphones that constantly collect audio and video data. 
            In many cases, this raw sensor data is transmitted directly to third-party cloud services without any user control 
            over what information is filtered or how privacy is enforced. Users cannot simply specify their privacy preferences 
            in natural language, such as "blur children's faces" or "mute medical terms," and have the system automatically 
            comply. This lack of control poses significant privacy risks for people in homes, hospitals, workplaces, and other 
            sensitive environments. Our objective is to build a system where users can express privacy requirements in plain 
            language, and an intelligent agent automatically constructs and enforces the necessary data-sanitization pipelines.
          </p>
        </div>

        <div>
  <h3 className="text-xl font-semibold text-gray-800 mb-3">State of the Art & Its Limitations</h3>
  <p className='text-justify mb-2'>
    Current approaches to privacy enforcement follow two main paradigms:
  </p>
  <ul className="list-disc list-inside space-y-2 text-justify">
    <li className='indent-4'> Systems like Peekaboo establish a trusted in-home hub that mediates and locally preprocesses 
      sensor data using developer-defined pipelines. While these systems provide strong architectural 
      guarantees and complete transparency, they suffer from low adaptability and high developer overhead. 
      Implementing novel, user-specific requirements demands hand-coded operators and reconfiguration, 
      limiting the system to predefined, anticipated privacy rules.
    </li>
    <li className='indent-4'> 
      Recent research has explored using Large Language Models as multi-agent reasoning frameworks to 
      interpret and enforce complex privacy policies specified in natural language. While these approaches 
      offer high flexibility and fast adaptability, they raise major concerns regarding robustness and 
      privacy correctness, as agent-generated pipelines are difficult to audit and validate, creating 
      risks of subtle data leakages.
    </li>
  </ul>
</div>

{/* 1.3 Novelty & Rationale */}
<div>
  <h3 className="text-xl font-semibold text-gray-800 mb-3">Novelty & Rationale</h3>
  <p className='text-justify mb-2'>
    Our approach introduces several novel elements that address the limitations of existing systems:
  </p>
  <ul className="list-disc list-inside space-y-2 text-justify mb-2"> 
    <li className='indent-4'> 
      It enables autonomous tool generation in a sandboxed environment, allowing the system to 
      create custom privacy operators when existing tools are insufficient.
    </li>
    <li className='indent-4'> 
      We implement a unified policy framework that handles diverse input types including video, audio, 
      and multimodal, both live and non-live, data while maintaining consistent privacy behavior.
    </li>
    <li className='indent-4'> 
      It includes dynamic verification with a closed-loop recovery mechanism: if verification fails, 
      the system first attempts local retries with substitute tools, then escalates to full replanning 
      when necessary.
    </li>
    <li className='indent-4'> 
      We maintain strong auditability through comprehensive manifests and provenance logs.
    </li>
  </ul>
  <p className='text-justify'>
    We expect this approach to succeed because it combines the flexibility of LLM-driven reasoning 
    with the safety guarantees of verification and sandboxing, bridging the gap between adaptability 
    and trustworthiness.
  </p>
</div>

        {/* 1.4 Potential Impact */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Potential Impact</h3>
          <p className='text-justify'>
            If successful, this project could fundamentally change how privacy is enforced in smart environments. On a technical 
            level, it demonstrates the feasibility of using LLM-based agents for safety-critical infrastructure, providing insights 
            into the safe integration of agentic AI systems. For end users, it enables true user-driven privacy control without 
            requiring technical expertise. For organizations, it significantly reduces the engineering burden of implementing and 
            maintaining privacy systems while making compliance with dynamic regulations like GDPR more manageable. More broadly, 
            the project protects vulnerable populations in homes, hospitals, and workplaces by giving them fine-grained control 
            over their data, and it establishes design principles for trustworthy, efficient, and auditable privacy enforcement 
            that can guide future research and development.
          </p>
        </div>

        {/* 1.5 Challenges */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Challenges</h3>
          <p className='text-justify'>
            TODO
          </p>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Metrics of Success</h3>
          <p className="mb-4 text-justify">
            We evaluate our system using several quantitative metrics across multiple dimensions to ensure comprehensive assessment 
            of correctness, reliability, efficiency, and trustworthiness:
          </p>
          <div className="overflow-x-auto flex justify-center">
            <div className="max-w-2xl w-full">
              <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-4 py-2 text-center font-semibold">Category</th>
                  <th className="border border-gray-300 px-4 py-2 text-center font-semibold">Metrics</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 text-center font-semibold">Correctness</td>
                  <td className="border border-gray-300 px-4 py-2">Face-blur accuracy; keyword F1; mute/beep correctness</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Robustness</td>
                  <td className="border border-gray-300 px-4 py-2">Pipeline success rate; tool-generation success %; recovery success</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Adaptability</td>
                  <td className="border border-gray-300 px-4 py-2">Time to generate new pipeline; # of LLM steps; success rate on unseen requirements</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Performance</td>
                  <td className="border border-gray-300 px-4 py-2">End-to-end latency; resource usage (CPU/GPU); throughput</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Security</td>
                  <td className="border border-gray-300 px-4 py-2">Sandbox compliance; manifest verification; generated code safety</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Auditability</td>
                  <td className="border border-gray-300 px-4 py-2">Log completeness; manifest accuracy; decision traceability</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Baseline Comparison</td>
                  <td className="border border-gray-300 px-4 py-2">Performance vs. hand-coded pipelines; vs. predefined operator systems</td>
                </tr>
              </tbody>
              </table>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600 italic mb-2">Table 1: Evaluation metrics organized by category</p>

      </div>
    </section>
  );
};

export default IntroductionSection;