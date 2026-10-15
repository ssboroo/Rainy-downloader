"""Mongolian Windows desktop UI. All Tk operations stay on the UI thread."""
import queue,threading,os,webbrowser
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from desktop.controller import Controller
from desktop.tasks import TaskRunner
from host.storage import DEFAULTS
from host.runtime import ROOT,health,ensure_worker
from host.browser_install import register,status,CHROMIUM_ID
BLUE='#2868F4';BG='#F4F7FC';INK='#192C4D';MUTED='#8797B1';BORDER='#E5ECF7'
LABELS={'queued':'Хүлээж байна','downloading':'Татаж байна','processing':'Нэгтгэж байна','done':'Дууссан','error':'Алдаа','cancelled':'Цуцлагдсан','interrupted':'Тасарсан'}

class App(ctk.CTk):
    def __init__(self):
        super().__init__();ctk.set_appearance_mode('light');ctk.set_default_color_theme('blue')
        self.title('RAINY Татагч');self.geometry('1120x800');self.minsize(940,680);self.configure(fg_color=BG)
        icon=ROOT/'browser-extensions'/'chromium'/'icons'/'rainy.ico'
        if not icon.is_file():icon=ROOT/'extension'/'icons'/'rainy.ico'
        if os.name=='nt' and icon.is_file():self.after(350,lambda:self.iconbitmap(str(icon)))
        self.controller=None;self.runner=TaskRunner();self.selected='download';self.last_jobs=None;self.forms={};self.poll_pending=False
        self.grid_columnconfigure(1,weight=1);self.grid_rowconfigure(0,weight=1)
        self.sidebar=ctk.CTkFrame(self,width=220,corner_radius=0,fg_color='white');self.sidebar.grid(row=0,column=0,sticky='nsew');self.sidebar.grid_propagate(False)
        self.label(self.sidebar,'R',38,BLUE,True).pack(anchor='w',padx=27,pady=(35,0))
        self.label(self.sidebar,'RAINY',23,INK,True).pack(anchor='w',padx=27)
        self.label(self.sidebar,'ТАТАГЧ · DESKTOP',10,MUTED,True).pack(anchor='w',padx=29,pady=(3,34))
        self.nav={}
        for key,text in [('download','↓   Шинэ таталт'),('queue','☷   Таталтууд'),('browsers','↗   Браузерын холболт'),('settings','⚙   Тохиргоо')]:
            b=ctk.CTkButton(self.sidebar,text=text,anchor='w',height=45,corner_radius=12,font=('Segoe UI',13),fg_color='white',text_color=MUTED,hover_color='#EEF4FF',command=lambda k=key:self.show(k));b.pack(fill='x',padx=17,pady=5);self.nav[key]=b
        self.label(self.sidebar,'ТАНЫ ТӨХӨӨРӨМЖИД\nШУУД ХАДГАЛНА.',10,MUTED).pack(side='bottom',padx=27,pady=30,anchor='w')
        self.shell=ctk.CTkFrame(self,fg_color='transparent');self.shell.grid(row=0,column=1,sticky='nsew',padx=33,pady=27);self.shell.grid_columnconfigure(0,weight=1);self.shell.grid_rowconfigure(2,weight=1)
        head=ctk.CTkFrame(self.shell,fg_color='transparent');head.grid(row=0,column=0,sticky='ew');head.grid_columnconfigure(0,weight=1)
        self.label(head,'Таны жижиг таталтын студи',12,MUTED).grid(row=0,column=0,sticky='w')
        self.health_label=self.label(head,'● Шалгаж байна…',11,MUTED);self.health_label.grid(row=0,column=1,sticky='e')
        self.notice=ctk.CTkLabel(self.shell,text='',text_color=BLUE,font=('Segoe UI',12),wraplength=750,justify='left',anchor='w');self.notice.grid(row=1,column=0,sticky='ew',pady=(8,10))
        self.body=ctk.CTkScrollableFrame(self.shell,fg_color='transparent');self.body.grid(row=2,column=0,sticky='nsew');self.body.grid_columnconfigure(0,weight=1)
        self.pages={}
        for name in self.nav:
            p=ctk.CTkFrame(self.body,fg_color='transparent');p.grid_columnconfigure(0,weight=1);self.pages[name]=p
        self.build_download();self.build_queue();self.build_browsers();self.build_settings();self.show('download')
        self.after(80,self.drain);self.after(400,self.poll)
        def initialize():
            controller=Controller();snapshot=controller.snapshot();h=health()
            if controller.store.next():ensure_worker()
            return controller,snapshot,h
        self.async_call(initialize,self.initialized)
        if os.name=='nt':
            from desktop.floating import FloatingControl
            self.floating=FloatingControl(self)
            self.protocol('WM_DELETE_WINDOW',self.withdraw)
    def label(self,parent,text,size=13,color=INK,bold=False,**kw):return ctk.CTkLabel(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),text_color=color,justify='left',**kw)
    def card(self,parent):return ctk.CTkFrame(parent,fg_color='white',corner_radius=18,border_width=1,border_color=BORDER)
    def heading(self,page,title,sub):
        self.label(page,title,32,INK,True).grid(row=0,column=0,sticky='w',pady=(6,4));self.label(page,sub,12,MUTED).grid(row=1,column=0,sticky='w',pady=(0,24))
    def show(self,key):
        self.selected=key
        for k,p in self.pages.items():p.grid_remove();self.nav[k].configure(fg_color='#EAF1FF' if k==key else 'white',text_color=BLUE if k==key else MUTED)
        self.pages[key].grid(row=0,column=0,sticky='nsew')
        if key=='queue':self.last_jobs=None
        if key=='browsers':self.refresh_browsers()
    def say(self,text,error=False):self.notice.configure(text=str(text),text_color='#B65858' if error else BLUE)
    def async_call(self,fn,callback=None,submission=False,on_error=None):
        self.runner.submit(fn,callback,submission,on_error)
    def initialized(self,result):
        self.controller,snap,h=result
        settings=snap['settings'];self.format.set(settings['format']);self.quality.set(str(settings['quality'])+'p');self.folder.set(settings['folder']);self.on_health(h);self.on_snapshot(snap)
    def drain(self):
        def deliver(callback,value,error):
            if error:self.say(error,True)
            elif callback:
                try:callback(value)
                except Exception as exc:self.runner.finish_submission();self.say(str(exc),True)
        self.runner.drain(deliver);self.after(80,self.drain)
    def on_health(self,h):self.health_label.configure(text='● '+h['message'],text_color='#2C9F80' if h['ready'] else '#BA7754')
    def build_download(self):
        p=self.pages['download'];self.heading(p,'Таалагдсан уу? Татаад ав.','Холбоосоо оруул. Чанараа сонго. Үлдсэнийг RAINY хийе.')
        card=self.card(p);card.grid(row=2,column=0,sticky='ew',pady=(0,16));card.grid_columnconfigure(0,weight=1)
        self.label(card,'БИЧЛЭГИЙН ХОЛБООС',11,MUTED,True).grid(row=0,column=0,sticky='w',padx=24,pady=(23,10))
        line=ctk.CTkFrame(card,fg_color='transparent');line.grid(row=1,column=0,sticky='ew',padx=24);line.grid_columnconfigure(0,weight=1)
        self.url=ctk.CTkEntry(line,placeholder_text='https://…',height=48,corner_radius=11,border_color=BORDER,fg_color='#F8FAFF',font=('Segoe UI',14));self.url.grid(row=0,column=0,sticky='ew',padx=(0,8))
        ctk.CTkButton(line,text='Хуулах сангаас',width=135,height=48,fg_color='#EAF1FF',text_color=BLUE,hover_color='#DEE9FF',command=self.paste).grid(row=0,column=1)
        self.label(card,'YouTube    Facebook    Instagram    X    TikTok    + бусад',11,MUTED).grid(row=2,column=0,sticky='w',padx=26,pady=(10,22))
        fields=ctk.CTkFrame(card,fg_color='transparent');fields.grid(row=3,column=0,sticky='ew',padx=24);fields.grid_columnconfigure((0,1),weight=1)
        settings=DEFAULTS;self.format=ctk.StringVar(value=settings['format']);self.quality=ctk.StringVar(value=str(settings['quality'])+'p')
        self.label(fields,'Формат',11,MUTED).grid(row=0,column=0,sticky='w',pady=(0,8));self.label(fields,'Дээд чанар',11,MUTED).grid(row=0,column=1,sticky='w',padx=8,pady=(0,8))
        ctk.CTkSegmentedButton(fields,values=['mp4','mp3'],variable=self.format,height=40,selected_color=BLUE,font=('Segoe UI',13)).grid(row=1,column=0,sticky='ew',padx=(0,8))
        ctk.CTkOptionMenu(fields,values=['360p','480p','720p','1080p','1440p','2160p'],variable=self.quality,fg_color='#EAF1FF',button_color='#DCE8FF',button_hover_color='#C8DCFF',text_color=BLUE,height=40).grid(row=1,column=1,sticky='ew',padx=(8,0))
        self.info_label=self.label(card,'',12,INK,wraplength=680);self.info_label.grid(row=4,column=0,sticky='w',padx=24,pady=(14,2))
        ctk.CTkButton(card,text='↓   Шалгаж татах',height=49,corner_radius=11,fg_color=BLUE,font=('Segoe UI',15,'bold'),command=self.download_url).grid(row=5,column=0,sticky='ew',padx=24,pady=(8,12))
        self.label(card,'Эх видеод байгаа чанараас сонгоно. MP3: 192 kbps.',10,MUTED).grid(row=6,column=0,pady=(0,20))
        batch=self.card(p);batch.grid(row=3,column=0,sticky='ew');batch.grid_columnconfigure(0,weight=1)
        self.label(batch,'Олон холбоос · автоматаар дараалан татах',13,INK,True).grid(row=0,column=0,sticky='w',padx=22,pady=(20,9))
        self.batch=ctk.CTkTextbox(batch,height=100,corner_radius=10,border_width=1,border_color=BORDER,fg_color='#F8FAFF');self.batch.grid(row=1,column=0,sticky='ew',padx=22)
        ctk.CTkButton(batch,text='Дараалалд нэмэх',height=36,fg_color='#EAF1FF',text_color=BLUE,hover_color='#DEE9FF',command=self.download_batch).grid(row=2,column=0,sticky='e',padx=22,pady=16)
    def paste(self):
        try:self.url.delete(0,'end');self.url.insert(0,self.clipboard_get().strip())
        except Exception:self.say('Хуулах санд холбоос олдсонгүй.',True)
    def download_url(self):
        if self.controller is None:self.say('Програм бэлдэж байна. Түр хүлээнэ үү.');return
        if not self.runner.begin_submission():return
        url=self.url.get().strip();settings={'format':self.format.get(),'quality':int(self.quality.get()[:-1])};self.say('Бичлэгийг шалгаж байна…')
        def run():
            self.controller.save_settings(settings)
            return url,self.controller.inspect(url),settings
        self.async_call(run,self.inspected,on_error=lambda e:self.runner.finish_submission())
    def inspected(self,value):
        url,info,settings=value
        if info.get('playlist'):self.runner.finish_submission();self.playlist_dialog(info,settings);return
        self.info_label.configure(text=info['title']);self.async_call(lambda:self.controller.enqueue(url,info['title'],**settings),lambda j:self.added(1),submission=True)
    def added(self,count):self.say(f'{count} бичлэг дараалалд нэмэгдлээ.');self.show('queue')
    def playlist_dialog(self,info,settings):
        win=ctk.CTkToplevel(self);win.title('Татах бичлэгээ сонгох');win.geometry('650x560');win.transient(self);win.grab_set()
        self.label(win,'Эхний 100 хүртэл бичлэгээс сонгоно уу',15,INK,True).pack(pady=20)
        frame=ctk.CTkScrollableFrame(win,fg_color=BG);frame.pack(fill='both',expand=True,padx=20,pady=(0,15));choices=[]
        for entry in info['entries']:
            var=ctk.BooleanVar(value=False);ctk.CTkCheckBox(frame,text=entry['title'][:70],variable=var,font=('Segoe UI',12)).pack(anchor='w',pady=8);choices.append((var,entry))
        def selected():
            entries=[e for var,e in choices if var.get()]
            if not entries:self.say('Татах бичлэгээ сонгоно уу.');return
            if not self.runner.begin_submission():return
            win.destroy()
            def enqueue():
                count=0;errors=[]
                for e in entries:
                    try:self.controller.enqueue(e['url'],e['title'],**settings);count+=1
                    except Exception as exc:errors.append(str(exc))
                return count,errors
            self.async_call(enqueue,self.batch_added,submission=True)
        ctk.CTkButton(win,text='Сонгосон бичлэгүүдийг татах',command=selected,height=40).pack(pady=20)
    def download_batch(self):
        if self.controller is None:self.say('Програм бэлдэж байна. Түр хүлээнэ үү.');return
        if self.runner.submission_active:return
        urls=[x.strip() for x in self.batch.get('1.0','end').splitlines() if x.strip()]
        if not 1<=len(urls)<=100:self.say('1–100 холбоос оруулна уу.',True);return
        settings={'format':self.format.get(),'quality':int(self.quality.get()[:-1])};self.runner.begin_submission();self.say('Холбоосуудыг шалгаж дараалалд нэмж байна…')
        def run():
            count=0;errors=[]
            for url in dict.fromkeys(urls):
                try:
                    info=self.controller.inspect(url)
                    if info.get('playlist'):raise ValueError('Олон бичлэгтэй холбоосыг үндсэн хэсэгт сонгож нэмнэ үү.')
                    self.controller.enqueue(url,info['title'],**settings);count+=1
                except Exception as e:errors.append(str(e))
            return count,errors
        self.async_call(run,self.batch_added,submission=True)
    def batch_added(self,result):
        count,errors=result;self.added(count)
        if errors:self.say(f'{count} нэмэгдлээ. {len(errors)} холбоос нэмэгдсэнгүй: {errors[0]}',True)
    def build_queue(self):
        p=self.pages['queue'];self.heading(p,'Таны таталтууд','Цонхоо хаасан ч таталтын worker ажлаа үргэлжлүүлнэ.')
        self.stats=self.label(p,'',12,MUTED);self.stats.grid(row=2,column=0,sticky='w',pady=(0,15))
        self.jobs_frame=ctk.CTkFrame(p,fg_color='transparent');self.jobs_frame.grid(row=3,column=0,sticky='ew');self.jobs_frame.grid_columnconfigure(0,weight=1)
    def poll(self):
        if self.controller is not None and not self.poll_pending:
            self.poll_pending=True
            self.async_call(self.controller.snapshot,self.on_snapshot,on_error=lambda e:setattr(self,'poll_pending',False))
        self.after(1200,self.poll)
    def on_snapshot(self,snap):
        self.poll_pending=False
        self.nav['queue'].configure(text=f"☷   Таталтууд   {snap['active_count']}")
        if self.selected=='queue' and snap['jobs']!=self.last_jobs:
            self.last_jobs=snap['jobs'];self.render_jobs(snap)
    def render_jobs(self,snap):
        for w in self.jobs_frame.winfo_children():w.destroy()
        self.stats.configure(text=f"{snap['active_count']} идэвхтэй · {snap['omitted']} ажил дэлгэцэд багтаагүй" if snap['omitted'] else f"{snap['active_count']} идэвхтэй")
        if not snap['jobs']:self.label(self.jobs_frame,'↓\nЭхний бичлэгээ татаарай.\nБраузерын товчоор нэмсэн таталт ч энд харагдана.',16,MUTED).grid(pady=45);return
        for i,j in enumerate(snap['jobs']):
            card=self.card(self.jobs_frame);card.grid(row=i,column=0,sticky='ew',pady=(0,12));card.grid_columnconfigure(0,weight=1)
            self.label(card,j['title'][:110],13,INK,True,wraplength=610).grid(row=0,column=0,sticky='w',padx=20,pady=(17,10))
            pc=ctk.CTkProgressBar(card,height=6,progress_color='#31B68C' if j['status']=='done' else BLUE,fg_color='#EBF1FC');pc.grid(row=1,column=0,sticky='ew',padx=20);pc.set(min(1,max(0,(j['progress'] or 0)/100)))
            details=f"{LABELS.get(j['status'],j['status'])} · {j['format'].upper()} · {round(j['progress'] or 0)}%"
            if j.get('speed'):details+=f" · {j['speed']/1048576:.1f} MB/с"
            if j.get('eta'):details+=f" · {int(j['eta'])} сек"
            self.label(card,details,11,MUTED).grid(row=2,column=0,sticky='w',padx=20,pady=(9,16))
            if j['status'] in ('queued','downloading','processing'):text='Цуцлах';fn=lambda id=j['id']:self.async_call(lambda:self.controller.cancel(id))
            elif j['status']=='done':text='Хавтас нээх';fn=lambda id=j['id']:self.async_call(lambda:self.controller.open_folder(id))
            else:text='Дахин татах';fn=lambda job=j:self.async_call(lambda:self.controller.enqueue(job['url'],job['title'],folder=job['folder'],quality=job['quality'],format=job['format']))
            ctk.CTkButton(card,text=text,width=105,height=29,fg_color='#EAF1FF',text_color=BLUE,hover_color='#DEE9FF',command=fn).grid(row=2,column=1,padx=(0,20))
            if j['error']:self.label(card,j['error'][:500],10,'#B76D6D',wraplength=650).grid(row=3,column=0,columnspan=2,sticky='w',padx=20,pady=(0,14))
    def build_browsers(self):
        p=self.pages['browsers'];self.heading(p,'Браузерын холболт','Өргөтгөлгүй: браузерын хажуугийн RAINY хөвөгч товчийг дарна. Доорх helper нь нэмэлт сонголт.')
        self.browser_rows=ctk.CTkFrame(p,fg_color='transparent');self.browser_rows.grid(row=2,column=0,sticky='ew');self.browser_rows.grid_columnconfigure(0,weight=1)
        ctk.CTkButton(p,text='Холболтыг бүртгэх / засах',height=43,command=lambda:self.async_call(lambda:register(ROOT),lambda r:(self.say('Native host бүртгэгдлээ. Өргөтгөлийг тусад нь зөвшөөрнө үү.'),self.refresh_browsers()))).grid(row=3,column=0,sticky='ew',pady=(18,10))
        ctk.CTkButton(p,text='Chromium өргөтгөлийн хавтас нээх',height=40,fg_color='#EAF1FF',text_color=BLUE,command=self.open_extension).grid(row=4,column=0,sticky='ew',pady=6)
        self.label(p,'Chrome: chrome://extensions   ·   Edge: edge://extensions\nBrave: brave://extensions   ·   Opera: opera://extensions\n\nDeveloper mode → Load unpacked → нээгдсэн chromium хавтас.\nӨргөтгөлийн ⚙ хэсгээс «Сайтууд дээр товч гаргах»-ыг зөвшөөрнө.\nFirefox: signed XPI шаардлагатай; developer туршилтад about:debugging.\nВидео бүр болон сайт бүр дээр товч/таталт ажиллана гэсэн баталгаа байхгүй.',12,MUTED,wraplength=670).grid(row=5,column=0,sticky='w',pady=18)
    def refresh_browsers(self):
        for w in self.browser_rows.winfo_children():w.destroy()
        for i,b in enumerate(status()):
            card=self.card(self.browser_rows);card.grid(row=i,column=0,sticky='ew',pady=5);card.grid_columnconfigure(0,weight=1)
            self.label(card,b['name'],15,INK,True).grid(row=0,column=0,sticky='w',padx=18,pady=16)
            self.label(card,'Host бүртгэлтэй · өргөтгөлөө шалгана уу' if b['registered'] else 'Host бүртгээгүй',11,'#339E80' if b['registered'] else MUTED).grid(row=0,column=1,padx=18)
    def open_extension(self):
        folder=ROOT/'browser-extensions'/'chromium'
        if not folder.exists():folder=ROOT/'extension'
        if os.name=='nt':os.startfile(str(folder))
        else:self.say(str(folder))
    def build_settings(self):
        p=self.pages['settings'];self.heading(p,'Танд тохируулъя.','Хавтас, формат, чанарыг санаж дараагийн таталтад хэрэглэнэ.')
        card=self.card(p);card.grid(row=2,column=0,sticky='ew');card.grid_columnconfigure(0,weight=1)
        s=DEFAULTS;self.folder=ctk.StringVar(value=s['folder'])
        self.label(card,'Хадгалах хавтас',12,MUTED).grid(row=0,column=0,sticky='w',padx=23,pady=(23,10))
        ctk.CTkEntry(card,textvariable=self.folder,height=42,border_color=BORDER).grid(row=1,column=0,sticky='ew',padx=23)
        ctk.CTkButton(card,text='Хавтас сонгох',height=33,fg_color='#EAF1FF',text_color=BLUE,command=self.choose_folder).grid(row=2,column=0,sticky='w',padx=23,pady=12)
        self.label(card,'Үндсэн формат, чанарыг «Шинэ таталт» хэсэгт сонгоно.\nБраузерын товч энэ тохиргоог ашиглана.',12,MUTED).grid(row=3,column=0,sticky='w',padx=23,pady=12)
        ctk.CTkButton(card,text='Тохиргоо хадгалах',height=43,command=self.save_settings).grid(row=4,column=0,sticky='ew',padx=23,pady=(10,23))
        self.label(p,'Сайтын нэвтрэх cookie-г автоматаар уншихгүй.\nТатсан файлыг RAINY сервер рүү дамжуулахгүй.\nПрограмыг хаахад таталтын worker ажиллаж үлдэж болно.',11,MUTED).grid(row=3,column=0,sticky='w',pady=24)
    def choose_folder(self):
        folder=filedialog.askdirectory(parent=self,title='Таталт хадгалах хавтас')
        if folder:self.folder.set(folder)
    def save_settings(self):
        if self.controller is None:self.say('Програм бэлдэж байна. Түр хүлээнэ үү.');return
        settings={'folder':self.folder.get(),'format':self.format.get(),'quality':int(self.quality.get()[:-1])}
        self.async_call(lambda:self.controller.save_settings(settings),lambda s:self.say('Тохиргоо хадгалагдлаа.'))

def main():App().mainloop()
