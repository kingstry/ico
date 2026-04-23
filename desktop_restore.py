import ctypes
import ctypes.wintypes
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, font

# 2K/高分辨率 DPI 适配（必须在创建窗口前调用）
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# Windows API
user32 = ctypes.windll.user32
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "positions.json")

LVM_GETITEMCOUNT     = 0x1004
LVM_GETITEMPOSITION  = 0x1010
LVM_SETITEMPOSITION32 = 0x100F
LVM_GETITEMTEXTW     = 0x1073

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask",       ctypes.c_uint),
        ("iItem",      ctypes.c_int),
        ("iSubItem",   ctypes.c_int),
        ("state",      ctypes.c_uint),
        ("stateMask",  ctypes.c_uint),
        ("pszText",    ctypes.c_wchar_p),
        ("cchTextMax", ctypes.c_int),
        ("iImage",     ctypes.c_int),
        ("lParam",     ctypes.c_long),
        ("iIndent",    ctypes.c_int),
    ]

def get_listview_hwnd():
    """获取桌面 SysListView32 句柄（支持多种 Windows 桌面结构）"""
    hwnd = user32.GetShellWindow()
    # 方式1: 标准结构
    defview = user32.FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
    if defview:
        lv = user32.FindWindowExW(defview, None, "SysListView32", None)
        if lv:
            return lv
    # 方式2: WorkerW 结构（部分 Win11）
    workerw = None
    def enum_proc(h, _):
        nonlocal workerw
        dv = user32.FindWindowExW(h, None, "SHELLDLL_DefView", None)
        if dv:
            lv = user32.FindWindowExW(dv, None, "SysListView32", None)
            if lv:
                workerw = lv
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(WNDENUMPROC(enum_proc), None)
    return workerw

def get_icon_count(hwnd):
    return user32.SendMessageW(hwnd, LVM_GETITEMCOUNT, 0, 0)

def get_icon_name(hwnd, index):
    buf = ctypes.create_unicode_buffer(512)
    lvi = LVITEMW()
    lvi.mask = 0x0001  # LVIF_TEXT
    lvi.iItem = index
    lvi.iSubItem = 0
    lvi.pszText = buf
    lvi.cchTextMax = 512
    user32.SendMessageW(hwnd, LVM_GETITEMTEXTW, index, ctypes.addressof(lvi))
    return buf.value

def get_icon_pos(hwnd, index):
    pt = POINT()
    user32.SendMessageW(hwnd, LVM_GETITEMPOSITION, index, ctypes.addressof(pt))
    return pt.x, pt.y

def set_icon_pos(hwnd, index, x, y):
    pt = POINT(x, y)
    user32.SendMessageW(hwnd, LVM_SETITEMPOSITION32, index, ctypes.addressof(pt))

def save_positions():
    hwnd = get_listview_hwnd()
    if not hwnd:
        messagebox.showerror("错误", "无法读取桌面图标\n请右键程序 → 以管理员身份运行")
        return
    count = get_icon_count(hwnd)
    positions = {}
    for i in range(count):
        name = get_icon_name(hwnd, i)
        x, y = get_icon_pos(hwnd, i)
        if name:
            positions[name] = {"x": x, "y": y}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)
    messagebox.showinfo("✅ 保存成功", f"已保存 {len(positions)} 个图标的位置！\n\n文件：{SAVE_FILE}")

def restore_positions():
    if not os.path.exists(SAVE_FILE):
        messagebox.showerror("错误", "还没有保存过位置\n请先点击【保存当前位置】")
        return
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        positions = json.load(f)
    hwnd = get_listview_hwnd()
    if not hwnd:
        messagebox.showerror("错误", "无法获取桌面窗口\n请右键程序 → 以管理员身份运行")
        return
    count = get_icon_count(hwnd)
    restored = 0
    for i in range(count):
        name = get_icon_name(hwnd, i)
        if name in positions:
            set_icon_pos(hwnd, i, positions[name]["x"], positions[name]["y"])
            restored += 1
    messagebox.showinfo("✅ 恢复成功", f"已恢复 {restored} 个图标的位置！")

# ── 界面 ──────────────────────────────────────────────
root = tk.Tk()
root.title("桌面图标位置管理")
root.resizable(False, False)
root.configure(bg="#f5f5f5")

# 根据屏幕实际DPI自动缩放界面
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# 2K(2560x1440)及以上放大1.8倍，1080P保持原尺寸
if screen_w >= 2560 or screen_h >= 1440:
    scale = 1.8
elif screen_w >= 1920:
    scale = 1.3
else:
    scale = 1.0

win_w = int(380 * scale)
win_h = int(220 * scale)

# 居中显示
x = (screen_w - win_w) // 2
y = (screen_h - win_h) // 2
root.geometry(f"{win_w}x{win_h}+{x}+{y}")

fs_title = int(13 * scale)
fs_sub   = int(9  * scale)
fs_btn   = int(10 * scale)
pad_top  = int(18 * scale)
pad_btn  = int(6  * scale)
btn_w    = int(22 * scale / 1.4)  # tkinter width 单位是字符
btn_h    = int(2  * scale / 1.2)

try:
    root.iconbitmap(default="")
except:
    pass

title_lbl = tk.Label(root, text="🖥️ 桌面图标位置管理", bg="#f5f5f5",
                     font=("微软雅黑", fs_title, "bold"), fg="#333")
title_lbl.pack(pady=(pad_top, int(4 * scale)))

sub_lbl = tk.Label(root, text="保存 / 一键恢复你的图标布局", bg="#f5f5f5",
                   font=("微软雅黑", fs_sub), fg="#888")
sub_lbl.pack(pady=(0, int(14 * scale)))

btn_save = tk.Button(root, text="📸  保存当前位置", width=btn_w, height=btn_h,
                     bg="#4CAF50", fg="white", font=("微软雅黑", fs_btn, "bold"),
                     relief="flat", cursor="hand2", command=save_positions)
btn_save.pack(pady=pad_btn)

btn_restore = tk.Button(root, text="🔄  恢复保存的位置", width=btn_w, height=btn_h,
                        bg="#2196F3", fg="white", font=("微软雅黑", fs_btn, "bold"),
                        relief="flat", cursor="hand2", command=restore_positions)
btn_restore.pack(pady=pad_btn)

root.mainloop()
