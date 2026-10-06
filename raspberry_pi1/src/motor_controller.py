import time
import serial

# シリアルポートの設定（ラズパイのハードウェアUART）
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 115200

def main():
    print("Initializing Raspberry Pi Serial Bridge to ESP32...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(1)
        
        # 例: Axis 0 をクローズドループ制御（状態 8）にする
        print("Requesting Closed Loop Control for Node 0...")
        ser.write(b"S 0 8\n")
        time.sleep(1)
        
        # 例: 速度 2.0 で回転
        print("Sending velocity command (2.0)...")
        for _ in range(20):
            ser.write(b"V 0 2.0\n")
            time.sleep(0.1)
            
        # 停止
        print("Stopping motor...")
        ser.write(b"V 0 0.0\n")
        ser.close()
        
    except Exception as e:
        print(f"Error communicating with ESP32: {e}")

if __name__ == '__main__':
    main()
