login_manager = LoginManager()

def load_user(userid):
    return User.get(userid)