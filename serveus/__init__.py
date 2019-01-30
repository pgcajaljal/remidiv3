import os, time, sys, logging
from logging.handlers import RotatingFileHandler
from flask import Flask

import flask_sqlalchemy._compat as _
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

import flask_script._compat as _
from flask_script import Manager

from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

# CONFIG
#app.config.from_object('config')
serveus = os.path.abspath(os.path.dirname(__file__))
app.config['BASE_DIR'] = os.path.abspath(os.path.dirname(serveus))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/main.db'
app.config['HIDE_MICROSCOPIST_FROM_VALIDATOR'] = True
app.config['LONGLAT_PRECISION_PT'] = 2
app.config['CRSF_ENABLED'] = False
app.config['SECRET_KEY'] = 'r3m1d1v2S3cr3T'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['GMAPS_APIKEY'] = os.environ.get('GMAPS_APIKEY')
mail = Mail(app)
db = SQLAlchemy(app)

# MIGRATION
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# LOGGING
DATE_INIT = time.strftime("%Y-%m-%d")
TIME_INIT = time.strftime("%H.%M.%S")
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(app.config['BASE_DIR'], "logs", DATE_INIT))
app.config['LOG_DIR'] = LOG_DIR
LOG_FILE = os.path.join(LOG_DIR, TIME_INIT + ".log")

try:
    os.mkdir(os.path.join(app.config['BASE_DIR'], "logs", time.strftime("%Y-%m-%d")))
except OSError:
    pass
    
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
        
    def flush(self):
        try:
          self.logger.flush()
        except: pass

logging.basicConfig(
   level=logging.DEBUG,
   format='> %(message)s',
   stream=sys.stderr
)

formatter = logging.Formatter("> %(message)s")
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount = 5)
file_handler.setFormatter(formatter) 
root = logging.getLogger('')
sys.stderr = StreamToLogger(root, logging.INFO)
root.addHandler(file_handler)

try:
    root.log(logging.DEBUG, "Initialized logger")
except IOError as e:
    # Remove stderr logger if console is hidden. Print statements will not be logged
    root.removeHandler(root.__dict__['handlers'][0])
    
# IMPORT PARTS OF APP
from serveus import views, models, admin
