from django.dispatch import Signal


post_logout = Signal(providing_args=['user','request'])

# session data is content of session before login
post_login = Signal(providing_args=['user','request','session_data'])

post_register = Signal(providing_args=['user','request'])