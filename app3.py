from  flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
import json



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite3'

db=SQLAlchemy(app)


class Info(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    userId=db.Column(db.Integer )
    title=db.Column(db.String(250))
    body=db.Column(db.Text)
    
    def __repr__(self):
        return f"{self.id}"



# response_api=requests.get('https://jsonplaceholder.typicode.com/posts/')
# data=response_api.text
# parse=json.loads(data)
# print(parse[0])

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)