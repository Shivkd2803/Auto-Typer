import customtkinter as ctk
from PIL import Image
import pyautogui
import threading
import time
import keyboard
import sys
import os

# ── Windows-only sound, graceful fallback ──────────────────────────────────
def beep(freq=1000, dur=120):
    try:
        if sys.platform == "win32":
            import winsound
            winsound.Beep(freq, dur)
    except Exception:
        pass

# ── pyautogui safety ───────────────────────────────────────────────────────
pyautogui.FAILSAFE = True
pyautogui.PAUSE   = 0.0

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════════════════════════════════════
#  TOOLTIP HELPER
# ══════════════════════════════════════════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tip    = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = ctk.CTkToplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        ctk.CTkLabel(self.tip, text=self.text,
                     fg_color="#1e1e2e", corner_radius=6,
                     font=ctk.CTkFont(size=11), padx=8, pady=4).pack()

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ══════════════════════════════════════════════════════════════════════════════
#  SHORTCUT ROW WIDGET
# ══════════════════════════════════════════════════════════════════════════════
class ShortcutRow(ctk.CTkFrame):
    def __init__(self, master, item, on_delete, on_test, **kwargs):
        super().__init__(master, corner_radius=12,
                         fg_color=("#1e1e2e", "#16162a"),
                         border_width=1, border_color="#2a2a4a", **kwargs)
        self.item      = item
        self.on_delete = on_delete

        # keyword badge
        badge = ctk.CTkLabel(self,
                             text=f" {item['key']} ",
                             font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
                             fg_color="#5865f2", corner_radius=6,
                             text_color="white")
        badge.pack(side="left", padx=(10, 6), pady=8)

        # preview text
        preview = item["msg"][:45] + ("…" if len(item["msg"]) > 45 else "")
        ctk.CTkLabel(self,
                     text=preview,
                     font=ctk.CTkFont(size=12),
                     text_color="#a0a0c0",
                     anchor="w").pack(side="left", padx=4, fill="x", expand=True)

        # speed chip
        ctk.CTkLabel(self,
                     text=f"⚡ {item['type_speed']}s",
                     font=ctk.CTkFont(size=11),
                     text_color="#5865f2",
                     fg_color="#1a1a3a", corner_radius=8).pack(side="left", padx=4)

        # repeat chip
        rep = item.get("repeat", 1)
        ctk.CTkLabel(self,
                     text=f"🔁 ×{rep}",
                     font=ctk.CTkFont(size=11),
                     text_color="#43b581",
                     fg_color="#1a2a1a", corner_radius=8).pack(side="left", padx=4)

        # test button
        test_btn = ctk.CTkButton(self, text="▶ Test", width=68,
                                 height=28, corner_radius=8,
                                 fg_color="#2f855a", hover_color="#276749",
                                 font=ctk.CTkFont(size=11),
                                 command=lambda: on_test(item))
        test_btn.pack(side="left", padx=4)
        Tooltip(test_btn, "Type this message now (3 s delay)")

        # delete button
        del_btn = ctk.CTkButton(self, text="✕", width=34,
                                height=28, corner_radius=8,
                                fg_color="#c0392b", hover_color="#a93226",
                                font=ctk.CTkFont(size=12, weight="bold"),
                                command=lambda: on_delete(item))
        del_btn.pack(side="left", padx=(4, 10))
        Tooltip(del_btn, "Remove this shortcut")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class AutoTyperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Typer Pro 3.0")
        self.geometry("820x750")
        self.minsize(700, 600)
        self.resizable(True, True)

        # State
        self.running      = False
        self.stop_typing  = False
        self.entries: list[dict] = []
        self.typed_chars  = ""
        self._lock        = threading.Lock()

        # ── HEADER ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(22, 0))

        ctk.CTkLabel(header,
                     text="AUTO TYPER PRO",
                     font=ctk.CTkFont(family="Courier New", size=32, weight="bold"),
                     text_color="#5865f2").pack(side="left")

        ctk.CTkLabel(header,
                     text="v3.0",
                     font=ctk.CTkFont(size=11),
                     text_color="#555577").pack(side="left", padx=(8, 0), pady=(12, 0))

        # theme toggle
        self._mode = ctk.StringVar(value="Dark")
        theme_btn = ctk.CTkButton(header, text="☀ Light",
                                  width=80, height=28, corner_radius=8,
                                  fg_color="#2a2a4a", hover_color="#3a3a6a",
                                  command=self._toggle_theme)
        theme_btn.pack(side="right")
        self._theme_btn = theme_btn

        ctk.CTkLabel(self,
                     text="Type a keyword anywhere → message auto-types  |  ESC cancels",
                     font=ctk.CTkFont(size=11),
                     text_color="#555577").pack(pady=(2, 0))

        # ── STATUS BAR ────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self,
                                          text="● READY",
                                          font=ctk.CTkFont(family="Courier New",
                                                           size=12, weight="bold"),
                                          text_color="#43b581")
        self.status_label.pack(pady=(6, 0))

        # ── INPUT CARD ────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, corner_radius=16,
                            fg_color=("#1a1a2e", "#12121f"),
                            border_width=1, border_color="#2a2a4a")
        card.pack(padx=28, pady=12, fill="x")

        ctk.CTkLabel(card, text="MESSAGE",
                     font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
                     text_color="#5865f2").pack(anchor="w", padx=16, pady=(14, 2))

        self.msg_box = ctk.CTkTextbox(card, height=110, corner_radius=10,
                                       border_width=1, border_color="#2a2a4a",
                                       font=ctk.CTkFont(size=13))
        self.msg_box.pack(padx=16, pady=(0, 10), fill="x")

        # ── CONTROLS ROW ──────────────────────────────────────────────────
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 14))

        # keyword
        kf = ctk.CTkFrame(row, fg_color="transparent")
        kf.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(kf, text="KEYWORD",
                     font=ctk.CTkFont(family="Courier New", size=9, weight="bold"),
                     text_color="#555577").pack(anchor="w")
        self.key_entry = ctk.CTkEntry(kf, placeholder_text="e.g.  ;;hello",
                                       corner_radius=8,
                                       font=ctk.CTkFont(family="Courier New", size=13))
        self.key_entry.pack(fill="x")

        # speed
        sf = ctk.CTkFrame(row, fg_color="transparent")
        sf.pack(side="left", padx=6)
        ctk.CTkLabel(sf, text="DELAY (s)",
                     font=ctk.CTkFont(family="Courier New", size=9, weight="bold"),
                     text_color="#555577").pack(anchor="w")
        self.speed_entry = ctk.CTkEntry(sf, width=80, corner_radius=8,
                                         font=ctk.CTkFont(family="Courier New", size=13))
        self.speed_entry.insert(0, "0.03")
        self.speed_entry.pack()
        Tooltip(self.speed_entry, "Seconds between each keystroke (0 = instant)")

        # repeat
        rf = ctk.CTkFrame(row, fg_color="transparent")
        rf.pack(side="left", padx=6)
        ctk.CTkLabel(rf, text="REPEAT",
                     font=ctk.CTkFont(family="Courier New", size=9, weight="bold"),
                     text_color="#555577").pack(anchor="w")
        self.repeat_entry = ctk.CTkEntry(rf, width=60, corner_radius=8,
                                          font=ctk.CTkFont(family="Courier New", size=13))
        self.repeat_entry.insert(0, "1")
        self.repeat_entry.pack()
        Tooltip(self.repeat_entry, "How many times to repeat the message")

        # add button
        self.add_button = ctk.CTkButton(row, text="＋  Add",
                                         width=110, height=38, corner_radius=10,
                                         fg_color="#5865f2", hover_color="#4752c4",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         command=self.add_entry)
        self.add_button.pack(side="left", padx=(10, 0), pady=(14, 0))

        # ── SHORTCUTS LIST ────────────────────────────────────────────────
        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.pack(fill="x", padx=28, pady=(4, 0))
        ctk.CTkLabel(list_header,
                     text="ACTIVE SHORTCUTS",
                     font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
                     text_color="#5865f2").pack(side="left")
        self.count_label = ctk.CTkLabel(list_header, text="0 shortcuts",
                                         font=ctk.CTkFont(size=11),
                                         text_color="#555577")
        self.count_label.pack(side="left", padx=8)

        self.scroll_frame = ctk.CTkScrollableFrame(self,
                                                    corner_radius=14,
                                                    fg_color=("#12121f", "#0d0d1a"),
                                                    border_width=1,
                                                    border_color="#2a2a4a")
        self.scroll_frame.pack(padx=28, pady=6, fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(self.scroll_frame,
                                         text="No shortcuts yet.\nAdd one above ↑",
                                         font=ctk.CTkFont(size=13),
                                         text_color="#333355")
        self.empty_label.pack(pady=40)

        # ── BOTTOM BAR ────────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=28, pady=(6, 18))

        self.reset_btn = ctk.CTkButton(bottom,
                                        text="🗑  Clear All",
                                        width=120, height=36, corner_radius=10,
                                        fg_color="#2a0a0a", hover_color="#4a1a1a",
                                        border_width=1, border_color="#c0392b",
                                        text_color="#c0392b",
                                        font=ctk.CTkFont(size=13),
                                        command=self.reset_all)
        self.reset_btn.pack(side="left")
        Tooltip(self.reset_btn, "Remove all shortcuts")

        ctk.CTkLabel(bottom,
                     text="ESC  →  cancel current typing",
                     font=ctk.CTkFont(family="Courier New", size=10),
                     text_color="#333355").pack(side="right")

        # ── START BACKGROUND THREADS ──────────────────────────────────────
        threading.Thread(target=self.monitor_keywords,  daemon=True).start()
        threading.Thread(target=self.monitor_stop_key,  daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    #  THEME TOGGLE
    # ─────────────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self._theme_btn.configure(text="🌙 Dark")
        else:
            ctk.set_appearance_mode("Dark")
            self._theme_btn.configure(text="☀ Light")

    # ─────────────────────────────────────────────────────────────────────────
    #  ADD SHORTCUT
    # ─────────────────────────────────────────────────────────────────────────
    def add_entry(self):
        message = self.msg_box.get("1.0", "end-1c").strip()
        keyword = self.key_entry.get().strip()

        if not message:
            self._flash_error("Message cannot be empty")
            return
        if not keyword:
            self._flash_error("Keyword cannot be empty")
            return
        # Check duplicate keyword
        if any(e["key"] == keyword for e in self.entries):
            self._flash_error(f"Keyword '{keyword}' already exists")
            return

        try:
            speed_val = max(0.0, float(self.speed_entry.get()))
        except ValueError:
            speed_val = 0.03

        try:
            repeat = max(1, int(self.repeat_entry.get()))
        except ValueError:
            repeat = 1

        item = {
            "msg":        message,
            "key":        keyword,
            "type_speed": speed_val,
            "repeat":     repeat,
            "widget":     None,
        }

        row = ShortcutRow(self.scroll_frame, item,
                          on_delete=self.delete_entry,
                          on_test=self.test_entry)
        row.pack(fill="x", padx=6, pady=4)
        item["widget"] = row
        self.entries.append(item)

        # Clear inputs
        self.msg_box.delete("1.0", "end")
        self.key_entry.delete(0, "end")

        self._hide_empty_label()
        self._update_count()
        self.update_status("Shortcut added ✓", "#43b581")
        beep(900, 80)

    def _flash_error(self, msg):
        self.update_status(f"⚠ {msg}", "#e74c3c")

    def delete_entry(self, item):
        if item in self.entries:
            item["widget"].destroy()
            self.entries.remove(item)
        self._update_count()
        if not self.entries:
            self.empty_label.pack(pady=40)
        self.update_status("Shortcut removed", "#f39c12")

    def test_entry(self, item):
        if self.running:
            self.update_status("⚠ Already typing — wait or press ESC", "#e74c3c")
            return
        self.update_status("Test starts in 3 s — click target window now!", "#f39c12")
        threading.Thread(target=self._test_delayed, args=(item,), daemon=True).start()

    def _test_delayed(self, item):
        time.sleep(3)
        self.running     = True
        self.stop_typing = False
        self.execute_action(item, remove_after=False)

    def _hide_empty_label(self):
        self.empty_label.pack_forget()

    def _update_count(self):
        n = len(self.entries)
        self.count_label.configure(text=f"{n} shortcut{'s' if n != 1 else ''}")

    # ─────────────────────────────────────────────────────────────────────────
    #  KEYBOARD MONITOR — STOP KEY
    # ─────────────────────────────────────────────────────────────────────────
    def monitor_stop_key(self):
        while True:
            try:
                if keyboard.is_pressed("esc") and self.running:
                    self.stop_typing = True
            except Exception:
                pass
            time.sleep(0.05)

    # ─────────────────────────────────────────────────────────────────────────
    #  KEYBOARD MONITOR — KEYWORD DETECTION
    #  FIX: keyword check runs after EVERY keypress, not only after backspace
    # ─────────────────────────────────────────────────────────────────────────
    def monitor_keywords(self):
        while True:
            try:
                event = keyboard.read_event()
            except Exception:
                time.sleep(0.05)
                continue

            # Skip KEY_UP events
            if event.event_type != keyboard.KEY_DOWN:
                continue

            # If the app window itself is focused, reset buffer and skip
            try:
                focused = self.focus_get()
                if focused is not None:
                    self.typed_chars = ""
                    continue
            except Exception:
                pass

            # If already typing, ignore keystrokes
            if self.running:
                continue

            name = event.name

            # Update the rolling buffer
            if name in ("enter", "tab", "return"):
                self.typed_chars = ""
                continue
            elif name == "backspace":
                self.typed_chars = self.typed_chars[:-1]
            elif len(name) == 1:
                self.typed_chars += name
            elif name == "space":
                self.typed_chars += " "
            else:
                # Non-printable key (shift, ctrl, …) — reset
                self.typed_chars = ""
                continue

            # ── Check all shortcuts ───────────────────────────────────────
            with self._lock:
                entries_snapshot = list(self.entries)

            for item in entries_snapshot:
                if self.typed_chars.endswith(item["key"]):
                    self.running     = True
                    self.stop_typing = False
                    self.typed_chars = ""
                    threading.Thread(
                        target=self.execute_action,
                        args=(item,),
                        daemon=True
                    ).start()
                    break

    # ─────────────────────────────────────────────────────────────────────────
    #  TYPE THE MESSAGE
    # ─────────────────────────────────────────────────────────────────────────
    def execute_action(self, item, remove_after=True):
        # Erase the keyword from the target field
        kw_len = len(item["key"])
        for _ in range(kw_len):
            pyautogui.press("backspace")
            time.sleep(0.02)

        self.update_status("Typing… (ESC to cancel)", "#5865f2")

        interrupted = False
        for rep in range(item.get("repeat", 1)):
            if self.stop_typing:
                interrupted = True
                break

            for char in item["msg"]:
                if self.stop_typing:
                    interrupted = True
                    break

                # Handle special characters properly
                if char == "\n":
                    pyautogui.press("enter")
                elif char == "\t":
                    pyautogui.press("tab")
                else:
                    # pyautogui.write can't handle unicode; use typewrite with fallback
                    try:
                        pyautogui.write(char, interval=0)
                    except Exception:
                        pyautogui.hotkey("ctrl", "shift")  # no-op fallback

                if item["type_speed"] > 0:
                    time.sleep(item["type_speed"])

            # Add a newline between repeats (optional)
            if not interrupted and rep < item.get("repeat", 1) - 1:
                pyautogui.press("enter")
                time.sleep(0.05)

        # Remove widget after use (single-fire behaviour)
        if remove_after and item in self.entries:
            def _remove():
                item["widget"].destroy()
                self.entries.remove(item)
                self._update_count()
                if not self.entries:
                    self.empty_label.pack(pady=40)
            self.after(0, _remove)

        if interrupted:
            self.update_status("● Cancelled (ESC)", "#e74c3c")
            beep(350, 300)
        else:
            self.update_status("● Done", "#43b581")
            beep(1000, 90)

        self.running = False

    # ─────────────────────────────────────────────────────────────────────────
    #  STATUS
    # ─────────────────────────────────────────────────────────────────────────
    def update_status(self, text, color="#43b581"):
        self.after(0, lambda: self.status_label.configure(
            text=text, text_color=color))

    # ─────────────────────────────────────────────────────────────────────────
    #  CLEAR ALL
    # ─────────────────────────────────────────────────────────────────────────
    def reset_all(self):
        with self._lock:
            self.entries.clear()
        self.typed_chars = ""
        for w in self.scroll_frame.winfo_children():
            if w is not self.empty_label:
                w.destroy()
        self.empty_label.pack(pady=40)
        self._update_count()
        self.update_status("● All shortcuts cleared", "#f39c12")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = AutoTyperApp()
    app.mainloop()
