"""
audio_feedback.py — Non-blocking text-to-speech.
"""

import threading
import queue
import multiprocessing
import config


def _speak_in_subprocess(text, rate):
    
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()


class SpeechEngine:
    def __init__(self, rate=None):
        self.rate = rate or config.SPEECH_RATE

        self._queue = queue.Queue()
        self.muted = False

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while True:
            text = self._queue.get()
            if text is None:  # sentinel for shutdown
                break
            if self.muted:
                continue
            try:
                p = multiprocessing.Process(target=_speak_in_subprocess, args=(text, self.rate))
                p.start()
                p.join(timeout=10)  # wait for this utterance to finish before the next
                if p.is_alive():
                    p.terminate()
            except Exception as e:
                print(f"[SpeechEngine] failed to speak '{text}': {e}")

    def speak(self, text, priority=False):
        """Queue text to be spoken. If priority=True, drop pending messages first."""
        if priority:
            with self._queue.mutex:
                self._queue.queue.clear()
        self._queue.put(text)

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def shutdown(self):
        self._queue.put(None)
