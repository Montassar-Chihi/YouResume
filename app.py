from flask import Flask , render_template , url_for, request, redirect,session,jsonify,make_response
from  werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
from datetime import datetime, timedelta
from flask_mongoengine import MongoEngine
#from flask_session import Session

app = Flask(__name__)

app.config['MONGODB_DB'] = 'resume'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017

app.config['SECRET_KEY'] = 'ZU83RZ3CR31B055'

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/images/'

# Create database connection object
db = MongoEngine(app)

class User(db.Document):
      user_id= db.SequenceField(primary_key=True)
      email = db.StringField(required=True,unique=True)
      first_name = db.StringField(max_length=100)
      last_name = db.StringField(max_length=100)
      password = db.StringField(max_length=10000)
      picture = db.StringField(max_length=100)
      profession = db.StringField(max_length=100)
      linkedin = db.StringField(max_length=100)
      github = db.StringField(max_length=100)
      description = db.StringField(max_length=10000)
      location = db.StringField(max_length=100)
      
class Portfolio(db.Document):
      portfolio_id= db.SequenceField(primary_key=True)
      name = db.StringField(max_length=100)
      description = db.StringField(max_length=10000)
      url = db.StringField(max_length=100)
      user_id = db.ListField(db.ReferenceField(User))
      
class Education(db.Document):
      education_id= db.SequenceField(primary_key=True)
      place = db.StringField(max_length=100)
      started_at = db.DateField()
      finished_at = db.DateField()
      user_id = db.ListField(db.ReferenceField(User))
      
class Profession(db.Document):
      profession_id= db.SequenceField(primary_key=True)
      title = db.StringField(max_length=100)
      company = db.StringField(max_length=100)
      description = db.StringField(max_length=10000)
      started_at = db.DateField()
      finished_at = db.DateField()
      place = db.StringField(max_length=100)
      user_id = db.ListField(db.ReferenceField(User))

class Skill(db.Document):
      skill_id = db.SequenceField(primary_key=True)
      name = db.StringField(max_length=100)
      skill_type = db.StringField(max_length=100)
      user_id =  db.ListField(db.ReferenceField(User))


@app.route("/", methods = ["POST","GET"])
def index():
      if request.method == "POST":
      
            session["login"] = request.form.get("form-username")
            session["register"] = request.form.get("form-email")
                  
            if (session.get("login")):
                  session["email"] = request.form.get("form-username")
                  session["password"] = request.form.get("form-password")
                  user = User.objects(email=session["email"]).first()                  
                  if user == None: 
                        if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                              return make_response(
                                    'Could not verify',
                                    403,
                                    {'WWW-Authenticate' : 'Basic realm ="Email is wrong, please verify !!"'})
                        session["login_error"] = "Email is wrong, please verify !!"
                  else: 
                        if check_password_hash(user.password, session["password"]):
                              id = User.objects(email=session["email"]).only('user_id').first().user_id
                              session["logged"]= True
                              token = jwt.encode({
                                    'user_id': id,
                                    'exp' : datetime.utcnow() + timedelta(minutes = 300)
                              }, app.config['SECRET_KEY'], algorithm="HS256")
                              if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                                    return make_response(jsonify({'token' : token}), 200)
                              return redirect(url_for("profile",id=id))
                        else:
                              if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                                    return make_response(
                                                'Could not verify',
                                                403,
                                                {'WWW-Authenticate' : 'Basic realm ="Password is wrong, please verify !!"'}
                                          )
                              session["login_error"] = "Password is wrong, please verify !!"
                        
            if (session.get("register")):
                  session["name"] = request.form.get("form-first-name")
                  session["last"] = request.form.get("form-last-name")
                  session["email"] = request.form.get("form-email")
                  session["password"] = request.form.get("password")
                  try:
                        User(first_name=session["name"],last_name=session["last"],email=session["email"],password= generate_password_hash(session["password"])).save()
                        session["registered"]= True
                        id = User.objects(email=session["email"]).only('user_id').first().user_id
                        token = jwt.encode({
                              'user_id': id,
                              'exp' : datetime.utcnow() + timedelta(minutes = 300)
                        }, app.config['SECRET_KEY'], algorithm="HS256")
                        if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                              return make_response(jsonify({'token' : token.decode('UTF-8')}),201)
                        return redirect(url_for("profile",id=id))
                  except:
                        if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                              return make_response('Email already exists.', 202)
                        session["register_error"] = "Email already exists"
                              
      if (session.get("logged")):
            id = User.objects(email=session["email"]).only('user_id').first().user_id
            return redirect(url_for("profile",id=id))
      
      if (session.get("registered")):
            id = User.objects(email=session["email"]).only('user_id').first().user_id
            return redirect(url_for("profile",id=id))
            
      return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/profile/<id>/")
