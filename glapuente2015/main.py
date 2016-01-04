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
import string
import smtplib # libreria para correos electronicos

from google.appengine.api import mail

import random
import cgi # escape characters
import re # regular expressions
import jinja2 # template management
from google.appengine.ext import ndb # data storage
import hashlib # hashing data
import urllib # web services
import json # json
from webapp2_extras import sessions # session handling
import session_module # session handling
from google.appengine.ext import blobstore # blobstore import
from google.appengine.ext.webapp import blobstore_handlers # blobstore_handlers import

class User(ndb.Model):
	nombre = ndb.StringProperty(required=True)
	uemail = ndb.StringProperty(required=True)
	contra = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	intentos = ndb.IntegerProperty()
	
	@classmethod
	def query_user(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.created)
		
		
class Password_Change_Request(ndb.Model):
	request_date = created = ndb.DateTimeProperty(auto_now_add=True)
	hashed_id = ndb.StringProperty(required=True)
	user_email = ndb.StringProperty(required=True)
	
		
class Image(ndb.Model):
	user_email = ndb.StringProperty()
	public = ndb.BooleanProperty()
	blob_key = ndb.BlobKeyProperty()
	
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))	

	
FORM_SUBIR_FOTO = '''
<html>
<body>
	<form class="form-horizontal" action="%(url)s" method="POST" enctype="multipart/form-data">
		<div class="form-group">
			<label for="File" class="col-sm-2 control-label">File</label>
			<div class="col-sm-10">
				<input id="File" type="file" name="file" accept="image/*" />
			</div>
		</div>
		<div class="form-group">
			<div class="col-sm-offset-2 col-sm-10">
				<div class="radio">
					<label><input type="radio" name="access" value="public" checked="checked">Public</label>
				</div>
			</div>
		</div>
		<div class="form-group">
			<div class="col-sm-offset-2 col-sm-10">
				<div class="radio">
					<label><input type="radio" name="access" value="private">Private</label>
				</div>
			</div>
		</div>
		<div class="form-group">
			<div class="col-sm-offset-2 col-sm-10">
				<input type="submit" name="submit" class="btn btn-default" value="Enviar"/>
			</div>
		</div>
	</form>
</body>
</html>
'''
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler, session_module.BaseSessionHandler):
	def get(self):
		# Si el usuario se ha autenticado, mando el formulario
		if self.session.get('logged_email'):
			upload_url = blobstore.create_upload_url('/upload')
			template=JINJA_ENVIRONMENT.get_template('generic.html')
			self.response.write(template.render())
			self.response.out.write(FORM_SUBIR_FOTO%{'url':upload_url})
		else:
			self.response.out.write("<script>alert('Para subir fotos necesitas estar registrado');window.location.href='/login';</script>")
		
	def post(self):

		file_info = self.get_file_infos()[0] # se recogen los datos de la imagen que nos llega
		rtn_data = {
            "filename": file_info.filename,
            "content_type": file_info.content_type, # tipo mime del fichero subido en el formulario
            "creation": file_info.creation,
            "size": file_info.size,
            "md5_hash": file_info.md5_hash,
            "gs_object_name": file_info.gs_object_name
        }
		
		if ("image" in rtn_data["content_type"]): # se trata de una imagen. Subirla
			upload_files = self.get_uploads('file')
			blob_info = upload_files[0] # save the image in the BlobStore
			img = Image(user_email=self.session.get('logged_email'),
			public=self.request.get("access")=="public", blob_key=blob_info.key())
			img.put() # save the object Image
			self.response.out.write("<script>window.location.href='/download';</script>")
		
		else: # no se trata de una imagen. NO SE SUBE!
			self.response.out.write("<script>window.location.href='/download';alert('Solo se pueden subir imagenes');</script>")


class Fotos(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('generic.html')
		self.response.write(template.render())
		self.response.write('<div class="containter">')
		self.response.write('<div class="row">')
		self.response.write('''
		<div class="col-lg-12">
			<h1 class="page-header">Todas las fotos p&uacute;blicas</h1>
		</div>
		''')
		fotos = ndb.gql("SELECT * FROM Image WHERE public=True")
		for foto in fotos:
			self.response.write('''
			<div class="col-lg-3 col-md-4 col-xs-6 thumb">
				<a class="thumbnail" href="#">
			''')
			
			self.response.out.write('<img class="img-responsive" src="serve/%s"></img></td>' % foto.blob_key)
			self.response.write('''
				</a>
				<div class="desc">
					<p class="desc_content">%s</p>
				</div>
			</div>
			''' % foto.user_email)
		self.response.write('''
		</div>
		</div>
		''')
	
class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler, session_module.BaseSessionHandler):
	def get(self):
		if self.session.get('logged_email'):
			template=JINJA_ENVIRONMENT.get_template('bienvenido.html')
			self.response.write(template.render())
			self.response.write('<div class="containter">')
			self.response.write('<div class="row">')
			self.response.write('''
			<div class="container">
				<div class="page-header">
					<h1>Tus fotos</h1>
				</div>
				<p>Pincha en <a href="/upload">este enlace</a> para subir fotos<p>
			</div>
			''')
			fotos = ndb.gql("SELECT * FROM Image WHERE user_email=:1", self.session.get('logged_email'))
			for foto in fotos:
				self.response.write('''
				<div class="col-lg-3 col-md-4 col-xs-6 thumb">
					<a class="thumbnail" href="#">
						
				''')
			
				self.response.out.write('<img class="img-responsive" src="serve/%s"></img></td>' % foto.blob_key)
				self.response.write('''
					</a>
					<div class="desc">
						<p class="desc_content">%s</p>
					</div>
				</div>
				''' % foto.user_email)
			self.response.write('''
			</div>
			</div>
			''')
		else:
			self.response.out.write("<script>alert('No te puedes colar sin estar registrado');window.location.href='/login';</script>")
		
		
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		resource = str(urllib.unquote(resource))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)

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
			self.response.out.write('<td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td>'.format(cgi.escape(user.nombre),cgi.escape(user.uemail),str(user.created),str(user.contra),str(user.intentos)))
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
			datos = User(parent=ndb.Key("User", "*notitle*"),uemail=email,nombre=username,contra=str(hashlib.sha224(password).hexdigest()),intentos=0)
			
			
			usuarios = ndb.gql("SELECT * FROM User WHERE uemail=:1", email)
			if usuarios.count() == 1:
				self.response.write("<h1>El usuario esta en el modelo</h1>")
				self.response.out.write("<script>alert('Ya hay un usuario con ese email');window.location.href='/login';</script>")

			else:
				self.response.write("<h1>El usuario no esta en el modelo</h1>")
				datos.put()
				self.response.out.write("<script>alert('Gracias por registrarte');window.location.href='/login';</script>")

				
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
		

