import os
from groq import Groq
from dotenv import load_dotenv
import json
import time 


load_dotenv()
# For the moment the list of the available tools is just written in the prompt. Future improvement idea: Think of
# a way to have give it direclty from the registry, so that it is always updated
SYSTEM_PROMPT = """You are a privacy-protection pipeline planner. Given a user request, generate a JSON manifest.

AVAILABLE TOOLS:

1. detect_faces - Detect faces only
   Args: video_path (str)
   Returns: mask_stream_path (detection coordinates)

2. blur - Apply blur to video regions
   Args: video_path (str), mask_stream_path (str), kernel (int, must be ODD number)
   Returns: output_video_path (blurred video)

3. blur_faces - Blur faces in video (composite tool, uses detect_faces and blur)
   Args: video_path (str)
   Returns: output_video_path (blurred video)

4. detect_keywords - Detect keywords only
   Args: audio_path (str), keywords (list)
   Returns: segments (timestamps of detected keywords)

5. mute_segments - Mute audio segments
   Args: audio_path (str), segments (list), mode (str: "silence" or "beep")
   Returns: output_audio_path (processed audio)

6. mute_keywords - Mute keywords in audio (composite tool)
   Args: audio_path (str), keywords (list), mode (str: "silence" or "beep")
   Returns: output_audio_path (processed audio)

CRITICAL RULES:
- ONLY use tools from the list above
- Video tools (detect_faces, blur, blur_faces) work ONLY with video files (.mp4, .avi, .mov, etc.)
- Audio tools (detect_keywords, mute_segments, mute_keywords) work ONLY with audio files (.wav, .mp3, .flac, etc.)
- You CANNOT mix video and audio processing in the same pipeline - they require separate input files
- If a request requires BOTH video and audio processing on different files, create separate steps for each
- If a request requires extracting audio from video or mixing modalities, respond with an error
- If a requested capability is NOT in the available tools, you MUST respond with:
  {"error": "Tool 'X' not available", "available_tools": ["list", "of", "related", "tools"]}
- Use $prev.field_name to reference outputs from previous steps (e.g., $prev.mask_stream_path, $prev.segments)
- Blur kernel MUST be an odd number (e.g., 31, 21, 15, 51)
- Output valid JSON only
- For composite tools (blur_faces, mute_keywords), prefer using them over manual chaining unless custom parameters are needed

EXAMPLES:

Request: "Blur faces in my video"
Response:
{"pipeline": [{"tool": "blur_faces", "args": {"video_path": "video.mp4"}}]}

Request: "Mute password mentions"
Response:
{"pipeline": [{"tool": "mute_keywords", "args": {"audio_path": "audio.wav", "keywords": ["password"], "mode": "beep"}}]}

Request: "Detect faces with custom blur kernel 41"
Response:
{"pipeline": [
  {"tool": "detect_faces", "args": {"video_path": "video.mp4"}},
  {"tool": "blur", "args": {"video_path": "video.mp4", "mask_stream_path": "$prev.mask_stream_path", "kernel": 41}}
]}

Request: "Remove license plates from video"
Response:
{"error": "Tool 'detect_license_plates' not available", "available_tools": ["blur_faces", "detect_faces", "blur"]}

Request: "Blur faces and mute keywords in the same video"
Response:
{"error": "Cannot process video and audio together. Please provide separate audio file or split into two requests.", "suggestion": "Use blur_faces for video, then extract audio separately and use mute_keywords"}

Request: "Transcribe this audio"
Response:
{"error": "Tool 'transcribe' not available", "available_tools": ["detect_keywords", "mute_keywords", "mute_segments"]}

IMPORTANT: If the user asks for something that doesn't match ANY available tool, return an error response. Do NOT try to work around missing capabilities.

Generate manifest for:"""


