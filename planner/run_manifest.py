#!/usr/bin/env python3

"""Module for executing pipeline manifests."""

import os
import subprocess
import inspect
from pathlib import Path
import audit.logger as audit


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


def _get_tool_type(accepted_params):
    """Determine if a tool is video-based, audio-based, or mixed based on its accepted parameters.
    
    Args:
        accepted_params: Set of parameter names the tool accepts
        
    Returns:
        'video', 'audio', or 'mixed'
    """
    accepts_video = 'video_path' in accepted_params
    accepts_audio = 'audio_path' in accepted_params
    
    if accepts_video and accepts_audio:
        return 'mixed'
    elif accepts_video:
        return 'video'
    elif accepts_audio:
        return 'audio'
    else:
        # Tool doesn't accept standard paths - could be a utility tool
        return 'unknown'


def run_manifest(manifest, file_path=None, base_path=None):
    """Execute the generated pipeline and return results.
    
    Automatically chains outputs to inputs based on tool type:
    - Video tools receive the most recent video output as input
    - Audio tools receive the most recent audio output as input
    - No need for $prev references in the manifest
    """
    
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
    
    # Track the most recent output of each type for automatic chaining
    last_video_output = None  # Most recent video output path
    last_audio_output = None  # Most recent audio output path
    
    # Define file extensions
    video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    audio_exts = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
    
    # Determine original file type
    original_file_type = None
    if file_path:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in video_exts:
            original_file_type = 'video'
        elif file_ext in audio_exts:
            original_file_type = 'audio'
    
    for i, step in enumerate(manifest["pipeline"], 1):
        tool_name = step.get("tool")
        args = step.get("args", {}).copy()  # Make a copy to avoid modifying the manifest
        
        print(f"\nStep {i}: Executing '{tool_name}'")
        
        # Get the tool from registry
        tool = registry.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found in registry"}
        
        # Inspect the tool's apply method to see what parameters it accepts
        try:
            apply_method = tool.apply
            sig = inspect.signature(apply_method)
            accepted_params = set(sig.parameters.keys())
        except Exception:
            # If inspection fails, assume it accepts common parameters
            accepted_params = {'video_path', 'audio_path', 'live', 'kwargs'}
        
        # Determine what type of tool this is based on its signature
        tool_type = _get_tool_type(accepted_params)
        print(f"  Tool type: {tool_type} (accepts: {', '.join(p for p in ['video_path', 'audio_path'] if p in accepted_params) or 'neither'})")
        audit.tool_start(i, tool_name, tool_type, args)
        
        # Smart input injection: use previous output of same type, or fall back to original file
        if 'video_path' in accepted_params and 'video_path' not in args:
            if last_video_output:
                # Use the output from a previous video processing step
                args['video_path'] = last_video_output
                print(f"  Chained video_path from previous step: {Path(last_video_output).name}")
            elif file_path and original_file_type == 'video':
                # Fall back to original input file
                args['video_path'] = file_path
                print(f"  Using original video_path: {Path(file_path).name}")
        
        if 'audio_path' in accepted_params and 'audio_path' not in args:
            if last_audio_output:
                # Use the output from a previous audio processing step
                args['audio_path'] = last_audio_output
                print(f"  Chained audio_path from previous step: {Path(last_audio_output).name}")
            elif file_path:
                # Fall back to original input file (video files also contain audio)
                args['audio_path'] = file_path
                print(f"  Using original audio_path: {Path(file_path).name}")
        
        # Legacy support: Replace $prev references if they exist in the manifest
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
                print(f"  ✓ Step {i} completed successfully")
                
                # Check for various output path field names
                output_path_field = None
                if "output_path" in result:
                    output_path_field = result['output_path']
                elif "output_video_path" in result:
                    output_path_field = result['output_video_path']
                elif "audio_path" in result:
                    output_path_field = result['audio_path']
                
                audit.tool_end(i, tool_name, True, output_path_field)
                
                if output_path_field:
                    print(f"    Output: {output_path_field}")
                    # Track video and audio outputs separately for automatic chaining
                    output_ext = os.path.splitext(output_path_field)[1].lower()
                    if output_ext in video_exts:
                        last_video_output = output_path_field
                        print(f"    → Updated last_video_output")
                    elif output_ext in audio_exts:
                        last_audio_output = output_path_field
                        print(f"    → Updated last_audio_output")
                        
                previous_result = result
            else:
                err = result.get('error', 'Unknown error') if result else 'No result'
                audit.tool_end(i, tool_name, False, error=err)
                print(f"  ✗ Step {i} failed: {err}")
                break
                
        except Exception as e:
            error_result = {"error": str(e)}
            results.append({
                "step": i,
                "tool": tool_name,
                "result": error_result,
                "success": False
            })
            audit.tool_end(i, tool_name, False, error=str(e))
            print(f"  ✗ Step {i} exception: {e}")
            break
    
    # Determine final output
    print("\n" + "=" * 40)
    print("Pipeline Summary")
    print("=" * 40)
    
    # If we have both video and audio outputs from different steps, merge them
    if last_video_output and last_audio_output:
        print("Both video and audio were processed - merging streams...")
        
        # Generate merged output filename
        results_dir = Path("data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(file_path).stem if file_path else "output"
        merged_output = results_dir / f"{base_name}_processed.mp4"
        
        audit.merge_start(last_video_output, last_audio_output)
        merge_result = merge_video_audio(last_video_output, last_audio_output, str(merged_output))
        
        if merge_result.get("success"):
            audit.merge_end(True, merge_result["output_path"])
            # Update the final result to point to merged file
            previous_result = {
                "output_path": merge_result["output_path"],
                "video_source": last_video_output,
                "audio_source": last_audio_output,
                "merged": True
            }
            print(f"\n✓ Final merged output: {merge_result['output_path']}")
        else:
            err = merge_result.get('error', 'Unknown error')
            audit.merge_end(False, error=err)
            print(f"\n✗ Merge failed: {err}")
            # Still return the individual outputs
            previous_result = {
                "video_output": last_video_output,
                "audio_output": last_audio_output,
                "merged": False,
                "merge_error": err
            }
    elif last_video_output:
        print(f"Video-only processing completed")
        print(f"✓ Final output: {last_video_output}")
        previous_result = {"output_path": last_video_output}
    elif last_audio_output:
        print(f"Audio-only processing completed")
        print(f"✓ Final output: {last_audio_output}")
        previous_result = {"output_path": last_audio_output}
    else:
        print("No output files generated")
    
    return {"pipeline_results": results, "final_result": previous_result}
