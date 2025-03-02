# 画像処理アプリ

このプロジェクトは、画像の圧縮、形式変更、リサイズを行うためのTkinterベースのデスクトップアプリケーションです。オフラインでも画像の圧縮等を行うことができ、ファイル数を気にする必要もないのがメリットです。

## 機能概要

- 画像の圧縮
- 画像形式の変更
- 画像のリサイズ
- ドラッグ&ドロップ対応
- 複数ファイルの一括処理

## 環境

- Python 3.12
- Macの場合はシステムのPythonバージョンに対応したpython-tk
    - 例）pyenvでバージョンを管理しており、`pyenv global`が3.11の場合
        - -> `brew install python-tk@3.11`

## 使い方

### ターミナルから実行
- 必要に応じて仮想環境を作成、ライブラリをインストールした後にmain.pyを実行
```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python3 main.py
```

### アプリを作成
- .spec形式のファイルを用意して、PyInstallerを使ってアプリを作成
- Macで作成する場合の例はsample_spec.txt
```
$ pyinstaller --clean file_name.spec
```
