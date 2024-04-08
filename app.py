from flask import Flask,render_template,request,redirect,url_for,session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,TextAreaField,SubmitField
from wtforms.validators import InputRequired
import jwt


app=Flask(__name__)

app.config['SECRET_KEY']='shivam'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.sqlite3'
db=SQLAlchemy(app)

#page creation

class signing(FlaskForm):
    email=EmailField("Email ;",validators=[InputRequired()])
    password=PasswordField('password',validators=[InputRequired()])
    submit=SubmitField('SignIn')

class registration(FlaskForm):
    name=StringField("Name :",validators=[InputRequired()])
    email=EmailField("Email ;",validators=[InputRequired()])
    password=PasswordField('password',validators=[InputRequired()])
    submit=SubmitField('SignUP')


class notes_update(FlaskForm):
    note_name=StringField('Note_Name',validators=[InputRequired()])
    description=TextAreaField('Description',validators=[InputRequired()])
    submit=SubmitField('submit')

#table creation 

class Userinfo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100),unique=True)
    role=db.Column(db.String(100))
    password=db.Column(db.String(100))

    def __repr__(self):
        return "{self.name}"

class Notes(db.Model):
    note_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,unique=True)
    note_name=db.Column(db.String(100))
    description=db.Column(db.String(200))
    
    def __repr__(self):
       return "{self.note_name}"





@app.route('/signin',methods=['POST'])
def signin():
    email = request.get_json().get("email")
    password = request.get_json().get("password")


    # // check if email and password != ""
    user = Userinfo.query.filter_by(email=email).first()
    if not user:
        return {"Error": "User not found"}
    
    if password != user.password:
        return {"Error": "password is in correct"}
    
    data = {"id": user.id, "email": user.email}

    token = jwt.encode(data, "secret", algorithm='HS256')
    print(token)

    return jsonify({"access_token": str(token)})
    


    

    # form=signing()
    # if form.validate_on_submit():
    #     email=form.email.data
    #     password=form.password.data
    #     verify=Userinfo.query.filter_by(email=email).filter_by(password=password).first()
    #     if verify:

    #         session['user_id']=verify.id

    #         return redirect(url_for('note'))
    #     else:
    #         return render_template('signin.html',form=form,error='please enter the correct credentials')
        
    # return render_template('signin.html',form=form)

@app.route("/get_notes", methods=["GET"])
def getNotes():
    headers = request.headers.get('Authorization')
    print(headers)

    tokenDecode = jwt.decode(headers, "stringsecret", algorithm='HS256')
    print(tokenDecode)

    notes = Notes.query.all()

    print(notes)
    return {"notes": notes}




@app.route('/register',methods=['GET','POST'])
def register():
    form=registration()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data
        user=Userinfo(name=name,email=email,role='Customer',password=password)
        db.session.add(user)
        db.session.commit()

        return f'{name} registeration sucessfully'
    return render_template('register.html',form=form)

@app.route('/note', methods=['GET','POST'])
def note():
   
    form=notes_update()
    note_name=form.note_name.data
    description=form.description.data

    if request.method=='POST':
        user_id = session.get('user_id')
        if user_id:
            user=Notes.query.get(user_id)
            user.note_name=note_name
            user.description=description
            db.session.commit()

            # user=Notes(user_id=user_id,note_name=note_name,description=description)
            # db.session.add(user)
            # db.session.commit()
            return "updated sucessfully "
        else:
            return "user not loged in"

    return render_template('notes.html',form=form)

if __name__=='__main__':
    with app.app_context():
        try:
            user=Userinfo(name='shivam',email='shivam123@gmail.com',role='Admin',password='1234')
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            pass
        db.create_all()
    app.run(debug=True)
