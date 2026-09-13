import tkinter as tk
from tkinter import ttk, messagebox
import threading

from translator import KannadaTranslator


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English → Kannada Translator")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)

        self.translator = None
        self.translating = False

        self.setup_style()
        self.build_ui()

        self.root.after(300, self.load_model)

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("vista")
        except Exception:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Status.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Translate.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=10
        )

    def build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        title = ttk.Label(
            main,
            text="English → Kannada Translator",
            style="Title.TLabel"
        )
        title.pack(pady=(0, 5))

        subtitle = ttk.Label(
            main,
            text="Offline AI translation • No internet required after installation"
        )
        subtitle.pack(pady=(0, 15))

        # English section
        english_header = ttk.Frame(main)
        english_header.pack(fill="x")

        ttk.Label(
            english_header,
            text="English",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        self.input_count = ttk.Label(
            english_header,
            text="0 characters"
        )
        self.input_count.pack(side="right")

        self.input_text = tk.Text(
            main,
            height=10,
            wrap="word",
            font=("Segoe UI", 13),
            undo=True
        )
        self.input_text.pack(fill="both", expand=True, pady=(5, 12))

        self.input_text.bind(
            "<KeyRelease>",
            self.update_input_count
        )

        # Buttons
        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=5)

        self.translate_button = ttk.Button(
            button_frame,
            text="Translate to Kannada",
            style="Translate.TButton",
            command=self.translate
        )
        self.translate_button.pack(side="left")

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear
        ).pack(side="left", padx=8)

        ttk.Button(
            button_frame,
            text="Copy Kannada",
            command=self.copy_output
        ).pack(side="left")

        # Kannada section
        kannada_header = ttk.Frame(main)
        kannada_header.pack(fill="x", pady=(15, 0))

        ttk.Label(
            kannada_header,
            text="Kannada",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        self.output_count = ttk.Label(
            kannada_header,
            text="0 characters"
        )
        self.output_count.pack(side="right")

        self.output_text = tk.Text(
            main,
            height=10,
            wrap="word",
            font=("Noto Sans Kannada", 14)
        )
        self.output_text.pack(fill="both", expand=True, pady=(5, 10))

        self.status = ttk.Label(
            main,
            text="Loading translation model...",
            style="Status.TLabel"
        )
        self.status.pack(fill="x")

        self.progress = ttk.Progressbar(
            main,
            mode="indeterminate"
        )
        self.progress.pack(fill="x", pady=(5, 0))

    def load_model(self):
        def worker():
            try:
                self.set_status("Loading offline AI model...")
                self.progress.start(10)

                self.translator = KannadaTranslator()

                self.progress.stop()
                self.set_status(
                    "Ready — translation works completely offline."
                )

                self.root.after(
                    0,
                    lambda: self.translate_button.config(
                        state="normal"
                    )
                )

            except Exception as e:
                self.progress.stop()

                error = str(e)

                self.set_status("Model loading failed.")

                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Model Error",
                        "Could not load the Kannada translation model.\n\n"
                        + error
                    )
                )

        self.translate_button.config(state="disabled")

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def update_input_count(self, event=None):
        text = self.input_text.get("1.0", "end-1c")
        self.input_count.config(
            text=f"{len(text)} characters"
        )

    def update_output_count(self):
        text = self.output_text.get("1.0", "end-1c")
        self.output_count.config(
            text=f"{len(text)} characters"
        )

    def set_status(self, text):
        self.root.after(
            0,
            lambda: self.status.config(text=text)
        )

    def translate(self):
        if self.translating:
            return

        if self.translator is None:
            messagebox.showwarning(
                "Please wait",
                "The translation model is still loading."
            )
            return

        text = self.input_text.get("1.0", "end-1c").strip()

        if not text:
            messagebox.showwarning(
                "No text",
                "Enter some English text first."
            )
            return

        self.translating = True

        self.translate_button.config(
            state="disabled"
        )

        self.progress.start(10)

        self.set_status(
            "Translating..."
        )

        threading.Thread(
            target=self.translate_worker,
            args=(text,),
            daemon=True
        ).start()

    def translate_worker(self, text):
        try:
            result = self.translator.translate(text)

            self.root.after(
                0,
                lambda: self.show_translation(result)
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Translation Error",
                    str(e)
                )
            )

            self.root.after(
                0,
                lambda: self.finish_translation(
                    "Translation failed."
                )
            )

    def show_translation(self, result):
        self.output_text.delete(
            "1.0",
            "end"
        )

        self.output_text.insert(
            "1.0",
            result
        )

        self.update_output_count()

        self.finish_translation(
            "Translation complete — offline."
        )

    def finish_translation(self, status):
        self.translating = False

        self.progress.stop()

        self.translate_button.config(
            state="normal"
        )

        self.set_status(status)

    def clear(self):
        self.input_text.delete(
            "1.0",
            "end"
        )

        self.output_text.delete(
            "1.0",
            "end"
        )

        self.update_input_count()
        self.update_output_count()

        self.set_status("Ready.")

    def copy_output(self):
        text = self.output_text.get(
            "1.0",
            "end-1c"
        )

        if not text.strip():
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

        self.set_status(
            "Kannada translation copied to clipboard."
        )


def main():
    root = tk.Tk()

    app = TranslatorApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
