from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkImage, CTkOptionMenu, CTkTextbox
from tkinter import messagebox
from PIL import Image, ImageSequence
import time
import os
from tkinter import filedialog


from LIBS.audio_download import download_youtube_audio
from LIBS.transcriber import Transcriber
from LIBS.gemini_prompt import generate_video_script

appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata,'.Quilla')
login_path = os.path.join(quilla_folder,'login_data.csv')
signup_path = os.path.join(quilla_folder,'signup_data.csv')



class ScriptWriterVideo:
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
                print("Selected file:", self.file_path) 
                self.file_select_indication.configure(text="File Selected") 
                return self.file_path 

    def save_script(self):
        if hasattr(self, 'scroll_text_indication'):
            # Get the text from the CTkTextbox
            text = self.scroll_text_indication.get("0.0", "end-1c")
            if text.strip() == "":
                messagebox.showwarning(title="Empty Script", message="There is no script to save!")
                return

            # Ask user where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                title="Save Script As"
            )
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    messagebox.showinfo(title="Saved", message=f"Script saved successfully at:\n{file_path}")
                except Exception as e:
                    messagebox.showerror(title="Error", message=f"Failed to save file:\n{e}")
        else:
            messagebox.showwarning(title="No Script", message="Generate a script first before saving.")


    def GenerateScript(self):
        link = self.file_path
        self.generate_script_btn.configure(state="disabled")

        try: 
            self.save_script_btn.destroy()
        except:
            pass 


        try: 
            if link == "" or link is None:
                messagebox.showwarning(
                    title="Zero Reference",
                    message="Please enter any video/audio contain reference"
                )
                self.generate_script_btn.configure(state="normal")

            else:

                if os.path.exists(login_path) or os.path.exists(signup_path):
                    language = self.language_option.get().strip()
                    tone = self.tone_option.get().strip()
                    duration = self.time_option.get().strip()

                    start_time = time.time()
                    print(f"Start time: {start_time} ")
                    print(f"Link: {link}\nLanguage: {language}\nTone: {tone}\nDuration: {duration}\n")

                    self.indication()
                    self.show_details.configure(text="Please wait while\nyour assistant\nis fetching details")

                    self.show_details.configure(text="Your Script is\nbeing generated.\nPlease wait a moment.")
                    transcriber = Transcriber(
                        video_file_path=self.file_path,
                        show_details=self.show_details
                    )
                    result = transcriber.video_to_text()
                    result = generate_video_script(transcribed_text=result,language=language,duration=duration,tone=tone)

                    print(f"Result: {result}")

                    end_time = time.time()
                    print(f" Total Consume time: {(end_time - start_time)} sec ")

                    self.scrollable_text(result)

                    self.show_details.configure(
                        text="Your words are woven\ninto form — time to save\nthis creation."
                    )

                    # Stop the loading animation
                    self.loading_running = False
                    self.in_progress.configure(text="Done")
                    # Show success frame with check.png
                    self.success()
                    self.generate_script_btn.configure(state="normal")

                    self.save_script_btn = CTkButton(
                        master=self.element_window, text="Save Script", font=("", 14, "bold"),
                        height=38, corner_radius=10, fg_color="#007bff",
                        text_color="white", hover_color="#0157b3",
                        command=self.save_script
                    )
                    self.save_script_btn.place(relx=0.45, rely=0.85)
                else: 
                    messagebox.showinfo(title="Signup",message="Please signup first to continue!")
        except:
            pass
        finally:
            self.generate_script_btn.configure(state="normal")
    
    def th_generateScript(self):

        from threading import Thread
        th = Thread(target=self.GenerateScript,daemon=True)
        th.start()

    def gui(self):

        for widget in self.window.winfo_children():
            widget.destroy()

        self.element_window = CTkFrame(master=self.window, fg_color="white")
        self.element_window.grid(column=1, row=0, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        generate_video_script = CTkLabel(
            master=self.element_window,
            text="Generate Video Script",
            font=("", 27, 'bold')
        )
        generate_video_script.place(relx=0.04, rely=0.05)

        discription = CTkLabel(
            master=self.element_window,
            text="Generate script from your video file.\nSet tone, language & duration —— Al takes care of the rest.",
            font=("", 14),
            text_color="#a1a0a0",
            anchor="w",
            justify="left"
        )
        discription.place(relx=0.04, rely=0.12)

        input_method = CTkLabel(
            master=self.element_window,
            text="Input Method",
            font=("", 18, "bold")
        )
        input_method.place(relx=0.04, rely=0.25)

        # Input buttons
        self.make_button(self.element_window, "Link", 0.01)
        self.make_button(self.element_window, "Video File", 0.1,default=True)
        self.make_button(self.element_window, "Audio File", 0.19)
        self.make_button(self.element_window, "Text Prompt", 0.28)

        paste_link = CTkLabel(master=self.element_window, text="Upload Video file", font=("", 14, "bold"))
        paste_link.place(relx=0.03, rely=0.43)
        self.file_select_indication = CTkLabel(master=self.element_window,text="Select Video file",width=140,height=40,corner_radius=15,
                                               fg_color="#f4f2f2")
        self.file_select_indication.place(relx=0.03,rely=0.43)

        file = CTkButton(master=self.element_window,text="File",height=40,corner_radius=15,font=("",15,"bold"),width=100,text_color="white",command=self.select_video_file)
        file.place(relx=0.18,rely=0.43)

        script_setting = CTkLabel(master=self.element_window, text="Script Setting", font=("", 14, "bold"))
        script_setting.place(relx=0.03, rely=0.58)

        language = CTkLabel(master=self.element_window, text="Language", font=("", 13, "bold"))
        language.place(relx=0.03, rely=0.63)

        tone = CTkLabel(master=self.element_window, text="Tone", font=("", 13, "bold"))
        tone.place(relx=0.15, rely=0.63)

        Duration = CTkLabel(master=self.element_window, text="Duration(min)", font=("", 13, "bold"))
        Duration.place(relx=0.27, rely=0.63)

        languages = ["English", "Hindi", "Hinglish", "Custom"]
        self.language_option = CTkOptionMenu(
            master=self.element_window, values=languages, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7"
        )
        self.language_option.place(relx=0.03, rely=0.69)

        tones = ["Professional", "Casual", "Comedy", "Informative", "Custom"]
        self.tone_option = CTkOptionMenu(
            master=self.element_window, values=tones, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7"
        )
        self.tone_option.place(relx=0.15, rely=0.69)

        ltime = ["30s", "1 min", "3 min", "5 min", "8 min", "10 min"]
        self.time_option = CTkOptionMenu(
            master=self.element_window, values=ltime, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7"
        )
        self.time_option.place(relx=0.27, rely=0.69)

        self.generate_script_btn = CTkButton(
            master=self.element_window, text="Generate Script", font=("", 14, "bold"),
            height=38, corner_radius=10, fg_color="#007bff",
            text_color="white", hover_color="#0157b3",
            command=self.th_generateScript
        )
        self.generate_script_btn.place(relx=0.03, rely=0.8)

        

    def scrollable_text(self, text):
        try:
            self.scroll_text_indication.destroy()
        except:
            pass

        self.scroll_text_indication = CTkTextbox(
            master=self.element_window,
            width=600, height=250,
            corner_radius=10
        )
        self.scroll_text_indication.place(relx=0.45, rely=0.83, anchor="sw")
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
        self.indication_progress_frame.place(relx=0.45, rely=0.1)

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
            text="Your Script is\nbeing generated.\nPlease wait a moment.",
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
        self.success_frame.place(relx=0.63, rely=0.1)

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

            elif text.strip() =="Audio File":

                from window.script_writer_audio import ScriptWriterAudio

                app = ScriptWriterAudio(window=self.element_window)
                app.gui()
            
            elif text.strip() == "Text Prompt":

                from window.script_writer_prompt import ScriptWriterPrompt

                app = ScriptWriterPrompt(window=self.element_window)
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


'''# Run window
window = CTk()
app = ScriptWriterLink(window=window)
app.gui()
window.mainloop()'''