class MainSessionHandler(session_module.BaseSessionHandler):
	def get(self):
		if self.session.get('counter'):
			self.response.out.write('Existe una sesion activa')
			counter = self.session.get('counter')
			self.session['counter'] = counter + 1
			self.response.out.write('Counter = '+str(self.session.get('counter')))
		else:
			self.response.out.write('Sesion nueva')
			self.session['counter'] = 1
			self.response.out.write('Counter = '+str(self.session.get('counter')))
	
class LogoutHandler(session_module.BaseSessionHandler):
	def get(self):
		if self.session.get('logged_email'):
			del self.session['logged_email']
			self.response.out.write("<script>alert('Gracias por visitarnos');window.location.href='/';</script>")
		else:
			self.response.out.write("<script>alert('Para salir de la sesion primero necesitas iniciarla');window.location.href='/login';</script>")
		
class Login(session_module.BaseSessionHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('login.html')
		self.response.write(template.render())
	
	def post(self):
		email = cgi.escape(self.request.get('email'),quote=True)
		password_in = cgi.escape(self.request.get('password'),quote=True)
		
		usuarios = ndb.gql("SELECT * FROM User WHERE uemail=:1", email)
		usuario = usuarios.get()
		password = str(usuario.contra)
		hash_pass = str(hashlib.sha224(password_in).hexdigest())
		
		if usuario.intentos>2:
			template=JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render())
			self.response.write('''
			<div class="alert alert-warning">
			<strong>Cuidado!</strong> Has superado el numero de intentos de acceso y la cuenta esta en cuarentena. Solicita cambiar la constrasena.
			</div>
			''')
		
		elif password == hash_pass and password!="":
			usuario.intentos=0 # poner a cero los intentos del usuario
			usuario.put() # actualizar el usuario en el datastore
			self.redirect("/download") # Redirect to welcome page
			self.session['logged_email'] = email # create session
			
		else: # the user was not found
			template=JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render())
			self.response.write('''
			<div class="alert alert-danger">
			<strong>Error!</strong> Password incorrecto.
			</div>
			''')
			usuario.intentos+=1
			usuario.put()
			if(usuario.intentos>2):
				self.response.write('''
				<div class="alert alert-warning">
				<strong>Cuidado!</strong> Has superado el numero de intentos de acceso. Solicita cambiar la constrasena.
				</div>
				''')

			
		#if self.session.get('logged_email'):
		#	self.response.out.write('Ya te has logueado con ese email. Bienvenido')
		#	email_session = self.session.get('logged_email')
		#else:
		#	self.response.out.write('No te has logueado con ese mail')
		#	self.session['logged_email'] = self.request.get('email')
		#	self.response.out.write('Email = '+str(self.session.get('logged_email')))
	
	
class Bienvenido(session_module.BaseSessionHandler):
	def get(self):
		if self.session.get('logged_email'):
			template=JINJA_ENVIRONMENT.get_template('bienvenido.html')
			self.response.write(template.render())
		else:
			self.redirect('/login')
			

			
class ForgotPassword(webapp2.RequestHandler):
	def get(self):
		template=JINJA_ENVIRONMENT.get_template('forget_password.html')
		self.response.write(template.render())
		
	def post(self):
		email = cgi.escape(self.request.get('email'),quote=True) # email cuya password queremos cambiar
		id=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) # se genera el id aleatorio sin cifrar
		datos = Password_Change_Request(parent=ndb.Key("Password_Change_Request", "*notitle*"),user_email=email,hashed_id=str(hashlib.sha224(id).hexdigest())) # se almacena el registro en la BD con el id cifrado
		# datos.put()
		
		sender_address="Example.com Support <support@example.com>"
		subject="Pruebita"
		body="PRUEBAPRUEBAPRUEBAPRUEBA"
		mail.send_mail(sender_address, email, subject, body)
		
		
app = webapp2.WSGIApplication([
    ('/', Links),
    ('/saludaEN', MainHandler),
    ('/saludaES', MainHandlerES),
	('/saludaEUS', MainHandlerEUS),
	('/loginForm', LoginForm),
	('/validar', ValidarHandle),
	('/DBContent', DBContent),
	('/exists', Exists),
	('/Maps', Maps),
	('/Session', MainSessionHandler),
	('/logout', LogoutHandler),
	('/login', Login),
	('/bienvenido', Bienvenido),
	('/upload', UploadHandler),
	('/download', ViewHandler),
	('/serve/([^/]+)?', ServeHandler),
	('/fotos', Fotos),
	('/forgotpassword', ForgotPassword)
], debug=True, config = session_module.myconfig_dict)
