
import os
from groq import Groq
from dotenv import load_dotenv
import json
import time
import sys

try:
    from .tool_generator import generate_custom_tool
except ImportError:
    from tool_generator import generate_custom_tool 

# Add project root to path for registry access
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import registry
import audit.logger as audit

load_dotenv()
# For the moment the list of the available tools is just written in the prompt. Future improvement idea: Think of
# a way to have give it direclty from the registry, so that it is always updated
SYSTEM_PROMPT = """You are a privacy-protection pipeline planner. Given a user request, generate a JSON manifest.

BUILT-IN TOOLS (pre-coded and available):

1. detect_faces - Detect faces only
   Args: none (input file provided at runtime)
   Returns: mask_stream_path (detection coordinates)

2. blur - Apply blur to video regions
   Args: mask_stream_path (str), kernel (int, must be ODD number)
   Returns: output_video_path (blurred video)

3. blur_faces - Blur faces in video (composite tool, uses detect_faces and blur)
   Args: none (input file provided at runtime)
   Returns: output_video_path (blurred video)

4. detect_keywords - Detect keywords only
   Args: user_intent (string)
   Returns: segments (timestamps of detected keywords)

5. mute_segments - Mute audio segments
   Args: segments (list), mode (str: "silence" or "beep")
   Returns: output_audio_path (processed audio)

6. mute_keywords - Mute keywords in audio (composite tool)
   Args: user_intent, mode (str: "silence" or "beep")
   Returns: output_audio_path (processed audio)

TOOL NAMING CONVENTION:
When proposing custom tools (not in the built-in list), use these naming patterns:
- For detection: detect_<object> (e.g., detect_license_plates, detect_text)
- For blurring/removal: blur_<object> or remove_<object> (e.g., blur_license_plates, remove_background)
- For audio processing: <action>_<target> (e.g., transcribe_audio, enhance_audio)
- For composite operations: <action>_<objects> (e.g., blur_license_plates_and_faces)

CRITICAL RULES:
- For requests matching built-in tools, use those tools directly
- For requests needing capabilities NOT in the built-in list, propose a sensible tool name following the naming convention
- If a request requires BOTH video and audio processing, create separate steps for each
- Blur kernel MUST be an odd number (e.g., 31, 21, 15, 51)
- Output valid JSON only
- For composite tools (blur_faces, mute_keywords), prefer using them over manual chaining unless custom parameters are needed
- NEVER return an error for unavailable tools - just propose what tool would be needed

EXAMPLES:

Request: "Blur faces in my video"
Response:
{"pipeline": [{"tool": "blur_faces", "args": {}}]}

Request: "Mute password mentions"
Response:
{"pipeline": [{"tool": "mute_keywords", "args": {"user_intent": "Mute password mentions", "mode": "beep"}}]}

Request: "Remove license plates from video"
Response:
{"pipeline": [{"tool": "blur_license_plates", "args": {}}]}

Request: "Transcribe this audio"
Response:
{"pipeline": [{"tool": "transcribe_audio", "args": {}}]}

Request: "Blur faces and remove license plates"
Response:
{"pipeline": [{"tool": "blur_faces", "args": {}}, {"tool": "blur_license_plates", "args": {}}]}

Request: "Blur faces and mute password mentions"
Response:
{"pipeline": [{"tool": "blur_faces", "args": {}}, {"tool": "mute_keywords", "args": {"user_intent": "Mute password mentions", "mode": "beep"}}]}

IMPORTANT: Always propose a pipeline with sensible tool names. The system will automatically generate any missing tools.

Generate manifest for:"""


