import React from 'react';
import diagramoush from '../assets/diagramoush.png';
import feedback_loop from '../assets/feedback_diagram.jpg';
import nonLiveDataPipeline from '../assets/non-live-data-pipeline.png';
import faceDetectionFlow from '../assets/face_detection.png';
import speechDetectionFlow from '../assets/speech_detection.png';


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
        </div>

        {/* 3.3 Algorithm / Model Details */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">3.3 Algorithm / Model Details</h3>
          
          <div className="space-y-4">
            <div className='text-justify'>
            <h4 className="text-lg font-semibold text-gray-700 mb-2 text-center">LLM-Based Planning Agent</h4>
            
            <p className="mb-3 ">
              Our planning agent uses the llama-3.3-70b-versatile model, as it balances speed 
              and accuracy in generating structured outputs. The agent receives natural language privacy requests from users 
              (e.g., "blur faces in my video" or "mute password mentions") and converts them into executable JSON manifests 
              that define the processing pipeline.
            </p>

            <h5 className="text-base font-semibold text-gray-700 mb-2 mt-4 text-center" >Prompt Structure</h5>
            <p className="mb-2">The agent operates according to a system prompt which provides:</p>
            <ul className="list-disc list-outside ml-6 space-y-2 mb-3">
              <li>
                A catalog of pre-coded tools including face detection, blurring, 
                keyword detection, and audio muting operations. For example, <code className="bg-gray-100 px-1 rounded">blur_faces</code> detects 
                and blurs faces in video, and <code className="bg-gray-100 px-1 rounded">mute_keywords</code> detects and mutes specified 
                keywords in audio.
              </li>
              <li>
                Clear naming patterns for proposing new tools when built-in capabilities are 
                insufficient, such as <code className="bg-gray-100 px-1 rounded">detect_&lt;object&gt;</code> for detection 
                tools (e.g., <code className="bg-gray-100 px-1 rounded">detect_license_plates</code>), 
                <code className="bg-gray-100 px-1 rounded">blur_&lt;object&gt;</code> for blurring 
                tools, and <code className="bg-gray-100 px-1 rounded">&lt;action&gt;_&lt;target&gt;</code> for audio tools.
              </li>
              <li>
                Specific rules such as using built-in tools when they match the request, ensuring blur kernel values are odd numbers for video blurring, and 
                outputting only valid JSON.
              </li>
              <li>
                Several example requests and their corresponding manifest outputs to guide the model's responses.
              </li>
            </ul>

            <h5 className="text-base font-semibold text-gray-700 mb-2 mt-4 text-center">Pipeline Generation Process</h5>
            <p className="mb-2">When a user submits a privacy request, the planner:</p>
            <ul className="list-decimal list-outside ml-6 space-y-2 mb-3">
              <li>
                The LLM analyzes the natural language input to identify what privacy operations are needed (e.g., face blurring, keyword muting).
              </li>
              <li>
                The model outputs a JSON manifest containing a pipeline of sequential steps. 
                Each step specifies a tool name (either built-in or proposed custom tool) and arguments needed for that tool.
              </li>
              <li>
                The system checks whether each tool in the manifest exists. If the tool 
                is built-in or already in the registry, it proceeds. If not, the system automatically triggers tool generation.
              </li>
              <li>
                For missing tools, the planner creates a specific generation request 
                that includes the desired tool name, context from the original user request, and any parameters specified in the 
                manifest. This request is sent to the tool generator, which creates the missing functionality.
              </li>
              <li>
                Once all tools are available (either pre-existing or newly generated), 
                the manifest is finalized with metadata about any generated tools and is ready for execution.
              </li>
            </ul>

            <h5 className="text-base font-semibold text-gray-700 mb-2 mt-4 text-center">Example Flow</h5>
            <p className="mb-2">User Request: "Blur faces and remove license plates"</p>
            <p className="mb-2">Generated Manifest:</p>
            <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-2 text-sm">
          {`{
            "pipeline": [
              {"tool": "blur_faces", "args": {}},
              {"tool": "blur_license_plates", "args": {}}
            ]
}`}
            </pre>
            <p className="mb-2">System Action:</p>
            <ul className="list-disc list-outside ml-6 space-y-1 mb-3">
              <li><code className="bg-gray-100 px-1 rounded">blur_faces</code> is built-in, therefore ready to use.</li>
              <li><code className="bg-gray-100 px-1 rounded">blur_license_plates</code> is not available so the system plans the tool generation</li>
              <li>Final manifest includes both tools, with metadata noting that <code className="bg-gray-100 px-1 rounded">blur_license_plates</code> was generated</li>
            </ul>
          </div>
            
            <div className='text-justify'>
  <h4 className="text-lg font-semibold text-gray-700 mb-2 text-center">Face Detection and Tracking</h4>
  
  <p className="mb-3">
    The face detection algorithm uses a hybrid approach combining three complementary techniques: 
     YuNet face detector for initial detection, KCF (Kernelized Correlation Filters) tracker for 
    efficient frame-to-frame tracking, and Kalman filtering for motion prediction and smoothing.
  </p>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Detection Strategy</h5>
  <p className="mb-2">
    The system operates in a cascaded manner to balance accuracy and computational efficiency:
  </p>
  <ul className="list-decimal list-outside ml-6 space-y-2 mb-3">
    <li>
      YuNet Detector (Primary): Runs periodically (every 3 frames by default) to detect faces from scratch. 
      YuNet is a deep learning-based face detector optimized for speed and accuracy. We configure it with a score threshold of 
      0.5 and NMS (Non-Maximum Suppression) threshold of 0.3 to filter overlapping detections.
    </li>
    <li>
      KCF Tracker (Secondary): Between detection intervals, a KCF tracker follows each detected face across frames. 
      This is computationally cheaper than running the detector every frame and maintains continuity when faces are visible.
    </li>
    <li>
      Kalman Filter (Fallback): When both the detector and tracker fail (e.g., due to temporary occlusion or 
      motion blur), the Kalman filter predicts the face position based on its previous trajectory. The filter models face motion 
      using a constant velocity model with 8 states: position (x, y, w, h) and velocity (vx, vy, vw, vh).
    </li>
  </ul>
  
  <div className="flex justify-center my-8">
  <img src={faceDetectionFlow} alt="Data Pipeline" className="w-full max-w-3xl rounded-lg" />
</div>
<p className="text-sm text-gray-600 italic mb-2 text-center">Figure 4: Face prediction algorithm.</p>


  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Kalman Filter Configuration</h5>
  <p className="mb-2">
    The Kalman filter uses a constant velocity motion model where the next position is predicted as:
  </p>
  <div className="bg-gray-100 p-3 rounded-lg mb-3">
    <p className="font-mono text-sm">x(t) = x(t-1) + v(t-1) × Δt</p>
    <p className="font-mono text-sm">v(t) = v(t-1)</p>
  </div>
  <p className="mb-2">Key parameters:</p>
  <ul className="list-disc list-outside ml-6 space-y-1 mb-3">
    <li>Process noise covariance: Low for position (0.01) to maintain stable predictions, higher for velocity (1.0) 
    to allow for sudden changes in motion</li>
    <li>Measurement noise covariance: Low (0.05) to trust detector/tracker measurements when available</li>
    <li>Prediction limit: Maximum 60 frames of pure Kalman prediction before requiring a new detection, preventing 
    unbounded drift. This ensures no blinking in the detection.</li>
  </ul>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Grayscale Video Handling</h5>
  <p className="mb-3">
    Grayscale videos often have lower contrast and faces are harder to detect, therefore we apply CLAHE (Contrast Limited Adaptive 
    Histogram Equalization) preprocessing. This enhances local contrast with a clip limit of 4.0 and tile size of 6×6, followed 
    by Gaussian blur sharpening to improve face detection accuracy.
  </p>

    <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">System Flow Example</h5>
  <div className="bg-gray-50 border-l-4 border-indigo-600 p-4 mb-3">
    <p className="text-sm">Frame 0: YuNet detects 2 faces → Initialize 2 KCF trackers + 2 Kalman filters</p>
    <p className="text-sm">Frames 1-2: KCF tracks faces, Kalman corrects positions</p>
    <p className="text-sm">Frame 3: YuNet re-detects, confirms/updates face positions</p>
    <p className="text-sm">Frame 4-5: Tracker temporarily fails on one face → Kalman predicts its position</p>
    <p className="text-sm">Frame 6: YuNet detects again, tracker recovers</p>
  </div>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Blurring Algorithm</h5>
  <p className="mb-3">
    Once faces are detected and tracked, a Gaussian blur is applied to each face region. The system supports both live 
    streaming and offline processing modes. For each detected face bounding box (x, y, w, h), the region is expanded by 
    a scale factor of 2× (configurable) from its center to ensure complete coverage even with slight tracking errors. 
    The blur kernel size is configurable (must be an odd number, typically 31, 51, or 121 pixels) to control the strength 
    of anonymization. The kernel is dynamically clamped to the ROI (Region of Interest) size if the face region is smaller 
    than the specified kernel. The larger the kernel, the stronger the blur, making faces completely unrecognizable. The 
    blurred region is then written back into the original frame, and the processed frame is either displayed in real-time 
    (live mode) or written to an output video file (offline mode).
  </p>

<h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Live vs. Non-Live Processing</h5>
<p className="mb-2">
  The system implements two distinct processing modes to handle different use cases, live and offline modes:
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    Live Streaming Mode is designed for real-time applications such as video conferencing or live surveillance. 
    In this mode, detection and blurring operate in a pipelined fashion: each frame is detected, immediately blurred, and 
    then broadcasted frame-by-frame. The detector yields frame-detection pairs as a generator, which are consumed on-the-fly 
    by the blur function. This minimizes latency and enables real-time privacy enforcement, though it sacrifices the ability 
    to verify detection quality before blurring.
  </li>
  <li>
    Offline (Non-Live) Mode is designed for processing pre-recorded videos where quality and verification are 
    priorities. In this mode, the entire video is first processed through the detection pipeline, producing a complete set of 
    face detections. These detections are then verified to ensure they meet quality thresholds (e.g., detection accuracy, 
    miss ratio). Only if verification passes does the system proceed to the blurring stage, processing the entire video again 
    with the verified detection coordinates. If detection verification fails, the pipeline halts and reports an error. This 
    two-pass approach ensures high-quality output but introduces higher latency, making it unsuitable for real-time applications.
  </li>
</ul>

<h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Verification of Video Redaction (Offline Mode Only)</h5>
<p className="mb-3">
  Before outputting the video in Offline mode, two verification checks are performed: 
  </p>
<h6 className="text-base font-medium text-gray-600 mb-1 mt-3">1. Detection Quality Check: Miss Ratio Analysis</h6>
<p className="mb-2">
  This check verifies the continuity of the face tracking trace. The system calculates the miss ratio, which is the percentage of frames where a detected face was unexpectedly lost due to tracking failure (a 'gap').
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    The algorithm is set to Pass if the overall miss ratio is below 10%.
  </li>
  <li>
    Additionally, it passes if the ratio of short gaps (detection failures lasting less than 0.5 seconds) to successful detection time is also below 10%. 
  </li>
</ul>

<h6 className="text-base font-medium text-gray-600 mb-1 mt-3">2. Redaction Intensity Check: Laplacian Variance</h6>
<p className="mb-3">
  This check ensures the blurring applied to the output video is strong enough for anonymity. It uses the Laplacian Variance, a metric that measures image sharpness: high variance means sharp (weak blur), and low variance means smooth (strong blur).
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    The system calculates the average Laplacian variance within all blurred regions across the video.
  </li>
  <li>
    A strict verification threshold of 50 is enforced. If the average variance is below 50, the blurring is verified as sufficiently strong to render faces unrecognizable; otherwise, the pipeline fails.  </li>
</ul>

</div>



            
<div className='text-justify'>
  <h4 className="text-center text-lg font-semibold text-gray-700 mb-2">Speech Processing and Keyword Detection</h4>
  
  <p className="mb-3">
    Our audio privacy system uses a two-stage approach: automatic speech recognition (ASR) to transcribe audio into text 
    with word-level timestamps, followed by LLM-based sensitive content identification and precise temporal localization. 
    This allows the system to understand natural language privacy requests like "mute my address" or "remove financial 
    information" and automatically identify and redact the relevant audio segments.
  </p>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Transcription with Whisper</h5>
  <p className="mb-3">
    We use OpenAI's Whisper model (base variant) for automatic speech recognition. Whisper transcribes the entire audio 
    file while generating word-level timestamps. The model returns 
    both a full transcript and detailed segment information, where each segment contains individual words with their start 
    and end times in seconds. This word-level granularity enables accurate detection and muting of specific phrases without 
    affecting surrounding speech.
  </p>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">LLM-Based Sensitive Content Detection</h5>
  <p className="mb-2">
    After transcription, the full transcript and the user's privacy intent (e.g., "mute my phone number and email") are 
    sent to an LLM (llama-3.3-70b-versatile) which acts as a privacy protection assistant. The LLM is prompted with 
    comprehensive redaction guidelines covering seven categories:
  </p>
  <ul className="list-decimal list-outside ml-6 space-y-2 mb-3">
    <li>Addresses: Street addresses, apartment numbers, cities, zip codes</li>
    <li>Phone Numbers: Any phone format including country codes</li>
    <li>Email Addresses: Complete email addresses and domains</li>
    <li>Passwords: Passwords, PINs, security codes, secret phrases</li>
    <li>Usernames: Social media handles, login usernames</li>
    <li>Personal Information: Names, SSNs, dates of birth, license plates</li>
    <li>Financial Data: Credit card numbers, bank accounts, routing numbers</li>
  </ul>
  <p className="mb-3">
    The LLM extracts exact phrases from the transcript that match the user's intent, returning them as a JSON array. For 
    example, if the user says "mute my address," the LLM identifies phrases like "123 Main Street" and "New York" from 
    the transcript. This approach is more flexible than hardcoded keyword matching, as it understands context and can 
    adapt to various phrasings of sensitive information.
  </p>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Phrase Localization Algorithm</h5>
  <p className="mb-2">
    Once sensitive phrases are identified, the system locates them in the word-level timestamp data using a sliding window 
    algorithm:
  </p>
  <ul className="list-decimal list-outside ml-6 space-y-2 mb-3">
    <li>
      All word-level timestamps from all segments are flattened into a single sequential 
      list with normalized (lowercase, punctuation-removed) word text.
    </li>
    <li>
      For each sensitive phrase (e.g., "123 Main Street"), the algorithm slides through 
      the word list looking for consecutive matches. For single-word phrases, exact matching is required. For multi-word 
      phrases, fuzzy matching allows slight variations in transcription.
    </li>
    <li>
      When a match is found, the system records the start time of the first word 
      and the end time of the last word in the phrase, creating a temporal segment.
    </li>
    <li>
      After detecting a phrase, the algorithm skips past those words to avoid 
      overlapping detections.
    </li>
  </ul>

    <div className="flex justify-center my-8">
  <img src={speechDetectionFlow} alt="Data Pipeline" className="w-full max-w-3xl rounded-lg" />
</div>
<p className="text-sm text-gray-600 italic mb-2 text-center">Figure 5: Keyword detection and localization flow.</p>

 

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Example Detection Flow</h5>
  <div className="bg-gray-50 border-l-4 border-indigo-600 p-4 mb-3">
    <p className="text-sm">Input Audio: "Hi, my name is John and I live at 123 Main Street in New York. 
    You can reach me at 555-1234."</p>
    <p className="text-sm">User Intent: "Mute my address and phone number"</p>
    <p className="text-sm">Whisper Transcription: Full transcript + word timestamps</p>
    <p className="text-sm">LLM Detection: Identifies phrases: ["123 Main Street", "New York", "555-1234"]</p>
    <p className="text-sm">Localization: Finds temporal segments:</p>
    <p className="text-sm ml-4">• "123 Main Street" at 2.3s - 2.8s</p>
    <p className="text-sm ml-4">• "New York" at 4.1s - 4.5s</p>
    <p className="text-sm ml-4">• "555-1234" at 6.2s - 7.0s</p>
    <p className="text-sm">Output: JSON with 3 segments ready for muting</p>
  </div>

  <h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Audio Redaction and Output</h5>
<p className="mb-3">
  After precise temporal localization, the system applies audio redaction using the time windows identified. We use the 
  <a href="https://github.com/jiaaro/pydub" className="text-indigo-600 hover:text-indigo-800" target="_blank" rel="noopener noreferrer"> pydub </a> 
  library to manipulate the audio file directly. Users can select one of two redaction modes: mute (replace with silence) or beep (insert a beep sound) or beep (replace with a 1KHz tone). 
  The redacted audio is then exported as a new file, preserving the original format and quality.
</p>
<h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Live Redaction: Real-Time Streaming</h5>
<p className="mb-3">
  For live audio streams, a different algorithm is used to enforce privacy instantly. This pipeline prioritizes speed over the deep contextual understanding offered by the LLM in the batch system.
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    The audio is processed in small chunks using a specialized streaming ASR model (FasterWhisperASR).
  </li>
  <li>
    Keywords are detected in real-time as the ASR model transcribes and commits each word, recording its precise start and end time in the stream.
  </li>
  <li>
    Audio chunks are held in a playback queue for a short buffer period. This crucial delay provides the necessary time for the ASR model to process the chunk and register any sensitive keywords.
  </li>
  <li>
    Just before a chunk is released for playback, the system checks for any overlapping keyword intervals. If a match is found, the system replaces the segment with a beep (or silence) directly within the audio data, ensuring the censorship occurs before the sound reaches the listener.
  </li>
</ul>

<h5 className="text-center text-base font-semibold text-gray-700 mb-2 mt-4">Verification of Audio Redaction (Offline Mode Only)</h5>
<p className="mb-3">
  To confirm compliance for offline audio redaction, a two-stage verification is performed, focusing first on the technical correctness of the time markers and then on the effectiveness of the muting.
</p>

<h6 className="text-base font-medium text-gray-600 mb-1 mt-3">1. Temporal Integrity Check</h6>
<p className="mb-2">
  This check ensures the time segments generated for redaction are valid and reasonable:
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    Verifies that all segment markers are chronologically correct (start before end) and do not extend beyond the total audio duration.
  </li>
  <li>
    Flags any single redaction segment longer than 15 seconds, as very long segments are unlikely to be a single keyword or phrase.
  </li>
  <li>
    Counts the number of segments that overlap or have identical timestamps. If excessive overlap (over 50% of all segments) or duplicates are found, the pipeline fails, suggesting an error in the localization algorithm.
  </li>
</ul>

<h6 className="text-base font-medium text-gray-600 mb-1 mt-3">2. Compliance Check: Muting Effectiveness</h6>
<p className="mb-3">
  This is the final check that confirms the privacy goal was achieved:
</p>
<ul className="list-disc list-outside ml-6 space-y-2 mb-3">
  <li>
    The newly redacted audio file (containing beeps or silence) is sent back through the Whisper ASR model to generate a new transcript.
  </li>
  <li>
    The system checks this new transcript against the original list of sensitive phrases that were supposed to be muted (e.g., phone numbers, addresses).
  </li>
  <li>
    If any of the original sensitive phrases is successfully recognized in the new, muted transcript, the system reports a compliance failure, proving the redaction was ineffective and preventing the file from being released.
  </li>
</ul>


</div>
            
            
            
            <div>

              

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