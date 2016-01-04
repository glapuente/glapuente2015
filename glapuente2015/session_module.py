import webapp2
from webapp2_extras import sessions

SESSION_TIME_LIMIT = 180 #duracion de la sesion a 180 segundos = 3 mins

# This is needed to configure the session secret keys
# Runs first in the whole app
myconfig_dict = {}
myconfig_dict['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key-somemorearbitarythingstosay',
	'session_max_age': SESSION_TIME_LIMIT
}

# Session Handling class, gets the store, dispatches the request
class BaseSessionHandler(webapp2.RequestHandler):
	def dispatch(self):
		# Get a session store for this request
		self.session_store = sessions.get_store(request=self.request)
		try:
			# Dispatch the request
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key
		return self.session_store.get_session()

# End of BaseSessionHandler class