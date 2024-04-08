
# file uploading 



from flask import Flask,request,jsonify

import os
app=Flask("__name__")

@app.route("/fileuploading",methods=["POST"])
def fileuploading():
    upload_file=request.files["upload_file"]
    location=os.path.join('uploads/',upload_file.filename)
    upload_file.save(location)
    return jsonify({"file": "upload succesfully"})



if __name__=="__main__":   
    app.run(debug=True)