class PipelinePlanner():
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile" # this model was chosen since it's fast and accurate enough

    def plan(self, user_request: str, file_path: str = None):

        if file_path:
            user_request += f"\nFile: {file_path}"
        response = self.client.chat.completions.create(
            model= self.model,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role':'user', 'content': user_request}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        manifest = json.loads(response.choices[0].message.content)
        return manifest
    
    def save_manifest(self, manifest: dict, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    
    planner = PipelinePlanner(api_key=api_key)
    
    test_cases = [
        # === BASIC VIDEO TESTS ===
        ("Blur faces in my video", "video.mp4"),
        ("Just detect faces, don't blur", "video.mp4"),
        ("Blur with kernel size 51", "video.mp4"),
        ("Blur faces with very strong blur", "video.mp4"),
        ("Detect and blur faces with kernel 15", "video.mp4"),
        
        # === BASIC AUDIO TESTS ===
        ("Mute password mentions", "audio.wav"),
        ("Use beep instead of mute for profanity", "audio.wav"),
        ("Detect keywords 'credit card' and 'ssn'", "audio.wav"),
        ("Silence mentions of 'address' and 'phone number'", "audio.wav"),
        ("Beep out bad words", "audio.mp3"),
        
        # === MULTI-KEYWORD TESTS ===
        ("Mute 'password', 'username', 'email', and 'ssn'", "audio.wav"),
        ("Remove mentions of medical terms like 'diagnosis' and 'prescription'", "audio.wav"),
        ("Beep profanity words", "audio.wav"),
        
        # === CUSTOM PARAMETERS ===
        ("Blur with kernel 91", "video.mp4"),
        ("Use silence mode instead of beep", "audio.wav"),
        ("Detect faces only, no processing", "video.mp4"),
        ("Detect keywords only, don't mute", "audio.wav"),
        
        # === CHAINING TESTS ===
        ("First detect faces, then blur with kernel 25", "video.mp4"),
        ("Detect keywords then mute them with beep", "audio.wav"),
        
        # === ERROR CASES - UNAVAILABLE TOOLS ===
        ("Transcribe this audio", "audio.wav"),
        ("Remove license plates from video", "video.mp4"),
        ("Detect text in video", "video.mp4"),
        ("Convert speech to text", "audio.wav"),
        ("Remove background noise", "audio.wav"),
        ("Enhance video quality", "video.mp4"),
        ("Detect objects in video", "video.mp4"),
        
        # === ERROR CASES - MULTI-MODAL CONFUSION ===
        ("Blur faces and mute keywords 'password' and 'ssn'", "video.mp4"),
        ("Process both video and audio", "video.mp4"),
        
        # === EDGE CASES ===
        ("Blur everything in the video", "video.mp4"),
        ("Mute the entire audio", "audio.wav"),
        ("Don't do anything", "video.mp4"),
    ]

    total_time = 0
    success_count = 0
    error_count = 0
    results = {}
    for i, (request, file) in enumerate(test_cases, 1):
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"TEST {i}/{len(test_cases)}: {request}")
        print(f"File: {file}")
        print('='*60)
        
        
        try:
            manifest = planner.plan(request, file)
            print(json.dumps(manifest, indent=2))
            
            if "error" in manifest:
                outcome = 'error'
                error_count += 1
                print("Result: ERROR (expected for some tests)")
            else:
                outcome = 'success'
                success_count += 1
                print("Result: SUCCESS")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")
            error_count += 1
        
        end_time = time.time()
        test_time = end_time - start_time
        total_time += test_time
        results[i] = {'manifest': manifest, 'result': outcome, 'time': test_time}
        print(f"Time: {test_time:.2f}s")
    

    with open('planner_outcome.json', 'w') as f:
        json.dump(results, f, indent=2)
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Total tests: {len(test_cases)}")
    print(f"Successful manifests: {success_count}")
    print(f"Error responses: {error_count}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per test: {total_time/len(test_cases):.2f}s")
    print('='*60)

