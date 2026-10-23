import math
import socket
import time
import pygame

# ラズパイのIPアドレス
RASPBERRY_PI_IP = '192.168.137.2'
PORT = 5000

# アームの長さ
L1 = 45.0
L2 = 15.0

# サーボの制限範囲
MIN_BASE = 10.5
MAX_BASE = 120.5
MIN_TIP = 0.0
MAX_TIP = 270.0

# 初期位置の角度原点
INITIAL_BASE = 10.5
INITIAL_TIP = 215.0


def calculate_height(b_ang, t_ang):
  alpha1 = (b_ang - 10.5) * (math.pi / 180.0)
  alpha2 = alpha1 + (math.pi / 2.0) + ((t_ang - 215.0) * (math.pi / 180.0))
  y = L1 * math.sin(alpha1) + L2 * math.sin(alpha2)
  return y


def main():
  pygame.init()
  pygame.joystick.init()

  if pygame.joystick.get_count() == 0:
    print("エラー: ゲームパッド（JC-GP20X）が接続されていません。")
    return

  joystick = pygame.joystick.Joystick(0)
  joystick.init()
  print(f"接続されたコントローラー: {joystick.get_name()}")

  print("Connecting to Raspberry Pi...")
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((RASPBERRY_PI_IP, PORT))
  print("Connected!")

  INITIAL_HEIGHT = calculate_height(INITIAL_BASE, INITIAL_TIP)

  print("\n【操作アサイン (JC-GP20X)】")
  print("  [左スティック 上下] : 車輪 前後移動")
  print("  [右スティック 左右] : 車輪 ステアリング旋回")
  print("  [十字キー 左右]     : 超信地旋回")
  print("  [十字キー 上下]     : GDS810 速度制御")
  print("  [ Y ボタン ]        : 根元サーボ +2° (上)")
  print("  [ A ボタン ]        : 根元サーボ -2° (下)")
  print("  [ X ボタン ]        : 先サーボ   -2° (左)")
  print("  [ B ボタン ]        : 先サーボ   +2° (右)")
  print("  [START/BACK]        : 終了\n")

  # 状態変数
  current_v0 = 0.0
  current_v1 = 0.0
  current_gds = 0.0
  ALPHA = 0.2
  DEADZONE = 0.1

  current_base = INITIAL_BASE
  current_tip = INITIAL_TIP
  ANGLE_STEP = 2.0

  try:
    running = True
    while running:
      pygame.event.pump()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False

      # --- 1. 車輪・GDSの入力取得 ---
      left_y = joystick.get_axis(1)
      right_x = joystick.get_axis(2)

      if abs(left_y) < DEADZONE:
        left_y = 0.0
      if abs(right_x) < DEADZONE:
        right_x = 0.0

      hat_x, hat_y = 0, 0
      if joystick.get_numhats() > 0:
        hat_x, hat_y = joystick.get_hat(0)

      target_v0 = 0.0
      target_v1 = 0.0

      if hat_x < 0:
        target_v0 = -10.0
        target_v1 = -10.0
      elif hat_x > 0:
        target_v0 = 10.0
        target_v1 = 10.0
      else:
        throttle = left_y * 10.0
        steer_sensitivity = 0.5
        left_scale = 1.0 + (right_x * steer_sensitivity)
        right_scale = 1.0 - (right_x * steer_sensitivity)
        target_v0 = -throttle * left_scale
        target_v1 = throttle * right_scale

      target_gds = 0.0
      if hat_y > 0:
        target_gds = 30.0
      elif hat_y < 0:
        target_gds = -30.0

      # --- 2. カメラサーボの入力取得 (ABXYボタン) ---
      btn_a = joystick.get_button(0)
      btn_b = joystick.get_button(1)
      btn_x = joystick.get_button(2)
      btn_y = joystick.get_button(3)

      if joystick.get_button(8) or joystick.get_button(9):
        break

      target_base = current_base
      target_tip = current_tip

      if btn_y:
        target_base += ANGLE_STEP
      if btn_a:
        target_base -= ANGLE_STEP
      if btn_x:
        target_tip -= ANGLE_STEP
      if btn_b:
        target_tip += ANGLE_STEP

      # 範囲クランプ ＆ 高さガード
      if MIN_BASE <= target_base <= MAX_BASE and MIN_TIP <= target_tip <= MAX_TIP:
        new_height = calculate_height(target_base, target_tip)
        if new_height >= INITIAL_HEIGHT - 0.05:
          current_base = target_base
          current_tip = target_tip

      # --- 3. 制御値のスムージングとコマンド送信 ---
      current_v0 += (target_v0 - current_v0) * ALPHA
      current_v1 += (target_v1 - current_v1) * ALPHA
      current_gds += (target_gds - current_gds) * ALPHA

      # 車輪＋GDSコマンド ＋ サーボ制御コマンドを結合して送信
      cmd = (
          f"V 3 {current_v0:.1f}\nV 1 {current_v1:.1f}\nG 2"
          f" {current_gds:.1f}\nS 0 {current_base:.1f}\nS 1 {current_tip:.1f}\n"
      )
      client_socket.sendall(cmd.encode('utf-8'))

      time.sleep(0.08)

  except KeyboardInterrupt:
    pass
  finally:
    try:
      client_socket.sendall(
          b'V 3 0.0\nV 1 0.0\nG 2 0.0\n'
          + f'S 0 {INITIAL_BASE:.1f}\nS 1 {INITIAL_TIP:.1f}\n'.encode('utf-8')
      )
    except:
      pass
    client_socket.close()
    pygame.quit()
    print('Disconnected.')


if __name__ == '__main__':
  main()