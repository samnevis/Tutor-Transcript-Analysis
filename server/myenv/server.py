from process import both
import os
from flask import Flask, request


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

members_list = []

@app.route("/members", methods=["GET"])
def members():  
    return {"members": members_list}

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files['file']
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    with open(filename, 'r', encoding='utf-8') as f:
        json_object = both(f)
        json_object["filename"] = file.filename
    
    members_list.insert(0, json_object)
    if os.path.exists(filename):
            os.remove(filename)
    return {"members": members_list}, 201


if __name__ == "__main__":
    app.run(debug=True)




    
    