def profile(id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
      
      try:     
            user = User.objects(user_id=id,email = session["email"]).first()
            portfolio = Portfolio.objects(user_id=[id])
            education = Education.objects(user_id=[id])
            profession = Profession.objects(user_id=[id])
            skill = Skill.objects(user_id=[id])
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                        output = []
                        output.append({
                              'name' : user.first_name,
                              'last_name' : user.last_name,
                              'email' : user.email,
                              'profession' : user.profession,
                              'linkedin' : user.linkedin,
                              'github' : user.github,
                              'description' : user.description,
                              'location' : user.location
                        })
                        for portfolios in portfolio:
                              output.append({
                                    'name' : portfolios.name,
                                    'description' : portfolios.description,
                                    'url' : portfolios.url
                              })
                        for educations in education:
                              output.append({
                                    'place' : educations.place,
                                    'started_at' : educations.started_at,
                                    'finished_at' : educations.finished_at
                              })
                        for professions in profession:
                              output.append({
                                    'title' : professions.title,
                                    'company' : professions.company,
                                    'description' : professions.description,
                                    'started_at' : professions.started_at,
                                    'place' : professions.place,
                                    'finished_at' : professions.finished_at
                              })   
                        for skills in skill:
                              output.append({
                              'skill_id': skills.skill_id,
                              'name' : skills.name,
                              'skill_type' : skills.skill_type
                              })   
                        return make_response(jsonify({'data': output}),200)
            return render_template("profile.html",user=user,portfolio=portfolio,education=education,profession=profession,skill=skill)
      except:
            return make_response('Profile you asked for is Not Found! If you are manually inserting links please verify',404)
            
            
@app.route("/profile/<user_id>/portfolio/<portfolio_id>" , methods = ["DELETE","PUT","GET","POST"])
def portfolio(user_id,portfolio_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
      if request.method =="POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response("Method Not alowed !!", 405)
            else:
                  if "delete" in request.form :
                        Portfolio.objects(portfolio_id=portfolio_id).delete()
                        return redirect(url_for("profile",id=user_id))
                  if "update" in request.form :
                        name = request.form.get("name")
                        description = request.form.get("description")
                        url = request.form.get("url")
                        Portfolio.objects(portfolio_id=portfolio_id).update(name = name,description = description,url = url)
                        return redirect(url_for("profile",id=user_id))   
              
      if request.method == "DELETE":
            Portfolio.objects(portfolio_id=portfolio_id).delete()
            return make_response('Project Deleted', 200)
      
      if request.method == "PUT":
            name = request.json.get("name")
            description = request.json.get("description")
            url = request.json.get("url")
            Portfolio.objects(portfolio_id=portfolio_id).update(name = name,description = description,url = url)
            return make_response('Project Updated', 200)
      try:     
            session["delup_portfolio"] = True
            session["add_portfolio"]=False
            user = User.objects(user_id=user_id,email=session["email"]).first()
            portfolio = Portfolio.objects(portfolio_id=portfolio_id).first()
            if portfolio == None:
                  return make_response("Portfolio index is incorrect! please verify!",404)
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                         })
                  output.append({
                        'portfolio_id': portfolio.portfolio_id,
                        'name' : portfolio.name,
                        'description' : portfolio.description,
                        'url' : portfolio.url
                  })
                  return make_response(jsonify({'data': output}),200)
            return render_template("portfolio.html",user=user,portfolio=portfolio)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)
            

