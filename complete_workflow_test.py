#!/usr/bin/env python3

import os
import sys
import json
import time
from dotenv import load_dotenv
import importlib

# Add project root to path
project_root = sys.path[0]

def setup_environment():
    """Setup environment and check requirements."""
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in environment variables")
        return False
    
    return True

def get_test_files():
    """Get available test files."""
    videos_dir = f"{project_root}/data/samples"
    if not os.path.exists(videos_dir):
        return []
    
    video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
    return sorted(video_files)

def execute_pipeline(manifest, file_path=None, base_path=None):
    """Execute the generated pipeline and return results."""
    
    if "error" in manifest:
        return {"error": f"Cannot execute pipeline: {manifest['error']}"}
    
    if "pipeline" not in manifest:
        return {"error": "No pipeline found in manifest"}
    
    print("\nExecuting Pipeline...")
    print("=" * 40)
    
    # Import registry to access tools
    import registry
    
    results = []
    previous_result = None
    
    for i, step in enumerate(manifest["pipeline"], 1):
        tool_name = step.get("tool")
        args = step.get("args", {}).copy()  # Make a copy to avoid modifying the manifest
        
        print(f"Step {i}: Executing '{tool_name}'")
        
        # Get the tool from registry
        tool = registry.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found in registry"}
        
        # Inject file_path if provided and tool needs it
        if file_path:
            # Determine whether this is a video or audio file based on file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
            audio_exts = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
            
            # Inject appropriate file path based on file extension
            # This works for both known and dynamically generated tools
            if file_ext in video_exts:
                if 'video_path' not in args:  # Only inject if not already specified
                    args['video_path'] = file_path
                    print(f"  Injected video_path: {file_path}")
            elif file_ext in audio_exts:
                if 'audio_path' not in args:  # Only inject if not already specified
                    args['audio_path'] = file_path
                    print(f"  Injected audio_path: {file_path}")
        
        # Replace $prev references with actual values from previous step
        if previous_result:
            for key, value in args.items():
                if isinstance(value, str) and value.startswith("$prev."):
                    field_name = value.replace("$prev.", "")
                    if field_name in previous_result:
                        args[key] = previous_result[field_name]
                        print(f"  Replaced {value} with {previous_result[field_name]}")
        
        try:
            # Execute the tool
            result = tool.apply(**args)
            results.append({
                "step": i,
                "tool": tool_name,
                "result": result,
                "success": "error" not in result
            })
            
            if "error" not in result:
                print(f"  Step {i} completed successfully")
                if "output_path" in result:
                    print(f"     Output: {result['output_path']}")
                previous_result = result
            else:
                print(f"  Step {i} failed: {result['error']}")
                break
                
        except Exception as e:
            error_result = {"error": str(e)}
            results.append({
                "step": i,
                "tool": tool_name,
                "result": error_result,
                "success": False
            })
            print(f"  Step {i} exception: {e}")
            break
    
    return {"pipeline_results": results, "final_result": previous_result}

