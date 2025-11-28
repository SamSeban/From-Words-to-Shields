from registry import register
import sys
import time
import numpy as np
from pathlib import Path
import pygame
import sounddevice as sd
import threading


# Calculate the path to the directory containing whisper_online.py 
# (ROOT/models/whisper_streaming)
WHISPER_STREAMING_DIR = Path(__file__).resolve().parent.parent.parent / 'models' / 'whisper_streaming'

# Add the directory to the Python search path.
sys.path.append(str(WHISPER_STREAMING_DIR))

try:
    # Import the model wrapper and the real-time processing handler
    from whisper_online import FasterWhisperASR, OnlineASRProcessor
except ImportError as e:
    # This should now only trigger if the class names change or the path is wrong.
    print(f"FATAL ERROR: Could not import necessary ASR classes. {e}")


# params for live streaming
SAMPLE_RATE = 16000
PLAYBACK_DELAY = 7.0  # seconds. This parameter is to be tuned. Can decrease it if using GPU
CHUNK_SIZE_SAMPLES = SAMPLE_RATE * 1  # 1-second chunks for processing
# initialize mic pygame
pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)

class MuteKeywordsLive():
    name = 'mute_keywords_live'

    def __init__(self):
        self.playback_queue = []
        self.keyword_intervals = [] # list of (beg, end) in stream seconds
        self.intervals_lock = threading.Lock()
        threading.Thread(target=self._playback_worker, daemon=True).start()

    def queue_for_playback(self, chunk, sample_rate, stream_time):
        # stream_time is the "audio time" (in seconds) at the start of this chunk
        self.playback_queue.append((time.time(), chunk, sample_rate, stream_time))

    def _playback_worker(self):
        while True:
            now = time.time()
            if self.playback_queue:
                timestamp, chunk, sr, stream_time = self.playback_queue[0]
                if now - timestamp >= PLAYBACK_DELAY:
                    self._play_chunk(chunk, sr, stream_time)
                    self.playback_queue.pop(0)
            time.sleep(0.01)

    def _play_chunk(self, chunk, sample_rate, stream_time):
        # chunk: NumPy mono float32 array (shape: [N,] or [N,1])
        mono = chunk.squeeze()  # ensure 1D
        chunk_len = len(mono)
        chunk_duration = chunk_len / sample_rate

        chunk_start = stream_time
        chunk_end = stream_time + chunk_duration

        # Convert to 16-bit PCM
        pcm16 = (mono * 32767).astype(np.int16)

        # Copy intervals under the lock
        with self.intervals_lock:
            intervals = list(self.keyword_intervals)
            self.keyword_intervals = [(beg, end) for (beg, end) in self.keyword_intervals 
                                   if end > chunk_start]

        # Apply beep over any overlapping intervals
        freq = 1000
        for (beg, end) in intervals:
            # No overlap?
            if end <= chunk_start or beg >= chunk_end:
                continue

            # Overlap in stream time
            ov_start = max(beg, chunk_start)
            ov_end = min(end, chunk_end)

            start_idx = int((ov_start - chunk_start) * sample_rate)
            end_idx = int((ov_end - chunk_start) * sample_rate)

            if end_idx <= start_idx:
                continue

            seg_len = end_idx - start_idx
            t = np.linspace(0, seg_len / sample_rate, seg_len, endpoint=False)
            beep_wave = (0.6 * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

            # Replace the audio segment with the beep
            pcm16[start_idx:end_idx] = beep_wave

        # Stereo for pygame
        stereo = np.column_stack((pcm16, pcm16))
        sound = pygame.sndarray.make_sound(stereo.copy())
        sound.play()


    def audio_chunk_generator(self, samplerate, chunk_size, channels = 1):
        """
        A generator function that captures mic audio and yields a numpy array 
        of audio data chunks when the buffer is full.
        """
        # Queue for incoming audio data
        q = np.empty((0, channels), dtype=np.float32)

        # these params are required by the api, even if not used
        def callback(indata, frames, time_info, status):
            nonlocal q
            if status:
                print(f"Stream warning: {status}", file=sys.stderr)
            q = np.vstack([q, indata])
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='float32', callback=callback):
            print("Started microphone stream")
            stream_time = 0.0  # seconds from start of stream
            while True:
                # Check if the buffer has enough data for a chunk
                if len(q) >= chunk_size:
                    # Get the chunk and remove it from the buffer
                    chunk = q[:chunk_size]
                    q = q[chunk_size:]   
                    self.queue_for_playback(chunk, samplerate, stream_time)
                    stream_time += chunk_size / samplerate
                    # Yield the chunk for ASR processing
                    yield chunk
                else:
                    # Wait briefly for more audio data (non-blocking)
                    time.sleep(0.01)
   

    def detect_keyword(self, keywords: list):
        model = FasterWhisperASR(lan='en', modelsize='tiny.en')
        online = OnlineASRProcessor(model)

        audio_chunks = self.audio_chunk_generator(
            samplerate=SAMPLE_RATE, 
            chunk_size=CHUNK_SIZE_SAMPLES, 
            channels=1
        ) 
        last_processed_index = 0
   
        try:
            for audio_chunk in audio_chunks:
                online.insert_audio_chunk(audio_chunk)
                online.process_iter()  # Process to update commited
                
                # Check new committed words. Use committed mode to avoid issues (non-committed are not precise)
                if hasattr(online, 'commited'):
                    # Process only new words since last check
                    for i in range(last_processed_index, len(online.commited)):
                        word_data = online.commited[i]
                        
                        if len(word_data) >= 3:
                            beg, end, word = word_data
                            word_clean = word.strip()
                            
                            if word_clean:
                                for keyword in keywords:
                                    if keyword.lower() in word_clean.lower():
                                        # Register interval in stream seconds
                                        with self.intervals_lock:
                                            self.keyword_intervals.append((beg, end))
                                        break

                    last_processed_index = len(online.commited)
        
        except KeyboardInterrupt:
            print("\n\nStopping detection...")

TOOL = MuteKeywordsLive()
register(TOOL)