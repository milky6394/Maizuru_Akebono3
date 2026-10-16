import socket
import serial
import time

# ESP32とのシリアル接続設定（環境に合わせて /dev/ttyUSB0 や /dev/ttyACM0 を変更）
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

print("Connecting to ESP32...")
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
time.sleep(2) # 起動待ち
print("Connected to ESP32!")

# ソケットサーバー設定
HOST = '0.0.0.0'
PORT = 5000  # モータ制御用TCPポート

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Motor Server listening on port {PORT}...")

try:
    while True:
        conn, addr = server_socket.accept()
        print(f"Connected from PC: {addr}")
        
        # ODriveの初期化 (必要に応じて)
        ser.write(b"S 3 8\n")
        time.sleep(0.3)
        ser.write(b"S 1 8\n")
        time.sleep(0.3)
        ser.write(b"E 2\n") # GDS810スタート
        
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # PCから受け取ったコマンドをそのままESP32へシリアル送信
                ser.write(data)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
        # 切断時は安全のため全モータ停止指令を送る
            ser.write(b"V 3 0.0\nV 1 0.0\nG 2 0.0\n")
            conn.close()
            print("Client disconnected. Motors stopped.")

except KeyboardInterrupt:
    print("Server shutting down.")
finally:
    server_socket.close()
    ser.close()
