from django.dispatch import Signal

# signal to get the user activity in the website once the user logs in
user_logged_in = Signal(providing_args=['instance', 'request'])