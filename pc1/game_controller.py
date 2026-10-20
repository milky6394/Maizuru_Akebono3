import socket
import time
import pygame

# ラズパイのIPアドレス
RASPBERRY_PI_IP = '192.168.137.2'
PORT = 5000

def main():
    # Pygameとジョイスティック（ゲームパッド）の初期化
    pygame.init()
    pygame.joystick.init()
    
    if pygame.joystick.get_count() == 0:
        print("エラー: ゲームパッド（JC-GP20X）が接続されていません。接続を確認してください。")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"接続されたコントローラー: {joystick.get_name()}")

    print("Connecting to Raspberry Pi...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((RASPBERRY_PI_IP, PORT))
    print("Connected!")
    print("Controls (JC-GP20X):")
    print("  [左スティック 上下] : 前後移動")
    print("  [右スティック 左右] : ステアリング（走行中の旋回）")
    print("  [十字キー 左右]     : その場で逆回転する超信地旋回（ピボットターン）")
    print("  [十字キー 上下]     : GDS810 (CAN ID 2) 速度制御")
    print("  [START/BACKボタン]  : 終了 (ESC)")

    # 追従制御（スムージング）用の現在値変数
    current_v0 = 0.0
    current_v1 = 0.0
    current_gds = 0.0
    ALPHA = 0.2

    # スティックのデッドゾーン（遊び）設定
    DEADZONE = 0.1

    try:
        running = True
        while running:
            pygame.event.pump()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- ジョイスティックの入力取得 ---
            left_y = joystick.get_axis(1)   # 左スティック上下
            right_x = joystick.get_axis(2)  # 右スティック左右

            # デッドゾーン処理
            if abs(left_y) < DEADZONE: left_y = 0.0
            if abs(right_x) < DEADZONE: right_x = 0.0

            # 十字キーの取得
            hat_x, hat_y = 0, 0
            if joystick.get_numhats() > 0:
                hat_x, hat_y = joystick.get_hat(0)

            # --- 制御目標値の計算 ---
            target_v0 = 0.0
            target_v1 = 0.0

            # 優先判定：十字キーの左右が押されている場合は「超信地旋回（その場旋回）」を優先
            if hat_x < 0:  # 十字キー「左」：その場で左旋回（左車輪=後退, 右車輪=前進）
                target_v0 = -10.0   # ID 3
                target_v1 = -10.0   # ID 1 (モーターの取付向きを考慮して同符号で逆転)
            elif hat_x > 0:  # 十字キー「右」：その場で右旋回（左車輪=前進, 右車輪=後退）
                target_v0 = 10.0  # ID 3
                target_v1 = 10.0  # ID 1
            else:
                # 通常走行：左スティック＋右スティックによるスケーリング制御
                throttle = left_y * 10.0
                steer_sensitivity = 0.5 

                left_scale = 1.0 + (right_x * steer_sensitivity)   # ID 3 用
                right_scale = 1.0 - (right_x * steer_sensitivity)  # ID 1 用

                target_v0 = -throttle * left_scale   # ID 3
                target_v1 =  throttle * right_scale  # ID 1

            # --- 十字キー上下による GDS810 制御 (CAN ID 2) ---
            target_gds = 0.0
            if hat_y > 0:    # 上
                target_gds = 30.0
            elif hat_y < 0:  # 下
                target_gds = -30.0

            # 終了ボタン
            if joystick.get_button(8) or joystick.get_button(9):
                break

            # 現在値を目標値に向かって少しずつ近づける（スムージング）
            current_v0 += (target_v0 - current_v0) * ALPHA
            current_v1 += (target_v1 - current_v1) * ALPHA
            current_gds += (target_gds - current_gds) * ALPHA

            # コマンドを生成・送信 (ODrive IDは 3 と 1)
            cmd = f"V 3 {current_v0:.1f}\nV 1 {current_v1:.1f}\nG 2 {current_gds:.1f}\n"
            client_socket.sendall(cmd.encode('utf-8'))
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            client_socket.sendall(b"V 3 0.0\nV 1 0.0\nG 2 0.0\n")
        except:
            pass
        client_socket.close()
        pygame.quit()
        print("Disconnected.")

if __name__ == '__main__':
    main()