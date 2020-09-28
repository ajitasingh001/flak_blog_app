from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from werkzeug.utils import secure_filename
from routes.get_api import get_api_blueprint

import os
import json
import traceback
import math
with open('./config/config.json') as jfile:
    param = json.load(jfile)["param"]
local_server =param['local_server']
app=Flask(__name__)
app.register_blueprint(get_api_blueprint)
app.config['UPLOAD_FOLDER']=param['upload_file']
app.config.update(MAIL_SERVER = 'smtp.gmail.com',MAIL_PORT='465',MAIL_USE_SSL =True,
                  MAIL_USERNAME ='ajeeta.krlprogrammer@gmail.com',
                  MAIL_PASSWORD='singh@1992')
#app.config[]=param['upload_file']
mail = Mail(app)
#secret key
app.secret_key = 'the random string'
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['prod_uri']
db = SQLAlchemy(app)
class contacts(db.Model):
    '''
     sno, name phone_num, msg, date, email
     '''
    Sno = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(80),nullable = False)
    Phone_number = db.Column(db.Integer,nullable = False)
    Msg =db.Column(db.String(80),nullable =False)
    Date =db.Column(db.String(80),nullable=True)
    Email=db.Column(db.String(80),nullable =False)

class posts(db.Model):
    '''Sno	Tittle	Conent	Date	'''
    Sno = db.Column(db.Integer, primary_key=True)
    Tittle = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    Conent = db.Column(db.String(120), nullable=False)
    Image = db.Column(db.String(120), nullable=True)
    Date = db.Column(db.String(12), nullable=True)


@app.route("/",methods=['GET'])
def home():
    query_result=posts.query.filter_by().all()
    print(len(query_result))
    last = math.floor(len(query_result)/2)
    page = request.args.get('page')
    print(type(page))
    if (not str(page).isnumeric()):
        page=1
    else:
        page = int(page)
    post = query_result[2 * page-2:2*page]
    print(page)
    print(post)
    if page ==1:
        prev="#"
        next="/?page="+str(page+1)
    elif page==last:
        prev ="/?page="+str(page-1)
        next ="#"
    else:
        prev ="/?page="+str(page-1)
        next ="/?page="+str(page+1)

    return render_template('index.html', param=param, posts=post,prev=prev,next=next)
@app.route("/about")
def about():
    return render_template('about.html',param=param)
@app.route("/contact",methods =['GET','POST'])
def contact():
    '''add entery ti the datadbase'''
    if(request.method =='POST'):
        name =request.form.get('name')
        phonenumber =request.form.get('phonenumber')
        message = request.form.get('message')
        email=request.form.get('email')
        entry = contacts(Name=name,Phone_number=phonenumber,Msg=message,Date =datetime.now(),Email =email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=['ajeeta.krlprorammer@gmail.com'],
                          body=message + "\n" + phonenumber
                          )
    return render_template('contact.html',param=param)
@app.route("/post/<var>",methods=['GET'])
def post_route(var):
    try:
        print(var)
        print("SELECT * FROM posts where slug ='{}'".format(str(var)))
        query_result= db.session.execute("SELECT * FROM posts where slug ='{}'".format(str(var)))

        print("hi how",query_result)
        # print("query_result",[r for r in query_result])
        print(type(query_result))
        for n in query_result:
            print("hjhjhj",n)
            return render_template('post.html',param=param,postss =n)
    except:
        print(str(traceback.format_exc()))
        return "OT OK"
@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    query_result = posts.query.all()
    if('user' in session and session['user']==param['admin_user']):
        return render_template('dashboard.html',query_result =query_result)
    if request.method=='POST':
        username =request.form.get('username')
        userpass =request.form.get('password')
        if(username==param['admin_user'] and userpass ==param['admin_password']):
            session['user']=username
            render_template('dashboard.html',query_result =query_result)
    return render_template('login.html',param=param)
@app.route("/addedit/<Sno>",methods=['GET','POST'])
def addedit(Sno):
    print(type(Sno))

    '''add entery ti the datadbase'''
    if (request.method == 'POST'):
        Tittle = request.form.get('Tittle')
        slug = request.form.get('slug')
        Conent = request.form.get('Conent')
        Image = request.form.get('Image')
        if Sno=='0':
            entry = posts(Tittle=Tittle,slug=slug,Conent=Conent,Image=Image,Date=datetime.now())
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            post = posts.query.filter_by(Sno=Sno).first()
            post.Tittle=Tittle
            post.slug=slug
            post.Conent=Conent
            post.Image=Image
            db.session.commit()
            return redirect(url_for('dashboard'))
    post = posts.query.filter_by(Sno=Sno).first()
    print(post)
    return render_template('addedit.html',param=param,post=post)
@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user']==param['admin_user']:
        if request.method=='POST':
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "uploaded succesfully"
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect(url_for('dashboard'))
@app.route("/delete/<Sno>")
def delete(Sno):
    post =posts.query.filter_by(Sno=Sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('dashboard')

app.run(debug=True)