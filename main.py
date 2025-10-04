import customtkinter as ctk
import os, sys, json, datetime

try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")
theme_path = os.path.join(base_path, "orange_theme.json")
ctk.set_default_color_theme(theme_path)

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note app!")
        self.root.geometry("650x750")

        search_entry = ctk.CTkEntry(self.root, width=300, placeholder_text="Поиск по заметкам...")
        search_entry.pack(pady=10, padx=20)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_notes(search_entry.get()))

        self.notes_frame = ctk.CTkScrollableFrame(self.root, width=450)
        self.notes_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.notes_frame.bind("<Button-1>", lambda e: self.root.focus())

        self.note_widgets = []
        self.note_labels = []

        my_folder = os.path.join(os.path.expanduser("~"), "MyNotes")
        notes_path = os.path.join(my_folder, "notes.json")
        self.notes = []
        if os.path.exists(notes_path):
            try:
                with open(notes_path, "r", encoding="utf-8") as f:
                    loaded_notes = json.load(f)
                for note_data in loaded_notes:
                    self.notes.append(note_data)
                    self.create_note_widget(note_data)
            except:
                print("Ошибка загузки")

        new_note_btn = ctk.CTkButton(
            self.root, text="+", command=self.new_note_write, width=50, height=50, font=("Arial", 40)
        )
        new_note_btn.place(relx=0.9, rely=0.92, anchor="center")

    def new_note_write(self):
        current_date = datetime.datetime.now().strftime("%m-%d-%Y")
        note_data = {"header": "Новая заметка",
                     "text": "",
                     "created": current_date,
                     "last_edited": current_date}
        self.create_note_widget(note_data)
        self.open_note_window(note_data)
        self.notes.append(note_data)

    def create_note_widget(self, note_data):
        note_widget = ctk.CTkFrame(self.notes_frame)
        note_widget.pack(pady=(10, 5), padx=25, fill="x")
        note_widget.grid_columnconfigure(0, weight=1, minsize=150)
        note_widget.grid_columnconfigure(1, weight=2)
        note_widget.grid_columnconfigure(2, weight=1, minsize=150)

        dates_widget = ctk.CTkFrame(note_widget, border_width=0)
        dates_widget.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        created = ctk.CTkLabel(dates_widget, text=f"📅 {note_data["created"]}", font=("Arial", 12), text_color="#CD853F")
        created.pack(pady=1)
        edited = ctk.CTkLabel(dates_widget, text=f"✏ {note_data["last_edited"]}", font=("Arial", 12), text_color="#CD853F")
        edited.pack(pady=1)

        note = ctk.CTkLabel(note_widget, text=note_data["header"], font=("Arial", 16))
        note.grid(row=0, column=1, padx=10, pady=5)
        note_data["label"] = note
        note_data["edited_label"] = edited

        delete_btn = ctk.CTkButton(note_widget, text="🗑",
                                 command=lambda: self.delete_note(note_data, note_widget),
                                 width=40, height=40, font=("Arial", 24))
        delete_btn.grid(row=0, column=2, sticky="e", padx=15, pady=5)

        for clickable in note, note_widget:
            clickable.bind("<Button-1>", lambda e: self.open_note_window(note_data))
            clickable.bind("<Enter>", lambda e: note.configure(cursor="hand2"))
            clickable.bind("<Leave>", lambda e: note.configure(cursor=""))

    def open_note_window(self, note_data):
        note_window = ctk.CTkToplevel(self.root)
        note_window.title(note_data["header"])
        note_window.geometry("450x510")
        note_window.attributes("-topmost", True)

        header_note = ctk.CTkEntry(note_window, width=400, height=40, font=("Arial", 32))
        header_note.insert(0, note_data["header"])
        header_note.pack(pady=20)

        text_note = ctk.CTkTextbox(note_window, width=400, height=350, font=("Arial", 16))
        text_note.insert(0.0, note_data["text"])
        text_note.pack()

        save_btn = ctk.CTkButton(note_window,text="Сохранить",
            command=lambda: self.save_note(note_data, header_note.get(), text_note.get("0.0", "end-1c")),
            width=120, height=40, font=("Arial", 24)
        )
        save_btn.pack(pady=20)

    def save_note(self, note_data, header, text):
        if not header.strip():
            header = "Безымянная заметка"

        note_data["header"] = header
        note_data["text"] = text
        note_data["label"].configure(text=header)
        note_data["edited_label"].configure(text=datetime.datetime.now().strftime("%m-%d-%Y"))

    def delete_note(self, note_data, note_widget):
        note_widget.destroy()
        clean_notes = [note for note in self.notes if note["header"] != note_data["header"]]
        self.notes = clean_notes

    def filter_notes(self, search):
        search = search.lower()
        headers_match = []

        for note_data in self.notes:
            header = note_data["header"].lower()
            match = 0

            if search in header:
                match = len(search)
            else:
                for i in range(len(search)):
                    for j in range(i + 1, len(search) + 1):
                        if search[i:j] in header:
                            match = max(match, j - i)

            headers_match.append((match, note_data))

        headers_match.sort(key=lambda x: x[0], reverse=True)

        row = 0

        for _, note_data in headers_match:
            note_data["label"].master.pack_forget()

        for _, note_data in headers_match:
            note_data["label"].master.pack(pady=10, padx=25, fill="x")

    def save_notes_local(self):
        my_folder = os.path.join(os.path.expanduser("~"), "MyNotes")
        if not os.path.exists(my_folder):
            os.makedirs(my_folder)
        file_path = os.path.join(my_folder, "notes.json")

        notes_to_save = []
        for note in self.notes:
            note_data = {
                "header": note["header"],
                "text": note["text"],
                "created": note["created"],
                "last_edited": note["last_edited"]
            }
            notes_to_save.append(note_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notes_to_save, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = ctk.CTk()
    app = NoteApp(root)

    try:
        root.mainloop()
    finally:
        app.save_notes_local()
