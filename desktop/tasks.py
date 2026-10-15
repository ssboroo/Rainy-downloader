"""Threaded jobs with independent submission lifecycle; drain only on UI thread."""
import queue,threading
class TaskRunner:
    def __init__(self):self.results=queue.Queue();self.submission_active=False
    def begin_submission(self):
        if self.submission_active:return False
        self.submission_active=True;return True
    def finish_submission(self):self.submission_active=False
    def completed(self,callback,value,error,submission=False,on_error=None):self.results.put((callback,value,error,submission,on_error))
    def submit(self,fn,callback=None,submission=False,on_error=None):
        def run():
            try:self.completed(callback,fn(),None,submission,on_error)
            except Exception as e:self.completed(None,None,str(e),submission,on_error)
        thread=threading.Thread(target=run,daemon=True);thread.start();return thread
    def drain(self,deliver):
        while True:
            try:callback,value,error,submission,on_error=self.results.get_nowait()
            except queue.Empty:return
            if submission:self.finish_submission()
            if error and on_error:on_error(error)
            deliver(callback,value,error)
