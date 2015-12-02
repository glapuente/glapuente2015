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

indexHTML = '''
<html>
	<head>
		<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
		<title>Hola/Hello/Kaixo</title>
	</head>
	<body>
		<h1>Primer proyecto en GAE</h1>
		<h2>DSSW</h2>
		<div>
			<table>
			<tr><td><a href="/saludaES">Saluda en Castellano</a></td></tr>
			<tr><td><a href="/saludaEN">Say Hello in English</a></td></tr>
			<tr><td><a href="/saludaEUS">Agurtu Euskaraz</a></td></tr>
			</table>
		</div>
		<div>
			<img src="img/app-engine-logo.png" alt="GAE logo">
		</div>
	</body>
</html>
'''

helloWorld = '''
<html>
	<head>
		<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
		<title>Hello</title>
	</head>
	<body>
		<h1>Hello World!</h1>
		<a href="../">Back</a>
	</body>
</html>
'''

holaMundo = '''
<html>
	<head>
		<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
		<title>Hola</title>
	</head>
	<body>
		<h1>Hola Mundo!</h1>
		<a href="../">Back</a>
	</body>
</html>
'''

kaixoMundua = '''
<html>
	<head>
		<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
		<title>Kaixo</title>
	</head>
	<body>
		<h1>Kaixo Mundua!</h1>
		<a href="../">Back</a>
	</body>
</html>
'''

class Links(webapp2.RequestHandler):
    def get(self):
        self.response.write(indexHTML)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(helloWorld)

class MainHandlerES(webapp2.RequestHandler):
    def get(self):
        self.response.write(holaMundo)
		
class MainHandlerEUS(webapp2.RequestHandler):
    def get(self):
        self.response.write(kaixoMundua)

app = webapp2.WSGIApplication([
    ('/', Links),
    ('/saludaEN', MainHandler),
    ('/saludaES', MainHandlerES),
	('/saludaEUS', MainHandlerEUS)
], debug=True)
