"""Small desktop interface; only reads game files and writes a new mod ZIP."""
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from build_from_game import build, locate


def main():
    window = tk.Tk()
    window.title('STEINS;GATE RE:BOOT 双语字幕生成器')
    window.geometry('640x330')
    folder = tk.StringVar()
    messages = queue.Queue()
    frame = ttk.Frame(window, padding=18)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='选择包含 sgre_steam.exe 的正版游戏目录').pack(anchor='w')
    row = ttk.Frame(frame)
    row.pack(fill='x', pady=10)
    ttk.Entry(row, textvariable=folder).pack(side='left', fill='x', expand=True)
    def choose():
        selected = filedialog.askdirectory(title='选择 SGRE 游戏目录')
        if selected:
            folder.set(selected)
    choose_button = ttk.Button(row, text='选择目录', command=choose)
    choose_button.pack(side='right', padx=(8, 0))
    status = tk.Text(frame, height=10, state='disabled', wrap='word')
    status.pack(fill='both', expand=True, pady=10)
    busy = False
    def start():
        nonlocal busy
        if not folder.get():
            messagebox.showinfo('提示', '请先选择游戏目录。')
            return
        output = filedialog.asksaveasfilename(title='保存生成的字幕 Mod', defaultextension='.zip', initialfile='bilingual_subtitles.zip', filetypes=[('ZIP', '*.zip')])
        if not output:
            return
        selected = folder.get()
        busy = True
        button.configure(state='disabled')
        choose_button.configure(state='disabled')
        def work():
            try:
                build(*locate(selected), output, progress=lambda text: messages.put(('log', text)))
                messages.put(('done', '生成完成。请用兼容 Mod Manager 加载 ZIP，并将游戏设为日语。'))
            except Exception as error:
                messages.put(('error', str(error)))
        threading.Thread(target=work, daemon=True).start()
    button = ttk.Button(frame, text='生成双语字幕 Mod', command=start)
    button.pack(anchor='w')
    def poll():
        nonlocal busy
        while not messages.empty():
            kind, text = messages.get_nowait()
            status.configure(state='normal')
            status.insert('end', text + '\n')
            status.see('end')
            status.configure(state='disabled')
            if kind in ('done', 'error'):
                busy = False
                button.configure(state='normal')
                choose_button.configure(state='normal')
                if kind == 'error':
                    messagebox.showerror('生成失败', text)
                else:
                    messagebox.showinfo('完成', text)
        window.after(100, poll)
    def close():
        if busy:
            messagebox.showinfo('提示', '正在生成，请完成后再关闭窗口。')
        else:
            window.destroy()
    window.protocol('WM_DELETE_WINDOW', close)
    poll()
    window.mainloop()

if __name__ == '__main__':
    main()
