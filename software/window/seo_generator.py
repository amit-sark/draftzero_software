from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkImage, CTkTextbox
from tkinter import messagebox
from PIL import Image, ImageSequence
import os
from tkinter import filedialog
from threading import Thread

from LIBS.caption import Transcriber
from LIBS.gemini_prompt import GeminiApiClient


appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata,'.Quilla')
login_path = os.path.join(quilla_folder,'login_data.csv')
signup_path = os.path.join(quilla_folder,'signup_data.csv')


class SeoGenerator:
    def __init__(self, window):
        self.window = window
        self.selected_button = None
        self.selected_line = None
        self.loading_frames = []
        self.loading_index = 0
        self.loading_running = False

    def select_video_file(self):
        filetypes = (
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("All files", "*.*")
        )
        self.file_path = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=filetypes
        )
        if self.file_path:
            if os.path.exists(login_path) or os.path.exists(signup_path):

                print("Selected file:", self.file_path) 

                try:
                    self.savebtn.destroy()
                    self.seo_info.destroy()
                except:
                    pass



                
                try: 
                    for widget in self.seo_info.winfo_children():
                        widget.destroy()
                except:
                    pass

                self.indication()
                self.t=Transcriber(video_file_path=self.file_path,show_details=self.show_details)

                result = self.t.video_to_text()

                seo = GeminiApiClient().generate_seo(transcribed_text=result)
                self.loading_running = False



                self.scrollable_text(text=seo)
                self.success()

                
                self.save_title = CTkLabel(master=self.element_window,text="Save/Export Metadata",font=("",15,'bold'))
                self.save_title.place(relx=0.44,rely=0.85)
                
                self.savebtn = CTkButton(master=self.element_window,text="Save Metadata",width=120,height=40,corner_radius=10,text_color="white",
                                    command=self.save_script,fg_color="#007bff",hover_color="#007bff",font=("",14,"bold"))
                self.savebtn.place(relx=0.44,rely=0.9)
            else:
                messagebox.showinfo(title="Signup",message="Please signup first to continue!")


    def select_audio_file(self):
        filetypes = (
            ("Video files", "*.mp3 *.wav"),
            ("All files", "*.*")
        )
        self.file_path = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=filetypes
        )
        if self.file_path:

            if os.path.exists(login_path) or os.path.exists(signup_path):
                print("Selected file:", self.file_path) 
            
                try:
                    self.savebtn.destroy()
                    self.seo_info.destroy()
                except:
                    pass

                try: 
                    for widget in self.seo_info.winfo_children():
                        widget.destroy()
                except:
                    pass

                self.indication()
                self.t=Transcriber(audio_file_path=self.file_path,show_details=self.show_details)

                result = self.t.audio_to_text()
                seo = GeminiApiClient().generate_seo(transcribed_text=result)

                self.loading_running = False
                self.scrollable_text(text=seo)
                self.success()

                
                self.save_title = CTkLabel(master=self.element_window,text="Save/Export Metadata",font=("",15,'bold'))
                self.save_title.place(relx=0.44,rely=0.85)
                
                self.savebtn = CTkButton(master=self.element_window,text="Save Metadata",width=120,height=40,corner_radius=10,text_color="white",
                                    command=self.save_script,fg_color="#007bff",hover_color="#007bff",font=("",14,"bold"))
                self.savebtn.place(relx=0.44,rely=0.9)

            else:
                messagebox.showinfo(title="Signup",message="Please signup first to continue!")

    def th_video(self):

        th = Thread(target=self.select_video_file,daemon=True)
        th.start()

    def th_audio(self):

        th = Thread(target=self.select_audio_file,daemon=True)
        th.start()





    def save_script(self):
        self.t.generate_srt()
        
        

    def gui(self):

        for widget in self.window.winfo_children():
            widget.destroy()

        self.element_window = CTkFrame(master=self.window, fg_color="white")
        self.element_window.grid(column=1, row=0, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        video_seo_optimizer = CTkLabel(master=self.element_window,text="Video SEO Optimizer",font=("",27,"bold"))
        video_seo_optimizer.place(relx=0.04,rely=0.05)

        discription = CTkLabel(
            master=self.element_window,
            text="Get more view, more clicks, more reach\n\n\t\t—— through complete video optimization.",
            font=("", 14),
            text_color="#a1a0a0",
            anchor="w",
            justify="left"
        )
        discription.place(relx=0.04, rely=0.12)

        video_input = CTkLabel(master=self.element_window,text="Input Method",font=("",18,"bold"))
        video_input.place(relx=0.04, rely=0.25)

        upload_videobtn = CTkButton(master=self.element_window,text="Upload Video",fg_color="#d4daff",hover_color="#afbae8",text_color="#427eff",height=40,width=120,corner_radius=10,command=self.th_video)
        upload_videobtn.place(relx=0.04,rely=0.35)

        upload_audiobtn = CTkButton(master=self.element_window,text="Upload Audio",fg_color="#d4daff",hover_color="#afbae8",text_color="#427eff",height=40,width=120,corner_radius=10,command=self.th_audio)
        upload_audiobtn.place(relx=0.18,rely=0.35)


        self.seo_info = CTkFrame(master=self.element_window,width=480,height=250,fg_color="white")
        self.seo_info.place(relx=0.03,rely=0.5)

        summary = CTkLabel(master=self.seo_info,text="SEO Optimization Summary",font=("",17,'bold'),fg_color="white")
        summary.place(relx=0.03,rely=0.03)

        _ = CTkLabel(master=self.seo_info,text='We Genarate SEO-optimized titels and discriptions tailored for your\nvideo content.While this help boost visisbility, ture performace\ndepends on multiple factors:',font=("",12),justify='left',fg_color="white",text_color="#a4b3c0")
        _.place(relx=0.03,rely=0.21)

        _ = CTkLabel(master=self.seo_info,text='Thumbnail quality: Your thumbnail should grab attention instantly.\nSharing & Engagement: The more your video is shared and commented on,\nthe better it performs.Watch time & retention: YouTube promotes videosn\nthat keep viewers engaged.',font=("",15,),justify='left',fg_color="white",text_color="#a4b3c0")
        _.place(relx=0.03,rely=0.43)

        _ = CTkLabel(master=self.seo_info,text="NOTE:SEO does't give instant result s.It may takes a few days to week for\nsearch performace to improve as YouTube indexs and ranks your content gradually.",font=("",13,),justify='left',fg_color="white",text_color="#a4b3c0")
        _.place(relx=0.03,rely=0.76)



    def scrollable_text(self, text):
        try:
            self.scroll_text_indication.destroy()
        except:
            pass

        self.scroll_text_indication = CTkTextbox(
            master=self.element_window,
            width=600, height=550,
            corner_radius=10
        )
        self.scroll_text_indication.place(relx=0.43, rely=0.83, anchor="sw")
        self.scroll_text_indication.insert("0.0", text)
        self.scroll_text_indication.configure(state="disabled")

    def indication(self):
        try:
            self.indication_progress_frame.destroy()
        except:
            pass

        self.indication_progress_frame = CTkFrame(
            master=self.element_window, corner_radius=25,
            height=270, width=180, fg_color="#f4f2f2"
        )
        self.indication_progress_frame.place(relx=0.04, rely=0.5)

        gif_path = os.path.join(os.getcwd(), 'assets', 'indicators', 'loading.gif')
        gif = Image.open(gif_path)
        self.loading_frames = [
            CTkImage(light_image=frame.copy(), dark_image=frame.copy(), size=(56, 56))
            for frame in ImageSequence.Iterator(gif)
        ]
        self.loading_index = 0
        self.loading_running = True

        self.indicator_img = CTkLabel(master=self.indication_progress_frame, text="")
        self.indicator_img.place(relx=0.02, rely=0.03)

        self.animate_gif()

        self.in_progress = CTkLabel(master=self.indication_progress_frame, text="In Progress",
                               text_color="#007bff", font=("", 17, 'bold'))
        self.in_progress.place(relx=0.05, rely=0.2)

        _ = CTkLabel(master=self.indication_progress_frame, text="Generating\nScript",
                     font=("", 25, 'bold'), justify="left")
        _.place(relx=0.03, rely=0.35)

        self.show_details = CTkLabel(
            master=self.indication_progress_frame,
            text="Your Caption is\nbeing generated.\nPlease wait a moment.",
            justify='left', font=("", 14), text_color="#a0a1a1"
        )
        self.show_details.place(relx=0.03, rely=0.69)

    def animate_gif(self):
        if self.loading_running and self.loading_frames:
            frame = self.loading_frames[self.loading_index]
            self.indicator_img.configure(image=frame)
            self.loading_index = (self.loading_index + 1) % len(self.loading_frames)
            self.window.after(100, self.animate_gif)

    def success(self):
        success = Image.open(os.path.join(os.getcwd(), 'assets', 'indicators', 'check.png'))
        success_ctkimg = CTkImage(light_image=success, dark_image=success, size=(26, 26))
        self.success_frame = CTkFrame(
            master=self.element_window, corner_radius=25,
            height=270, width=180, fg_color="#f4f2f2"
        )
        self.success_frame.place(relx=0.23, rely=0.5)

        indicator_img = CTkLabel(master=self.success_frame, image=success_ctkimg, text="")
        indicator_img.place(relx=0.1, rely=0.083)

        in_progress = CTkLabel(master=self.success_frame, text="Success",
                               text_color="#007bff", font=("", 17, 'bold'))
        in_progress.place(relx=0.05, rely=0.2)

        _ = CTkLabel(master=self.success_frame, text="Script Ready",
                     font=("", 25, 'bold'), justify="left")
        _.place(relx=0.03, rely=0.35)

        _ = CTkLabel(
            master=self.success_frame,
            text="Lights, camera, words!\nYour script is ready.",
            justify='left', font=("", 14), text_color="#a0a1a1"
        )
        _.place(relx=0.03, rely=0.67)

    def make_button(self, master, text, x, default=False):
        btn = CTkButton(
            master=master, text=text,
            fg_color="white", hover_color="white",
            text_color="#a1a0a0", cursor="hand2",
            width=100, height=30
        )
        btn.place(relx=x, rely=0.32)
        line = CTkFrame(master=master, fg_color="black", height=2, width=70)
        line.place_forget()

        def on_enter(e):
            if btn != self.selected_button:
                btn.configure(text_color="black")

        def on_leave(e):
            if btn != self.selected_button:
                btn.configure(text_color="#a1a0a0")

        def on_click():
            print(f"{text} clicked")

            if text.strip() =="Link":
                from window.scripts_writer_link import ScriptWriterLink

                app = ScriptWriterLink(window=self.element_window)
                app.gui()




            if self.selected_button is not None and self.selected_line is not None:
                self.selected_button.configure(text_color="#a1a0a0")
                self.selected_line.place_forget()
            btn.configure(text_color="black")
            line.place(relx=x + 0.015, rely=0.31, y=btn.winfo_height() + 5)
            self.selected_button = btn
            self.selected_line = line

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.configure(command=on_click)

        if default:
            btn.configure(text_color="black")

            def place_default_line():
                line.place(relx=x + 0.015, rely=0.31, y=btn.winfo_height() + 5)
                self.selected_button = btn
                self.selected_line = line

            self.window.after_idle(place_default_line)
        return btn



'''
window = CTk()
app = SeoGenerator(window=window)
app.gui()
window.mainloop()'''