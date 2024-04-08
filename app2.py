from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite://info.sqlite3"

db=SQLAlchemy(app)

class User(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(250))
    role=db.Column(db.String(200))
    email=db.Column(db.String(250),unique=True)
    password=db.Column(db.String(200))

    def __repr__(self):
        return f"{self.name}"
    
class Notes(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    notes_name=db.Column(db.String(250))
    description=db.Column(db.Text)
    user=db.relationship('User',backref=db.backref('notes',lazy=True))

    def __repr__(self):
        return f"{self.user_id}"
    

def token_decodee():
    header=request.headers.get("Authorization")
    token_decode=jwt.decode(header,"stringsecret",algorithms="HS256")
    return token_decode

@app.route('/')
def home():

    return jsonify({"message":"HOME PAGE"})

@app.route('/register',methods=["POST"])
def register():
    name=request.get_json().get('name')
    email=request.get_json().get('email')
    password=request.get_json().get('password')
    exist_user=User.query.filter_by(email=email).first()
    if exist_user:
        return jsonify({"message":"user already exist"})
    new_user=User(name=name,email=email,password=password,role="customer")
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"user updated sucessfully"})

@app.route("/login",methods=['POST'])
def login():

    email=request.get_json().get('email')
    password=request.get_json().get("password")

    verify=User.query.filter_by(email=email).first()
    if not verify:
        return jsonify({"message":"user email does not exist"})
    if password!=verify.password:
        return jsonify({"message":"user password does not exist"})
    print(verify.id)
    data={"role":verify.role,"id":verify.id}
   
    token=jwt.encode(data,"stringsecret",algorithm='HS256')

    return jsonify({"access_token":str(token)})


@app.route('/createnote',methods=["POST"])
def createnote():
    token_decode=token_decodee()
    notes_name=request.get_json().get('notes_name')
    description=request.get_json().get('description')

    new_note=Notes(notes_name=notes_name,description=description,user_id=token_decode["id"])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message":"note created sucessfully"})


@app.route('/listnotes')
def notes():
    token_decode=token_decodee()
    if token_decode['role']:
        
        notes=Notes.query.all()
        print(notes)
        return jsonify({"message":str(notes)})
    
    return jsonify({"message":"not authorized"})


@app.route('/updatenote/<int:id>',methods=['PUT'])
def updatenote(id):
    token_decode=token_decodee()
    user_id=token_decode["id"]
    verify=Notes.query.filter_by(user_id=user_id).all()
    note_ids = [note.id for note in verify]
    print(note_ids)
    if id in note_ids:
        query=Notes.query.filter_by(id=id).first()
        if query:
            
            query.id=id
            query.notes_name=request.get_json().get("notes_name")
            query.description=request.get_json().get("description")
            db.session.commit()
            return jsonify({"message":"note updated sucessfully"})
            
        return jsonify({"message":"no need to update "})
    return jsonify({"message":"user list not found"})

@app.route("/deletenote/<int:id>",methods=["DELETE"])
def deletenote(id):
    token_decode=token_decodee()
    if token_decode["role"]!="admin":
        return jsonify({"message":"only admin can perform operation"})
   
    user=Notes.query.filter_by(id=id).first()
    if not user:
        return jsonify({"message":"user notes does not exist"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user notes deleted sucess fully"})

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)