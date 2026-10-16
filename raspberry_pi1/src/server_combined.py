import socket
import subprocess
import threading
import time
import serial

# --- 設定 ---
SERIAL_PORT = '/dev/ttyACM0'  # ESP32が繋がっているポートに合わせて変更
BAUD_RATE = 115200
HOST = '0.0.0.0'
MOTOR_PORT = 5000  # モーター制御用ポート
PC_IP = '192.168.3.10'  # パソコンのIPアドレス（映像送信先）
VIDEO_PORT = 5001  # カメラ映像用ポート（PC側と合わせる）

# シリアルポートの初期化（ESP32へ接続）
try:
  ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
  time.sleep(2)
  print(f'Connected to ESP32 on {SERIAL_PORT}')
except Exception as e:
  print(f'Serial connection error: {e}')
  ser = None


def camera_stream_task():
  """GStreamerを使ってカメラ映像をUDPでPCへストリーミングし続ける関数"""
  cmd = [
      'gst-launch-1.0',
      '-v',
      'v4l2src',
      'device=/dev/video0',
      '!',
      'image/jpeg,width=1920,height=1080,framerate=30/1',
      '!',
      'rtpjpegpay',
      '!',
      f'udpsink',
      f'host={PC_IP}',
      f'port={VIDEO_PORT}',
  ]
  print('[Camera Stream] 配信を開始します...')
  while True:
    try:
      # GStreamerプロセスを起動
      process = subprocess.Popen(cmd)
      process.wait()
    except Exception as e:
      print(f'[Camera Stream] エラー: {e}')
    # 万が一プロセスが落ちた場合に備えて少し待って再起動
    time.sleep(2.0)


def motor_server_task():
  """PCからのモーター制御コマンドをTCPで受信し、ESP32へシリアル転送する関数"""
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((HOST, MOTOR_PORT))
  server_socket.listen(1)
  print(f'[Motor Server] ポート {MOTOR_PORT} で接続待機中...')

  while True:
    conn, addr = server_socket.accept()
    print(f'[Motor Server] パソコンと接続しました: {addr}')
    try:
      while True:
        data = conn.recv(1024)
        if not data:
          break
        # PCから受け取ったコマンド文字列をそのままESP32へシリアル送信
        if ser and ser.is_open:
          ser.write(data)
    except Exception as e:
      print(f'[Motor Server] 通信エラー: {e}')
    finally:
      conn.close()
      print('[Motor Server] 接続が切断されました。再待機します...')


if __name__ == '__main__':
  # 1. カメラ配信をバックグラウンドスレッドで開始
  cam_thread = threading.Thread(target=camera_stream_task, daemon=True)
  cam_thread.start()

  # 2. メインスレッドでモーター制御サーバーを動作させる
  try:
    motor_server_task()
  except KeyboardInterrupt:
    print('終了します...')
    if ser and ser.is_open:
      ser.close()
