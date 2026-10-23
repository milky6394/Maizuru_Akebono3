import socket
import serial
import time
from adafruit_servokit import ServoKit

# 16チャンネル用のServoKitオブジェクトを作成
kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 270
kit.servo[1].actuation_range = 270
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)

# ESP32とのシリアル接続設定
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

print("Connecting to ESP32...")
try:
  ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
  time.sleep(2)
  print("Connected to ESP32!")
except Exception as e:
  print(f"ESP32 Connection Error (Simulation/No hardware mode): {e}")
  ser = None

# ソケットサーバー設定
HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Combined Server listening on port {PORT}...")

try:
  while True:
    conn, addr = server_socket.accept()
    print(f"Connected from PC: {addr}")

    if ser and ser.is_open:
      try:
        ser.write(b"S 3 8\n")
        time.sleep(0.3)
        ser.write(b"S 1 8\n")
        time.sleep(0.3)
        ser.write(b"E 2\n")
      except:
        pass

    try:
      while True:
        data = conn.recv(1024)
        if not data:
          break

        commands = data.decode("utf-8").strip().split("\n")
        esp32_cmds = []

        for cmd in commands:
          parts = cmd.split(" ")
          if len(parts) == 3 and parts[0] == "S" and parts[1] in ("0", "1"):
            # サーボ制御コマンド (例: S 0 45.0)
            servo_idx = int(parts[1])
            angle = float(parts[2])
            kit.servo[servo_idx].angle = angle
          else:
            # それ以外のコマンド（ODrive / GDS用）はESP32へ転送
            esp32_cmds.append(cmd)

        # まとめてESP32へ送信
        if ser and ser.is_open and esp32_cmds:
          ser.write(("\n".join(esp32_cmds) + "\n").encode("utf-8"))

    except Exception as e:
      print(f"Connection error: {e}")
    finally:
      if ser and ser.is_open:
        try:
          ser.write(b"V 3 0.0\nV 1 0.0\nG 2 0.0\n")
        except:
          pass
      conn.close()
      print("Client disconnected. Motors stopped.")

except KeyboardInterrupt:
  print("Server shutting down.")
finally:
  server_socket.close()
  if ser and ser.is_open:
    ser.close()
