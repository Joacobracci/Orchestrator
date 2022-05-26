from datetime import date
import json
from socket import SocketIO, socket
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
    user_logged_in,
)
from numpy import broadcast
from werkzeug.security import check_password_hash
#from functions.function_jwt import write_token
from flask_socketio import SocketIO,send



app = Flask(__name__)
csrf = CSRFProtect(app)
socketio = SocketIO(app)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://root:root@localhost/sys"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

############################### MODELS FROM DB ###############################
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(102))
    company = db.Column(db.String(45))
    robots = db.relationship("Robot", backref="user", lazy="select")
    status = db.relationship("Status", backref="user", lazy="select", uselist=False)
    reports = db.relationship("Report", backref="user", lazy="select")

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


class Robot(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    robotname = db.Column(db.String(45))
    description = db.Column(db.String(45))
    status = db.Column(db.String(45))
    path = db.Column(db.String(90))
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    reports = db.relationship("Report", backref="robot", lazy="select")


class Report(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    reportname = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    robot_id = db.Column(db.Integer, db.ForeignKey("robot.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    logs = db.relationship("Log", backref="report", lazy="select")

    def __init__(self, reportname , date, robot_id, user_id):
        self.reportname = reportname
        self.date = date   
        self.robot_id = robot_id  
        self.user_id = user_id   

class Log(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    flow = db.Column(db.String(45))
    message = db.Column(db.String(45))
    status = db.Column(db.String(45))
    time = db.Column(db.String(45))
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"))

    def __init__(self, flow , message, status, time,report_id):
        self.flow = flow
        self.message = message   
        self.status = status  
        self.time = time   
        self.report_id = report_id   

class Status(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    currentStatus = db.Column(db.String(5))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, currentStatus):
        self.currentStatus = currentStatus

############################### MODELS FROM DB ###############################

############################### SQUEMAS FROM DB ###############################

class ReportSchema(ma.Schema):
    class Meta:
        fields =('id' , 'reportname' , 'date' , 'robot_id' , 'user_id')

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

class LogSchema(ma.Schema):
    class Meta:
        fields =('id' , 'flow' , 'message' , 'status' , 'time','report_id')

log_schema = LogSchema()
logs_schema = LogSchema(many=True)


class StatusSchema(ma.Schema):
    class Meta:
        fields = ("id", "currentStatus", "user_id")


status_schema = StatusSchema()

############################### SQUEMAS FROM DB ###############################

############################### LOGIN MANAGER ###############################

login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return User.query.get(int(id))

############################### LOGIN MANAGER ###############################

############################### ROUTES ###############################

@app.route("/api/getStatus", methods=["GET"])
def get_status():
    actualstatus = Status.query.get(1)
    return status_schema.jsonify(actualstatus)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()
        if user:            
            if User.check_password(user.password , request.form['password']) :
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Contraseña incorrecta...")
                return render_template("auth/login.html")
        else:
            flash("Usuario no encontrado...")
            return render_template("auth/login.html")
    else:
         return render_template("auth/login.html")

#    if request.method == "POST":
#        user = User(0, request.form["username"], request.form["password"])
#        logged_user = ModelUser.login(db, user)
#        session["id"] = logged_user.id
#        if logged_user != None:
#            if logged_user.password:
#                login_user(logged_user)
#                return redirect(url_for("home"))
#            else:
#                flash("Contraseña invalida...")
#                return render_template("auth/login.html")
#        else:
#            flash("Usuario no encontrado...")
#            return render_template("auth/login.html")
#    else:
#        return render_template("auth/login.html")

@app.route("/logout")
def logout():
    logout_user
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/robots")
@login_required
def robots():


    headings = (
         "#",
         "Robot Name",
         "Description",
         "Orden",
         "Reports",
     )

    # robots = Robot.query.all()
    # output = []
    # for robot in robots:
    #     if robot.user_id == session["id"]:

    #         robots_data = {}
    #         robots_data["id"] = robot.id
    #         robots_data["robotname"] = robot.robotname
    #         robots_data["description"] = robot.description
    #         robots_data["status"] = robot.status
    #         output.append(robots_data)

    return render_template("robots.html" , headings=headings) #headings=headings, data=output)


@app.route("/reports")
@login_required
def reports():    
    headings = (
         "#",
         "Report Name",
         "Date",
         "Robot",
         "Logs",
     )
    return render_template("reports.html",  headings=headings)

@app.route("/report/<int:id>")
@login_required
def report(id):
    headings = (
         "#",
         "Flow",
         "Message",
         "Time",
         "Status",
         "Robot Name",
     )
    report = Report.query.get_or_404(id)
    return render_template("report.html" , report=report, headings=headings)


@app.route("/robotReports/<int:id>")
@login_required
def robotReports(id):
    headings = (
         "#",
         "Report Name",
         "Date",
         "Robot",
         "Logs",
     )
    reports = Report.query.filter_by(robot_id=id).all()
    print(report)
    return render_template("reportsforRobot.html" , reports=reports, headings=headings)


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html")


@app.route("/status")
@login_required
def status():
    # status = Status.query.all()
    # for status in status:
    #     if status.user_id == session["id"]:
    #         status_data = {}
    #         status_data["id"] = status.id
    #         status_data["currentStatus"] = status.currentStatus

    # statusid = str(status_data["currentStatus"])
    # robots = Robot.query.all()
    # current_robot = []
    # for robot in robots:
    #     if robot.status == statusid:
    #         if robot.user_id == session["id"]:
    #             robots_data = {}
    #             robots_data["id"] = robot.id
    #             robots_data["robotname"] = robot.robotname
    #             robots_data["description"] = robot.description
    #             robots_data["status"] = robot.status
    #             current_robot.append(robots_data)
    # print(current_robot)
    # for robot in current_robot:
    #     current_robot_name = robot["robotname"]

    for robot in current_user.robots:
        if robot.status == current_user.status.currentStatus:
            current_robot_name = robot.robotname
    return render_template(
         "status.html", current_robot_name = current_robot_name #status_data=status_data, current_robot_name=current_robot_name
    )



@app.route("/editRobots/<string:id>")
@login_required
def editRobots(id):
    return "<h1>esta es una vista protegida , solo para usuarios auth </h1>"




############################### ROUTES ###############################

############################### WEB SOCKETS ###############################

# import websockets
# import asyncio

# async def echo(websocket, path):
#     print("cliente connectado")
#     async for message in websockets:<
#         print("mensaje recibido del cliente")
#         await websockets.send("back Xd")

# start_server = (websockets.serve(echo, "localhost",7777))
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()


@socketio.on("message")
def handleMessage(msg):
    print(msg)  
    if msg == "Procesando":
        print("Recivido el procesando")
    else:
        send(msg, broadcast=True)





############################### WEB SOCKETS ###############################

############################### API ROUTES ###############################

#Api para crear el reporte
@app.route("/api/createReport" , methods=['POST'])
@csrf.exempt
def createReport():

    reportname = request.json['reportname']
    date = request.json['date']
    robot_id = request.json['robot_id']
    user_id = request.json['user_id']

    new_report = (Report(reportname,date,robot_id,user_id))
    db.session.add(new_report)
    db.session.commit()

    return report_schema.jsonify({'id' : new_report.id})

#Api para crear log
@app.route("/api/createLog" , methods=['POST'])
@csrf.exempt
def createLog():

    flow = request.json['flow']
    message = request.json['message']
    status = request.json['status']
    time = request.json['time']
    report_id = request.json['report_id']

    new_log = (Log(flow,message,status,time,report_id))

    db.session.add(new_log)
    db.session.commit()

    return log_schema.jsonify(new_log)

#API para obtener el id de usuario teniendo el nombre de la company
@app.route("/api/getUserId/<string:company>" , methods=['GET'])
@csrf.exempt
def getUserId(company):
    user = User.query.filter_by(company=company).first()
    print(user.id)
    return jsonify({"User_Id" : user.id})

#Api para obtener la Id del robot con su nombre y el id de usuario
@app.route("/api/getRobotId/<string:robotname>/<int:user_id>" , methods=['GET'])
@csrf.exempt
def getRobotId(robotname,user_id):
    robot = Robot.query.filter_by(robotname=robotname,user_id=user_id).first()
    return jsonify({"robot Id" : robot.id})

#API para obtener el status , el path del siguiente robot a ejecutar, el nombre y actualiza al siguiente status.
@app.route("/api/getStatuz/" , methods=['GET'])
@csrf.exempt
def getStatuz():
    
    user_id = request.json['user_id']

    user = User.query.filter_by(id=user_id).first()
    robotCount = 0
    for robot in user.robots:
        robotCount = robotCount + 1


    statusObject = Status.query.filter_by(user_id=user_id).first()
    currentStatus = statusObject.currentStatus

    robot = Robot.query.filter_by(status=currentStatus, user_id=user_id).first()
 

    if (int(currentStatus)) >= robotCount: 
        startOver = "1"
        statusObject.currentStatus = startOver
        db.session.commit()
        return jsonify({"Current Status" : currentStatus , "Robot a Ejecutar" : robot.robotname , "Path": robot.path , "New Status" : startOver})
    else:
            
        newStatus = int(currentStatus) + 1
        strNewStatus = str(newStatus)
        statusObject.currentStatus = strNewStatus
        db.session.commit()
        return jsonify({"Current Status" : currentStatus , "Robot a Ejecutar" : robot.robotname , "Path": robot.path , "New Status" : strNewStatus})


############################### API ROUTES ###############################

############################### ERROR ###############################

def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Pagina no encontrada</h1>"

############################### ERROR ###############################

if __name__ == "__main__":
    csrf.init_app(app)
    app.config.update(dict(
        SECRET_KEY="12345",
        WTF_CSRF_SECRET_KEY="a csrf secret key"
    ))

    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)

    socketio.run(app)
    #app.run(debug=True, port="7777")
