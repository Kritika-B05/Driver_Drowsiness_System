import tkinter as tk
import threading
import subprocess
import os
import sys
import psutil

class DrowsinessUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚘 Drowsiness Detection System")
        self.root.geometry("520x450")  
        self.root.configure(bg="#dfe9f3")

        self.process = None 

       
        icon_path = "car_icon.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

       
        main_frame = tk.Frame(root, bg="#dfe9f3")
        main_frame.pack(expand=True, fill="both", pady=10)

        header = tk.Canvas(main_frame, width=500, height=70, highlightthickness=0)
        header.pack(fill="x", pady=(0, 20))
        header.create_rectangle(0, 0, 520, 70, fill="#0d47a1", outline="")
        header.create_text(260, 35, text="🚘 Driver Drowsiness Detection",
                           fill="white", font=("Segoe UI Semibold", 16, "bold"))

        self.status_frame = tk.Frame(main_frame, bg="#dfe9f3")
        self.status_frame.pack(pady=20)

        self.status_icon = tk.Label(self.status_frame, text="🔴", font=("Arial", 22), bg="#dfe9f3")
        self.status_icon.pack()

        self.status_label = tk.Label(self.status_frame, text="Status: Not Started",
                                     font=("Segoe UI", 13, "bold"), bg="#dfe9f3", fg="#333")
        self.status_label.pack(pady=10)

   
        self.button_frame = tk.Frame(main_frame, bg="#dfe9f3")
        self.button_frame.pack(pady=10)

        self.start_btn = tk.Button(self.button_frame, text="▶ Start Monitoring",
                                   font=("Segoe UI", 12, "bold"), fg="white",
                                   bg="#1b5e20", activebackground="#2e7d32",
                                   relief="flat", padx=20, pady=10,
                                   command=self.start_detection)
        self.start_btn.grid(row=0, column=0, padx=10, ipadx=5)

        self.stop_btn = tk.Button(self.button_frame, text="⏹ Stop Monitoring",
                                  font=("Segoe UI", 12, "bold"), fg="white",
                                  bg="#b71c1c", activebackground="#d32f2f",
                                  relief="flat", padx=20, pady=10,
                                  command=self.stop_detection, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=10, ipadx=5)

  
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#2e7d32"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#1b5e20"))
        self.stop_btn.bind("<Enter>", lambda e: self.stop_btn.config(bg="#d32f2f"))
        self.stop_btn.bind("<Leave>", lambda e: self.stop_btn.config(bg="#b71c1c"))

        self.info_label = tk.Label(main_frame,
                                   text="Keep your eyes open and drive safe.\nAI monitoring is active during detection.",
                                   font=("Segoe UI", 10, "italic"),
                                   bg="#dfe9f3", fg="#444")
        self.info_label.pack(pady=(15, 20))

        footer = tk.Label(root, text="Developed by Kritika 🚀",
                          font=("Segoe UI", 9, "italic"),
                          bg="#dfe9f3", fg="#555")
        footer.pack(side="bottom", pady=8)

    def start_detection(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running...", fg="#2e7d32")
        self.status_icon.config(text="🟢")

        self.thread = threading.Thread(target=self.run_detection)
        self.thread.start()

    def run_detection(self):
        self.process = subprocess.Popen([sys.executable, "driver_drowsiness.py"])
        self.process.wait()
        self.update_after_stop()

    def stop_detection(self):
        self.status_label.config(text="Status: Stopping...", fg="#ff6f00")
        self.status_icon.config(text="🟠")

        if self.process and self.process.poll() is None:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except Exception as e:
                print("Error stopping process:", e)

        self.update_after_stop()

    def update_after_stop(self):
        self.status_label.config(text="Status: Stopped", fg="#b71c1c")
        self.status_icon.config(text="🔴")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrowsinessUI(root)
    root.mainloop()