@app.route("/profile/<user_id>/portfolio" , methods = ["GET","POST"])
def add_portfolio(user_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method == "POST":
            if "add" in request.form:
                  name = request.form.get("name")
                  description = request.form.get("description")
                  url = request.form.get("url")
                  Portfolio(name=str(name),description=str(description),url=str(url),user_id=[user_id]).save()
                  return redirect(url_for("profile",id=user_id))
            name = request.json.get("name")
            description = request.json.get("description")
            url = request.json.get("url")
            Portfolio(name=str(name),description=str(description),url=str(url),user_id=[user_id]).save()
            return make_response("Project created",201)
            
      try:
            session["add_portfolio"] = True
            session["delup_portfolio"]=False
            user = User.objects(user_id=user_id,email=session["email"]).first()
            portfolio = Portfolio.objects(user_id=[user_id])
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                  })
                  for portfolios in portfolio:
                        output.append({
                              'portfolio_id': portfolios.portfolio_id,
                              'name' : portfolios.name,
                              'description' : portfolios.description,
                              'url' : portfolios.url
                        })
                  return make_response(jsonify({'data': output}),200)
            return render_template("portfolio.html",portfolio=portfolio,user=user)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

@app.route("/profile/<user_id>/profession/<profession_id>" , methods = ["DELETE","PUT","GET","POST"])
def profession(user_id,profession_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method =="POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response("Method Not alowed !!", 405)
            else:
                  if "delete" in request.form :
                        Profession.objects(profession_id=profession_id).delete()
                        return redirect(url_for("profile",id=user_id))
                  if "update" in request.form :
                        title = request.form.get("title")
                        company = request.form.get("company")
                        description = request.form.get("description")
                        started_at = request.form.get("started")
                        finished_at = request.form.get("finished")
                        place = request.form.get("place")
                        Profession.objects(profession_id=profession_id).update(title = title,company = company,description = description,
                                                                   started_at = started_at,finished_at = finished_at,place = place)
                        return redirect(url_for("profile",id=user_id))
      if request.method == "DELETE":
            Profession.objects(profession_id=profession_id).delete()
            return make_response('Profession Deleted', 200)
            
      if request.method == "PUT":
            title = request.json.get("title")
            company = request.json.get("company")
            description = request.json.get("description")
            started_at = request.json.get("started")
            finished_at = request.json.get("finished")
            place = request.json.get("place")
            Profession.objects(profession_id=profession_id).update(title = title,company = company,description = description,
                                                                   started_at = started_at,finished_at = finished_at,place = place)
            return make_response('Project Updated', 200)
      
      try:
            session["delup_profession"] = True
            session["add_profession"]=False
            user = User.objects(user_id=user_id,email=session["email"]).first()
            profession = Profession.objects(profession_id=profession_id).first()
            if profession == None:
                  return make_response("Profession index is incorrect! please verify!",404)
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                         })
                  output.append({
                        'profession_id': profession.profession_id,
                        'title' : profession.title,
                        'company' : profession.company,
                        'description' : profession.description,
                        'started_at' : profession.started_at,
                        'finished_at' : profession.finished_at,
                        'place' : profession.place
                  })
                  return make_response(jsonify({'data': output}),200)      
            return render_template("profession.html",user=user,profession=profession)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

