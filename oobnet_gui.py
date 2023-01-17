#!/usr/bin/env python3
"""   
(c) Research Group CAMMA, University of Strasbourg, IHU Strasbourg, France
Website: http://camma.u-strasbg.fr
"""

import os, sys
from threading import Thread
from time import sleep
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fdlg
from tkinter import messagebox
from PIL import ImageTk, Image

from oobnet_exec import Inference

class FileSelDlgDemo(ttk.Frame):
    
    def __init__(self, isapp=True, name='fileseldlgdemo'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=tk.Y, fill=tk.BOTH)
        self.master.title('Out-of-Body Image Detector')
        self.isapp = isapp
        
        self.file_entries = {}

        program_directory=sys.path[0]

        if 'base_library.zip' in program_directory: #for pyinstaller
            program_directory = os.path.dirname(program_directory)

        self.logo1_path = os.path.join(program_directory, 'icons', 'camma.png')
        self.logo2_path = os.path.join(program_directory, 'icons', 'unistra.png')
        self.logo3_path = os.path.join(program_directory, 'icons', 'ihu.png')
        self.logo4_path = os.path.join(program_directory, 'icons', 'inselspital.png')
        self.logo5_path = os.path.join(program_directory, 'icons', 'unibern.png')
        self.about_img_path = os.path.join(program_directory, 'icons', 'question-mark-icon.png')
        
        # style = ttk.Style(self.master)
        # style.theme_use('clam')

        self._create_frame()

        self.ckpt_path = os.path.join(program_directory, 'ckpt', 'oobnet_weights.h5')

        self.progress_window = None

        self.inference = None
        self.thread_inference = None

        self.progress_monitor = None
        self.thread_progress_monitor = None

    def _create_frame(self):
        """https://pyinmyeye.blogspot.com/2012/08/tkinter-filedialog-demo.html"""
        demoPanel = tk.Frame(self)
        demoPanel.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y, pady=15)
        
        
        for item in ('open_video', 'save_video', 'save_text'):
            frame = ttk.Frame(demoPanel)

            w = 45
            if item == 'open_video':
                lbl = ttk.Label(frame, width=w,
                                text='Select input video file to anonymize ')
            elif item == 'save_video':
                lbl = ttk.Label(frame, width=w,
                                text='Select path to output video file (optional)')
            elif item == 'save_text':
                lbl = ttk.Label(frame, width=w,
                                text='Select path to output text file (optional)')

            ent = ttk.Entry(frame, width=25)
            self.file_entries[item] = ent
            btn = ttk.Button(frame, text='Browse...', 
                             command=lambda i=item, e=ent: self._file_dialog(i, e))
            lbl.pack(side=tk.LEFT)
            ent.pack(side=tk.LEFT, expand=tk.Y, fill=tk.X)
            btn.pack(side=tk.LEFT)

            frame.pack(fill=tk.X, padx='1c', pady=5)
           
        def get_image_with_height(img_path, height):
            img = Image.open(img_path)
            img= img.convert(mode="RGBA")
            w, h = img.size
            return img.resize([int(height/h * w), height])
        
        frame = ttk.Frame(demoPanel)

        self.transform = tk.IntVar()
        self.transform.set(0)  # default is solid color

        tk.Label(frame, text="""OOB frame transformation""", padx = 2).pack(side=tk.LEFT)

        tk.Radiobutton(frame, text="Solid color", padx = 20, variable=self.transform, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(frame, text="Blur", padx = 20, variable=self.transform, value=1).pack(side=tk.LEFT)

        btn_cancel = ttk.Button(frame, text='Cancel', command=self.on_closing)
        btn_cancel.pack(side=tk.RIGHT, padx=2)
        btn_convert = ttk.Button(frame, text='Convert', command=self._convert)
        btn_convert.pack(side=tk.RIGHT, padx=2)
        self.qmark_img = ImageTk.PhotoImage(get_image_with_height(self.about_img_path, 12))#18))
        btn_about = tk.Button(frame, image=self.qmark_img, command= self._about_pressed)
        btn_about.pack(side=tk.RIGHT, padx=1, ipadx=3, ipady=3)
        # btn_about.pack(side=tk.RIGHT, padx=2)

        frame.pack(fill=tk.X, padx='1c', pady=5)

        logo_height = 70 
        logo_img1 = ImageTk.PhotoImage(get_image_with_height(self.logo1_path, logo_height))
        logo_label1 = ttk.Label(self, image=logo_img1)
        logo_label1.image = logo_img1
        logo_label1.pack(side=tk.LEFT, pady=3, padx=3)

        logo_img4 = ImageTk.PhotoImage(get_image_with_height(self.logo4_path, logo_height))
        logo_label4 = ttk.Label(self, image=logo_img4)
        logo_label4.image = logo_img4
        logo_label4.pack(side=tk.LEFT, pady=3, padx=3)

        logo_img5 = ImageTk.PhotoImage(get_image_with_height(self.logo5_path, logo_height))
        logo_label5 = ttk.Label(self, image=logo_img5)
        logo_label5.image = logo_img5
        logo_label5.pack(side=tk.LEFT, pady=3, padx=3)

        logo_img3 = ImageTk.PhotoImage(get_image_with_height(self.logo3_path, logo_height))
        logo_label3 = ttk.Label(self, image=logo_img3)
        logo_label3.image = logo_img3
        logo_label3.pack(side=tk.RIGHT, pady=3, padx=3)

        logo_img2 = ImageTk.PhotoImage(get_image_with_height(self.logo2_path, logo_height))
        logo_label2 = ttk.Label(self, image=logo_img2)
        logo_label2.image = logo_img2
        logo_label2.pack(side=tk.RIGHT, pady=3, padx=3)

        

    def _file_dialog(self, type, ent):
        # triggered when the user clicks a 'Browse' button 
        fn = None

        opts = {'initialfile': ent.get()}

        if type == 'open_video':
            opts['title'] = 'Select a file to open...'
            opts['filetypes'] = (('Video files', ['.mp4','.MP4','.mov','.MOV', '.avi','.AVI']),
                                ('All files', '.*'),)
            fn = fdlg.askopenfilename(**opts)
        elif type == 'save_video':
            opts['title'] = 'Select a file to save...'
            opts['filetypes'] = (('Video files', ['.mp4','.MP4','.mov','.MOV', '.avi','.AVI']),
                                ('All files', '.*'),)
            fn = fdlg.asksaveasfilename(**opts)
        else: #save_text
            opts['title'] = 'Select a file to save...'
            opts['filetypes'] = (('Text files', ['.txt','.TXT','.csv','.CSV']),
                                ('All files', '.*'),)
            fn = fdlg.asksaveasfilename(**opts)

        if fn:
            ent.delete(0, tk.END)
            ent.insert(tk.END, fn)

    def _convert(self):
        
        video_in_path = self.file_entries['open_video'].get()
        video_out_path = self.file_entries['save_video'].get()
        text_out_path = self.file_entries['save_text'].get()
        
        if not video_in_path:
            return
        
        if not (video_out_path or text_out_path):
            return

        transform_options = {0: 'solid', 1:'blur'}
        transform_type = transform_options[self.transform.get()]
        self.inference = Inference(
                            ckpt_path=self.ckpt_path, 
                            in_video_path=video_in_path, 
                            out_video_path=video_out_path, 
                            out_text_path=text_out_path, 
                            transform_type=transform_type,
                            )


        self.thread_inference = Thread(target = self.inference.run)
        self.thread_inference.start()

        self.progress_window = ProgressWindow(self.on_closing)
       
        self.progress_monitor = MonitorProgress(self.inference, self.progress_window.update_progress_bar, self.progress_window)
        self.thread_progress_monitor = Thread(target = self.progress_monitor.run)
        self.thread_progress_monitor.start()
    
    def _about_pressed(self):
        
        text = """  Out-of-body frames in endoscopic surgeries can contain privacy sensitive information. \
This tool is meant to help protect privacy by detecting and blurring out these out-of-body frames. \
The output can be either a video file (.mp4, .mov, .avi format) with out-of-body frames replaced by \
solid color or blurred frames, or a text file (plain text, .txt or spreadsheet, .csv) returning frame \
IDs and corresponding out-of-body predictions. The performance of this tool is reported in the publication mentioned below. \
This tool is provided for demonstration and without warranty. \
The authors or their institutions can not be held liable for any privacy concern due to undetected out-of-body frames.

  When referring to this software, please cite the following publication:

  This code is available for non-commercial scientific research purposes as defined in the CC BY-NC-SA 4.0. \
By downloading and using this code you agree to the terms in the LICENSE. \
Third-party codes are subject to their respective licenses.

  Developed by Research Group CAMMA, IHU Strasbourg, University of Strasbourg
  http://camma.u-strasbg.fr"""
        
        messagebox.showinfo(title="About",message=text)
        
    
    def on_closing(self):
        if self.thread_inference is not None:
            self.inference.stop = True
            self.thread_inference.join()

        if self.thread_progress_monitor is not None:
            self.progress_monitor.stop = True
            self.thread_progress_monitor.join()
        
        if self.progress_window is not None:
            self.progress_window.destroy()

        self.master.destroy()


class ProgressWindow(tk.Toplevel):
    #https://stackoverflow.com/a/58922734
    
    def __init__(self, close_fn):
        
        super().__init__()
        
        self.title("Progress")
        self.style = ttk.Style(self)
        self.style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                    {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.progress_bar = ttk.Progressbar(self, style='text.Horizontal.TProgressbar', length=200,
                               maximum=100, value=0)
        self.progress_bar.pack(side=tk.LEFT, padx=10, pady=10)
        self.stop_button = tk.Button(self, text="Stop", command=close_fn)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

    def update_progress_bar(self, num, limit):
        if num is None:
            return
        if num <= limit:
            percentage = round(num/limit * 100)  # Calculate percentage.
            self.progress_bar.config(value=num)
            self.style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(percentage))

            if num == limit:
                self.stop_button.config(text='Done')

class MonitorProgress:
    def __init__(self, inference_obj, update_fn, window_obj):
        self.inference_obj = inference_obj
        self.update_fn = update_fn
        self.window_obj = window_obj
        self.stop = False
        self.progress = 0 # %
        pass
    
    def run(self):

        while not self.stop:
            if not self.window_obj.winfo_exists():
                break
            if self.progress != self.inference_obj.status['percents']:
                self.progress = self.inference_obj.status['percents']
                self.update_fn(self.progress, 100)

            if self.progress == 100:
                break
            
            sleep(1)
        

if __name__ == '__main__':
    root = FileSelDlgDemo()
    root.master.protocol("WM_DELETE_WINDOW", root.on_closing)
    root.mainloop()
