"""OS-level floating download control; does not inject anything into browser pages."""
import os
import customtkinter as ctk
from tkinter import Menu
from desktop.browser_capture import foreground_browser,capture_address
class FloatingControl:
    def __init__(self,app):
        self.app=app;self.last_browser=None;self.busy=False
        self.window=ctk.CTkToplevel(app);self.window.withdraw();self.window.overrideredirect(True);self.window.attributes('-topmost',True)
        self.window.geometry('150x44+20+100')
        self.button=ctk.CTkButton(self.window,text='↓  RAINY · Татах',corner_radius=12,height=42,width=148,fg_color='#2868F4',font=('Segoe UI',12,'bold'),command=self.capture)
        self.button.pack(padx=1,pady=1)
        self.menu=Menu(self.window,tearoff=0);self.menu.add_command(label='RAINY програм нээх',command=self.open_app);self.menu.add_separator();self.menu.add_command(label='Програмаас гарах',command=app.destroy)
        self.button.bind('<Button-3>',lambda e:self.menu.tk_popup(e.x_root,e.y_root))
        self.app.after(600,self.poll)
    def open_app(self):self.app.deiconify();self.app.lift()
    def poll(self):
        try:
            browser=foreground_browser() if self.app.float_enabled else None
            if browser:
                self.last_browser=browser
                x=max(5,self.app.winfo_screenwidth()-180)
                self.window.geometry(f'150x44+{x}+115');self.window.deiconify()
            elif not self.busy:self.window.withdraw()
        except Exception:pass
        if self.app.winfo_exists():self.app.after(700,self.poll)
    def capture(self):
        if self.busy or not self.last_browser:return
        self.busy=True;self.button.configure(text='Шалгаж байна…',state='disabled')
        handle=self.last_browser['handle']
        def reset():self.busy=False;self.button.configure(text='↓  RAINY · Татах',state='normal')
        def received(url):
            reset();self.open_app();self.app.show('download');self.app.url.delete(0,'end');self.app.url.insert(0,url)
            self.app.download_url()
        def failed(error):reset();self.open_app()
        self.app.async_call(lambda:capture_address(handle),received,on_error=failed)
