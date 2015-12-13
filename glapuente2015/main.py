#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import cgi # escape characters
import re # regular expressions
import jinja2 # template management
from google.appengine.ext import ndb # data storage
import hashlib # hashing data
import urllib # web services
import json # json

class User(ndb.Model):
	nombre = ndb.StringProperty(required=True)
	uemail = ndb.StringProperty(required=True)
	contra = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	
	@classmethod
	def query_user(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.created)

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))	


class Links(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render())

class MainHandler(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoEN.html')
		self.response.write(template.render())

class MainHandlerES(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoES.html')
		self.response.write(template.render())
		
class MainHandlerEUS(webapp2.RequestHandler):
    def get(self):
		template=JINJA_ENVIRONMENT.get_template('saludoEUS.html')
		self.response.write(template.render())
		
class LoginForm(webapp2.RequestHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('login_form.html')
		self.response.write(template.render())
		
class DBContent(webapp2.RequestHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('dbcontent.html')
		self.response.write(template.render())
		ancestor_key = ndb.Key("User", "*notitle*")
		users = User.query_user(ancestor_key).fetch(20)
		
		self.response.write('''<section>
        <div class="container">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="section-heading">GAE+Python</h1>
                    <p class="lead section-lead">Desarrollo de Software Seguro en la Web</p>
                    <p class="section-paragraph">Usuarios ya registrados</p>
					<table class="table table-striped">
						<thead>
							<tr>
								<th>Username</td>
								<th>Email</td>
								<th>Date of creation</td>
								<th>Password SHA224</td>
							</tr>
						</thead>
						<tbody>
                ''')
		
		for user in users:
			self.response.write('<tr>')
			self.response.out.write('<td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>'.format(cgi.escape(user.nombre),cgi.escape(user.uemail),str(user.created),str(user.contra)))
			self.response.write('</tr>')
			
		self.response.write('''
						</tbody>
					</table>
				</div>
            </div>
        </div>
    </section>''')
		
class ValidarHandle(webapp2.RequestHandler):
	def post(self):
		username = cgi.escape(self.request.get('username'),quote=True)
		email = cgi.escape(self.request.get('email'),quote=True)
		password = cgi.escape(self.request.get('password'),quote=True)
		rePassword = cgi.escape(self.request.get('rePassword'),quote=True)
		
		html_error_msg=""
		error_flag=1
			
		# Empty fields
		if(username==""):
			html_error_msg+="<h3>The username field cannot be empty</h3></hr>"
			error_flag=-1
		if(email==""):
			html_error_msg+="<h3>The email field cannot be empty</h3></hr>"
			error_flag=-1
		if(password=="" or rePassword==""):
			html_error_msg+="<h3>The password field cannot be empty</h3></hr>"
			error_flag=-1
		
		# Repeat passwords
		if(password!=rePassword):
			html_error_msg+="<h3>The passwords must match</h3></hr>"
			error_flag=-1
		
		# Password regexp - Min. 8 Max.12. At least 1 num, lower and upper
		if not re.match("((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,12})",password):
			html_error_msg+="<h3>The password does not comply with the pattern</h3></hr>"
			error_flag=-1
			
		if not re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$",email):
			html_error_msg+="<h3>The email does not comply with the pattern</h3></hr>"
			error_flag=-1

		tpl_vars={"username":username,"email":email}

		if(error_flag==-1):
			template=JINJA_ENVIRONMENT.get_template('login_form.html')
			self.response.write(template.render(tpl_vars))
			self.response.write(html_error_msg)
		else:
			datos = User(parent=ndb.Key("User", "*notitle*"),uemail=email,nombre=username,contra=str(hashlib.sha224(password).hexdigest()))
			
			
			usuarios = ndb.gql("SELECT * FROM User WHERE uemail=:1", email)
			if usuarios.count() == 1:
				self.response.write("<h1>El usuario esta en el modelo</h1>")
			else:
				self.response.write("<h1>El usuario no esta en el modelo</h1>")
				datos.put()
			
			# datos.put()
			self.response.write("<h1>Bienvenido "+username+"</h1>")
			ancestor_key = ndb.Key("User", "*notitle*")
			users = User.query_user(ancestor_key).fetch(20)
			
			for user in users:
				self.response.out.write('<blockquote>%s</blockquote>' % cgi.escape(user.uemail))
			
		
		
class Exists(webapp2.RequestHandler):
	def post(self):	
		email = cgi.escape(self.request.get('email'),quote=True)
		
		usuarios = ndb.gql("SELECT * FROM User WHERE uemail=:1", email)
		if usuarios.count() > 0:
			self.response.write('''
			<div class="alert alert-warning">
			<strong>Cuidadin!</strong> Ya hay un usuario con ese email.
			</div>
			<script>
				$("#btn_submit").prop("disabled",true);
			</script>
			''')
		else:
			self.response.write('''
			<div class="alert alert-success">
			<strong>Bien!</strong> El email no esta registrado
			</div>
			<script>
				$("#btn_submit").prop("disabled",false);
			</script>
			''')

class Maps(webapp2.RequestHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('maps.html')
		self.response.write(template.render())
		
	def post(self):
		serviceurl = 'http://maps.googleapis.com/maps/api/geocode/json?'
		address=self.request.get('lugar')
		# address = 'Barakaldo'
		url = serviceurl + urllib.urlencode({'address': address})
		
		uh = urllib.urlopen(url)
		data = uh.read()
		
		js = json.loads(str(data))
		location = js['results'][0]['geometry']['location']
		# self.response.write(js)
		# self.response.write(location)
		lat = str(js['results'][0]['geometry']['location']['lat'])
		lng = str(js['results'][0]['geometry']['location']['lng'])
		# self.response.write("La latitud es: "+lat)
		# self.response.write("La longitud es: "+lng)
		lat_long = {"lat":lat, "lng":lng}
		self.response.write(lat_long)
		
			
app = webapp2.WSGIApplication([
    ('/', Links),
    ('/saludaEN', MainHandler),
    ('/saludaES', MainHandlerES),
	('/saludaEUS', MainHandlerEUS),
	('/loginForm', LoginForm),
	('/validar', ValidarHandle),
	('/DBContent', DBContent),
	('/exists', Exists),
	('/Maps', Maps)
], debug=True)
