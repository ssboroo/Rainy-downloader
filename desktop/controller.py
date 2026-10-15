"""GUI-independent controller; callbacks and widgets belong to the UI layer."""
from host.storage import Store
from host.core import normalize_url
from host.runtime import DATA,health,ensure_worker
from host.native import inspect,dispatch
class Controller:
    def __init__(self,path=None):self.store=Store(path or DATA/'queue.db')
    def snapshot(self):return self.store.snapshot()
    def save_settings(self,values):return self.store.settings(values)
    def inspect(self,url):
        if not health()['ready']:raise ValueError(health()['message'])
        return inspect(normalize_url(url))
    def enqueue(self,url,title='',**settings):
        if not health()['ready']:raise ValueError(health()['message'])
        job=self.store.enqueue({'url':normalize_url(url),'title':title,**settings});ensure_worker();return job
    def cancel(self,id):return dispatch('cancel',{'id':id},self.store)
    def open_folder(self,id):return dispatch('open_folder',{'id':id},self.store)