class PipelinePlanner():
    # Built-in tools that are pre-coded and available
    BUILTIN_TOOLS = {
        "detect_faces", "blur", "blur_faces",
        "detect_keywords", "mute_segments", "mute_keywords"
    }
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile" # this model was chosen since it's fast and accurate enough

    def plan(self, user_request: str):
        """Generate a manifest for the user request, auto-generating any missing tools."""
        
        # Generate the initial manifest
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_request}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        manifest = json.loads(response.choices[0].message.content)
        
        # Check if manifest has a pipeline
        if "pipeline" not in manifest:
            return manifest  # Return as-is if no pipeline (might be an error or something else)
        
        # Find tools that need to be generated
        tools_to_generate = []
        for step in manifest["pipeline"]:
            tool_name = step.get("tool")
            if tool_name and not self._tool_exists(tool_name):
                tools_to_generate.append((tool_name, step))
        
        # Generate any missing tools
        generated_tools = []
        failed_tools = []
        
        for tool_name, step in tools_to_generate:
            print(f"🔧 Tool '{tool_name}' not found. Generating...")
            
            # Create a specific request for this tool based on the user's original intent
            tool_request = self._create_tool_request(tool_name, user_request, step.get("args", {}))
            
            audit.tool_gen_start(tool_name)
            generation_result = generate_custom_tool(tool_request, list(self.BUILTIN_TOOLS))
            
            if generation_result.get("success"):
                actual_tool_name = generation_result['tool_name']
                audit.tool_gen_end(tool_name, True, actual_tool_name)
                print(f"✅ Successfully generated tool: {actual_tool_name}")
                generated_tools.append({
                    "requested": tool_name,
                    "generated": actual_tool_name,
                    "file_path": generation_result.get('tool_file_path')
                })
                
                # Update the manifest if the generated tool has a different name
                if actual_tool_name != tool_name:
                    for s in manifest["pipeline"]:
                        if s.get("tool") == tool_name:
                            s["tool"] = actual_tool_name
                            break
            else:
                error_msg = generation_result.get('error', 'Unknown error')
                audit.tool_gen_end(tool_name, False, error=error_msg)
                print(f"❌ Failed to generate tool '{tool_name}': {error_msg}")
                failed_tools.append({
                    "tool": tool_name,
                    "error": error_msg
                })
        
        # Add metadata about generated tools to manifest
        if generated_tools:
            manifest["_generated_tools"] = generated_tools
        
        if failed_tools:
            manifest["_generation_errors"] = failed_tools
            # Don't fail the whole manifest - let the executor handle missing tools
        
        return manifest
    
    def _tool_exists(self, tool_name: str) -> bool:
        """Check if a tool exists in the registry or as a built-in."""
        # Check built-in tools first
        if tool_name in self.BUILTIN_TOOLS:
            return True
        
        # Check the registry for dynamically registered tools
        try:
            tool = registry.get(tool_name)
            return tool is not None
        except Exception:
            return False
    
    def _create_tool_request(self, tool_name: str, user_request: str, args: dict) -> str:
        """Create a specific request for generating a tool based on context."""
        # Build a descriptive request for the tool generator
        request_parts = [f"Create a tool named '{tool_name}'"]
        
        # Add context from the original user request
        # request_parts.append(f"based on user request: '{user_request}'")
        
        # Add any args context
        if args:
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            request_parts.append(f"with parameters: {args_str}")
        
        # Add hints based on tool name patterns
        if "license_plate" in tool_name.lower():
            request_parts.append("- Should detect and blur license plates in video using cv2")
        elif "transcribe" in tool_name.lower():
            request_parts.append("- Should transcribe audio to text using whisper")
        elif "background" in tool_name.lower():
            request_parts.append("- Should remove or blur background in video using cv2")
        elif "text" in tool_name.lower():
            request_parts.append("- Should detect and blur text in video using cv2")
        elif "object" in tool_name.lower():
            request_parts.append("- Should detect and blur objects in video using cv2")
        
        return " ".join(request_parts)
    
    def save_manifest(self, manifest: dict, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    
    planner = PipelinePlanner(api_key=api_key)
    
    test_cases = [
        # === BASIC VIDEO TESTS (built-in tools) ===
        "Blur faces in my video",
        "Just detect faces, don't blur",
        "Blur with kernel size 51",
        "Blur faces with very strong blur",
        "Detect and blur faces with kernel 15",
        
        # === BASIC AUDIO TESTS (built-in tools) ===
        "Mute password mentions",
        "Use beep instead of mute for profanity",
        "Detect keywords 'credit card' and 'ssn'",
        "Silence mentions of 'address' and 'phone number'",
        "Beep out bad words",
        
        # === MULTI-KEYWORD TESTS (built-in tools) ===
        "Mute 'password', 'username', 'email', and 'ssn'",
        "Remove mentions of medical terms like 'diagnosis' and 'prescription'",
        "Beep profanity words",
        
        # === CUSTOM PARAMETERS (built-in tools) ===
        "Blur with kernel 91",
        "Use silence mode instead of beep",
        "Detect faces only, no processing",
        "Detect keywords only, don't mute",
        
        # === CHAINING TESTS (built-in tools) ===
        "First detect faces, then blur with kernel 25",
        "Detect keywords then mute them with beep",
        
        # === TOOL GENERATION TESTS (should auto-generate) ===
        "Transcribe this audio",
        "Remove license plates from video",
        "Detect text in video",
        "Convert speech to text",
        "Remove background noise",
        "Enhance video quality",
        "Detect objects in video",
        
        # === MIXED TESTS (built-in + generated) ===
        "Blur faces and remove license plates",
        "Blur faces and mute keywords 'password' and 'ssn'",
        "Transcribe audio and blur faces in video",
        
        # === EDGE CASES ===
        "Blur everything in the video",
        "Mute the entire audio",
        "Don't do anything",
    ]

    total_time = 0
    success_count = 0
    error_count = 0
    generated_count = 0
    results = {}
    for i, request in enumerate(test_cases, 1):
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"TEST {i}/{len(test_cases)}: {request}")
        print('='*60)
        
        
        try:
            manifest = planner.plan(request)
            print(json.dumps(manifest, indent=2))
            
            if "error" in manifest:
                outcome = 'error'
                error_count += 1
                print("Result: ERROR")
            elif "_generated_tools" in manifest:
                outcome = 'generated'
                generated_count += 1
                success_count += 1
                gen_tools = [t['generated'] for t in manifest['_generated_tools']]
                print(f"Result: SUCCESS (generated tools: {gen_tools})")
            else:
                outcome = 'success'
                success_count += 1
                print("Result: SUCCESS (built-in tools only)")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")
            outcome = 'exception'
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
    print(f"  - Built-in tools only: {success_count - generated_count}")
    print(f"  - With generated tools: {generated_count}")
    print(f"Error responses: {error_count}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per test: {total_time/len(test_cases):.2f}s")
    print('='*60)

