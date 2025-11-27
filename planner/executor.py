#!/usr/bin/env python3

"""Module for executing complete workflows from prompts to results."""

import os
import json
import time
from planner.write_manifest import PipelinePlanner
from planner.run_manifest import run_manifest


def executor(prompt, file_path=None, planner=None):
    """Run the complete workflow for a given prompt.
    
    Args:
        prompt: User prompt/description
        file_path: Path to input file
        planner: PipelinePlanner instance (optional)
    """
    
    print(f"\nRunning Complete Workflow")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    if file_path:
        print(f"File: {file_path}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Step 1: Generate manifest
        if not planner:
            api_key = os.environ.get("GROQ_API_KEY")
            planner = PipelinePlanner(api_key=api_key)
        
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
        
        execution_results = run_manifest(manifest, file_path)
        
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
            
            # Check for various output path field names
            output_path = None
            if "output_path" in final:
                output_path = final["output_path"]
            elif "output_video_path" in final:
                output_path = final["output_video_path"]
            elif "audio_path" in final:
                output_path = final["audio_path"]
                
            if output_path:
                print(f"  File: {output_path}")
                if os.path.exists(output_path):
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"  Size: {size_mb:.1f} MB")
                else:
                    print("  WARNING: Output file not found")
            
            # Show merge info if available
            if "merged" in final and final["merged"]:
                print(f"  Video source: {final.get('video_source', 'N/A')}")
                print(f"  Audio source: {final.get('audio_source', 'N/A')}")
            
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

