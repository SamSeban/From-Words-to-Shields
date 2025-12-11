import React from 'react';

const SupplementarySection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Supplementary Material</h2>
      <div className="text-gray-700 leading-relaxed space-y-8">

        {/* ============================================ */}
        {/* SECTION A: Datasets */}
        {/* ============================================ */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">7.a. Datasets</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold w-1/5">Dataset</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold w-1/5">Source</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Format & Preprocessing</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">YuNet Model Weights</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet" 
                       target="_blank" rel="noopener noreferrer" 
                       className="text-indigo-600 hover:underline">
                      OpenCV Zoo
                    </a>
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    <ul className="list-disc list-inside space-y-1 text-left">
                      <li><strong>Format:</strong> ONNX model file</li>
                      <li><strong>Preprocessing:</strong> Pre-trained, used as-is</li>
                    </ul>
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Whisper Model Weights</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://github.com/openai/whisper" 
                       target="_blank" rel="noopener noreferrer" 
                       className="text-indigo-600 hover:underline">
                      OpenAI Whisper
                    </a>
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    <ul className="list-disc list-inside space-y-1 text-left">
                      <li><strong>Format:</strong> PyTorch checkpoint (base model)</li>
                      <li><strong>Preprocessing:</strong> Pre-trained, word-level timestamps enabled</li>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-sm text-gray-600 italic mt-2">Table 6: Datasets and model weights used in evaluation</p>
        </div>

        {/* ============================================ */}
        {/* SECTION B: Software */}
        {/* ============================================ */}
        <div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">7.b. Software</h3>
          
          {/* External Libraries */}
          <h4 className="text-lg font-semibold text-gray-700 mb-3">External Libraries & Models</h4>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse border border-gray-300 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Library/Model</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Version</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Purpose</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Link</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">OpenAI Whisper</td>
                  <td className="border border-gray-300 px-4 py-2">≥20231117</td>
                  <td className="border border-gray-300 px-4 py-2">ASR transcription (offline)</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://github.com/openai/whisper" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">GitHub</a>
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Faster Whisper</td>
                  <td className="border border-gray-300 px-4 py-2">≥0.6.0</td>
                  <td className="border border-gray-300 px-4 py-2">ASR transcription (live streaming)</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://github.com/SYSTRAN/faster-whisper" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">GitHub</a>
                  </td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">OpenCV (contrib)</td>
                  <td className="border border-gray-300 px-4 py-2">≥4.10.0</td>
                  <td className="border border-gray-300 px-4 py-2">Face detection (YuNet), KCF tracking, video I/O</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://opencv.org/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">opencv.org</a>
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">PyTorch</td>
                  <td className="border border-gray-300 px-4 py-2">≥2.0.0</td>
                  <td className="border border-gray-300 px-4 py-2">Deep learning backend for Whisper</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://pytorch.org/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">pytorch.org</a>
                  </td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Pydub</td>
                  <td className="border border-gray-300 px-4 py-2">≥0.25.1</td>
                  <td className="border border-gray-300 px-4 py-2">Audio manipulation (muting, beep insertion)</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://github.com/jiaaro/pydub" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">GitHub</a>
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Groq SDK</td>
                  <td className="border border-gray-300 px-4 py-2">≥0.4.0</td>
                  <td className="border border-gray-300 px-4 py-2">LLM API (llama-3.3-70b-versatile)</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://console.groq.com/docs" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">Docs</a>
                  </td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">NumPy</td>
                  <td className="border border-gray-300 px-4 py-2">≥1.24.0</td>
                  <td className="border border-gray-300 px-4 py-2">Array operations, Kalman filter math</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://numpy.org/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">numpy.org</a>
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Librosa</td>
                  <td className="border border-gray-300 px-4 py-2">≥0.10.0</td>
                  <td className="border border-gray-300 px-4 py-2">Audio feature extraction</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <a href="https://librosa.org/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">librosa.org</a>
                  </td>
                </tr>
              </tbody>
            </table>
            <p className="text-sm text-gray-600 italic mt-2">Table 7: External libraries and models used in the system</p>
          </div>

          {/* Internal Modules */}
          <h4 className="text-lg font-semibold text-gray-700 mb-3">Internal Modules</h4>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse border border-gray-300 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Module</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Path</th>
                  <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Planner Agent</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">planner/write_manifest.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">LLM-based manifest generation from natural language</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Tool Generator</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">planner/tool_generator.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Dynamic tool code generation via LLM</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Executor</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">planner/executor.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Pipeline execution with retry logic</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Face Detector</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">tools/detectors/face.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">YuNet + KCF + Kalman filter hybrid tracker</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Keyword Detector</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">tools/detectors/detect_keywords.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Whisper + LLM phrase localization</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Blur Transform</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">tools/transforms/blur.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Gaussian blur with configurable kernel</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Mute Transform</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">tools/transforms/mute_segments.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Audio muting/beep insertion</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Composites</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">tools/composites/</code></td>
                  <td className="border border-gray-300 px-4 py-2">End-to-end tools (blur_faces, mute_keywords, live_censor)</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-medium">Audit Logger</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">audit/logger.py</code></td>
                  <td className="border border-gray-300 px-4 py-2">Timestamped action logging</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">Metrics Evaluator</td>
                  <td className="border border-gray-300 px-4 py-2"><code className="bg-gray-100 px-1 rounded">metrics/</code></td>
                  <td className="border border-gray-300 px-4 py-2">Benchmark runner and log parser</td>
                </tr>
              </tbody>
            </table>
            <p className="text-sm text-gray-600 italic mt-2">Table 8: Internal modules used in the system</p>
          </div>
        </div>

      </div>
    </section>
  );
};

export default SupplementarySection;
