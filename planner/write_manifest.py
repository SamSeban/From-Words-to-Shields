
import os
from groq import Groq
from dotenv import load_dotenv
import json
import time
try:
    from .tool_generator import generate_custom_tool
except ImportError:
    from tool_generator import generate_custom_tool 


load_dotenv()
# For the moment the list of the available tools is just written in the prompt. Future improvement idea: Think of
# a way to have give it direclty from the registry, so that it is always updated
SYSTEM_PROMPT = """You are a privacy-protection pipeline planner. Given a user request, generate a JSON manifest.

AVAILABLE TOOLS:

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
   Args: keywords (list)
   Returns: segments (timestamps of detected keywords)

5. mute_segments - Mute audio segments
   Args: segments (list), mode (str: "silence" or "beep")
   Returns: output_audio_path (processed audio)

6. mute_keywords - Mute keywords in audio (composite tool)
   Args: keywords (list), mode (str: "silence" or "beep")
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
{"pipeline": [{"tool": "blur_faces", "args": {}}]}

Request: "Mute password mentions"
Response:
{"pipeline": [{"tool": "mute_keywords", "args": {"keywords": ["password"], "mode": "beep"}}]}

Request: "Detect faces with custom blur kernel 41"
Response:
{"pipeline": [
  {"tool": "detect_faces", "args": {}},
  {"tool": "blur", "args": {"mask_stream_path": "$prev.mask_stream_path", "kernel": 41}}
]}

Request: "Remove license plates from video"
Response:
{"error": "Tool 'detect_license_plates' not available", "available_tools": ["blur_faces", "detect_faces", "blur"]}

Request: "Blur faces and mute keywords in the same request"
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

    def plan(self, user_request: str):
            
        # First attempt to generate manifest
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
        
        # Check if this is an error response for unavailable tool
        if "error" in manifest and "not available" in manifest["error"]:
            try:
                # Extract the tool name from the error message
                error_msg = manifest["error"]
                # Look for pattern like "Tool 'X' not available"
                import re
                tool_match = re.search(r"Tool '([^']+)' not available", error_msg)
                if tool_match:
                    requested_tool = tool_match.group(1)
                    available_tools = manifest.get("available_tools", [])
                    
                    print(f"Attempting to generate custom tool: {requested_tool}")
                    
                    # Generate the custom tool
                    generation_result = generate_custom_tool(user_request, available_tools)
                    
                    if generation_result.get("success"):
                        print(f"Successfully generated tool: {generation_result['tool_name']}")
                        
                        # Update the system prompt to include the new tool
                        new_system_prompt = self._update_system_prompt_with_new_tool(
                            generation_result['tool_name'], user_request
                        )
                        
                        print(f"🔄 Retrying manifest generation with new tool available...")
                        
                        # Retry generating the manifest with the new tool available
                        retry_response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {'role': 'system', 'content': new_system_prompt},
                                {'role': 'user', 'content': user_request}
                            ],
                            temperature=0.1,
                            response_format={"type": "json_object"}
                        )
                        
                        retry_manifest = json.loads(retry_response.choices[0].message.content)
                        return retry_manifest
                    else:
                        # If tool generation failed, return an error
                        return {
                            "error": f"Failed to generate custom tool '{requested_tool}': {generation_result.get('error', 'Unknown error')}"
                        }
                        
            except Exception as e:
                # If anything goes wrong in tool generation, return the original error
                return {
                    "error": f"Tool generation failed: {str(e)}. Original error: {manifest['error']}"
                }
        
        return manifest
    
    def _update_system_prompt_with_new_tool(self, tool_name: str, user_request: str) -> str:
        """Update the system prompt to include the newly generated tool."""
        # Create a basic tool description based on the user request
        tool_description = self._infer_tool_description(tool_name, user_request)
        
        # Insert the new tool into the AVAILABLE TOOLS section
        lines = SYSTEM_PROMPT.split('\n')
        
        # Find where to insert the new tool (after the existing tools)
        insert_index = -1
        for i, line in enumerate(lines):
            if "6. mute_keywords - Mute keywords in audio (composite tool)" in line:
                insert_index = i + 1
                break
        
        if insert_index > 0:
            # Insert the new tool description with proper arguments
            if "background" in tool_name.lower():
                new_tool_line = f"\n7. {tool_name} - {tool_description}"
                new_tool_line += f"\n   Args: none (input file provided at runtime)"
                new_tool_line += f"\n   Returns: output_video_path (processed video)"
            elif "transcribe" in tool_name.lower():
                new_tool_line = f"\n7. {tool_name} - {tool_description}"
                new_tool_line += f"\n   Args: none (input file provided at runtime)"
                new_tool_line += f"\n   Returns: transcription (text)"
            else:
                new_tool_line = f"\n7. {tool_name} - {tool_description}"
                new_tool_line += f"\n   Args: none (input file provided at runtime)"
                new_tool_line += f"\n   Returns: output_path (processed file)"
            
            lines.insert(insert_index, new_tool_line)
            
            # Update the existing tool list to include this new tool in relevant contexts
            updated_prompt = '\n'.join(lines)
            
            # Update multiple references to available tools lists
            tool_lists_to_update = [
                ('"available_tools": ["blur_faces", "detect_faces", "blur"]',
                 f'"available_tools": ["blur_faces", "detect_faces", "blur", "{tool_name}"]'),
                ('ONLY use tools from the list above',
                 f'ONLY use tools from the list above (including newly available: {tool_name})'),
            ]
            
            for old_text, new_text in tool_lists_to_update:
                updated_prompt = updated_prompt.replace(old_text, new_text)
            
            return updated_prompt
        
        return SYSTEM_PROMPT
    
    def _infer_tool_description(self, tool_name: str, user_request: str) -> str:
        """Infer tool description based on the tool name and user request."""
        request_lower = user_request.lower()
        
        if "license plate" in request_lower:
            return "Detect and blur license plates in video"
        elif "transcribe" in request_lower:
            return "Transcribe audio to text"
        elif "text" in request_lower and ("detect" in request_lower or "blur" in request_lower):
            return "Detect and blur text in video"
        elif "object" in request_lower:
            return "Detect and blur objects in video"
        elif "background" in request_lower:
            return "Remove or blur background in video"
        else:
            # Generic description
            if "detect" in tool_name.lower():
                return f"Custom detection tool for {user_request.lower()}"
            elif any(word in tool_name.lower() for word in ["blur", "mute", "remove"]):
                return f"Custom privacy protection tool for {user_request.lower()}"
            else:
                return f"Custom tool for {user_request.lower()}"
    
    def save_manifest(self, manifest: dict, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    
    planner = PipelinePlanner(api_key=api_key)
    
    test_cases = [
        # === BASIC VIDEO TESTS ===
        "Blur faces in my video",
        "Just detect faces, don't blur",
        "Blur with kernel size 51",
        "Blur faces with very strong blur",
        "Detect and blur faces with kernel 15",
        
        # === BASIC AUDIO TESTS ===
        "Mute password mentions",
        "Use beep instead of mute for profanity",
        "Detect keywords 'credit card' and 'ssn'",
        "Silence mentions of 'address' and 'phone number'",
        "Beep out bad words",
        
        # === MULTI-KEYWORD TESTS ===
        "Mute 'password', 'username', 'email', and 'ssn'",
        "Remove mentions of medical terms like 'diagnosis' and 'prescription'",
        "Beep profanity words",
        
        # === CUSTOM PARAMETERS ===
        "Blur with kernel 91",
        "Use silence mode instead of beep",
        "Detect faces only, no processing",
        "Detect keywords only, don't mute",
        
        # === CHAINING TESTS ===
        "First detect faces, then blur with kernel 25",
        "Detect keywords then mute them with beep",
        
        # === ERROR CASES - UNAVAILABLE TOOLS ===
        "Transcribe this audio",
        "Remove license plates from video",
        "Detect text in video",
        "Convert speech to text",
        "Remove background noise",
        "Enhance video quality",
        "Detect objects in video",
        
        # === ERROR CASES - MULTI-MODAL CONFUSION ===
        "Blur faces and mute keywords 'password' and 'ssn'",
        "Process both video and audio",
        
        # === EDGE CASES ===
        "Blur everything in the video",
        "Mute the entire audio",
        "Don't do anything",
    ]

    total_time = 0
    success_count = 0
    error_count = 0
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

