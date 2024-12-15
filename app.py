from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import cv2
import numpy as np

app = Flask(
    __name__,
    template_folder="website/templates",
    static_folder="website/static",
    static_url_path="/website/static",
)

# Dosya yükleme klasörü
UPLOAD_FOLDER = "website/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Yüklemeye izin verilen uzantılar
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Modeli yükle
model = tf.keras.models.load_model("model/resnet50/resnet50.keras")


# Dosya uzantısını kontrol et
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Ana sayfa
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Dosya kontrolü
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            prediction = predict_tumor(filepath)
            return render_template(
                "index.html", filename=filename, prediction=prediction
            )
    return render_template("index.html")


# Model tahmini yap
def predict_tumor(image_path):
    labels = ["glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"]

    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = np.reshape(img, [1, 224, 224, 3])

    # Predict the image
    prediction = model.predict(img)
    prediction = labels[np.argmax(prediction)]
    print("The MRI is : ", prediction)

    return prediction


# Resim gösterme
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "_main_":
    app.run(debug=True)
