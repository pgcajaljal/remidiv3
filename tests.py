import os
import shutil
import unittest
import urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from flask.ext.testing import TestCase

from serveus import app
from serveus.models import db

class CommunicationTest(TestCase):

	def create_app(self):
		app.config['TESTING'] = True
		return app

	def setUp(self):
		# create database backup
		self.db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
		self.backup_path = os.path.join(os.path.dirname(self.db_path), 'test_backup.db')
		shutil.copy2(self.db_path, self.backup_path)

		# initialize Selenium web driver
		self.web = webdriver.Firefox()

	def tearDown(self):
		self.temp_path = os.path.join(os.path.dirname(self.db_path), 'lol.db')
		shutil.copy2(self.db_path, self.temp_path)
		os.remove(self.db_path)
		shutil.move(self.backup_path, self.db_path)
		self.web.close()

		# remove temporary upload folder
		shutil.rmtree('/home/befreicafsan/files/199/Malaria-Server/upload/02272014_151331_rodolfo/')

	
	def login_as_admin(self):
		web = self.web
		web.get('http://localhost/')
		elem = web.find_element_by_name('username')
		elem.send_keys('rodolfo')
		elem = web.find_element_by_name('password')
		elem.send_keys('genius123')
		web.find_element_by_css_selector('input[type="submit"]').click()
	
	def test_send(self):
		self.aux_send_init()
		self.aux_send_chunk()
		self.aux_send_all_chunks()
		raw_input()

	def aux_send_init(self):
		web = self.web
		web.get('http://localhost/api/init/')
		elem = web.find_element_by_name('file')
		# TODO: should be portable
		elem.send_keys('/home/befreicafsan/files/199/Malaria-Server/upload/a02272014_151331_rodolfo/02272014_151331_rodolfo.zip')
		elem = web.find_element_by_name('checksum')
		elem.send_keys('ab7cffd3279eae2057876d6293643e2c')
		web.find_element_by_css_selector('input[type="submit"]').click()

		self.login_as_admin()
		web.get('http://localhost/admin/chunklistview/')
		assert '02272014_151331_rodolfo' in web.page_source

	def aux_send_chunk(self):
		web = self.web
		web.get('http://localhost/api/chunk/')
		elem = web.find_element_by_name('file')
		# TODO: should be portable
		elem.send_keys('/home/befreicafsan/files/199/Malaria-Server/upload/a02272014_151331_rodolfo/02272014_151331_rodolfo.zip001.part')
		web.find_element_by_css_selector('input[type="submit"]').click()

		web.get('http://localhost/admin/chunkview/')
		assert '02272014_151331_rodolfo.zip001.part' in web.page_source

	def aux_send_all_chunks(self):
		web = self.web
		for i in xrange(2, 19):
			web.get('http://localhost/api/chunk/')
			elem = web.find_element_by_name('file')
			# TODO: should be portable
			elem.send_keys('/home/befreicafsan/files/199/Malaria-Server/upload/a02272014_151331_rodolfo/02272014_151331_rodolfo.zip%s.part' % (str(i).zfill(3)))
			web.find_element_by_css_selector('input[type="submit"]').click()

if __name__ == "__main__":
	unittest.main()
