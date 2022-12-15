from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
# from yolov5 import detect
import cv2
import track
from pathlib import Path

from werkzeug.utils import secure_filename
app=Flask(__name__)
UPLOAD_FOLDER = Path(__file__).parent.resolve() / "static"
print(UPLOAD_FOLDER)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER/"uploads/"
app.config['RESULT_FOLDER'] = UPLOAD_FOLDER/"outputs/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','mp4'])
filename = ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        global filename
        filename = secure_filename(file.filename)
        print(os.getcwd())
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # After saving file, then save the first frame in outputs folder

        f= cv2.VideoCapture(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("Video path:",os.path.join(app.config['UPLOAD_FOLDER'], filename))
        success, image = f.read()
        if success:
            cv2.imwrite(os.path.join(app.config['RESULT_FOLDER'], "first_frame.jpg"), image)  # save frame as JPEG file
        return redirect(url_for(".createROI"))
        # print('upload_image filename: ' + filename)

    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route("/createROI")
def createROI():
    return render_template("drawROI.html",filename=url_for('static', filename='outputs/first_frame.jpg'))
@app.route('/result')
def result():
    filename = request.args["filename"]
    return render_template("result.html",filename=filename)

@app.route("/submitROI", methods=["POST"])
def submitROI():
    res = request.json
    f = open(os.path.join(UPLOAD_FOLDER, "ROI.txt"),"w")
    f.write("0,"+str((int(res["startX"]) + (int(res["w"])/2) )/1920)+","
                +str((int(res["startY"]) + (int(res["h"])/2) )/1080)+","
                +str(int(res["w"])/1920)+","
                +str(int(res["h"])/1080))
    return ('', 204)
@app.route("/run")
def run():
    # Yolov5 run here...:
    yolo_weight = "weights/best.pt"
    strong_sort_weight = "osnet_x0_25_msmt17.pt"
    opt = track.parse_opt(source=os.path.join(app.config['UPLOAD_FOLDER'], filename), yolo_weight=yolo_weight,
                          strong_sort_weight=strong_sort_weight)
    track.run(**vars(opt))
    # detect.run(source=app.config['UPLOAD_FOLDER']+"/"+filename)
    flash('Image successfully uploaded and displayed below')
    return redirect(url_for(".result", filename=filename))

@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/displayResult/<filename>')
def display_result_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='outputs/' + filename), code=301)

progressValue_ = 0
@app.route('/progressValue/<value>')
def progressValue(value):
    global progressValue_
    progressValue_=value
    print("Server Progress Value:",progressValue_)

    return ('',204)

@app.route("/getProgressValue")
def getProgressValue():
    return {"value":progressValue_}

if __name__ == "__main__":
    app.run(threaded=True)