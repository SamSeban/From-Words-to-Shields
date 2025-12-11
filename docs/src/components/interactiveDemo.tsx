import React, { useState, useEffect, useRef } from 'react';
import { Play, ChevronRight, Code, FileJson, Video, Sparkles } from 'lucide-react';

// Declare Prism as a global (loaded from CDN)
declare global {
  interface Window {
    Prism: {
      highlightElement: (el: Element) => void;
      highlightAll: () => void;
    };
  }
}

interface Scenario {
  id: string;
  prompt: string;
  description: string;
  manifest: object;
  generatedTool?: {
    name: string;
    code: string;
  };
  resultVideo: string;
  terminalOutput: string[];
}

const scenarios: Scenario[] = [
  {
    id: 'blur-faces',
    prompt: 'Blur all faces in my video',
    description: 'Detects faces using YuNet model and Kalman Filter and applies Gaussian blur',
    manifest: {
      pipeline: [
        {
          tool: "blur_faces",
          args: {
            kernel: 31
          }
        }
      ]
    },
    resultVideo: './blurred_jn.mp4',
    terminalOutput: [
      '$ python cli.py',
      '> Enter your prompt: Blur all faces in my video',
      '> File path: data/samples/jn.mp4',
      '',
      'Analyzing request...',
      'Generating manifest...',
      'Manifest created: blur_faces pipeline',
      '',
      'Executing pipeline...',
      '   • Running detect_faces (YuNet detector)',
      '   • Found 1 face across 330 frames',
      '   • Running blur (kernel=31)',
      '   • Processing frames... 100%',
      '',
      'Output saved: data/results/blurred_jn.mp4',
      'Summary: 1 face blurred, 330 frames processed'
    ]
  },
  {
    id: 'mute-keywords',
    prompt: 'Mute the Lieutenant\'s name',
    description: 'Uses Whisper ASR to detect keywords and beeps them out',
    manifest: {
      "pipeline": [
        {
          "tool": "mute_keywords",
          "args": {
            "user_intent": "lieutenant's name",
            "mode": "beep"
          }
        }
      ]
    },
    resultVideo: './jn_beeped.mp4',
    terminalOutput: [
      '$ python cli.py',
      '> Enter your prompt: Mute the Lieutenant\'s name',
      '> File path: data/samples/jn.mp4',
      '',
      'Generating manifest...',
      'Manifest created: mute_keywords pipeline',
      '',
      'Executing pipeline...',
      '   • Extracting audio from video',
      '   • Running Whisper transcription...',
      '   • Detected 1 keyword mentions:',
      '      • "Lieutenant Weinberg" at 10.3s-11.1s',
      '   • Applying beep mode to segments...',
      '',
      'Output saved: data/results/jn_beeped.mp4',
      'Summary: 1 segments muted with beep tone'
    ]
  },
  {
    id: 'full-anonymize',
    prompt: 'Fully anonymize the people in this video',
    description: 'Generates a custom tool and combines it with existing tools',
    manifest: {
      "pipeline": [
        {
          "tool": "blur_faces",
          "args": {
            "kernel": 31
          }
        },
        {
          "tool": "anonymize_voice",
          "args": {
            "pitch_shift": -4,
            "preserve_tempo": true
          }
        }
      ]
    },
    generatedTool: {
      name: 'anonymize_voice',
      code: `from tool_api import PrivacyTool
from registry import register
import librosa
import soundfile as sf
import numpy as np
import os

class AnonymizeVoice(PrivacyTool):
    name = "anonymize_voice"
    
    def apply(self, audio_path: str, pitch_shift: int = -4,
              preserve_tempo: bool = True, **kwargs):
        """Anonymize voices by applying pitch shifting.
        
        Args:
            audio_path: Path to input audio/video file
            pitch_shift: Semitones to shift (-4 for deeper voice)
            preserve_tempo: Keep original speech tempo
        """
        output_dir = os.path.join("data", "results")
        os.makedirs(output_dir, exist_ok=True)
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Apply pitch shifting
        y_shifted = librosa.effects.pitch_shift(
            y, sr=sr, n_steps=pitch_shift
        )
        
        # Optional: add slight formant preservation
        if preserve_tempo:
            y_shifted = librosa.effects.time_stretch(
                y_shifted, rate=1.0
            )
        
        filename = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = os.path.join(output_dir, f"{filename}_anon.wav")
        
        sf.write(output_path, y_shifted, sr)
        
        return {
            "output_path": output_path,
            "summary": {
                "duration_seconds": len(y) / sr,
                "pitch_shift_semitones": pitch_shift
            }
        }
    
    def verify(self, **kwargs):
        return {"verified": True}

TOOL = AnonymizeVoice()
register(TOOL)`
    },
    resultVideo: './jn_anonymized.mp4',
    terminalOutput: [
      '$ python cli.py',
      '> Enter your prompt: Fully anonymize the people in this video',
      '> File path: data/samples/jn.mp4',
      '',
      'Analyzing request...',
      'Found existing tool: blur_faces',
      'No existing tool found for "anonymize_voice"',
      'Generating custom tool...',
      '',
      '   • Querying LLM for tool generation...',
      '   • Generated: anonymize_voice.py',
      '   • Registering tool in registry...',
      'Custom tool created and registered!',
      '',
      'Generating manifest...',
      'Manifest created: 2-step pipeline',
      '',
      'Executing pipeline...',
      '   [1/2] Running blur_faces',
      '   • Running detect_faces (YuNet detector)',
      '   • Found 1 face across 330 frames',
      '   • Applying blur (kernel=31)',
      '   [2/2] Running anonymize_voice',
      '   • Extracting audio from video',
      '   • Applying pitch shift (-4 semitones)',
      '   • Merging anonymized audio with video',
      '',
      'Output saved: data/results/jn_anon.mp4',
      'Summary: 1 face blurred, voice anonymized'
    ]
  }
];

