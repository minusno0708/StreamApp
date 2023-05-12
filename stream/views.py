import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views import View

from stream.detect.detect import detect

# ストリーミング画像・映像を表示するview
class IndexView(View):
    def get(self, request):
        return render(request, 'stream/index.html', {})

# ストリーミング画像を定期的に返却するview
def video_feed_view():
    video = generate_frame()
    return lambda _: StreamingHttpResponse(video, content_type='multipart/x-mixed-replace; boundary=frame')


# フレーム生成・返却する処理
def generate_frame():
    capture = cv2.VideoCapture(0)  # USBカメラから

    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # カメラからフレーム画像を取得
        ret, frame = capture.read()
        if not ret:
            print("Failed to read frame.")
            break

        conf, frame = detect(frame)

        # フレーム画像バイナリに変換
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()

        if conf:
            save_frame(frame)

        # フレーム画像のバイナリデータをユーザーに送付する
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    capture.release()

def save_frame(frame):
    cv2.imwrite("images/stream.jpg", frame)