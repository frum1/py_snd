import sounddevice as sd
import soundfile as sf
import threading


class AudioPlayer:
    def __init__(self):
        self.current_stream = None
        self.position = 0
        self.data = None
        self.fs = None
        self.lock = threading.Lock()
        
    def load(self, file_path):
        self.data, self.fs = sf.read(file_path, dtype='float32')
        self.position = 0
        
    def play(self, blocking=False):
        if self.data is None: return
        
        def callback(outdata, frames, time, status):
            with self.lock:
                if self.position >= len(self.data):
                    raise sd.CallbackStop()
                chunksize = min(len(self.data) - self.position, frames)
                outdata[:chunksize] = self.data[self.position:self.position + chunksize]
                self.position += chunksize

        self.current_stream = sd.OutputStream(
            samplerate=self.fs,
            channels=self.data.shape[1],
            callback=callback,
            finished_callback=lambda: self._set_event_complete()
        )
        self.current_stream.start()
        
    def pause(self):
        if self.current_stream and self.current_stream.active:
            self.current_stream.stop()
            
    def resume(self):
        if self.data is not None and self.position < len(self.data):
            self.play()
            
    def stop(self):
        if self.current_stream:
            self.current_stream.stop()
            self.current_stream.close()
            self.current_stream = None
        self.position = 0
        
    def _set_event_complete(self):
        pass

# Use example
if __name__ == "__main__":
    player =  AudioPlayer()
    player.load("sounds/example.wav")
    player.play()
