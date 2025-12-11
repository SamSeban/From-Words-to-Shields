# From Words to Shields

A natural language-driven privacy protection pipeline for video and audio. Describe what you want in plain English, and the system automatically applies privacy transformations like face blurring, keyword censoring, and more.

## Overview

This project uses LLM-based planning to convert user prompts into executable privacy pipelines. When you say "blur faces in my video" or "mute password mentions", the system:

1. **Plans**: Uses an LLM (Llama 3.3 via Groq) to generate a JSON manifest describing the required tools
2. **Generates**: Automatically creates custom tools if the requested functionality doesn't exist
3. **Executes**: Runs the pipeline with detection, tracking, and transformation stages
4. **Audits**: Logs all operations for traceability and verification

### Built-in Tools

- **detect_faces** - Face detection using YuNet with Kalman filtering and tracking
- **blur** - Apply blur to specified video regions
- **blur_faces** - Composite tool that detects and blurs faces
- **detect_keywords** - Detect spoken keywords using Whisper ASR
- **mute_segments** - Mute audio segments (silence or beep)
- **mute_keywords** - Composite tool that detects and mutes keywords

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from [Groq Console](https://console.groq.com/).

### 3. Download Models

Create a `models/` directory and download the required models:

```bash
mkdir -p models
```

**Required model:**
- **YuNet Face Detection**: Download `face_detection_yunet_2023mar.onnx` from the [OpenCV Zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) and place it in `models/`

### 4. Add Sample Files

Create the samples directory and add your test videos:

```bash
mkdir -p data/samples
```

Place your `.mp4` video files in `data/samples/`. The CLI uses `data/samples/4.mp4` as the default test file.

## Usage

### Interactive CLI (`cli.py`)

The main interface for testing the pipeline interactively:

```bash
python cli.py
```

This starts an interactive session where you can:
- Enter natural language prompts describing privacy transformations
- Specify input files (or use the default)
- See the pipeline execution in real-time

**Example session:**

```
Interactive Mode
==================================================
Enter prompts to test the complete workflow.
Type 'quit' to exit, 'files' to see available test files.

Available test files: 4.mp4, interview.mp4

Example prompts:
   • Remove background from video
   • Blur faces in my video
   • Detect license plates in video
   • Mute keywords 'password' and 'credit card'
   • Transcribe this audio file

--------------------------------------------------

Enter your prompt: Blur faces in my video
File path (or press Enter to use default): 
Using file: /path/to/project/data/samples/4.mp4
...
```

**Commands:**
- Type a prompt to execute a privacy pipeline
- `files` - List available test files in `data/samples/`
- `quit` - Exit the program

### Metrics Evaluation (`run_metrics.py`)

Run automated tests and evaluate pipeline performance:

```bash
# Run all test suites
python run_metrics.py

# Run specific test suite
python run_metrics.py --suite robustness

# Run quick smoke tests
python run_metrics.py --quick

# Evaluate existing logs without running new tests
python run_metrics.py --evaluate-only

# List available test suites
python run_metrics.py --list-suites

# Use a specific test video
python run_metrics.py --test-file path/to/video.mp4

# Specify output path for report
python run_metrics.py --output metrics/my_report.json
```

**Available test suites:**
- `robustness` - Pipeline success rate, recovery handling
- `adaptability` - Novel requirements, tool generation
- `performance` - Latency, resource usage, throughput
- `security` - Sandbox compliance, code safety
- `edge_cases` - Unusual inputs and edge conditions
- `baseline_comparison` - LLM planning overhead analysis

**Output:**
- Test results: `metrics/test_results.json`
- Metrics report: `metrics/report.json` (or custom path with `--output`)

## Project Structure

```
From-Words-to-Shields/
├── cli.py                 # Interactive CLI
├── run_metrics.py         # Metrics evaluation runner
├── registry.py            # Tool registry
├── tool_api.py            # Base class for privacy tools
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
│
├── models/                # ML models (create this)
│   └── face_detection_yunet_2023mar.onnx
│
├── data/
│   └── samples/           # Test video files (create this)
│       └── *.mp4
│
├── planner/               # LLM planning and execution
│   ├── write_manifest.py  # Manifest generation
│   ├── run_manifest.py    # Manifest execution
│   ├── executor.py        # Pipeline orchestration
│   └── tool_generator.py  # Dynamic tool creation
│
├── tools/                 # Privacy tools
│   ├── detectors/         # Detection tools (face, keywords)
│   ├── transforms/        # Transform tools (blur, mute)
│   └── composites/        # Composite pipelines
│
├── metrics/               # Evaluation framework
│   ├── runner.py          # Test execution
│   ├── evaluator.py       # Metrics calculation
│   └── log_parser.py      # Audit log parsing
│
├── audit/                 # Audit logging
│   └── logger.py
│
└── manifests/             # Example pipeline manifests
    └── *.json
```

## License

See [LICENSE](LICENSE) for details.
