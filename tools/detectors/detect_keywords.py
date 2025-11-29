"""
Detector: identifies sensitive keywords in audio → outputs segments file.
"""

from tool_api import PrivacyTool
from registry import register
from groq import Groq
import os
import re
from dotenv import load_dotenv
import json
import whisper
from pathlib import Path

load_dotenv()

class DetectKeywords(PrivacyTool):
    name = "detect_keywords"

    def extract_sensitive_content(self, transcript: str, user_intent: str):
        # this function uses groq to identify the sensitive words in the transcript of the speech
        # based on the prompt from the user

        try:
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

            prompt = f"""You are a privacy protection assistant. Analyze the transcript and identify EXACT phrases that should be redacted based on the user's intent.

Transcript: "{transcript}"

User's request: "{user_intent}"

REDACTION GUIDELINES:

1. ADDRESSES - If user mentions "address" or "location":
   - Street addresses with numbers (e.g., "123 Main Street", "Via Grande Vendono")
   - Apartment/unit numbers (e.g., "Apt 4B", "Unit 177")
   - Cities, neighborhoods, and regions mentioned as locations
   - States, provinces, countries in address context
   - Zip/postal codes

2. PHONE NUMBERS - If user mentions "phone", "number", "telephone":
   - Any phone number format (e.g., "555-1234", "123 456 7890")
   - Country codes (e.g., "+1", "+972")

3. EMAIL ADDRESSES - If user mentions "email", "e-mail":
   - Complete email addresses (e.g., "john@example.com")
   - Email domains if mentioned separately

4. PASSWORDS - If user mentions "password", "passcode", "PIN":
   - Any mentioned passwords, PINs, or security codes
   - Security answers or secret phrases

5. USERNAMES - If user mentions "username", "handle", "account":
   - Social media handles (e.g., "@username")
   - Login usernames or account names

6. PERSONAL INFORMATION - If user mentions "personal info", "personal data", "private info":
   - Full names (if context suggests they're private)
   - Social Security Numbers or national IDs
   - Credit card or bank account numbers
   - Dates of birth
   - License plate numbers
   - Any other identifying information

7. FINANCIAL - If user mentions "financial", "bank", "credit card":
   - Credit card numbers
   - Bank account numbers
   - Routing numbers
   - Financial institution names in sensitive context

IMPORTANT RULES:
- Extract EXACT phrases as they appear in the transcript
- Include ALL instances that match the user's intent
- Be comprehensive - better to include too much than miss sensitive data
- If the intent is general (e.g., "personal information"), include ALL applicable categories
- Match the exact spelling/wording from the transcript

Return a JSON object with a "phrases" key containing an array of exact phrases to redact.
Example: {{"phrases": ["123 Main Street", "New York", "555-1234", "john@email.com"]}}

If nothing should be redacted, return: {{"phrases": []}}

Response (JSON object only):"""
            
            response = client.chat.completions.create(model="llama-3.3-70b-versatile",
                                                        messages=[
                                                            {
                                                                "role": "system",
                                                                "content": "You are a privacy protection assistant. Always respond with valid JSON only."
                                                            },
                                                            {
                                                                "role": "user",
                                                                "content": prompt
                                                            }
                                                        ],
                                                        response_format={"type": "json_object"},  # Force JSON output
                                                        temperature=0
                                                    )
            
            data = json.loads(response.choices[0].message.content)
            phrases = data.get("phrases", [])           
            return phrases if isinstance(phrases, list) else []
            
            
        
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            # Fallback: use simple keyword extraction from intent
            # return self._fallback_extraction(transcript, user_intent)
            return []


    def apply(self, audio_path, user_intent, asr="whisper", **kwargs):
        """
        Detect keyword occurrences in audio using ASR and return segment timestamps.
        
        Args:
            audio_path: Path to the audio file
            keywords: List of keywords to detect
            asr: ASR engine to use (default: "whisper")
        
        Returns:
            {"segments_path": path to JSON file containing detected keyword segments}
        """
        
        # Ensure results directory exists
        results_dir = Path("data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename based on input audio
        audio_name = Path(audio_path).stem
        segments_filename = f"{audio_name}_keyword_segments.json"
        segments_path = results_dir / segments_filename
        
        detected_segments = []
        
        if asr == "whisper":
            try:           
                # Load whisper model
                model = whisper.load_model("base") # options: tiny, base, large
                
                # Transcribe with word-level timestamps
                result = model.transcribe(
                    audio_path,
                    word_timestamps=True,
                    verbose=False
                )
                # Get full transcript
                full_transcript = result.get("text", "")                
                segments_with_words = result.get("segments", [])
                # detect the sensitive words
                sensitive_phrases = self.extract_sensitive_content(full_transcript, user_intent)               
                # Search for keywords in word-level segments
                for phrase in sensitive_phrases:
                    phrase_lower = phrase.lower().strip()
                    phrase_words = phrase_lower.split()
                    
                    # Build a flat list of all words with their timestamps
                    all_words = []
                    for segment in segments_with_words:
                        words = segment.get("words", [])
                        for word_info in words:
                            all_words.append({
                                "word": word_info.get("word", "").strip().lower(),
                                "start": word_info.get("start", 0),
                                "end": word_info.get("end", 0)
                            })
                    
                    # Now search for the phrase in the flat word list
                    i = 0
                    while i < len(all_words):
                        # Try to match the phrase starting at position i
                        match_found = True
                        matched_words = []
                        
                        # Check if we have enough words left
                        if i + len(phrase_words) > len(all_words):
                            break
                        
                        # Try to match each word in the phrase
                        for j, target_word in enumerate(phrase_words):
                            current_word = all_words[i + j]["word"]
                            
                            # Normalize for comparison (remove punctuation)
                            current_word_clean = re.sub(r'[^\w\s]', '', current_word).strip()
                            target_word_clean = re.sub(r'[^\w\s]', '', target_word).strip()
                            
                            # STRICT MATCHING: Must be exact word match, not substring
                            # For single-word phrases, require exact match
                            if len(phrase_words) == 1:
                                if current_word_clean != target_word_clean:
                                    match_found = False
                                    break
                            else:
                                # For multi-word phrases, allow fuzzy matching
                                if target_word_clean not in current_word_clean and current_word_clean not in target_word_clean:
                                    match_found = False
                                    break
                            
                            matched_words.append(all_words[i + j])
                        
                        # If we found a match, record it
                        if match_found and matched_words:
                            phrase_start = matched_words[0]["start"]
                            phrase_end = matched_words[-1]["end"]
                            detected_text = " ".join([w["word"] for w in matched_words])
                                                        
                            detected_segments.append({
                                "start_time": phrase_start,
                                "end_time": phrase_end,
                                "sensitive_content": phrase,
                                "detected_text": detected_text, 
                                "confidence": segment.get("avg_logprob", 0)
                            })
                            
                            # Skip past this match to avoid overlapping detections
                            i += len(phrase_words)
                        else:
                            i += 1
                                
            except ImportError:
                print(f"Warning: whisper not installed")
                detected_segments = []
        
        # Save segments to JSON file
        segments_data = {
            "audio_path": audio_path,
            "user_intent": user_intent,
            "asr_engine": asr,
            "segments": detected_segments,
            "total_detections": len(detected_segments)
        }
        
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        return {"segments_path": str(segments_path)}
    
    def verify(self, segments_path, audio_path: str, **kwargs):
        # Basic verification answering these questions: 
        # 1) are the timestamps valid? meaning start_time>0, end_time <= audio_duration, start_time < end_time
        # 2) are there duplicates which are not supposed to be there?
        # 3) Do the segments make sense? If a segment is 15 sec long probably not
      
        with open(segments_path, 'r') as f:
            data = json.load(f)

        segments = data.get("segments", [])

        try: 
            audio = whisper.load_audio(audio_path)
            audio_duration = len(audio) / 16000 # whisper uses 16kHz as frequency
        except:
            audio_duration = float('inf')

        issues = []
        overlap_count = 0

        # check 1
        for i, seg in enumerate(segments):
            start = seg.get('start_time', 0)
            end = seg.get('end_time', 0)

            if start < 0:
                issues.append(f"Segment {i}: start time is negative")
            if end > audio_duration:
                issues.append(f"Segment {i}: end time beyond audio duration ({end:.2f}s > {audio_duration:.2f}s)")
            if start > end:
                issues.append(f"Segment {i}: start is after end ({start:.2f}s > {end:.2f}s)")
            if end - start > 15:   
                issues.append(f"Segment {i}: very long > 15s ({(end - start):.2f}s > 15s)")  

        # check for overlapping
            for j, seg2 in enumerate(segments[i+1:], start= i + 1):
                start_2 = seg2.get('start_time', 0)
                end_2 = seg2.get('end_time', 0)
                if start < end_2 and start_2 < end:
                    overlap_count += 1

        # if there is more than 50% overlap add issue
        if overlap_count > len(segments) * 0.5:
            issues.append(f"Excessive overlap: {overlap_count} overlaps for {len(segments)} segments")

        # check for duplicates
        timestamp_pairs = [(s['start_time'], s['end_time']) for s in segments]
        duplicates = len(timestamp_pairs) - len(set(timestamp_pairs))
        if duplicates > 0:
            issues.append(f"Found {duplicates} segments with identical timestamps (duplicates)")

        stats = {
            "total_segments": len(segments),
            "total_duration_redacted": sum(s["end_time"] - s["start_time"] for s in segments),
            "avg_segment_length": sum(s["end_time"] - s["start_time"] for s in segments) / len(segments) if segments else 0,
            "overlap_count": overlap_count,
            "audio_duration": audio_duration
        }

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "stats": stats,
            "segments_file": segments_path
        }


TOOL = DetectKeywords()
register(TOOL)