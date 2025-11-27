#!/usr/bin/env python3

"""Module for executing pipeline manifests."""

import os
import subprocess
import inspect
from pathlib import Path


def merge_video_audio(video_path, audio_path, output_path):
    """Merge video and audio streams into a single file using ffmpeg.
    
    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        output_path: Path for the merged output file
        
    Returns:
        dict: {"output_path": merged file path, "success": bool}
    """
    try:
        # Use ffmpeg to merge video and audio
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',  # Copy video stream without re-encoding
            '-c:a', 'aac',   # Encode audio as AAC
            '-map', '0:v:0', # Take video from first input
            '-map', '1:a:0', # Take audio from second input
            '-shortest',     # Match shortest stream duration
            '-y',            # Overwrite output file if it exists
            output_path
        ]
        
        print(f"  Merging video and audio streams...")
        print(f"    Video: {Path(video_path).name}")
        print(f"    Audio: {Path(audio_path).name}")
        print(f"    Output: {Path(output_path).name}")
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Successfully merged into: {output_path}")
            return {"output_path": output_path, "success": True}
        else:
            error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
            print(f"  ✗ Failed to merge: {error_msg}")
            return {"error": f"ffmpeg merge failed: {error_msg}", "success": False}
            
    except FileNotFoundError:
        return {"error": "ffmpeg not found. Please install ffmpeg.", "success": False}
    except Exception as e:
        return {"error": f"Merge failed: {str(e)}", "success": False}


def run_manifest(manifest, file_path=None, base_path=None):
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
    video_output = None  # Track video output
    audio_output = None  # Track audio output
    
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
            
            # Inspect the tool's apply method to see what parameters it accepts
            try:
                apply_method = tool.apply
                sig = inspect.signature(apply_method)
                accepted_params = set(sig.parameters.keys())
            except Exception:
                # If inspection fails, assume it accepts common parameters
                accepted_params = {'video_path', 'audio_path', 'live', 'kwargs'}
            
            # Inject appropriate file path based on file extension and what tool accepts
            # This works for both known and dynamically generated tools
            if file_ext in video_exts:
                # For video files, inject both video_path and audio_path
                # but only if the tool actually accepts them
                if 'video_path' not in args and 'video_path' in accepted_params:
                    args['video_path'] = file_path
                    print(f"  Injected video_path: {file_path}")
                if 'audio_path' not in args and 'audio_path' in accepted_params:
                    args['audio_path'] = file_path
                    print(f"  Injected audio_path: {file_path}")
            elif file_ext in audio_exts:
                if 'audio_path' not in args and 'audio_path' in accepted_params:
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
            
            # Check if result is a generator and consume it
            if hasattr(result, '__iter__') and hasattr(result, '__next__'):
                # Consume the generator and keep the last value
                final_result = None
                for final_result in result:
                    pass
                result = final_result
            
            results.append({
                "step": i,
                "tool": tool_name,
                "result": result,
                "success": "error" not in result if result else False
            })
            
            if result and "error" not in result:
                print(f"  Step {i} completed successfully")
                
                # Check for various output path field names
                output_path_field = None
                if "output_path" in result:
                    output_path_field = result['output_path']
                elif "output_video_path" in result:
                    output_path_field = result['output_video_path']
                elif "audio_path" in result:
                    output_path_field = result['audio_path']
                
                if output_path_field:
                    print(f"     Output: {output_path_field}")
                    # Track video and audio outputs separately
                    output_ext = os.path.splitext(output_path_field)[1].lower()
                    if output_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                        video_output = output_path_field
                    elif output_ext in ['.wav', '.mp3', '.aac', '.flac']:
                        audio_output = output_path_field
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
    
    # If we have both video and audio outputs, merge them
    if video_output and audio_output and len(results) > 1:
        print("\n" + "=" * 40)
        print("Merging video and audio streams...")
        print("=" * 40)
        
        # Generate merged output filename
        results_dir = Path("data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(file_path).stem if file_path else "output"
        merged_output = results_dir / f"{base_name}_processed.mp4"
        
        merge_result = merge_video_audio(video_output, audio_output, str(merged_output))
        
        if merge_result.get("success"):
            # Update the final result to point to merged file
            previous_result = {
                "output_path": merge_result["output_path"],
                "video_source": video_output,
                "audio_source": audio_output,
                "merged": True
            }
            print(f"\n✓ Final merged output: {merge_result['output_path']}")
        else:
            print(f"\n✗ Merge failed: {merge_result.get('error', 'Unknown error')}")
    
    return {"pipeline_results": results, "final_result": previous_result}