const InteractiveDemo: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [terminalLines, setTerminalLines] = useState<string[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showManifest, setShowManifest] = useState(false);
  const [showTool, setShowTool] = useState(false);
  const [showResult, setShowResult] = useState(false);
  
  const manifestRef = useRef<HTMLElement>(null);
  const toolRef = useRef<HTMLElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Highlight code when refs are ready and content is shown
  useEffect(() => {
    if (showManifest && manifestRef.current && window.Prism) {
      window.Prism.highlightElement(manifestRef.current);
    }
  }, [showManifest, selectedScenario]);

  useEffect(() => {
    if (showTool && toolRef.current && window.Prism) {
      window.Prism.highlightElement(toolRef.current);
    }
  }, [showTool, selectedScenario]);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLines]);

  const runDemo = async (scenario: Scenario) => {
    setSelectedScenario(scenario);
    setCurrentStep(1);
    setTerminalLines([]);
    setShowManifest(false);
    setShowTool(false);
    setShowResult(false);
    setIsAnimating(true);

    // Animate terminal output
    for (let i = 0; i < scenario.terminalOutput.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 120));
      setTerminalLines(prev => [...prev, scenario.terminalOutput[i]]);
      
      // Show manifest after "Manifest created" line
      if (scenario.terminalOutput[i].includes('Manifest created')) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setShowManifest(true);
        setCurrentStep(2);
      }
      
      // Show generated tool if applicable
      if (scenario.terminalOutput[i].includes('Custom tool created') && scenario.generatedTool) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setShowTool(true);
      }
      
      // Show result after "Output saved" line
      if (scenario.terminalOutput[i].includes('Output saved')) {
        setCurrentStep(3);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 500));
    setShowResult(true);
    setCurrentStep(4);
    setIsAnimating(false);
  };

  const reset = () => {
    setSelectedScenario(null);
    setCurrentStep(0);
    setTerminalLines([]);
    setShowManifest(false);
    setShowTool(false);
    setShowResult(false);
    setIsAnimating(false);
  };

  return (
    <section className="mb-12 p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl shadow-2xl border border-slate-700">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-emerald-500/20 rounded-lg">
          <Sparkles className="w-6 h-6 text-emerald-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">Interactive Demo</h2>
      </div>


      {/* Video Display - Side by Side */}
      <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
        <div className="grid grid-cols-2 gap-4">
          {/* Input Video */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Video className="w-5 h-5 text-blue-400" />
              <span className="text-sm font-medium text-slate-300">Input Video</span>
              <span className="text-xs text-slate-500 ml-auto">data/samples/jn.mp4</span>
            </div>
            <div className="aspect-video bg-slate-900 rounded-lg overflow-hidden">
              <video 
                src="./jn.mp4"
                className="w-full h-full object-cover"
                controls
                muted
                playsInline
              />
            </div>
          </div>
          
          {/* Output Video */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Video className={`w-5 h-5 ${showResult ? 'text-emerald-400' : 'text-slate-600'}`} />
              <span className={`text-sm font-medium ${showResult ? 'text-emerald-300' : 'text-slate-500'}`}>
                Output Video
              </span>
              {showResult && (
                <span className="text-xs text-emerald-500/70 ml-auto">data/results/</span>
              )}
            </div>
            <div className={`aspect-video rounded-lg overflow-hidden ${showResult ? 'bg-black' : 'bg-slate-900/50 border-2 border-dashed border-slate-700'}`}>
              {showResult && selectedScenario ? (
                <video 
                  src={selectedScenario.resultVideo}
                  className="w-full h-full object-cover"
                  controls
                  autoPlay
                  muted
                  playsInline
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-slate-600 text-sm">Output will appear here</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Selection */}
      {!selectedScenario && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            Choose a prompt to execute:
          </h3>
          <div className="grid gap-3">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                onClick={() => runDemo(scenario)}
                className="cursor-pointer group p-4 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600 hover:border-emerald-500/50 rounded-lg text-left transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-emerald-400 font-mono text-sm mb-1">"{scenario.prompt}"</p>
                    <p className="text-slate-400 text-sm">{scenario.description}</p>
                    {scenario.generatedTool && (
                      <span className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full">
                        <Code className="w-3 h-3" />
                        Generates custom tool
                      </span>
                    )}
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Demo Execution View */}
      {selectedScenario && (
        <div className="space-y-4">
          {/* Progress Steps */}
          <div className="flex items-center justify-between mb-4 px-2">
            {['Prompt', 'Manifest', 'Execute', 'Result'].map((step, idx) => (
              <div key={step} className="flex items-center">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors
                  ${currentStep > idx ? 'bg-emerald-500 text-white' : 
                    currentStep === idx ? 'bg-emerald-500/50 text-white animate-pulse' : 
                    'bg-slate-700 text-slate-400'}
                `}>
                  {idx + 1}
                </div>
                <span className={`ml-2 text-sm ${currentStep >= idx ? 'text-slate-200' : 'text-slate-500'}`}>
                  {step}
                </span>
                {idx < 3 && (
                  <div className={`w-12 h-0.5 mx-3 ${currentStep > idx ? 'bg-emerald-500' : 'bg-slate-700'}`} />
                )}
              </div>
            ))}
          </div>

          {/* Terminal & Manifest Side by Side */}
          <div className="grid grid-cols-2 gap-4">
            {/* Terminal Output */}
            <div className="bg-black rounded-lg overflow-hidden border border-slate-700">
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 border-b border-slate-700">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="text-slate-400 text-sm ml-2 font-mono">terminal</span>
              </div>
              <div 
                ref={terminalRef}
                className="p-4 font-mono text-sm h-72 overflow-y-auto text-left"
              >
                {terminalLines.map((line, idx) => (
                  <div 
                    key={idx} 
                    className={`
                      ${line.startsWith('$') ? 'text-emerald-400' : 
                        line.startsWith('>') ? 'text-blue-400' :
                        line.startsWith('   [') ? 'text-yellow-400' :
                        line.startsWith('      •') ? 'text-slate-500' :
                        'text-slate-300'}
                    `}
                  >
                    {line || '\u00A0'}
                  </div>
                ))}
                {isAnimating && (
                  <span className="inline-block w-2 h-4 bg-emerald-400 animate-pulse" />
                )}
              </div>
            </div>

            {/* Manifest JSON */}
            <div className={`bg-slate-800 rounded-lg overflow-hidden border ${showManifest ? 'border-slate-700' : 'border-dashed border-slate-700'}`}>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 border-b border-slate-600">
                <FileJson className={`w-4 h-4 ${showManifest ? 'text-blue-400' : 'text-slate-600'}`} />
                <span className={`text-sm font-medium ${showManifest ? 'text-slate-300' : 'text-slate-500'}`}>manifest.json (generated)</span>
              </div>
              <div className="h-72 overflow-y-auto">
                {showManifest ? (
                  <pre className="p-4 overflow-x-auto text-sm animate-in fade-in duration-300">
                    <code ref={manifestRef} className="language-json">
                      {JSON.stringify(selectedScenario.manifest, null, 2)}
                    </code>
                  </pre>
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <span className="text-slate-600 text-sm">Manifest will appear here</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Generated Tool Code (full width, only when applicable) */}
          {showTool && selectedScenario.generatedTool && (
            <div className="bg-slate-800 rounded-lg overflow-hidden border border-amber-500/30 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 border-b border-amber-500/30">
                <Code className="w-4 h-4 text-amber-400" />
                <span className="text-amber-300 text-sm font-medium">
                  {selectedScenario.generatedTool.name}.py
                </span>
                <span className="text-xs text-amber-500/70 ml-auto">Auto-generated</span>
              </div>
              <pre className="p-4 overflow-x-auto text-sm max-h-80 overflow-y-auto">
                <code ref={toolRef} className="language-python">
                  {selectedScenario.generatedTool.code}
                </code>
              </pre>
            </div>
          )}

          {/* Reset Button */}
          {!isAnimating && (
            <div className="flex justify-center pt-4">
              <button
                onClick={reset}
                className="px-6 py-2 bg-slate-700 hover:bg-slate-600 dark:text-slate-200 rounded-lg transition-colors flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                Try Another Scenario
              </button>
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default InteractiveDemo;

