import React from 'react';
import diagramoush from '../assets/diagramoush.png';
import feedback_loop from '../assets/feedback_diagram.jpg';
import nonLiveDataPipeline from '../assets/non-live-data-pipeline.png';


const TechnicalApproachSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Technical Approach</h2>
      <div className="text-gray-700 leading-relaxed space-y-8 ">
        
        {/* 3.1 System Architecture */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.1 System Architecture</h3>
          
          <p className="mb-4 text-justify">
            The system is designed as an agent-driven pipeline that processes raw sensor data and enforces privacy policies based on natural-language user requirements. The core components work in a closed loop to ensure that all data is sanitized and verified before leaving the local environment.
          </p>
          <div className="flex justify-center mb-4">
            <img src={diagramoush} alt="Feedback Loop Diagram" className="w-full max-w-3xl rounded-lg shadow-md" />
          </div>
          <p className="text-sm text-gray-600 italic mb-2">Figure 1: System Architecture Diagram</p>

          <p className="mb-4 text-justify"> 
            The process is divided into several steps which involve different components:
            <ul className="list-disc list-outside ml-6 space-y-2 text-justify">
                <li>    
                    <strong>Input & Preprocessing:</strong> Raw sensor data (video, audio) is ingested and pre-filtered to extract relevant segments for privacy processing. The natural language input is received from the user, specifying their privacy requirements.
                </li>
                <li>
                    <strong>Planner Agent Investigator: </strong>the LLM-based planner agent interprets the natural language input and generates a manifest which outlines the tools to use. It checks the tools registry for existing tools: if a relevant one is found, the 
                    planner specifies the tool in the manifest, along with the arguments to use. If no suitable tool exists, the planner invokes the tool generator to create a new one.
                </li>
                <li>
                    <strong>Tool Generator:</strong> In case the planner cannot find a suitable tool in the registry, the tool generator codes it and adds it to the tool registry for future use. 
                </li>
                <li>
                    <strong>Executor Agent Runtime: </strong> The executor agent reads the manifest and executes the specified tools in sequence.

                </li>
                <li>
                    <strong>Verification Module: </strong> After execution, the verification module checks the output against the privacy requirements outlined in the manifest. If verification fails, it triggers the closed-loop recovery mechanism, otherwise the output is saved.
                </li>
                <li>
                    <strong>Audit and Logs: </strong> A comprehensive audit log is mantained and it records time stamps, action type (planning, tool generation, tool execution, verification), and outcome of each step. 
                </li>
            </ul>
          </p >
          <p className='text-justify'>During execution, if a privacy transformation fails, the system retries the operation using predefined substitute tools or alternate model configurations for a limited number of attempts. If verification 
          continues to fail after these retries, the Executor automatically triggers a re-planning step, sending an error report and diagnostic log back to the Planner Agent. The Planner then revises the
            execution plan or requests new tool generation based on the failure context.
            </p>
            <div className="flex justify-center mb-4">
            <img src={feedback_loop} alt="Closed Loop Architecture" className="w-full max-w-3xl rounded-lg shadow-md" />
          </div>
          <p className="text-sm text-gray-600 italic mb-2">Figure 2: Closed loop architecture.</p>
          <p className='text-justify'>
            Starting from the left-hand side, the exector agent runs the generated pipeline on the input. The output is passed through the verification module:
            <ul className="list-disc list-outside ml-6 space-y-2 text-justify">
                <li> If the output passes verification, it is sent out, and it is recorded in the logs.</li>
                <li> If the output fails verification, the closed-loop recovery mechanism is triggered. The system first attempts local retries with substitute tools. If these retries also fail, the system escalates to full replanning by sending an error report and diagnostic log back to the planner agent, which revises the execution plan or requests new tool generation based on the failure context.</li>
            </ul>

            </p>     

        </div>

        {/* 3.2 Data Pipeline */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.2 Data Pipeline</h3>
          
          <p className="text-justify">
            The data pipeline consists of several stages which transform the input data into a privacy-compliant output. The data follows the flow outlined below:
          </p>
          <div className="flex justify-center my-8">
            <img src={nonLiveDataPipeline} alt="Data Pipeline" className="w-full max-w-3xl rounded-lg" />
          </div>
          <p className="text-sm text-gray-600 italic mb-2">Figure 3: Data Pipeline</p>
          
          <p className="text-justify">
            The pipeline consists of the following steps: 
          </p>
          <ul className="list-disc list-outside ml-6 space-y-2 text-justify mt-2">
                <li> The input file (audio or video) is received by the system.</li>
                <li> The detection takes place based on the user requested privacy policy. </li>
                <li> The output of the detection is verified by the verification module. </li>
                <li> If the verification is successful, the detection data is received by the transform module (such as blur faces for a video input) and the transform is applied. </li>
                <li> The output of the tranform is verified by the verification module </li>
                <li> If the verification is successful, a composite tool (detection + transform) is saved and the final output is released (for a video input, the output is saved as a .avi file while audio inputs are output as .wav files). </li>
            </ul>

          
          <p>
            <strong className="text-red-600">[TODO: Explain for each data type:]</strong>
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Video:</strong> <span className="text-red-600">[Frame extraction → Face detection → Blurring → Verification]</span></li>
            <li><strong>Audio:</strong> <span className="text-red-600">[Voice activity detection → Transcription → Keyword detection → Muting/beeping → Verification]</span></li>
            <li><strong>Tabular:</strong> <span className="text-red-600">[Data parsing → Filtering/masking → Verification]</span></li>
          </ul>
          
          <p className="mt-4">
            <strong className="text-red-600">[TODO: Describe data formats, transformations, and intermediate representations]</strong>
          </p>
        </div>

        {/* 3.3 Algorithm / Model Details */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.3 Algorithm / Model Details</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">LLM-Based Planning Agent</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe the LLM model (llama-3.3-70b-versatile), prompt structure, 
                how it parses natural language policies and generates execution plans]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Face Detection and Tracking</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe YuNet face detector, Kalman Filter for tracking, 
                blurring algorithm (e.g., Gaussian blur kernel size)]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Speech Processing</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe Whisper for transcription, keyword matching algorithm, 
                audio manipulation for muting/beeping]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Verification Algorithm</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe how verification checks compliance - re-running detection, 
                checking for unblurred faces, transcribing to verify muted keywords]</strong>
              </p>
              
              <div className="bg-gray-50 p-4 rounded-lg mt-2 font-mono text-sm">
                <p className="text-gray-500 italic mb-2">[Pseudocode example:]</p>
                <pre className="text-red-600">
{`function verify_privacy_compliance(output, manifest):
    for each rule in manifest.rules:
        if not check_rule(output, rule):
            return FAIL, rule
    return PASS`}
                </pre>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Closed-Loop Recovery</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe retry logic, when to trigger replanning, 
                error reporting mechanism]</strong>
              </p>
              
              <div className="bg-gray-100 border-2 border-dashed border-gray-300 p-8 rounded-lg text-center mt-2">
                <p className="text-gray-500 italic">
                  [Figure X: Flowchart showing: Execute → Verify → (Pass: Release) / (Fail: Retry with substitute) 
                  → (Still fails: Replan)]
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 3.4 Hardware / Software Implementation */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.4 Hardware / Software Implementation</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Hardware Setup</h4>
              <p>
                <strong className="text-red-600">[TODO: Describe your hardware setup]</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mt-2">
                <li><strong className="text-red-600">Development Machine:</strong> [Specs: CPU, GPU, RAM]</li>
                <li><strong className="text-red-600">Edge Device:</strong> [Raspberry Pi model, peripherals, sensors]</li>
                <li><strong className="text-red-600">Sensors:</strong> [Camera, microphone, other sensors if applicable]</li>
              </ul>
              
              <div className="bg-gray-100 border-2 border-dashed border-gray-300 p-8 rounded-lg text-center mt-4">
                <p className="text-gray-500 italic">
                  [Photo: Hardware setup showing Raspberry Pi, sensors, and connections]
                </p>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Software Stack</h4>
              <p>
                <strong className="text-red-600">[TODO: List all frameworks and libraries with versions]</strong>
              </p>
              
              <div className="overflow-x-auto mt-2">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Component</th>
                      <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Technology</th>
                      <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Purpose</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">LLM Agent</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[llama-3.3-70b-versatile / API]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Planning & tool generation]</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2">Agent Framework</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[LangChain / LlamaIndex]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Agent orchestration]</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Face Detection</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[YuNet / OpenCV]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Face detection & blurring]</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2">Speech Processing</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Whisper]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Audio transcription]</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Tracking</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Kalman Filter]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Face tracking across frames]</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2">Sandbox</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Docker / Python subprocess]</td>
                      <td className="border border-gray-300 px-4 py-2 text-red-600">[Isolated code execution]</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* 3.5 Key Design Decisions & Rationale */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.5 Key Design Decisions & Rationale</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Why an Agent-Based Approach?</h4>
              <p>
                <strong className="text-red-600">[TODO: Explain why you chose LLM agents over manual pipelines - 
                flexibility, adaptability, reduced engineering effort]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Why Closed-Loop Verification?</h4>
              <p>
                <strong className="text-red-600">[TODO: Explain the need for automatic verification and recovery - 
                LLMs can make mistakes, need to catch privacy violations]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Why Sandboxed Tool Generation?</h4>
              <p>
                <strong className="text-red-600">[TODO: Explain security concerns with executing LLM-generated code, 
                why sandbox is necessary]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Model Selection Rationale</h4>
              <p>
                <strong className="text-red-600">[TODO: Why llama-3.3-70b-versatile? Why YuNet for faces? 
                Why Whisper for speech? Consider accuracy, speed, resource constraints]</strong>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Tradeoffs Made</h4>
              <p>
                <strong className="text-red-600">[TODO: Discuss key tradeoffs:]</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mt-2">
                <li><strong>Accuracy vs. Latency:</strong> <span className="text-red-600">[How did you balance these?]</span></li>
                <li><strong>Flexibility vs. Security:</strong> <span className="text-red-600">[Allowing tool generation vs. only using pre-built tools]</span></li>
                <li><strong>Generality vs. Performance:</strong> <span className="text-red-600">[Supporting multiple modalities vs. optimizing for one]</span></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Alternatives Considered</h4>
              <p>
                <strong className="text-red-600">[TODO: What other approaches did you consider and why did you reject them? 
                E.g., fine-tuning vs. prompting, different LLMs, different verification strategies]</strong>
              </p>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};

export default TechnicalApproachSection;