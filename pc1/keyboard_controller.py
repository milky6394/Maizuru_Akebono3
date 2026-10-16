import socket
import time
import keyboard  # 要: pip install keyboard

# ラズパイのIPアドレス
RASPBERRY_PI_IP = '192.168.137.2'
PORT = 5000

def main():
    print("Connecting to Raspberry Pi...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((RASPBERRY_PI_IP, PORT))
    print("Connected!")
    print("Controls (Smooth Acceleration Enabled):")
    print("  [W / S] : ODrive 0 & 1 (W: Forward/Reverse, S: Reverse/Forward)")
    print("  [D / A] : ODrive 0 & 1 Both Forward / Both Reverse")
    print("  [↑ / ↓] : GDS810 (CAN ID 2) Speed Control")
    print("  [ESC]   : Exit")

    # 追従制御（スムージング）用の現在値変数
    current_v0 = 0.0
    current_v1 = 0.0
    current_gds = 0.0

    # 追従の係数 (0.0 < alpha <= 1.0)
    # 値が大きいほどキビキビ追従し、小さいほどゆっくり滑らかに加減速します
    ALPHA = 0.2

    try:
        while True:
            # 1. この瞬間のキー入力に応じた「目標値 (Target)」を決定
            target_v0 = 0.0
            target_v1 = 0.0
            target_gds = 0.0

            # ODriveの制御 (W, S, D, A キー)
            if keyboard.is_pressed('w'):
                target_v0 = 20.0
                target_v1 = -20.0
            elif keyboard.is_pressed('s'):
                target_v0 = -20.0
                target_v1 = 20.0
            elif keyboard.is_pressed('d'):
                target_v0 = 20.0
                target_v1 = 20.0
            elif keyboard.is_pressed('a'):
                target_v0 = -20.0
                target_v1 = -20.0

            # GDS810の制御 (上下キー、CAN ID: 2)
            if keyboard.is_pressed('up'):
                target_gds = 100.0
            elif keyboard.is_pressed('down'):
                target_gds = -100.0

            # 2. 現在値を目標値に向かって少しずつ近づける（ローパスフィルター）
            current_v0 += (target_v0 - current_v0) * ALPHA
            current_v1 += (target_v1 - current_v1) * ALPHA
            current_gds += (target_gds - current_gds) * ALPHA

            # 3. スムージングされた値を使ってコマンドを生成・送信
            # ※ V 3 を V 0 に修正しています
            cmd = f"V 3 {current_v0:.1f}\nV 1 {current_v1:.1f}\nG 2 {current_gds:.1f}\n"
            client_socket.sendall(cmd.encode('utf-8'))
            
            # 送信周期（0.1秒 = 10Hz）
            time.sleep(0.1)
            
            if keyboard.is_pressed('esc'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        try:
            # 終了時は全モータ停止
            client_socket.sendall(b"V 3 0.0\nV 1 0.0\nG 2 0.0\n")
        except:
            pass
        client_socket.close()
        print("Disconnected.")

if __name__ == '__main__':
    main()