import logging
import os, sys
from logging.handlers import RotatingFileHandler
from serveus import app, manager

if __name__ == '__main__':
    manager.run()
