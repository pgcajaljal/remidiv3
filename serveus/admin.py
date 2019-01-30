from serveus import app

#from flask.ext.admin import Admin, AdminIndexView, expose
from flask_admin import Admin, AdminIndexView, expose

#from flask.ext.admin.base import MenuLink
from flask_admin.base import MenuLink

#from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla import ModelView

#from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.fileadmin import FileAdmin

from wtforms import PasswordField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

#from flask.ext.login import current_user
from flask_login import current_user

from flask import request
from jinja2 import Markup

#from flask.ext.admin.actions import action
from flask_admin.actions import action

from flask import redirect, url_for
import os, webbrowser


from models import db, User, UserType, Case, Image, Chunk, Chunklist, Region, Province, Municipality, ParType, Infection, Patch
from views import dashboard

# Custom admin links on navbar

class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

# Custom admin pages
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        admin = UserType.query.filter(UserType.name == 'Administrator').first()
        localadmin = UserType.query.filter(UserType.name == 'Local Administrator').first()
        return current_user.is_authenticated and (current_user.usertype == admin or current_user.usertype == localadmin)
    @expose('/')
    def index(self):
        return self.render('admin.html', username = current_user.username)

class MyModelView(ModelView):
    def is_accessible(self):
        admin = UserType.query.filter(UserType.name == 'Administrator').first()
        localadmin = UserType.query.filter(UserType.name == 'Local Administrator').first()
        return current_user.is_authenticated and current_user.usertype == admin

admin = Admin(app, index_view=MyAdminIndexView())

def get_nonadmin_usertypes():
        return UserType.query.filter(UserType.name != 'Administrator').filter(UserType.name != 'Local Administrator').all();
 

# Custom admin pages
# More info in https://github.com/mrjoes/flask-admin/issues/173
class UserView(MyModelView):
    can_create = True
    column_list = ('username', 'usertype', 'firstname', 'lastname', 'contact', 'email', 'Download Images')
    #column_sortable_list = ('username', ('usertype', UserType.name), 'firstname', 'lastname', 'contact', 'email')
    column_sortable_list = ('username', ('usertype', 'usertype.name'), 'firstname', 'lastname', 'contact', 'email')
    column_searchable_list = ('username', 'firstname', 'lastname', 'email')
    form_excluded_columns = ('case', 'chunklists', 'validations')
    column_excluded_list = ('password')
   
    def create_form(self):
        self._refresh_forms_cache()
        return super(UserView, self).create_form() 

    def is_accessible(self):
        admin = UserType.query.filter(UserType.name == 'Administrator').first()
        localadmin = UserType.query.filter(UserType.name == 'Local Administrator').first()
        return current_user.is_authenticated and (current_user.usertype == admin or current_user.usertype == localadmin)

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = PasswordField()

        try:
            localadmin = UserType.query.filter(UserType.name == 'Local Administrator').first()
            if current_user.usertype == localadmin:
                form_class.usertype = QuerySelectField(query_factory=get_nonadmin_usertypes)
        except:
            pass

        return form_class

    def on_model_change(self, form, model):
        if len(model.password):
            model.password = User.hash_password(form.password.data)
        
    def _download_column(view, context, model, name):
        hasImages = False;
        for c in User.query.get(model.id).case:
            for i in c.images:
                hasImages = True
                break
            if hasImages:
                break
        return Markup(
            '<a href="/download/?user=%s">Download</a>' % model.id
        ) if hasImages else "No images"
    column_formatters = { 'Download Images': _download_column }

