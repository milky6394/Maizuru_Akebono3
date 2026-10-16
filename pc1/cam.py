import cv2

# UDP 5000番ポートで届く RTP/MJPEG ストリームの仕様を FFmpeg に伝える設定 (SDP)
sdp_data = """c=IN IP4 0.0.0.0
m=video 5000 RTP/AVP 26
a=rtpmap:26 JPEG/90000
"""

# OpenCV (FFmpeg) に SDP データを直接渡す設定
# protocol_whitelist に rtp,udp,file を指定
pipeline_url = f"data:application/sdp,{sdp_data}"

print("OpenCV (FFmpeg) で UDP/RTP ストリームを受信待機中... ('q' キーで終了)")

# FFmpegバックエンドで開く
cap = cv2.VideoCapture(pipeline_url, cv2.CAP_FFMPEG)

# 受信バッファの遅延を抑える設定
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print(
        "エラー: ストリームを開けませんでした。ファイアウォールまたはポート5000を確認してください。"
    )
    exit()

while True:
    ret, frame = cap.read()
    if ret and frame is not None:
        cv2.imshow("UDP Low Latency 1080p (FFmpeg)", frame)
    else:
        # パケットが届いていない場合は少し待機
        pass

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()