def interactive_mode():
    """Interactive mode for testing different prompts."""
    
    print("Interactive Mode")
    print("=" * 50)
    print("Enter prompts to test the complete workflow.")
    print("Type 'quit' to exit, 'files' to see available test files.\n")
    
    test_files = get_test_files()
    if test_files:
        print(f"Available test files: {', '.join(test_files)}")
    
    print("\nExample prompts:")
    example_prompts = [
        "Remove background from video",
        "Blur faces in my video", 
        "Detect license plates in video",
        "Mute keywords 'password' and 'credit card'",
        "Transcribe this audio file"
    ]
    
    for prompt in example_prompts:
        print(f"   • {prompt}")
    
    print("\n" + "-" * 50)
    
    from planner.write_manifest import PipelinePlanner
    api_key = os.environ.get("GROQ_API_KEY")
    planner = PipelinePlanner(api_key=api_key)
    
    while True:
        try:
            prompt = input("\nEnter your prompt: ").strip()
            
            if prompt.lower() == 'quit':
                print("Goodbye!")
                break
            elif prompt.lower() == 'files':
                test_files = get_test_files()
                print(f"Available files: {', '.join(test_files)}")
                continue
            elif not prompt:
                continue
            
            # Ask for file if needed
            file_path = None
            if any(word in prompt.lower() for word in ['video', 'audio', 'file']):
                file_input = input("File path (or press Enter to use 4.mp4): ").strip()
                if file_input:
                    if not file_input.startswith('/'):
                        file_path = f"{project_root}/data/samples/{file_input}"
                    else:
                        file_path = file_input
                else:
                    file_path = f"{project_root}/data/samples/273922_large.mp4"
                
                if not os.path.exists(file_path):
                    print(f"ERROR: File not found: {file_path}")
                    continue
                
                print(f"Using file: {file_path}")
            
            # Execute the complete workflow
            run_complete_workflow(prompt, file_path, planner)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_complete_workflow(prompt, file_path=None, planner=None):
    """Run the complete workflow for a given prompt."""
    
    print(f"\nRunning Complete Workflow")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    if file_path:
        print(f"File: {file_path}")
    print("-" * 60)
    
    if not planner:
        from planner.write_manifest import PipelinePlanner
        api_key = os.environ.get("GROQ_API_KEY")
        planner = PipelinePlanner(api_key=api_key)
    
    start_time = time.time()
    
    try:
        # Step 1: Generate manifest (may trigger tool generation)
        print("Step 1: Generating manifest...")
        manifest = planner.plan(prompt)
        
        planning_time = time.time() - start_time
        print(f"Planning completed in {planning_time:.2f} seconds")
        
        print("\nGenerated Manifest:")
        print(json.dumps(manifest, indent=2))
        
        if "error" in manifest:
            print(f"\nERROR: Planning failed: {manifest['error']}")
            return False
        
        # Step 2: Execute the pipeline
        print("\nStep 2: Executing generated pipeline...")
        execution_start = time.time()
        
        execution_results = execute_pipeline(manifest, file_path)
        
        execution_time = time.time() - execution_start
        total_time = time.time() - start_time
        
        print(f"\nExecution completed in {execution_time:.2f} seconds")
        print(f"Total workflow time: {total_time:.2f} seconds")
        
        # Step 3: Show results
        if "error" in execution_results:
            print(f"\nERROR: Execution failed: {execution_results['error']}")
            return False
        
        print("\nWORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Show pipeline results
        if "pipeline_results" in execution_results:
            print("Pipeline Execution Summary:")
            for result in execution_results["pipeline_results"]:
                status = "SUCCESS" if result["success"] else "FAILED"
                print(f"  {status}: Step {result['step']}: {result['tool']}")
        
        # Show final result
        if "final_result" in execution_results and execution_results["final_result"]:
            final = execution_results["final_result"]
            print("\nFinal Output:")
            if "output_path" in final:
                output_path = final["output_path"]
                print(f"  File: {output_path}")
                if os.path.exists(output_path):
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"  Size: {size_mb:.1f} MB")
                else:
                    print("  WARNING: Output file not found")
            
            if "summary" in final:
                print("  Summary:")
                for key, value in final["summary"].items():
                    print(f"     {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Workflow failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    
    print("Complete Workflow Test - From Prompt to Execution")
    print("=" * 70)
    
    # Setup
    if not setup_environment():
        return False
    
    # Check for command line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        file_path = f"{project_root}/data/samples/4.mp4"  # Default file
        
        print(f"Testing with prompt: '{prompt}'")
        success = run_complete_workflow(prompt, file_path)
        
        if success:
            print("\nTEST PASSED!")
        else:
            print("\nTEST FAILED!")
        
        return success
    else:
        # Interactive mode
        interactive_mode()
        return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
