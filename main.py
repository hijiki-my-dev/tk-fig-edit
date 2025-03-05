import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import tkinterdnd2
from PIL import Image
from tkinterdnd2 import DND_FILES

from logger import Logger

log_level = "WARNING"
logger = Logger(log_level)

DEFAULT_COMPRESS_RATE = 7
DEFAULT_RESIZE_VALUE = 800
PNG_COLORS = 256


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像処理アプリ")
        self.root.geometry("800x500")

        # 出力ディレクトリの設定
        self.output_dir = os.path.join(
            os.path.expanduser("~"), "Downloads", "edited_fig"
        )
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # ドラッグ&ドロップ対応
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.drop)

        # 画像ファイルパスリスト
        self.image_paths = []

        # UIの構築
        self.create_ui()

    def create_ui(self):
        logger.debug("create_ui")
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部フレーム (入力部分)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        # ファイル選択ボタン
        select_btn = ttk.Button(
            top_frame, text="ファイル選択", command=self.select_files
        )
        select_btn.pack(side=tk.LEFT, padx=5)

        # 出力ディレクトリ設定
        ttk.Label(top_frame, text="出力先:").pack(side=tk.LEFT, padx=(20, 5))
        self.output_entry = ttk.Entry(top_frame)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.output_entry.insert(0, self.output_dir)

        output_btn = ttk.Button(
            top_frame, text="出力先の変更", command=self.change_output_dir
        )
        output_btn.pack(side=tk.LEFT, padx=5)

        # タブコントロール
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=10)

        # 圧縮タブ
        self.compress_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.compress_tab, text="圧縮")
        self.setup_compress_tab()

        # 形式変更タブ
        self.format_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.format_tab, text="形式変更")
        self.setup_format_tab()

        # リサイズタブ
        self.resize_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.resize_tab, text="リサイズ")
        self.setup_resize_tab()

        # ファイルリスト表示
        file_frame = ttk.LabelFrame(main_frame, text="選択されたファイル")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.file_list = ScrolledText(file_frame, height=5)
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 実行ボタン
        execute_frame = ttk.Frame(main_frame)
        execute_frame.pack(fill=tk.X, pady=10)

        self.progress = ttk.Progressbar(
            execute_frame, orient=tk.HORIZONTAL, length=100, mode="determinate"
        )
        self.progress.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=5)

        self.execute_btn = ttk.Button(
            execute_frame, text="実行", command=self.execute
        )
        self.execute_btn.pack(side=tk.RIGHT, padx=5)

        # 取り消しボタン
        cancel_btn = ttk.Button(
            execute_frame, text="取り消し", command=self.cancel_upload
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def setup_compress_tab(self):
        logger.debug("setup_compress_tab")
        frame = ttk.Frame(self.compress_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="圧縮後の品質 (低 → 高):").grid(
            row=0, column=0, sticky=tk.W, pady=10
        )

        self.compress_quality = tk.DoubleVar(value=DEFAULT_COMPRESS_RATE)
        quality_scale = ttk.Scale(
            frame,
            from_=1,
            to=10,
            variable=self.compress_quality,
            orient=tk.HORIZONTAL,
        )
        quality_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        self.quality_label = ttk.Label(
            frame, text=str(int(self.compress_quality.get()))
        )
        self.quality_label.grid(row=0, column=2, padx=5)

        # スライダーの値が変わったら整数にしてラベルを更新
        def update_label(*args):
            self.quality_label.config(
                text=str(int(self.compress_quality.get()))
            )

        self.compress_quality.trace_add("write", update_label)
        ttk.Label(
            frame,
            text="低い値ほど低品質になり、ファイルサイズが小さくなります。",
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)

    def setup_format_tab(self):
        logger.debug("setup_format_tab")
        frame = ttk.Frame(self.format_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="変換先形式:").grid(
            row=0, column=0, sticky=tk.W, pady=10
        )

        self.target_format = tk.StringVar(value="jpeg")
        formats = ["jpeg", "png", "webp", "tiff", "bmp", "gif"]

        format_combo = ttk.Combobox(
            frame, textvariable=self.target_format, values=formats
        )
        format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

    def setup_resize_tab(self):
        logger.debug("setup_resize_tab")
        frame = ttk.Frame(self.resize_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        size_frame = ttk.LabelFrame(frame, text="現在のサイズ")
        size_frame.pack(fill=tk.X, pady=10)

        self.current_size_label = ttk.Label(
            size_frame, text="ファイルを選択してください"
        )
        self.current_size_label.pack(pady=5)

        resize_frame = ttk.Frame(frame)
        resize_frame.pack(fill=tk.X, pady=10)
        self.resize_by = tk.StringVar(value="width")
        ttk.Radiobutton(
            resize_frame,
            text="幅を指定",
            variable=self.resize_by,
            value="width",
        ).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Radiobutton(
            resize_frame,
            text="高さを指定",
            variable=self.resize_by,
            value="height",
        ).grid(row=1, column=0, padx=5, sticky=tk.W)

        self.resize_value = tk.IntVar(value=DEFAULT_RESIZE_VALUE)
        ttk.Entry(resize_frame, textvariable=self.resize_value, width=10).grid(
            row=0, column=1, rowspan=2, padx=5
        )
        ttk.Label(resize_frame, text="pixels").grid(
            row=0, column=2, rowspan=2, padx=5, sticky=tk.W
        )

    def select_files(self):
        logger.debug("select_files")
        files = filedialog.askopenfilenames(
            filetypes=[
                (
                    "画像ファイル",
                    "*.jpg *.jpeg *.png *.webp *.tiff *.bmp *.gif",
                )
            ]
        )
        if files:
            self.image_paths.extend(list(files))
            self.update_file_list()
            self.update_image_info()

    def drop(self, event):
        logger.debug("drop")
        files = self.root.tk.splitlist(event.data)
        logger.debug(f"files: {files}")
        valid_files = [f for f in files if self.is_valid_image(f)]
        if valid_files:
            self.image_paths.extend(valid_files)
            logger.debug(f"image_paths: {self.image_paths}")
            self.update_file_list()
            self.update_image_info()

    def is_valid_image(self, file_path):
        logger.debug("is_valid_image")
        _, ext = os.path.splitext(file_path)
        return ext.lower() in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".tiff",
            ".bmp",
            ".gif",
        ]

    def update_file_list(self):
        logger.debug("update_file_list")
        self.file_list.delete(1.0, tk.END)
        for path in self.image_paths:
            self.file_list.insert(tk.END, f"{path}\n")
        logger.debug(f"image_paths: {self.image_paths}")

    def update_image_info(self):
        logger.debug("update_image_info")
        if self.image_paths:
            try:
                img = Image.open(self.image_paths[0])
                width, height = img.size
                self.current_size_label.config(
                    text=f"幅: {width}px, 高さ: {height}px"
                )
            except Exception as e:
                self.current_size_label.config(text=f"エラー: {str(e)}")

    def show_preview(self):
        logger.debug("show_preview")
        if not self.image_paths:
            messagebox.showinfo("情報", "画像を選択してください")
            return

        try:
            img = Image.open(self.image_paths[0])
            width, height = img.size

            if self.resize_by.get() == "width":
                new_width = self.resize_value.get()
                new_height = int(height * (new_width / width))
            else:
                new_height = self.resize_value.get()
                new_width = int(width * (new_height / height))

            self.current_size_label.config(
                text=f"元のサイズ: {width}px x {height}px\n新しいサイズ: {new_width}px x {new_height}px"
            )
        except Exception as e:
            messagebox.showerror(
                "エラー", f"プレビューの生成中にエラーが発生しました: {str(e)}"
            )

    def change_output_dir(self):
        logger.debug("change_output_dir")
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_dir)

    def execute(self):
        logger.debug("execute")
        if not self.image_paths:
            messagebox.showinfo("情報", "画像を選択してください")
            return

        # 出力ディレクトリの確認と作成
        self.output_dir = self.output_entry.get()
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except Exception as e:
                messagebox.showerror(
                    "エラー", f"出力ディレクトリの作成に失敗しました: {str(e)}"
                )
                return

        # 現在のタブを取得
        current_tab = self.tab_control.tab(self.tab_control.select(), "text")

        # 処理を別スレッドで実行
        self.execute_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.image_paths)

        thread = threading.Thread(
            target=self.process_images, args=(current_tab,)
        )
        thread.daemon = True
        thread.start()

    def process_images(self, operation):
        logger.debug("process_images")
        success_count = 0
        error_count = 0

        for i, image_path in enumerate(self.image_paths):
            try:
                self.root.after(
                    0, lambda val=i: self.progress.config(value=val + 1)
                )

                img = Image.open(image_path)
                file_name = os.path.basename(image_path)
                base_name, ext = os.path.splitext(file_name)

                logger.debug(f"拡張子: {ext}")

                # 処理タイプに応じた処理
                if operation == "圧縮":
                    # 1から10の入力を5から95に変換
                    quality = (int(self.compress_quality.get()) - 1) * 10 + 5
                    output_path = os.path.join(
                        self.output_dir, f"{base_name}_edited{ext}"
                    )
                    if ext.lower()[1:] == "png":
                        img.quantize(colors=PNG_COLORS).save(
                            output_path, quality=quality, optimize=True
                        )
                    else:
                        img.save(output_path, quality=quality, optimize=True)

                elif operation == "形式変更":
                    target_format = self.target_format.get()
                    output_path = os.path.join(
                        self.output_dir, f"{base_name}_edited.{target_format}"
                    )

                    # PNGなどの形式に透過処理を適用
                    if (
                        target_format.lower() in ["png", "webp"]
                        and img.mode != "RGBA"
                    ):
                        img = img.convert("RGBA")
                    elif (
                        target_format.lower() in ["jpeg", "jpg"]
                        and img.mode == "RGBA"
                    ):
                        # JPEGは透過をサポートしないため、白背景を適用
                        background = Image.new(
                            "RGBA", img.size, (255, 255, 255)
                        )
                        img = Image.alpha_composite(background, img)
                        img = img.convert("RGB")

                    img.save(output_path, format=target_format.upper())

                elif operation == "リサイズ":
                    width, height = img.size

                    if self.resize_by.get() == "width":
                        new_width = self.resize_value.get()
                        new_height = int(height * (new_width / width))
                    else:
                        new_height = self.resize_value.get()
                        new_width = int(width * (new_height / height))

                    resized_img = img.resize(
                        (new_width, new_height), Image.LANCZOS
                    )
                    output_path = os.path.join(
                        self.output_dir, f"{base_name}_edited{ext}"
                    )
                    resized_img.save(output_path)

                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"エラー ({image_path}): {str(e)}")

        self.root.after(
            0, lambda: self.processing_complete(success_count, error_count)
        )

    def processing_complete(self, success_count, error_count):
        logger.debug("processing_complete")
        self.execute_btn.config(state=tk.NORMAL)
        messagebox.showinfo(
            "完了",
            f"処理が完了しました\n成功: {success_count}\nエラー: {error_count}",
        )

    def cancel_upload(self):
        logger.debug("cancel_upload")
        # アップロードした画像のファイルを削除する
        self.image_paths = []
        self.update_file_list()
        self.update_image_info()


if __name__ == "__main__":
    try:
        root = tkinterdnd2.TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
        logger.error(
            "tkinterdnd2がインストールされていないため、ドラッグ&ドロップ機能は無効です。"
        )
        logger.error("インストールするには: pip install tkinterdnd2")

    app = ImageProcessorApp(root)
    root.mainloop()
