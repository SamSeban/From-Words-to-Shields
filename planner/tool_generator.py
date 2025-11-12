"""Dynamic tool generator for privacy protection tools."""

import os
import json
import time
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ToolGenerator:
    """Generates custom privacy protection tools dynamically."""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
        # Available libraries - only use these, no external dependencies
        self.available_libraries = [
            "cv2", "numpy", "os", "time", "json", "pathlib", 
            "torch", "torchaudio", "whisper", "pydub", "librosa", 
            "soundfile", "typing", "abc", "registry", "tool_api"
        ]
        
        self.system_prompt = f"""You are a privacy protection tool code generator. Generate Python code for custom privacy tools.

CRITICAL REQUIREMENTS:
- Generate a complete Python class that inherits from PrivacyTool
- Only use these available libraries: {', '.join(self.available_libraries)}
- Follow the exact same pattern as existing tools
- Implement both apply() and verify() methods
- Include proper error handling
- Use existing file patterns (data/results/ for outputs)
- Generate working, runnable code

AVAILABLE LIBRARIES AND THEIR USES:
- cv2: Video/image processing, face detection, object detection, image transformations
- numpy: Array operations, mathematical computations
- torch/torchaudio: Deep learning, audio processing
- whisper: Speech recognition, transcription  
- pydub: Audio manipulation, format conversion
- librosa: Audio analysis, feature extraction
- soundfile: Audio I/O operations

TOOL STRUCTURE TEMPLATE:
```python
from tool_api import PrivacyTool
from registry import register
import cv2  # and other needed imports
import numpy as np
import os

class YourCustomTool(PrivacyTool):
    name = "your_tool_name"
    
    def apply(self, **kwargs) -> Dict[str, Any]:
        \"\"\"Apply the privacy protection operation.\"\"\"
        # Implementation here
        # Return dict with results
        return {{"output_path": "...", "summary": {{}}}}
    
    def verify(self, **kwargs) -> Dict[str, Any]:
        \"\"\"Verify the operation was successful.\"\"\"
        # Implementation here
        return {{"verified": True, "details": {{}}}}

TOOL = YourCustomTool()
register(TOOL)
```

EXAMPLES OF CAPABILITIES YOU CAN IMPLEMENT:
- License plate detection/blurring (using cv2 contour detection, edge detection)
- Object detection/blurring (using cv2 template matching, contour detection)
- Text detection/blurring (using cv2 text detection)
- Background removal (using cv2 background subtraction)
- Audio transcription (using whisper)
- Audio enhancement/filtering (using librosa, pydub)
- Custom audio/video effects

IMPLEMENTATION GUIDELINES:
1. For video processing: Use cv2.VideoCapture/VideoWriter pattern
2. For audio processing: Use librosa/pydub for loading, soundfile for saving
3. For detection: Use cv2 built-in detectors, contour detection, template matching
4. Save outputs to data/results/ directory
5. Include performance metrics in results
6. Handle edge cases and errors gracefully

Generate ONLY the Python code, no explanations. Make it production-ready.

Tool request:"""

    def generate_tool(self, tool_request: str, suggested_tools: list = None) -> Dict[str, Any]:
        """Generate a custom tool based on the request."""
        
        try:
            # Add context about related tools if provided
            context = ""
            if suggested_tools:
                context = f"\nRelated existing tools: {', '.join(suggested_tools)}"
            
            prompt = f"{tool_request}{context}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            generated_code = response.choices[0].message.content
            
            # Clean up the generated code (remove markdown syntax if present)
            generated_code = self._clean_generated_code(generated_code)
            
            # Extract tool name from generated code
            tool_name = self._extract_tool_name(generated_code)
            
            if not tool_name:
                return {"error": "Could not extract tool name from generated code"}
            
            # Create the tool file
            tool_file_path = self._create_tool_file(tool_name, generated_code)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "tool_file_path": tool_file_path,
                "generated_code": generated_code
            }
            
        except Exception as e:
            return {"error": f"Failed to generate tool: {str(e)}"}
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean up generated code by removing markdown syntax."""
        # Remove markdown code blocks
        if code.strip().startswith('```python'):
            lines = code.split('\n')
            # Remove first line (```python)
            lines = lines[1:]
            # Remove last line if it's just ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            code = '\n'.join(lines)
        elif code.strip().startswith('```'):
            lines = code.split('\n')
            # Remove first line (```)
            lines = lines[1:]
            # Remove last line if it's just ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        return code.strip()
    
    def _extract_tool_name(self, code: str) -> Optional[str]:
        """Extract tool name from generated code."""
        try:
            # Look for the name attribute
            for line in code.split('\n'):
                line = line.strip()
                if line.startswith('name = '):
                    # Extract the name value
                    name = line.split('=')[1].strip().strip('"\'')
                    return name
            return None
        except:
            return None
    
    def _create_tool_file(self, tool_name: str, code: str) -> str:
        """Create the tool file and return its path."""
        
        # Determine appropriate directory based on tool type
        if 'detect' in tool_name.lower():
            tool_dir = "/home/sam/Documents/GitHub/From-Words-to-Shields/tools/detectors"
        elif any(keyword in tool_name.lower() for keyword in ['blur', 'mute', 'transform', 'remove']):
            tool_dir = "/home/sam/Documents/GitHub/From-Words-to-Shields/tools/transforms"  
        else:
            tool_dir = "/home/sam/Documents/GitHub/From-Words-to-Shields/tools/composites"
        
        os.makedirs(tool_dir, exist_ok=True)
        
        # Create filename
        filename = f"{tool_name.lower().replace(' ', '_')}.py"
        file_path = os.path.join(tool_dir, filename)
        
        # Write the code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def register_tool_in_registry(self, tool_name: str, tool_file_path: str) -> bool:
        """Add the new tool to the registry and import it directly."""
        try:
            # Import the tool directly into the current process
            import sys
            import importlib.util
            
            # Add the project root to Python path if not already there
            project_root = "/home/sam/Documents/GitHub/From-Words-to-Shields"
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Import the tool module dynamically
            spec = importlib.util.spec_from_file_location(f"generated_tool_{tool_name}", tool_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the tool instance and register it manually
            if hasattr(module, 'TOOL'):
                tool_instance = module.TOOL
                
                # Import registry and register the tool directly
                import registry
                registry.TOOLS[tool_name] = tool_instance
                
                print(f"✅ Tool '{tool_name}' registered successfully in current process")
                return True
            else:
                print(f"❌ No TOOL instance found in generated module")
                return False
            
        except Exception as e:
            print(f"❌ Could not register tool in runtime: {e}")
            return False
    
    def wait_for_tool_availability(self, tool_name: str, max_wait_time: int = 5) -> bool:
        """Check if the tool is available in the registry."""
        try:
            import registry
            tool = registry.get(tool_name)
            if tool is not None:
                print(f"✅ Tool '{tool_name}' is now available in registry")
                return True
            else:
                print(f"❌ Tool '{tool_name}' not found in registry")
                return False
        except Exception as e:
            print(f"❌ Error checking tool availability: {e}")
            return False

def generate_custom_tool(tool_request: str, suggested_tools: list = None) -> Dict[str, Any]:
    """Main function to generate a custom tool."""
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not found in environment"}
    
    generator = ToolGenerator(api_key)
    
    # Generate the tool
    result = generator.generate_tool(tool_request, suggested_tools)
    
    if "error" in result:
        return result
    
    tool_name = result["tool_name"]
    tool_file_path = result["tool_file_path"]
    
    # Register the tool in registry
    registry_success = generator.register_tool_in_registry(tool_name, tool_file_path)
    
    # Wait for tool to become available
    tool_available = generator.wait_for_tool_availability(tool_name)
    
    if not tool_available:
        return {"error": f"Generated tool '{tool_name}' did not become available in registry"}
    
    return {
        "success": True,
        "tool_name": tool_name,
        "tool_file_path": tool_file_path,
        "registry_updated": registry_success,
        "tool_available": tool_available
    }

if __name__ == "__main__":
    # Test the generator
    test_request = "Remove license plates from video"
    result = generate_custom_tool(test_request, ["blur_faces", "detect_faces", "blur"])
    print(json.dumps(result, indent=2))
