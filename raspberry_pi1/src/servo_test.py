import math
import sys
import termios
import time
import tty
from adafruit_servokit import ServoKit

# 16チャンネル用のServoKitオブジェクトを作成
kit = ServoKit(channels=16)

# 270度サーボに対応させるため、可動範囲を270度に設定
kit.servo[0].actuation_range = 270
kit.servo[1].actuation_range = 270

kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)

# 【重要】アームの長さの設定（単位はcmなど任意。比率の計算に使います）
L1 = 45.0  # 根元の腕の長さ
L2 = 15.0  # 先の腕の長さ

# ユーザー指定の初期原点
INITIAL_BASE = 10.5  # 根元 (Servo 0)
INITIAL_TIP = 215.0  # 先 (Servo 1)


# 順運動学を用いて先端の高さ (Y座標) を計算する関数
def calculate_height(b_ang, t_ang):
  # 根元サーボ10.5度を水平(0rad)とする
  alpha1 = (b_ang - 10.5) * (math.pi / 180.0)
  # 先サーボ215度を「根元アームに対して垂直上向き」とする基準からのオフセット
  alpha2 = alpha1 + (math.pi / 2.0) + ((t_ang - 215.0) * (math.pi / 180.0))

  # 高さ Y の計算
  y = L1 * math.sin(alpha1) + L2 * math.sin(alpha2)
  return y


# 起動時の初期原点の高さを計算（これが下限の高さになる）
INITIAL_HEIGHT = calculate_height(INITIAL_BASE, INITIAL_TIP)

# 現在の角度を初期値に設定
base_angle = INITIAL_BASE
tip_angle = INITIAL_TIP

# 制限の定義
MIN_BASE = 10.5
MAX_BASE = 120.5
MIN_TIP = 0.0
MAX_TIP = 270.0


def set_angles(b_ang, t_ang):
  global base_angle, tip_angle

  # 1. 根元サーボの範囲制限 (10.5〜120.5度)
  if not (MIN_BASE <= b_ang <= MAX_BASE):
    print(
        f"【警告】根元サーボが制限範囲外です ({b_ang:.1f}度)。許可範囲:"
        f" {MIN_BASE}〜{MAX_BASE}°"
    )
    return False

  # 先サーボの範囲制限 (0〜270度)
  if not (MIN_TIP <= t_ang <= MAX_TIP):
    print(f"【警告】先サーボが範囲外です ({t_ang:.1f}度)")
    return False

  # 2. 順運動学による高さチェック（初期位置より下になっていないか）
  new_height = calculate_height(b_ang, t_ang)
  # 浮動小数点の誤差を考慮して少し余裕を持たせる
  if new_height < INITIAL_HEIGHT - 0.05:
    print(
        f"【警告】初期位置より下になるため拒否されました (移動先高さ:"
        f" {new_height:.2f} < 初期高さ: {INITIAL_HEIGHT:.2f})"
    )
    return False

  # すべてのチェックをクリアしたらモーターを動かす
  base_angle = b_ang
  tip_angle = t_ang

  kit.servo[0].angle = base_angle
  kit.servo[1].angle = tip_angle
  print(
      f"移動成功 -> 根元: {base_angle:5.1f}° | 先: {tip_angle:5.1f}° | 高さ(Y):"
      f" {new_height:5.2f}"
  )
  return True


# 起動時に原点へ移動
print("--- サーボ制御プログラム（制限・高さガード付き）開始 ---")
print(f"初期原点の高さ基準 (Y): {INITIAL_HEIGHT:.2f}")
print("初期原点へ移動します...")
set_angles(INITIAL_BASE, INITIAL_TIP)

print("\n【操作方法】")
print("  [ ↑ ] 根元 (Servo 0)  +10°")
print("  [ ↓ ] 根元 (Servo 0)  -10°")
print("  [ → ] 先   (Servo 1)  +10°")
print("  [ ← ] 先   (Servo 1)  -10°")
print("  [ q ] 終了\n")


def get_key():
  """Linuxのターミナルで1文字を取得する関数"""
  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  try:
    tty.setraw(fd)
    ch = sys.stdin.read(1)
    if ch == "\x1b":  # エスケープシーケンス
      ch2 = sys.stdin.read(1)
      ch3 = sys.stdin.read(1)
      if ch2 == "[":
        if ch3 == "A":
          return "UP"
        elif ch3 == "B":
          return "DOWN"
        elif ch3 == "C":
          return "RIGHT"
        elif ch3 == "D":
          return "LEFT"
    elif ch == "q" or ch == "Q":
      return "QUIT"
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return None


try:
  while True:
    key = get_key()
    if key == "UP":
      set_angles(base_angle + 10, tip_angle)
    elif key == "DOWN":
      set_angles(base_angle - 10, tip_angle)
    elif key == "RIGHT":
      set_angles(base_angle, tip_angle + 10)
    elif key == "LEFT":
      set_angles(base_angle, tip_angle - 10)
    elif key == "QUIT":
      print("\n終了します")
      break
except KeyboardInterrupt:
  print("\n終了します")