@app.route("/profile/<user_id>/profession" , methods = ["POST","GET"])
def add_profession(user_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method == "POST":
            if "add" in request.form:
                  title = request.form.get("title")
                  company = request.form.get("company")
                  description = request.form.get("description")
                  started_at = request.form.get("started")
                  finished_at = request.form.get("finished")
                  place = request.form.get("place")
                  Profession(title=title,company=company,description=description,started_at=started_at,finished_at=finished_at,place=place,user_id=[user_id]).save()
                  return redirect(url_for("profile",id=user_id))
            title = request.json.get("title")
            company = request.json.get("company")
            description = request.json.get("description")
            started_at = request.json.get("started")
            finished_at = request.json.get("finished")
            place = request.json.get("place")
            Profession(title=title,company=company,description=description,started_at=started_at,finished_at=finished_at,place=place,user_id=[user_id]).save() 
            return make_response("Profession created",201)
            
            
      try:
            session["delup_profession"] = False
            session["add_profession"] = True
            user = User.objects(user_id=user_id,email=session["email"]).first()
            profession = Profession.objects(user_id=[user_id])
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                  })
                  for professions in profession:
                        output.append({
                              'profession_id': professions.profession_id,
                              'title' : professions.title,
                              'company' : professions.company,
                              'description' : professions.description,
                              'started_at' : professions.started_at,
                              'finished_at' : professions.finished_at,
                              'place' : professions.place
                        })
                  return make_response(jsonify({'data': output}),200)
            return render_template("profession.html",profession=profession,user=user)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

      
@app.route("/profile/<user_id>/education/<education_id>" , methods = ["DELETE","PUT","GET","POST"])
def education(user_id,education_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
      if request.method =="POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response("Method Not alowed !!", 405)
            else:
                  if "delete" in request.form : 
                        Education.objects(education_id=education_id).delete()
                        return redirect(url_for("profile",id=user_id))
                  if "update" in request.form :
                        place = request.form.get("palce")
                        started_at = request.form.get("started")
                        finished_at = request.form.get("finished")
                        Education.objects(education_id=education_id).update(place = place,started_at = started_at,finished_at = finished_at)
                        return redirect(url_for("profile",id=user_id))
      if request.method == "DELETE":
            Education.objects(education_id=education_id).delete()
            return make_response('Education Deleted', 200)
            
      if request.method == "PUT":
            place = request.json.get("place")
            started_at = request.json.get("started")
            finished_at = request.json.get("finished")
            Education.objects(education_id=education_id).update(place = place,started_at = started_at,finished_at = finished_at)
            return make_response('Education Updated', 200)
            
      try:
            session["delup_education"] = True
            session["add_education"] = False
            user = User.objects(user_id=user_id,email=session["email"]).first()
            education = Education.objects(education_id=education_id).first()
            if education == None:
                  return make_response("Education index is incorrect! please verify!",404)
            # For Postman Tests
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                         })
                  output.append({
                        'education_id': education.education_id,
                        'place' : education.place,
                        'started_at' : education.started_at,
                        'finished_at' : education.finished_at
                  })
                  return make_response(jsonify({'data': output}),200)      
            # For simple users
            return render_template("education.html",user=user,education=education)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)


@app.route("/profile/<user_id>/education" , methods = ["POST","GET"])
def add_education(user_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method == "POST":
            if "add" in request.form:
                  place = request.form.get("place")
                  started_at = request.form.get("started")
                  finished_at = request.form.get("finished")
                  Education(place=place,started_at=started_at,finished_at=finished_at,user_id=[user_id]).save()
                  return redirect(url_for("profile",id=user_id))
            place = request.json.get("place")
            started_at = request.json.get("started")
            finished_at = request.json.get("finished")
            Education(place=place,started_at=started_at,finished_at=finished_at,user_id=[user_id]).save()
            return ("education created",201)
            
      try:
            session["delup_education"] = False
            session["add_education"] = True
            user = User.objects(user_id=user_id,email=session["email"]).first()
            education = Education.objects(user_id=[user_id])
            # For Postman Tests
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                  })
                  for educations in education:
                        output.append({
                              'place' : educations.place,
                              'started_at' : educations.started_at,
                              'finished_at' : educations.finished_at
                        })
                  return make_response(jsonify({'data': output}),200)
            # For simple users
            return render_template("education.html",user=user,education=education)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

