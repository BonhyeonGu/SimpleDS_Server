from flask import Flask
from . import file
from . import schedule
from . import server

app = Flask(__name__)
app.register_blueprint(file.file)
app.register_blueprint(schedule.schedule)
app.register_blueprint(server.server)
app.secret_key = 'abcd'
#-----------------------------------------------------s