class ImageView(MyModelView):
    can_create = True
    can_edit = True
    column_list = ('id', 'case_id', 'number')
    column_labels = dict(id='ID', case_id='Case')
    column_exclude_list = ('im')
    
    @action('open','Open')
    def action_open(self,ids):
        tempids=""
        for i in ids:
            tempids= tempids + "window.open(\"/pic/"+ str(Image.query.get(i).id) + ");"
        #return Markup( ' <a href="/pic/%s" id = "imlink" target="_blank">%s</a> ' % (str(Image.query.get(ids[0]).id), str(Image.query.get(ids[0]).id)) 
     #   return Markup( '  <a href="/pic/1" id = "imlink" target="_blank"></a> <script> document.getElementById("imlink").click(); alert("asd");</script> ')
        return Markup( '  <a href="/pic/1" class= "imlink" target="_blank"></a>  <a href="/pic/2" class = "imlink" target="_blank"></a><script> var l= document.getElementsByClassName("imlink"); \
        for (var i=0;i<l.length; i++) {l[i].click();}       </script>  ')
        
    @action('download','Download')
    def action_download(self,ids):
        tempids=""
        for i in ids:
            tempids= tempids + str(Image.query.get(i).id)+'|'
        return redirect('/downloadselected?ids=' + tempids)
    
    def scaffold_form(self):
        form_class = super(ImageView, self).scaffold_form()
        form_class.im = FileField()
        return form_class
        
    def on_model_change(self, form, model):
        temp = request.files[form.im.name].read()
        if temp:
            model.im = temp
        
    def _image_link(view, context, model, name):
        return Markup(
            '<a href="/pic/%s">%s</a>' % (model.id, model.id)
        ) if model.id else ""

    def _image_view(view, context, model, name):
        return Markup(
            '<a href="/pic/%s/" ><img src="/thumb/pic/%s/" class="thumbnail pull-left" style="width: 160px; height: 120px"/></a>' % (model.id, model.id)
        ) if model.im else ""
    column_formatters = { 'id': _image_view }
 
class PatchView(MyModelView):
    column_list = ('partype', 'image', 'xcoord', 'radius')
    column_labels = dict(partype='Diagnosis', xcoord='Coordinates')
    column_sortable_list = (('partype', 'partype.name'),)
    column_searchable_list = (ParType.name,)
    
    def _image_view(view, context, model, name):
        return Markup(
            '<a href="/pic/%s/" ><img src="/thumb/pic/%s/" class="thumbnail pull-left" style="width: 160px; height: 120px"/></a>' % (model.image.id, model.image.id)
        ) if model.image.im else ""

    def _coord_view(view, context, model, name):
        return Markup(
            '(%d, %d)' % (model.xcoord, model.ycoord)
        )

    column_formatters = { 'image': _image_view, 'xcoord': _coord_view }

class ParTypeView(MyModelView):
    column_list = ('infection', 'name')
    #column_sortable_list = (('infection', Infection.name), 'name')
    column_sortable_list = (('infection', 'infection.name'), 'name')
    column_searchable_list = (Infection.name, 'name')
    column_labels = dict(infection='Infection', type='Diagnosis')
    column_excluded_list = ('negative')
    form_excluded_columns = ('cases')

    def __init__(self, session, **kwargs): 
		super(ParTypeView, self).__init__(ParType, session, **kwargs)

class InfectionView(MyModelView):
	form_excluded_columns = ('results')

log_path = os.path.join(app.config['LOG_DIR'])
            
# Add pages to the admin page
admin.add_view(MyModelView(UserType, db.session, category='Accounts', name='User Types'))
admin.add_view(UserView(User, db.session, category='Accounts', name='User Accounts'))

admin.add_view(MyModelView(Case, db.session, category='Case Data', name='Case Summary'))
admin.add_view(MyModelView(Chunklist, db.session, category='Case Data'))
admin.add_view(MyModelView(Chunk, db.session, category='Case Data'))
admin.add_view(ImageView(Image, db.session, category='Case Data', name='Images'))
admin.add_view(PatchView(Patch, db.session, category='Case Data', name='Image Patches'))
admin.add_view(InfectionView(Infection, db.session, category='Diseases', name='Diseases and Infections'))
admin.add_view(ParTypeView(db.session, name='Diagnosis List', category='Diseases'))
admin.add_view(MyModelView(Region, db.session, category='Locations', name='Regions'))
admin.add_view(MyModelView(Province, db.session, category='Locations', name='Provinces'))
admin.add_view(MyModelView(Municipality, db.session, category='Locations', name='Municipalities'))
admin.add_view(FileAdmin(log_path, '/log/', name='Logs', url="/admin/logview"))

# Navbar links
admin.add_link(AuthenticatedMenuLink(name='Back to Website', url='/monitoring/1'))