@app.route("/profile/<user_id>/personal" , methods = ["PUT","GET","POST"])
def personal(user_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method =="POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response("Method Not alowed !!", 405)
            else:
                  first_name = request.form.get("first_name")
                  last_name = request.form.get("last_name")
                  email = request.form.get("email")
                  password = request.form.get("password")
                  if 'picture' in request.files:
                        file = request.files['picture']
                        if file.filename == '':
                              pass
                        else:
                              filename = file.filename
                              file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                              picture = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                  profession = request.form.get("profession")
                  linkedin = request.form.get("linkedin")
                  github = request.form.get("github")
                  description = request.form.get("description")
                  location = request.form.get("location")
                  User.objects(user_id=user_id).update(first_name = first_name,last_name = last_name,email = email,
                                                              password= generate_password_hash(password),picture = picture,profession = profession,
                                                              linkedin = linkedin,github = github,description=description,
                                                              location=location)
                  return redirect(url_for("profile",id=user_id))
      
      if request.method == "PUT":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  first_name = request.json.get("first_name")
                  last_name = request.json.get("last_name")
                  email = request.json.get("email")
                  password = request.json.get("password")
                  profession = request.json.get("profession")
                  linkedin = request.json.get("linkedin")
                  github = request.json.get("github")
                  description = request.json.get("description")
                  location = request.json.get("location")
                  if password != None:
                        User.objects(user_id=user_id).update(first_name = first_name,last_name = last_name,email = email,
                                                             password= generate_password_hash(password),profession = profession,
                                                              linkedin = linkedin,github = github,description=description,
                                                              location=location)
                  else:
                        User.objects(user_id=user_id).update(first_name = first_name,last_name = last_name,email = email,
                                                             profession = profession,linkedin = linkedin,github = github,
                                                             description=description,location=location)
                  return ("user updated",200)
            
      try:
            user = User.objects(user_id=user_id,email=session["email"]).first()
            # For Postman Tests
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name,
                        'email' : user.email,
                        'password' : user.password,
                        'profession' : user.profession,
                        'linkedin' : user.linkedin,
                        'github' : user.github,
                        'description' : user.description,
                        'location' : user.location
                  })
                  return make_response(jsonify({'data': output}),200)
            # For simple users
            return render_template("personal.html",user=user)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

@app.route("/profile/<user_id>/skill/<skill_id>" , methods = ["DELETE","PUT","GET","POST"])
def skill(user_id,skill_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
      if request.method =="POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response("Method Not alowed !!", 405)
            else:
                  if "delete" in request.form : 
                        Skill.objects(skill_id=skill_id).delete()
                        return redirect(url_for("profile",id=user_id))
                  if "update" in request.form :
                        name = request.form.get("name")
                        skill_type = request.form.get("skill_type")
                        Skill.objects(skill_id=skill_id).update(name = name,skill_type = skill_type)
                        return redirect(url_for("profile",id=user_id))
                  
      if request.method == "DELETE":
            Skill.objects(skill_id=skill_id).delete()
            return make_response('skill Deleted', 200)
        
      if request.method == "PUT":
            name = request.json.get("name")
            skill_type = request.json.get("skill_type")
            Skill.objects(skill_id=skill_id).update(name = name,skill_type = skill_type)
            return make_response('skill Updated', 200)
            
      try:
            session["delup_skill"] = True
            session["add_skill"] = False
            user = User.objects(user_id=user_id,email=session["email"]).first()
            skill = Skill.objects(skill_id=skill_id).first()
            if skill == None:
                  return make_response("Skill index is incorrect! please verify!",404)
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                         })
                  output.append({
                        'skill_id': skill.skill_id,
                        'name' : skill.name,
                        'skill_type' : skill.skill_type
                  })
                  return make_response(jsonify({'data': output}),200)  
            return render_template("skill.html",user=user,skill=skill)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)


