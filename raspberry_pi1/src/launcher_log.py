import os
import platform
import subprocess
import sys
import threading
import time

# OSの判定
is_windows = platform.system() == "Windows"

if is_windows:
  os.system("")

COLORS = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
]
RESET = "\033[0m"

# ---------------------------------------------------------
# 実行したいプログラム・コマンドのリスト
# (引数や記号「!」を含む場合は、文字列として丸ごと1行で書く)
# ---------------------------------------------------------
if is_windows:
  commands = [
      "python script1.py",
      "python script2.py",
  ]
else:
  commands = [
      # リストの要素を「文字列」にし、shell=True でそのまま渡せるようにする
      "python3 remote_server.py",
      (
          "gst-launch-1.0 -v v4l2src device=/dev/video0 !"
          " image/jpeg,width=1920,height=1080,framerate=30/1 ! rtpjpegpay !"
          " udpsink host=192.168.137.1 port=5000"
      ),
  ]


def stream_reader(process, name, color):
  """各プロセスの標準出力を監視し、色と名前をつけてリアルタイムで出力する関数"""
  try:
    for line in iter(process.stdout.readline, b""):
      decoded_line = line.decode("utf-8", errors="replace").rstrip()
      print(f"{color}[{name}]{RESET} {decoded_line}")
  except Exception as e:
    print(f"{color}[{name}] 読み取りエラー: {e}{RESET}")


processes = []
threads = []

try:
  print("=== 複数プログラムのログ統合ランチャーを開始します ===")
  print("-" * 50)

  for i, cmd_str in enumerate(commands):
    # ログ表示用の名前（コマンドの最初の単語、例: python3 や gst-launch-1.0）
    script_name = cmd_str.split()[0]
    color = COLORS[i % len(COLORS)]

    # shell=True を指定することで、スペースや「!」を含む長いコマンド文字列をそのまま実行できる
    p = subprocess.Popen(
        cmd_str,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    processes.append(p)

    t = threading.Thread(
        target=stream_reader, args=(p, script_name, color), daemon=True
    )
    t.start()
    threads.append(t)

  print(f"全 {len(commands)} 件のプログラムをバックグラウンドで起動しました。\n")

  while True:
    time.sleep(1)

except KeyboardInterrupt:
  print("\n" + "=" * 50)
  print("=== 終了シグナル（Ctrl+C）を検知しました。全プロセスを終了します ===")
  for p in processes:
    p.terminate()
    p.wait()
  print("すべてのプロセスを停止しました。")
