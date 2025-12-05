#!/usr/bin/env python3

import os
import sys
import time
from dotenv import load_dotenv
from planner.executor import executor

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
            
            file_path = None
            file_input = input("File path (or press Enter to use default): ").strip()
            if file_input:
                if not file_input.startswith('/'):
                    file_path = f"{project_root}/data/samples/{file_input}"
                else:
                    file_path = file_input
            else:
                file_path = f"{project_root}/data/samples/4.mp4"
              
            if not os.path.exists(file_path):
                print(f"ERROR: File not found: {file_path}")
                continue
                
            print(f"Using file: {file_path}")
            
            # Execute the complete workflow
            executor(prompt, file_path, planner)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function."""
    # Setup
    if not setup_environment():
        return False
    
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
