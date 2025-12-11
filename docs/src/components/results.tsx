import React from 'react';
import fpHeatmap from '../assets/fp_heatmap.png';
import successRate from '../assets/success.png';
import overhead from '../assets/overhead.png';

const ResultsSection: React.FC = () => {
  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Evaluation & Results</h2>
      
      {/* ============================================ */}
      {/* SECTION: Evaluation Metrics Overview */}
      {/* ============================================ */}
      <div className="text-gray-700 leading-relaxed space-y-6 mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-3">Evaluation Metrics</h3>
        <p className='text-justify mb-4'>
          We evaluate our system across six dimensions: robustness, adaptability, performance, security, auditability, and baseline comparison. The following table defines all metrics used in our evaluation.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Robustness */}
            <div className="overflow-hidden">
            <div className="bg-indigo-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-indigo-800 text-sm">Robustness</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">Pipeline Success Rate</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of workflows completing without fatal errors</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Tool Generation Success</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of LLM tools that compile & register</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Tool Execution Success</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of tool runs completing without errors</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Recovery Success Rate</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of workflows succeeding after retry</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Error Types</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Breakdown of error categories</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Failure Points</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Which tools fail most frequently</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Adaptability */}
          <div className="overflow-hidden">
            <div className="bg-emerald-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-emerald-800 text-sm">Adaptability</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">Avg Pipeline Gen Time</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">LLM time to plan a manifest</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Avg LLM Steps</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600"># of LLM calls (planning + generation)</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Avg Tool Gen Time</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Time to generate a custom tool via LLM</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Novel Tool Success Rate</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of generated tools that execute</td>
                </tr>
                <tr>
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Builtin/Generated Ratio</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Pre-coded vs LLM-generated tools used</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Performance */}
          <div className="overflow-hidden">
            <div className="bg-blue-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-blue-800 text-sm">Performance</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">End-to-End Latency</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Total time: prompt → output (min/avg/max)</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Avg Planning Time</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Time in manifest generation phase</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Avg Execution Time</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Time running the actual pipeline</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Avg Tool Exec Time</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Average runtime per individual tool</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Throughput</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Workflows processed per hour</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">CPU/Memory Usage</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Resource consumption during execution</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Security */}
          <div className="overflow-hidden">
            <div className="bg-red-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-red-800 text-sm">Security</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">Sandbox Compliance</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of tools with no unsafe code patterns</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Manifest Verification</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of manifests passing validation</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Unsafe Patterns</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Count of dangerous code (eval, exec, etc.)</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Import Compliance</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% using only allowed libraries</td>
                </tr>
                <tr>
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">File Access Compliance</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% writing only to allowed dirs (data/)</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Auditability */}
          <div className="overflow-hidden">
            <div className="bg-amber-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-amber-800 text-sm">Auditability</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">Log Completeness</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of expected events logged</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Manifest Accuracy</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Whether manifests match execution</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Decision Traceability</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">Can trace prompt → plan → execution</td>
                </tr>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Timestamp Coverage</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of events with valid timestamps</td>
                </tr>
                <tr>
                  <td className="px-3 py-1.5 border border-gray-300 font-medium">Error Log Completeness</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of failures with error details</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Baseline Comparison */}
          <div className="overflow-hidden">
            <div className="bg-purple-100 border-t border-x border-gray-300 px-3 py-2">
              <h4 className="font-semibold text-purple-800 text-sm">Baseline Comparison</h4>
            </div>
            <table className="w-full text-sm">
              <tbody>
                <tr>
                  <td className="px-3 py-1.5 border border-gray-300 font-medium w-2/5">LLM Planning Overhead</td>
                  <td className="px-3 py-1.5 border border-gray-300 text-gray-600">% of time on LLM calls (planning + gen)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <p className="text-sm text-gray-600 italic mt-4">
          Table 4: Evaluation metrics organized by category</p>
      </div>

      {/* ============================================ */}
      {/* SECTION: Evaluation Prompts */}
      {/* ============================================ */}
      <div className="text-gray-700 leading-relaxed space-y-4 mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-3">Evaluation Prompts</h3>
        <p className='text-justify mb-4'>
          We designed a diverse set of 23 prompts to comprehensively evaluate system capabilities. For each prompt in Table 5 below, we measured all metrics from Table 4 across multiple input videos to ensure statistical robustness.
        </p>
      </div>

      <div className="overflow-x-auto mb-8">



        
  <table className="w-full border-collapse border border-gray-300 text-sm text-slate-700">
    <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-700">
      <tr>
        <th className="border border-gray-300 px-4 py-2 text-left">Prompt</th>
        <th className="border border-gray-300 px-4 py-2 text-left">Expected Tools / Gen</th>
      </tr>
    </thead>
    <tbody className="divide-y divide-slate-100">

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Anonymize all faces in the video to comply with GDPR</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Mute any mentions of names, addresses, or phone numbers</td>
        <td className="border border-gray-300 px-3 py-2">mute_keywords</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Apply strong blur to faces, they must be completely unrecognizable</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Mute mentions of email addresses, social security numbers, and credit card numbers</td>
        <td className="border border-gray-300 px-3 py-2">mute_keywords</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Blur all license plates</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Detect and blur any visible text containing personal information</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Blur the background to hide location and environment details</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Anonymize people's bodies, not just faces</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Detect all faces in the video</td>
        <td className="border border-gray-300 px-3 py-2">detect_faces</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Blur faces in video</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Scan audio for sensitive keywords</td>
        <td className="border border-gray-300 px-3 py-2">detect_keywords</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Create a tool to pixelate regions of interest</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Apply audio filtering to mask voice identity</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Remove all identifiable information about a specific person</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces + tool generation</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Anonymize faces and mute names since consent was withdrawn</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces, mute_keywords</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Remove all unnecessary personal data, keep only essential content</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Detect and blur all children’s faces with extra care</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Blur all faces and mute all personal names</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces, mute_keywords</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Anonymize the speaker’s face and distort their voice</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces + tool generation</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2 ">Blur patient faces and mute medical record numbers or diagnoses</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces, mute_keywords</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Anonymize faces in the video</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-50">
        <td className="border border-gray-300 px-3 py-2">Blur all faces in a crowded public event</td>
        <td className="border border-gray-300 px-3 py-2">blur_faces</td>
      </tr>

      <tr className="bg-gray-100">
        <td className="border border-gray-300 px-3 py-2">Anonymize partially visible faces and people from behind</td>
        <td className="border border-gray-300 px-3 py-2">tool generation</td>
      </tr>

    </tbody>
  </table>
