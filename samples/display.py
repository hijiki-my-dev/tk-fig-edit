# 画像をウィンドウに表示させる

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinterdnd2
from tkinterdnd2 import DND_FILES
import threading
from PIL import Image, ImageTk
from pathlib import Path
import shutil

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像処理アプリ")
        self.root.geometry("800x600")

        # 出力ディレクトリの設定
        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "edited_fig")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # ドラッグ&ドロップ対応
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop)

        # 画像ファイルパスリスト
        self.image_paths = []

        # UIの構築
        self.create_ui()

    def create_ui(self):
        print("create_ui")
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部フレーム (入力部分)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        # ファイル選択ボタン
        select_btn = ttk.Button(top_frame, text="ファイル選択", command=self.select_files)
        select_btn.pack(side=tk.LEFT, padx=5)

        # 出力ディレクトリ設定
        ttk.Label(top_frame, text="出力先:").pack(side=tk.LEFT, padx=(20, 5))
        self.output_entry = ttk.Entry(top_frame)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.output_entry.insert(0, self.output_dir)

        # output_btn = ttk.Button(top_frame, text="変更", command=self.change_output_dir)
        # output_btn.pack(side=tk.LEFT, padx=5)

        # ファイルリスト表示
        file_frame = ttk.LabelFrame(main_frame, text="選択されたファイル")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.file_list = ScrolledText(file_frame, height=5)
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    def setup_compress_tab(self):
        print("setup_compress_tab")
        frame = ttk.Frame(self.compress_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="圧縮品質 (低 → 高):").grid(row=0, column=0, sticky=tk.W, pady=10)

        self.compress_quality = tk.DoubleVar(value=85)  # IntVar → DoubleVar に変更
        quality_scale = ttk.Scale(frame, from_=1, to=100, variable=self.compress_quality, orient=tk.HORIZONTAL)
        quality_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        self.quality_label = ttk.Label(frame, text=str(int(self.compress_quality.get())))  # 初期値を整数で表示
        self.quality_label.grid(row=0, column=2, padx=5)

        # スライダーの値が変わったら整数にしてラベルを更新
        def update_label(*args):
            self.quality_label.config(text=str(int(self.compress_quality.get())))

        self.compress_quality.trace_add("write", update_label)

        # 説明
        ttk.Label(frame, text="高い値ほど低品質になりますが、ファイルサイズは小さくなります。").grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)

    def select_files(self):
        print("select_files")
        files = filedialog.askopenfilenames(filetypes=[("画像ファイル", "*.jpg *.jpeg *.png *.webp *.tiff *.bmp *.gif")])
        # if files:
        #     self.image_paths = list(files)
        #     self.update_file_list()
        #     self.update_image_info()

    def drop(self, event):
        print("drop")
        files = self.root.tk.splitlist(event.data)
        valid_files = [f for f in files if self.is_valid_image(f)]
        if valid_files:
            self.image_paths = valid_files
            self.update_file_list()
            # self.update_image_info()
        img = Image.open(self.image_paths[0])
        self.display_preview(img)

    def is_valid_image(self, file_path):
        print("is_valid_image")
        _, ext = os.path.splitext(file_path)
        return ext.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp', '.gif']

    def update_file_list(self):
        print("update_file_list")
        self.file_list.delete(1.0, tk.END)
        for path in self.image_paths:
            self.file_list.insert(tk.END, f"{path}\n")

    def display_preview(self, img):
        print("display_preview")
        # プレビュー用にサイズ調整
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        # self.preview_label.config(image=photo)
        # self.preview_label.image = photo  # 参照を保持

if __name__ == "__main__":
    # root = tk.Tk()

    # TkinterのDnDを有効にする
    try:
        import tkinterdnd2
        root = tkinterdnd2.TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
        print("tkinterdnd2がインストールされていないため、ドラッグ&ドロップ機能は無効です。")
        print("インストールするには: pip install tkinterdnd2")

    app = ImageProcessorApp(root)
    root.mainloop()
