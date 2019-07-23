from flask import  abort, flash, render_template, redirect, request, url_for, g, \
    jsonify, current_app
from werkzeug.urls import url_parse
from flask_login import login_required, current_user
from app import db
from app.auth.forms import LoginForm
from app.home.forms import OrganisationForm, UserRegisterForm, UserAssignForm, RoleForm
from app.home import bp
from app.models import User, Organisation, Role, user_roles



def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.has_admin():
        abort(403)



@bp.route('/index', methods=['GET','POST'])

def index():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        return redirect(url_for('auth.login')) 

    return render_template('home/landing.html', form=form)



@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Prevent non-admins from accessing the page
    """
        

    return render_template('home/dashboard.html', title="Dashboard")

# organisation Views


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_user():

    check_admin()

    form = UserRegisterForm()

    if request.method=="POST" and form.validate_on_submit():
        user = User(username=form.username.data, 
                    email=form.email.data, 
                    first_name=form.firstname.data,
                    last_name=form.lastname.data,
                    is_admin=form.is_admin.data,
                    active=form.active.data  
                    )
        
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully')
        return redirect(url_for('home.list_users'))
    return render_template('home/register_user.html', title='Register User', form=form)


@bp.route('/users')
@login_required
def list_users():
    """
    List all employees
    """
    check_admin()
    
    form = UserRegisterForm()
    users = User.query.all()
    return render_template('home/users.html', form=form,
                           users=users, title='Users')


@bp.route('/users/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_user(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    user = User.query.get_or_404(id)
    

    # prevent admin from being assigned a organisation or role
    if user.has_admin():
        abort(403)

    form = UserAssignForm(obj=user)
    if request.method=="POST" and form.validate_on_submit():
        user.organisation = form.organisation.data
        
        user.roles.append(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully assigned a organisation and role.')

        # redirect to the roles page
        return redirect(url_for('home.list_users'))

    return render_template('home/user.html', id=id,
                           user=user, form=form,
                           title='Assign User')



@bp.route('/organisations', methods=['GET', 'POST'])
@login_required
def organisations():
    """
    List all organisations
    """
    check_admin()

    form=OrganisationForm()
    organisations = Organisation.query.all()

    return render_template('home/organisations.html', form=form,
                           organisations=organisations, title="Organisations")


@bp.route('/organisations/add', methods=['GET', 'POST'])
@login_required
def add_organisation():
    """
    Add a organisation to the database
    """
    check_admin()

    add_organisation = True

    form = OrganisationForm()
    if request.method=="POST" and form.validate_on_submit():
        organisation = Organisation(code=form.code.data, vrn=form.vrn.data,
                                    name=form.name.data)
        try:
            # add organisation to the database
            db.session.add(organisation)
            db.session.commit()
            flash('You have successfully added a new organisation.')
        except:
            # in case organisation name already exists
            flash('Error: organisation name already exists.')

        # redirect to organisations page
        return redirect(url_for('home.organisations'))

    # load organisation template
    return render_template('home/organisation.html', action="Add", id=None,
                           add_organisation=add_organisation, form=form,
                           title="Add Organisation")


@bp.route('/organisation/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_organisation(id):
    """
    Edit a organisation
    """
    check_admin()

    add_organisation = False

    organisation = Organisation.query.get_or_404(id)
    form = OrganisationForm(obj=organisation)
    if request.method == "POST" and form.validate_on_submit():
        organisation.code = form.code.data
        organisation.vrn = form.vrn.data
        organisation.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the organisation.')

        # redirect to the organisations page
        return redirect(url_for('home.organisations'))

    form.code.data = organisation.code
    form.vrn.data = organisation.vrn
    form.name.data = organisation.name
    return render_template('home/organisation.html', id=id , action="Edit",
                           add_organisation=add_organisation, form=form,
                           organisation=organisation, title="Edit Organisation")


@bp.route('/organisation/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_organisation(id):
    """
    Delete a organisation from the database
    """
    check_admin()

    organisation = Organisation.query.get_or_404(id)
    db.session.delete(organisation)
    db.session.commit()
    flash('You have successfully deleted the organisation.')

    # redirect to the organisations page
    return redirect(url_for('home.organisations'))

    return render_template(title="Delete Organisation")



# Role Views


@bp.route('/roles')
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """

    form=RoleForm()
    roles = Role.query.all()
    return render_template('home/roles.html', form=form,
                           roles=roles, title='Roles')


@bp.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('home.list_roles'))

    # load role template
    return render_template('home/role.html', add_role=add_role,
                           form=form, title='Add Role')


@bp.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if request.method=="POST" and form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('home.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('home/role.html', id=id,  add_role=add_role,
                           form=form, title="Edit Role")


@bp.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('home.list_roles'))

    return render_template(title="Delete Role")