</div>
      <p className="text-sm text-gray-600 italic mb-8">
        Table 5: Evaluation prompts categorized by test dimension
      </p>

      <p className="text-justify mb-6 text-gray-700">
        To gather all these metrics, we built a simple CLI tool called <code className="bg-gray-100 px-1 rounded">run_metrics.py</code>. It feeds test prompts into the pipeline, measures and logs every result into a JSON file.
      </p>

      <div className="text-gray-700 leading-relaxed space-y-6">

        {/* ============================================ */}
        {/* SECTION: Results */}
        {/* ============================================ */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Results</h3>


   <div className="w-full">
   <p className="text-justify mb-3">
      For both Figure 6 and Figure 7 below, note that "Vid 1", "Vid 2", and "Vid 3" correspond to a set of videos arranged by increasing complexity, ranging from single-person, simple scenes to challenging scenarios with multiple people, overlapping movement, and background noise. The specific type of complexity (such as visual clutter or overlapping speech) depends on the scenario being tested.
    </p>  
    </div>

    {/* Success Rate - double width */}
    <div className="flex flex-col items-center w-full">
      <img
        src={successRate}
        alt="Success Rate"
        className="w-full max-w-xl rounded-lg object-contain"
      />
      <p className="text-sm text-gray-600 italic mt-2 text-center">
        Figure 6: Robustness Metrics per Video category.
      </p>
    </div>
    <div className="w-full">
    <p className="text-justify mb-3">
      (Fig. 6) The "pipeline success rate" in this context means that the pipeline completed all stages without a single error or the need for any retries. The measured overall success rate before any retry attempts is 59%. When the recovery (retry) loop is triggered, an additional average recovery success rate of 24% is observed. As expected, all three success rates systematically decrease as scenario complexity increases.
    </p>
  </div>
        {/* Failure Points Heatmap - half width */}
        <div className="flex flex-col items-center w-full">
      <img
        src={fpHeatmap}
        alt="Failure Points Heatmap"
        className="w-full max-w-sm rounded-lg object-contain"
      />
      <p className="text-sm text-gray-600 italic mt-2 text-center">
        Figure 7: Failure Points Heatmap.
      </p>
    </div>
    <div>
  <div className="w-full">
    <p className="text-justify mb-3">
      (Fig. 7) The Failure Points Heatmap highlights the tools where the privacy pipeline struggled and where errors cluster by tool type and scenario complexity. In the most complex case ("Vid 3"), the <code>mute_keywords</code> tool struggled the most and frequently failed verification. These failures are primarily due to overlapping speech making automatic transcription more challenging, and the LLM’s difficulty in consistently understanding context and muting precisely the correct portions of the audio.
    </p>
  </div>

  <div className="flex justify-center mb-4">
  <img
        src={overhead}
        alt="Overhead"
        className="w-full max-w-3xl rounded-lg object-contain"
      />
      </div>
      <p className="text-sm text-gray-600 italic mt-2 text-center mb-3">
        Figure 8: Comparison of time spent in each stage between rigid traditional pipelines and adaptive LLM-based approach.
      </p>
      <p className="text-justify">
        Figure 8 shows that our LLM-based system adds ~10.2s overhead compared to traditional pipelines.
      </p>
      <p className="text-justify mb-3">
        The overhead is primarily due to the additional time spent in the LLM calls for planning, tool generation, and validation (35% on average). While some 8% are spent in error recovery, which is a feature that the traditional pipeline does not have.
      </p>

  </div>
        </div>

      </div>
    </section>
  );
};

export default ResultsSection;
