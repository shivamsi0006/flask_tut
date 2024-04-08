from flask import Flask,request,jsonify,session
from flask_sqlalchemy import SQLAlchemy
import jwt

app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///db.sqlite3"
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.Integer)
    role=db.Column(db.String(100))
    def __repr__(self):
        return f"{self.name}"

class Notes(db.Model):
    note_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"))
    note_name=db.Column(db.String)
    description=db.Column(db.Text)
    user=db.relationship("User",backref=db.backref('notes',lazy=True))
    def __repr__(self):
        return f"{self.note_id}"


def token_decodee():
    header=request.headers.get("Authorization")
    token_decode=jwt.decode(header,"stringsecret",algorithms="HS256")
    return token_decode

@app.route('/')
def home():
    return "home page"


@app.route('/register',methods=["POST"])
def register():
    name=request.get_json().get("name")
    email=request.get_json().get("email")
    password=request.get_json().get("password")
    exist=User.query.filter_by(email=email).first()
    if exist:
        return jsonify({"message":"user already exist"})
    new_user=User(name=name,email=email,password=password,role="Customer")
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"user Updted Sucessfully"})


@app.route('/login',methods=["POST"])
def login():
    email=request.get_json().get("email")
    password=request.get_json().get("password")
    exist=User.query.filter_by(email=email).first()
    if not exist:
        return jsonify({"message":"email  does not exist"})
    if password!=exist.password:
        return jsonify({"message":"password not match"})
    data={"role":exist.role,"id":exist.id}
    token=jwt.encode(data,"stringsecret",algorithm="HS256")
    # session["token"]=token_decodee()
    # print(session["token"])
    return jsonify({"acces_token":token})

@app.route('/createnote',methods=["POST"])
def createnote():
    token_decode= token_decodee()
    user_id=token_decode["id"]
    
    note_name=request.get_json().get("note_name")
    description=request.get_json().get("description")
    create_note=Notes(note_name=note_name,description=description,user_id=user_id)
    db.session.add(create_note)
    db.session.commit()

    return jsonify({"message":"note created sucessfully"})

@app.route('/listnote',methods=["GET"])
def listnote():
    token_decode= token_decodee()
    user_id=token_decode["id"]
    exist=Notes.query.filter_by(user_id=user_id).all()
    idlist=[str(i) for i in exist]
    if exist==[]:
        return jsonify({"message": "no note available "})
    return jsonify({"message":"availabe"})
    

@app.route('/updatenote/<int:id>',methods=["PUT"])
def updatenote(id):
    token_decode= token_decodee()
    user_id=token_decode["id"]
    exist=Notes.query.filter_by(user_id=user_id).all()
    idlist=[str(i) for i in exist]
    if exist==[]:
        return jsonify({"message": "no note available "})
    if str(id) in idlist:
    
        query_id=Notes.query.filter_by(note_id=id).first()

        query_id.note_name=request.get_json().get("note_name")
        query_id.description=request.get_json().get("description")
        db.session.commit()
        return jsonify({"message":"update sucessfully"})
     

    return jsonify({"message":"only own notes can be updated"})
    
    


@app.route('/deletenote/<int:id>',methods=["DELETE"])
def deletenote(id):
    token_decode=token_decodee()
    role=token_decode["role"]
    if role =="admin":
        delete_note=Notes.query.filter_by(note_id=id).first()
        db.session.delete(delete_note)
        db.session.commit()
        return jsonify({"message":"delete note sucessfully"})
    return jsonify({"message":"only admin can delete the note"})


# @app.route('/logout'):
# def logout():
#     if ses


if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)