@app.route("/profile/<user_id>/skill" , methods = ["POST","GET"])
def add_skill(user_id):
      token = None
      # jwt is passed in the request header
      if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # return 401 if token is not passed
      if not token:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is missing !! Please login/register to get access'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In to use the website' 
                  session["register_error"] = 'Please Sign Up to use the website' 
                  return redirect(url_for("index"))
      try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
            user = User.objects(user_id = data["user_id"],email = session["email"]).only('user_id').first()
      except:
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  return make_response(jsonify({'message' : 'Token is invalid !!'}), 403)
            if (not session.get("login") and not session.get("register")):
                  session["login_error"] = 'Please Log In with the right information to use the website' 
                  session["register_error"] = 'Please Sign UP with the right information to use the website' 
                  return redirect(url_for("index"))
            
            
      if request.method == "POST":
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  name = request.json.get("name")
                  skill_type = request.json.get("skill_type")
                  Skill(name=name,skill_type=skill_type,user_id=[user_id]).save()
                  return ("skill created",201)
            name = request.form.get("name")
            skill_type = request.form.get("skill_type")
            Skill(name=name,skill_type=skill_type,user_id=[user_id]).save()
            return redirect(url_for("profile",id=user_id))
      try:
            session["delup_skill"] = False
            session["add_skill"] = True
            user = User.objects(user_id=user_id,email=session["email"]).first()
            skill = Skill.objects(user_id=[user_id])
            # For Postman Tests
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                  output = []
                  output.append({
                        'name' : user.first_name,
                        'last_name' : user.last_name
                  })
                  for skills in skill:
                        output.append({
                        'skill_id': skills.skill_id,
                        'name' : skills.name,
                        'skill_type' : skills.skill_type
                        })
                  return make_response(jsonify({'data': output}),200)
            # For simple users
            return render_template("skill.html",user=user,skill=skill)
      except:
            return make_response('Page you asked for is Not Found! If you are manually inserting links please verify',404)

@app.route('/user/<id>/')
def user(id):
      try:     
            user = User.objects(user_id=id).first()
            portfolio = Portfolio.objects(user_id=[id])
            education = Education.objects(user_id=[id])
            profession = Profession.objects(user_id=[id])
            skill = Skill.objects(user_id=[id])
            if request.headers.get("User-Agent") == "PostmanRuntime/7.29.0":
                        output = []
                        output.append({
                              'name' : user.first_name,
                              'last_name' : user.last_name,
                              'email' : user.email,
                              'profession' : user.profession,
                              'linkedin' : user.linkedin,
                              'github' : user.github,
                              'description' : user.description,
                              'location' : user.location
                        })
                        for portfolios in portfolio:
                              output.append({
                                    'name' : portfolios.name,
                                    'description' : portfolios.description,
                                    'url' : portfolios.url
                              })
                        for educations in education:
                              output.append({
                                    'place' : educations.place,
                                    'started_at' : educations.started_at,
                                    'finished_at' : educations.finished_at
                              })
                        for professions in profession:
                              output.append({
                                    'title' : professions.title,
                                    'company' : professions.company,
                                    'description' : professions.description,
                                    'started_at' : professions.started_at,
                                    'place' : professions.place,
                                    'finished_at' : professions.finished_at
                              })   
                        for skills in skill:
                              output.append({
                              'skill_id': skills.skill_id,
                              'name' : skills.name,
                              'skill_type' : skills.skill_type
                              })   
                        return make_response(jsonify({'data': output}),200)
            return render_template("user.html",user=user,portfolio=portfolio,education=education,profession=profession,skill=skill)
      except:
            return make_response('User you asked for is Not Found! If you are manually inserting links please verify',404)



if __name__ == "__main__":
      app.run(debug=True)