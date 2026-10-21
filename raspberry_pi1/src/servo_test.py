import time
from adafruit_servokit import ServoKit

# 16チャンネル用のServoKitオブジェクトを作成（I2Cアドレスはデフォルトの0x40）
kit = ServoKit(channels=16)

# SG90などの一般的なマイクロサーボの場合、パルス幅の調整を行うことで可動域が安定します
# 必要に応じて min_pulse / max_pulse を調整してください（標準: 500〜2500μs）
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)

print("サーボモーター動作開始")

try:
    while True:
        print("0度")
        kit.servo[0].angle = 0
        time.sleep(2)

        print("90度")
        kit.servo[0].angle = 90
        time.sleep(2)

        print("180度")
        kit.servo[0].angle = 180
        time.sleep(2)

        print("0度")
        kit.servo[1].angle = 0
        time.sleep(2)

        print("90度")
        kit.servo[1].angle = 90
        time.sleep(2)

        print("180度")
        kit.servo[1].angle = 180
        time.sleep(2)

except KeyboardInterrupt:
    print("\n終了します")
