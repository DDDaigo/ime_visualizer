import os
import sys
import ctypes
import time
import tkinter as tk

# --- Windowsの解像度設定（文字がボヤけるのを防ぐ） ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# --- 定数設定 ---
WM_IME_CONTROL = 0x0283
IMC_GETOPENSTATUS = 0x0005

def get_ime_status():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd: return False
        hwnd_ime = ctypes.windll.imm32.ImmGetDefaultIMEWnd(hwnd)
        status = ctypes.windll.user32.SendMessageW(hwnd_ime, WM_IME_CONTROL, IMC_GETOPENSTATUS, 0)
        return status != 0
    except:
        return False

class ImeNotifierApp:
    def __init__(self):
        self.root = tk.Tk()
        
        # --- デザイン設定（ここをいじると変わります） ---
        self.W_WIDTH = 250       # 横幅
        self.W_HEIGHT = 200      # 高さ
        self.RADIUS = 40         # 角の丸み具合（大きくすると丸くなる）
        self.FONT = ("Segoe UI Black", 60) # フォント設定
        self.BG_COLOR = "#222222" # ポップアップの背景色（濃いグレー）
        
        # --- ウィンドウ設定 ---
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)

        # 【重要】透明色の設定（この色の部分が透けて見えなくなる）
        # 完全に透明にするための「魔法の色」として #000001 (ほぼ黒) を使います
        TRANS_KEY = "#000001"
        self.root.wm_attributes("-transparentcolor", TRANS_KEY)
        self.root.config(bg=TRANS_KEY)

        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_pos = (screen_width - self.W_WIDTH) // 2
        y_pos = (screen_height - self.W_HEIGHT) // 2
        self.root.geometry(f"{self.W_WIDTH}x{self.W_HEIGHT}+{x_pos}+{y_pos}")

        # --- キャンバスの作成（図形を描くための画用紙） ---
        self.canvas = tk.Canvas(self.root, width=self.W_WIDTH, height=self.W_HEIGHT, 
                                bg=TRANS_KEY, highlightthickness=0)
        self.canvas.pack()

        # 角丸四角形を描画（最初は隠しておく）
        self.round_rect = self.create_round_rect(0, 0, self.W_WIDTH, self.W_HEIGHT, self.RADIUS, fill=self.BG_COLOR)
        
        # 文字を描画
        self.text_id = self.canvas.create_text(self.W_WIDTH/2, self.W_HEIGHT/2, 
                                               text="", font=self.FONT, fill="white")

        self.last_status = None
        self.fade_job = None
        
        # 監視スタート
        self.check_loop()

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        """角丸四角形を描くための関数"""
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def show_notification(self, text, text_color):
        """表示処理"""
        # 文字と色を更新
        self.canvas.itemconfig(self.text_id, text=text, fill=text_color)
        
        # 表示（透明度を戻す）
        self.root.attributes("-alpha", 0.7) # 0.7 = 70%の濃さ
        self.root.deiconify()
        
        if self.fade_job:
            self.root.after_cancel(self.fade_job)
        
        # 0.4秒後に消す
        self.fade_job = self.root.after(400, self.hide_notification)

    def hide_notification(self):
        self.root.attributes("-alpha", 0.0)

    def check_loop(self):
        current_status = get_ime_status()
        
        if self.last_status is not None and self.last_status != current_status:
            if current_status:
                self.show_notification("JP", "#00FF00") # 緑
            else:
                self.show_notification("EN", "#00FFFF") # 水色
        
        self.last_status = current_status
        self.root.after(100, self.check_loop)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImeNotifierApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass