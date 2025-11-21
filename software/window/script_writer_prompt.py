from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkImage, CTkOptionMenu, CTkTextbox,CTkFont
from tkinter import messagebox
from PIL import Image, ImageSequence
import os
from tkinter import filedialog
from threading import Thread
from LIBS.gemini_prompt import GeminiApiClient


appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata,'.Quilla')
login_path = os.path.join(quilla_folder,'login_data.csv')
signup_path = os.path.join(quilla_folder,'signup_data.csv')

class ScriptWriterPrompt:
    def __init__(self, window):
        self.window = window
        self.selected_button = None
        self.selected_line = None
        self.loading_frames = []
        self.loading_index = 0
        self.loading_running = False
        
        # Initialize custom input attributes
        self.custom_language = None
        self.custom_platform = None
    
    def GenerateBtn(self):
        prompt = self.text_area.get("0.0", "end-1c").strip()

        try:                            
            self.save_script_btn.destroy()
            self.success_frame.destroy()
            self.scroll_text_indication.destroy()
        except:
            pass    

        try:
            if prompt == "" or prompt is None or prompt == self.placeholder:
                messagebox.showwarning(
                    title="Zero Reference",
                    message="Please enter any video/audio contain reference"
                )
                self.generate_script_btn.configure(state="normal")
            else:
                if os.path.exists(login_path) or os.path.exists(signup_path):
                    # Get script parameters
                    language, platform = self.get_script_parameters()
                    duration = self.time_option.get().strip()

                    print(f"Language: {language}\nPlatform: {platform}\nDuration: {duration}\n")
                    print(f"Prompt: {prompt}")
                    
                    self.generate_script_btn.configure(state='disabled')

                    self.indication()
                    # Use the selected language instead of hardcoded "Hinglish"
                    result = GeminiApiClient(type_of_operation="Text-Prompt-To-Script").generate_video_script(
                        transcribed_text=prompt,
                        language=language
                    )
                    self.loading_running = False
                    self.success()

                    self.scrollable_text(text=result)
                    
                    self.save_script_btn = CTkButton(
                        master=self.element_window, text="Save Script", font=("", 14, "bold"),
                        height=38, corner_radius=10, fg_color="#007bff",
                        text_color="white", hover_color="#0157b3",
                        command=self.save_script
                    )
                    self.save_script_btn.place(relx=0.45, rely=0.9)
                else:
                    messagebox.showinfo(title="Signup",message="Please signup first to continue!")
        except Exception as e:
            print(f"Error in GenerateBtn: {e}")
            messagebox.showerror(title="Error", message=f"An error occurred: {str(e)}")
        finally:
            self.generate_script_btn.configure(state='normal')

    def th_GenerateBtn(self):
        th = Thread(target=self.GenerateBtn,daemon=True)
        th.start()
   
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
            text="Create a personalized script by describing your idea in simple clear\nwords like you're telling a friend.Add any details and any feelings\nyou want the script to capture.",
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
        self.make_button(self.element_window, "Video File", 0.1)
        self.make_button(self.element_window, "Audio File", 0.19)
        self.make_button(self.element_window, "Text Prompt", 0.28,default=True)

        paste_link = CTkLabel(master=self.element_window, text="Your prompt", font=("", 14, "bold"))
        paste_link.place(relx=0.03, rely=0.36)

        self.text_area = CTkTextbox(
            master=self.element_window,
            width=440,
            height=280,
            corner_radius=25,
            border_width=1
        )
        self.text_area.place(relx=0.03, rely=0.5)

        # --- Placeholder setup ---
        self.placeholder = "Got an idea? Hand it over — our AI loves turning thoughts into magic."
        self.text_area.insert("0.0", self.placeholder)
        self.text_area.configure(text_color="#a1a0a0")

        self.generate_script_btn = CTkButton(
            master=self.element_window, text="Generate Script", font=("", 14, "bold"),
            height=38, corner_radius=10, fg_color="#007bff",
            text_color="white", hover_color="#0157b3",
            command=self.th_GenerateBtn
        )
        self.generate_script_btn.place(relx=0.035, rely=0.91)

        # Platform dropdown
        platforms = ["Youtube", "Instagram","Web Series", "Micro-Drama","Custom"]
        self.platform = CTkOptionMenu(
            master=self.element_window, values=platforms, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7",
            command=self.on_platform_change
        )
        self.platform.place(relx=0.05, rely=0.42)

        # Language dropdown
        languages = ["English", "Hindi", "Hinglish","Bangla","Custom"]
        self.language_option = CTkOptionMenu(
            master=self.element_window, values=languages, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7",
            command=self.on_language_change
        )
        self.language_option.place(relx=0.17, rely=0.42)

        # Time dropdown
        time_options = ["30 seconds", "1 minute", "3 minute", "5 minute", "8 minute", "10 minute"]
        self.time_option = CTkOptionMenu(
            master=self.element_window, values=time_options, height=40, width=120,
            fg_color="#f9f9f7", text_color="black",
            button_color="#f9f9f7", dropdown_fg_color="#f9f9f7",
            button_hover_color="#f9f9f7"
        )
        self.time_option.place(relx=0.29, rely=0.42)

        self.text_area.bind("<FocusIn>", self.clear_placeholder)
        self.text_area.bind("<FocusOut>",self.add_placeholder)
    
    def on_language_change(self, choice):
        """Handle language dropdown change"""
        if choice == "Custom":
            self.open_custom_popup("Language", self.handle_custom_language)
    
    def on_platform_change(self, choice):
        """Handle platform dropdown change"""
        if choice == "Custom":
            self.open_custom_popup("Platform", self.handle_custom_platform)
    
    def open_custom_popup(self, input_type, callback):
        """Open the custom input popup"""
        from custom_pop_up import CustomInputPopup
        popup = CustomInputPopup(
            parent=self.window,
            input_type=input_type,
            callback=callback
        )
    
    def handle_custom_language(self, value):
        """Handle custom language input"""
        self.custom_language = value
        self.language_option.set(f"Custom: {value[:15]}...")
        print(f"Custom language set: {value}")
    
    def handle_custom_platform(self, value):
        """Handle custom platform input"""
        self.custom_platform = value
        self.platform.set(f"Custom: {value[:15]}...")
        print(f"Custom platform set: {value}")
    
    def get_script_parameters(self):
        """Get the actual values to use for script generation"""
        # Get language value
        language_choice = self.language_option.get()
        if language_choice.startswith("Custom:") and self.custom_language:
            language = self.custom_language
        else:
            language = language_choice
        
        # Get platform value
        platform_choice = self.platform.get()
        if platform_choice.startswith("Custom:") and self.custom_platform:
            platform = self.custom_platform
        else:
            platform = platform_choice
        
        return language, platform

    def clear_placeholder(self,event):
        if self.text_area.get("0.0", "end-1c") == self.placeholder:
            self.text_area.delete("0.0", "end")
            self.text_area.configure(text_color="black")

    def add_placeholder(self,event):
        if self.text_area.get("0.0", "end-1c").strip() == "":
            self.text_area.insert("0.0", self.placeholder)
            self.text_area.configure(text_color="#a1a0a0")

    def scrollable_text(self, text):
        try:
            self.scroll_text_indication.destroy()
        except:
            pass

        self.scroll_text_indication = CTkTextbox(
            master=self.element_window,
            corner_radius=20,font=CTkFont(size=16)
        )
        self.scroll_text_indication.place(relx=0.45, rely=0.87, anchor="sw",relheight=0.45,relwidth=0.52)
        self.scroll_text_indication.insert("0.0", text)
        self.scroll_text_indication.configure(state="disabled")

    def indication(self):
        try:
            self.indication_progress_frame.destroy()
        except:
            pass

        self.indication_progress_frame = CTkFrame(
            master=self.element_window, corner_radius=25,
            height=250, width=180, fg_color="#f4f2f2"
        )
        self.indication_progress_frame.place(relx=0.45, rely=0.05)

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
            height=250, width=180, fg_color="#f4f2f2"
        )
        self.success_frame.place(relx=0.63, rely=0.05)

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

            elif text.strip() =="Video File":
                from window.scripts_writer_video import ScriptWriterVideo
                app = ScriptWriterVideo(window=self.element_window)
                app.gui()

            elif text.strip() == "Audio File":    
                from window.script_writer_audio import ScriptWriterAudio
                app = ScriptWriterAudio(window=self.element_window)
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