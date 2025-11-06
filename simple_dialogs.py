# simpletk.py
import tkinter as tk
from tkinter import ttk

def user_query(message, *buttons, title=None):
    """
    Shows a modal dialog with the given message and buttons.
    Returns:
        - index of the button pressed
        - None if the user presses Escape or closes the window
    """
    root = tk.Tk()
    root.withdraw()  # Hide root

    win = tk.Toplevel(root)
    win.title(title or "Query")
    win.resizable(False, False)
    win.grab_set()  # Make modal

    result = None

    def on_press(i):
        nonlocal result
        result = i
        win.destroy()

    def on_escape(event=None):
        nonlocal result
        result = None
        win.destroy()

    win.bind("<Escape>", on_escape)

    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    msg = ttk.Label(frm, text=message, anchor="center", justify="center")
    msg.pack(pady=10)

    btn_frame = ttk.Frame(frm)
    btn_frame.pack(pady=5)

    for i, label in enumerate(buttons):
        ttk.Button(btn_frame, text=label, command=lambda i=i: on_press(i)).pack(
            side="left", padx=5
        )

    # Center window
    win.update_idletasks()
    w, h = win.winfo_width(), win.winfo_height()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"+{x}+{y}")

    win.wait_window()
    root.destroy()
    return result


def text_box(text, title=None, on_key=None):
    """
    Shows a scrollable text box containing the given text.
    If on_key(window, combo) is provided, it will be called on keypress.
    Escape closes the window.
    """
    root = tk.Tk()
    root.title(title or "Text")
    root.geometry("600x400")

    txt = tk.Text(root, wrap="word")
    txt.insert("1.0", text)
    txt.config(state="disabled")
    txt.pack(fill="both", expand=True, padx=5, pady=5)

    sb = ttk.Scrollbar(root, command=txt.yview)
    txt.config(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")

    def on_escape(event=None):
        root.destroy()

    def on_keypress(event):
        if event.keysym == "Escape":
            on_escape()
            return
        if on_key:
            combo = []
            if event.state & 0x0001: combo.append("S")
            if event.state & 0x0004: combo.append("C")
            if event.state & 0x0008: combo.append("A")
            if event.state & 0x0080: combo.append("M")
            combo.append(event.keysym)
            on_key(root, "-".join(combo))

    root.bind("<Key>", on_keypress)
    root.mainloop()

