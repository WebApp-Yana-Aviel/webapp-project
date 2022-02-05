

from flask import abort,flash,request,redirect, render_template, url_for
from flask_login import current_user, login_required
import datetime
from . import admin
import os
from .forms import UserForm,ModeForm,FaultForm,StationForm, UserForm_Edit
from .. import db
from ..models import LogUser,User,Mode,Station,Photo,Video,Faults,Route,RouteUser,RouteStation,StatusRoute
from  ..home.sendMessage import send_sms_user_message
from ..home.cameraPi import dropbox_folder_from_photos,delete_photo_from_dropbox,delete_video_from_dropbox
from ..auth.email import send_email_admin_fault
current_dir = os.path.abspath(os.path.dirname(__file__))
def check_admin():
    if not current_user.is_admin:
        abort(403)

        
#-----Users view-------
@admin.route('/users', methods=['GET', 'POST'])
@login_required
def list_users():
    """
    List all users
    """
    check_admin()

    users = User.query.all()

    return render_template('admin/users/users.html',
                           users=users, title="Users")


@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """
    Add a new user to the database
    """
    check_admin()

    add_user = True

    form = UserForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,
                                email=form.email.data,phone=form.phone.data)
        user.set_password(form.password.data)
        try:
            # add user to the database
            db.session.add(user)
            db.session.commit()
            flash('You have successfully added a new user.')
        except:
            # in case user name already exists
            flash('Error: user name already exists.')

        # redirect to users page
        return redirect(url_for('admin.list_users'))

    # load user template
    return render_template('admin/users/user.html', action="Add",add_user=add_user, form=form,title="Add User")


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    Edit a user
    """
    check_admin()

    add_user = False

    user = User.query.get_or_404(id)
    form = UserForm_Edit(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.phone=form.phone.data
        user.is_activity_user=form.is_activity_user.data
        db.session.commit()
        flash('You have successfully edited the user.')

        # redirect to the users page
        return redirect(url_for('admin.list_users'))

    form.name.data = user.name
    form.phone.data=user.phone
    form.is_activity_user.data= user.is_activity_user
    return render_template('admin/users/user.html', action="Edit", add_user=add_user, form=form, user=user, title="Edit User")


@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()

    user = User.query.get_or_404(id)
    users_route=RouteUser.query.filter(id==RouteUser.user_id).first()
    user_station=RouteStation.query.filter(users_route.route_id==RouteStation.route_id).all()
    route_user=Route.query.filter(Route.id==users_route.route_id).first()
    for user_st in user_station:
        db.session.delete(user_st)
    
    photos=Photo.query.filter(Photo.user_id==user.id).all()
    if (photos is not None):
        for photo in photos:
           try:
                delete_photo_from_dropbox(photo.name)
           except:
               print('[ERROR] not photos in dropbox')
           db.session.delete(photo)

    print('[INFO]  You have successfully deleted the photos.')

    videos=Video.query.filter(Video.user_id==user.id).all()
    if (videos is not None):
        for video in videos:
            try:
                delete_video_from_dropbox(video.name)
            except:
                print('[ERROR] not photos in dropbox')
            db.session.delete(video)

    print('[INFO]  You have successfully deleted the videos.')
    try:
        db.session.delete(user)
        db.ssesion.delete(users_route)
        db.session.delete(route_user)
        db.session.commit()
        flash('You have successfully deleted the user and all his history.')
    except:
        flash('Failure to delete user or all his history .')
        print('[ERROR] Failure to delete user ')

    # redirect to the users page
    return redirect(url_for('admin.list_users'))

#---########------
#-----Mode view-------
@admin.route('/modes', methods=['GET', 'POST'])
@login_required
def list_modes():
    """
    List all mode
    """
    check_admin()

    modes = Mode.query.all()

    return render_template('admin/modes/modes.html',
                           modes=modes, title="Modes")


@admin.route('/modes/add', methods=['GET', 'POST'])
@login_required
def add_mode():
    """
    Add a new mode to the database
    """
    check_admin()

    add_mode = True

    form = ModeForm()
    if form.validate_on_submit():
        mode = Mode(name=form.name.data)
        try:
            # add mode to the database
            db.session.add(mode)
            db.session.commit()
            flash('You have successfully added a new mode.')
        except:
            # in case mode name already exists
            flash('Error: mode name already exists.')

        # redirect to modes page
        return redirect(url_for('admin.list_modes'))

    # load mode template
    return render_template('admin/modes/mode.html', action="Add",
                           add_mode=add_mode, form=form,
                           title="Add Mode")


@admin.route('/modes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mode(id):
    """
    Edit a mode
    """
    check_admin()

    add_mode = False

    mode = Mode.query.get_or_404(id)
    form = ModeForm(obj=mode)
    if form.validate_on_submit():
        mode.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the mode.')

        # redirect to the modes page
        return redirect(url_for('admin.list_modes'))

    form.name.data = mode.name
    return render_template('admin/modes/mode.html', action="Edit",
                           add_mode=add_mode, form=form,
                           mode=mode, title="Edit Mode")


@admin.route('/modes/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_mode(id):
    """
    Delete a mode from the database
    """
    check_admin()

    mode = Mode.query.get_or_404(id)
    mode_route=Route.query.filter(id==Route.mode_id).first()
    mode_station=RouteStation.query.filter(mode_route.route_id==RouteStation.route_id).all()
    mode_user=RouteUser.query.filter(RouteUser.route_id==mode_route.route_id).first()
    for mode_st in mode_station:
        db.session.delete(mode_st)
    
    try:
        db.session.delete(mode)
        db.ssesion.delete(mode_route)
        db.session.delete(mode_user)
        db.session.commit()
        flash('You have successfully deleted the mode and records in routes.')
    except:
        flash('Failure to delete mode and records in db  .')
        print('[ERROR] Failure to delete mode ')
    flash('You have successfully deleted the mode.')

    # redirect to the modes page
    return redirect(url_for('admin.list_modes'))

#---########------
#-----Station view-------
@admin.route('/station', methods=['GET', 'POST'])
@login_required
def list_stations():
    """
    List all stations
    """
    check_admin()

    stations = Station.query.all()

    return render_template('admin/stations/stations.html',
                           stations=stations, title="Stations")


@admin.route('/stations/add', methods=['GET', 'POST'])
@login_required
def add_station():
    """
    Add a new station to the database
    """
    check_admin()

    add_station = True

    form = StationForm()
    if form.validate_on_submit():
        station = Station(name=form.name.data)
                      
        try:
            # add station to the database
            db.session.add(station)
            db.session.commit()
            flash('You have successfully added a new station.')
        except:
            # in case mode name already exists
            flash('Error: station name already exists.')

        # redirect to modes page
        return redirect(url_for('admin.list_stations'))

    # load station template
    return render_template('admin/stations/station.html', action="Add",
                           add_station=add_station, form=form,
                           title="Add Station")


@admin.route('/stations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_station(id):
    """
    Edit a station
    """
    check_admin()

    add_station = False

    station = Station.query.get_or_404(id)
    form = StationForm(obj=station)
    if form.validate_on_submit():
        station.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the station.')

        # redirect to the station page
        return redirect(url_for('admin.list_stations'))

    form.name.data = station.name
    return render_template('admin/stations/station.html', action="Edit",
                           add_station=add_station, form=form,
                           station=station, title="Edit Station")


@admin.route('/stations/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_station(id):
    """
    Delete a station from the database
    """
    check_admin()
    
    station = Station.query.get_or_404(id)
    route_station=RouteStation.query.filter(id==RouteStation.station_id).all()
    for route in route_station:
        user_station=RouteUser.query.filter(route.route_id==RouteUser.route_id).first()
        route_st=Route.query.filter(route.route_id==Route.id).all()
        print(route_st)
        for route_s in route_st:
            check_route=RouteStation.query.filter(route_s.id==RouteStation.route_id,
                                                  RouteStation.station_id != id).all()
            if(check_route is None):
                db.session.delete(route_s)   
        db.session.delete(user_station) 
        db.session.delete(route)
    try:
        db.session.delete(station)
        db.session.commit()
        flash('You have successfully deleted the station and records in routes, routes_user, and routes_station.')
    except:
        flash('Failure to delete station or records in db .')
        print('[ERROR] Failure to delete station ')
   
    flash('You have successfully deleted the station.')

    # redirect to the station page
    return redirect(url_for('admin.list_stations'))



###---------------
### Faults view
@admin.route('/faults', methods=['GET', 'POST'])
@login_required
def list_faults():
    """
    List all stations
    """
    check_admin()

    faults = Faults.query.all()

    return render_template('admin/faults/faults.html',
                           faults=faults, title="Faults")


@admin.route('/faults/add', methods=['GET', 'POST'])
@login_required
def add_fault():
    """
    Add a new fault to the database
    """
    check_admin()

    form = FaultForm()
    if form.validate_on_submit():
        fault = Faults(name=form.name.data)
        message_fault=form.message_fault.data 
        send_email_admin_fault(fault.name,message_fault)            
        try:
            # add fault to the database
            db.session.add(fault)
            db.session.commit()
            flash('You have successfully added a new fault.')
        except:
            # in case fault name already exists
            flash('Error: fault name already exists.')

        # redirect to fault page
        return redirect(url_for('admin.list_faults'))

    # load fault template
    return render_template('admin/faults/fault.html', action="Add", form=form,
                           title="Add Fault")


@admin.route('/faults/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_fault(id):
    """
    Delete a fault from the database
    """
    check_admin()

    fault = Faults.query.get_or_404(id)
    log_route=LogUser.query.filter(id==LogUser.fault_id).all()
    for log_rout in log_route:
        db.session.delete(log_rout)
    
    try:
        db.session.delete(fault)
        db.session.commit()
        flash('You have successfully deleted the fault and record LogUser')
    except:
        flash('Failure to delete fault or record in LogUser .')
        print('[ERROR] Failure to delete fault ')

    # redirect to the fault page
    return redirect(url_for('admin.list_faults'))

#-----Route view-------
@admin.route('/routes', methods=['GET', 'POST'])
@login_required
def list_routes():
    """
    List all routes
    """
    check_admin() 

    check_routes()     

    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode).all()
    station_user=RouteStation.query.join(Route,Station).all()  
    log_user=LogUser.query.join(Route,Faults).all() 
    photos=Photo.query.join(Route).filter(Photo.route_id != 1 ,Route.id==Photo.route_id).all()                                                                       
    return render_template('admin/routes/routes.html',title='Routes', file_names=routes_user, stations=station_user, logs=log_user,photos=photos)


def check_routes():
    print('[INFO ]check_routes and send sms')
    date_now=datetime.datetime.now()
    routes=Route.query.join(RouteStation).filter( Route.status_id==2 
                                                 ,Route.id==RouteStation.route_id
                                                 ,RouteStation.is_Done==0 or RouteStation.is_Open==0).all() 
    routes1=Route.query.join(RouteStation).filter( Route.status_id==1 
                                                 ,Route.id==RouteStation.route_id
                                                 ,RouteStation.is_Done==0 or RouteStation.is_Open==0).all() 
    
    users=[]
    if (routes is not None):
        for route in routes:
            date_route=date_now-route.date_start
            min_in_day=24*60*60
            if(divmod(date_route.days*min_in_day+date_route.seconds,60)[0]>20):
                route.status_id=4
                log_user=LogUser(fault_id=3,route_id=route.id)
                db.session.add(log_user) 
                db.session.add(route) 
                db.session.commit()
                users.append(RouteUser.query.join(User).filter(RouteUser.route_id==route.id).one())
        print(users)
        users=list(dict.fromkeys(users))
        print(users)  
        for user in users:
            message="Some routes have failed, please check the routes history!!!"
            #send_sms_user_message(message,user.user.name,user.user.phone)
        if (routes1 is not None):
            for route in routes1:
                route.status_id=4
 
                db.session.add(route) 
                db.session.commit()
                  
       
@admin.route('/routes/search', methods=['GET', 'POST'])
@login_required
def search_route():  
    check_admin()
    dates_array=[]
    station_user=""
    routes_user=""
    log_user=""
    if_all=0
    modes = Mode.query.filter(Mode.name != 'Basic').all()
    station = Station.query.filter(Station.name !='Basic').all()   
    users=User.query.filter(User.name != 'admin').all()
    status=StatusRoute.query.all() 
    fault=Faults.query.all()
       
    if request.method=="POST":
        try:
            qtc_data=request.form.get('selected_options','')
            print('[INFO] change : ' + qtc_data)
            select_option_user=request.form.get('selected_option_user','')
            select_option_mode=request.form.get('selected_option_mode','')
            select_option_station=request.form.get('selected_option_station','')
            select_option_status=request.form.get('selected_option_status','')
            select_option_fault=request.form.get('selected_option_fault','')
            dates_range=request.form.get('myCalendar','')
            if dates_range=="":
                print('[INFO ] Not dates change ')
                if_all=1

            else:
                dates_array=dates_range.split(' - ')
                dates_array[0]=dates_array[0] + ' 00:00:00'
                dates_array[1]=dates_array[1] + ' 59:59:59'
                print (dates_array)
                print(dates_range)
            if(qtc_data=="user"):
                if(if_all==1):
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,User.id==select_option_user
                                                                        ,Route.status_id==StatusRoute.id).all()
                    station_user=RouteStation.query.join(Station,Route,RouteUser).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id
                                                                              ,RouteUser.route_id==RouteStation.route_id
                                                                              ,RouteUser.user_id==select_option_user).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()                                                          
                
                    if_all=0
                else:
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,User.id==select_option_user
                                                                        ,Route.date_route.between(dates_array[0],dates_array[1])
                                                                        ,Route.status_id==StatusRoute.id).all()
                    station_user=RouteStation.query.join(Station,Route,RouteUser).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id
                                                                              ,RouteUser.route_id==RouteStation.route_id
                                                                              ,RouteUser.user_id==select_option_user).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()                                                          
                
            elif(qtc_data=="mode"):

                if(if_all==1):
                    routes_user=RouteUser.query.join(Route,StatusRoute,User,Mode).filter(RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==select_option_mode
                                                                        ,Route.mode_id==Mode.id
                                                                        ,RouteUser.user_id==User.id
                                                                        ,Route.status_id==StatusRoute.id).all()
               
                    station_user=RouteStation.query.join(Station,Route).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id , Route.mode_id==select_option_mode).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()  
                      
                    if_all=0
                else:
                    routes_user=RouteUser.query.join(Route,StatusRoute,User,Mode).filter(RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==select_option_mode
                                                                        ,Route.mode_id==Mode.id
                                                                        ,RouteUser.user_id==User.id
                                                                        ,Route.date_route.between(dates_array[0],dates_array[1])
                                                                        ,Route.status_id==StatusRoute.id).all()
               
                    station_user=RouteStation.query.join(Station,Route).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id , Route.mode_id==select_option_mode).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()  
                      
            elif(qtc_data=="station"):
                if(if_all==1):
                    routes_user=RouteUser.query.join(Route,StatusRoute,Mode,RouteStation).filter(RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,Route.status_id==StatusRoute.id
                                                                        ,RouteStation.route_id==RouteUser.route_id
                                                                        ,RouteStation.station_id==select_option_station).all()
              
                    
                    station_user=RouteStation.query.join(Route,Station).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id,RouteStation.station_id==select_option_station).all()  
                  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()  



                    if_all=0
                else:
                    routes_user=RouteUser.query.join(Route,StatusRoute,Mode,RouteStation).filter(RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,RouteStation.route_id==Route.id
                                                                        ,RouteStation.station_id==select_option_station
                                                                        ,Route.date_route.between(dates_array[0],dates_array[1])
                                                                        ,Route.status_id==StatusRoute.id).all()
              
                    station_user=RouteStation.query.join(Route,Station).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id,RouteStation.station_id==select_option_station).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()  
                 
            elif(qtc_data=="status"):
                if(if_all==1):
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,Route.status_id==select_option_status
                                                                        ,Route.status_id==StatusRoute.id).all()
                    station_user=RouteStation.query.join(Station,Route,StatusRoute).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id,Route.status_id==select_option_status).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()         
          
                    if_all=0
                else:
               
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,Route.mode_id==Mode.id
                                                                        ,Route.status_id==select_option_status
                                                                        ,Route.date_route.between(dates_array[0],dates_array[1])
                                                                        ,Route.status_id==StatusRoute.id).all()
                    station_user=RouteStation.query.join(Station,Route,StatusRoute).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id,Route.status_id==select_option_status).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(Route.id==LogUser.route_id).all()         
            
            elif(qtc_data=="fault"):
                if(if_all==1):
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode,LogUser).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,LogUser.route_id==Route.id
                                                                        ,LogUser.fault_id==select_option_fault
                                                                        ,Route.status_id==StatusRoute.id).all()
                
                    station_user=RouteStation.query.join(Station,Route,StatusRoute).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(LogUser.fault_id==select_option_fault).all()
                       
            
            

                    if_all=0
                else:               
                    routes_user=RouteUser.query.join(Route,User,StatusRoute,Mode,LogUser).filter(RouteUser.user_id==User.id
                                                                        ,RouteUser.route_id==Route.id
                                                                        ,LogUser.route_id==Route.id
                                                                        ,LogUser.fault_id==select_option_fault
                                                                        ,Route.date_route.between(dates_array[0],dates_array[1])
                                                                        ,Route.status_id==StatusRoute.id).all()
                
                    station_user=RouteStation.query.join(Station,Route,StatusRoute).filter(RouteStation.route_id==Route.id, Station.id==RouteStation.station_id).all()  
                    log_user=LogUser.query.join(Route,Faults).filter(LogUser.fault_id==select_option_fault).all()
                       
            
            
            return  render_template('admin/routes/route.html',modes=modes,users=users,status=status,station=station,faults=fault,file_names=routes_user,stations=station_user,log_user=log_user)
        except:
            print("Error")

    return render_template('admin/routes/route.html',title="Search Route",modes=modes,users=users,status=status,station=station,faults=fault)



@admin.route('/routes/photo/<int:id>', methods=['GET', 'POST'])
@login_required
def show_picture(id):
    """
    Show photos in a route from the database
    """
    check_admin()
    user_photo=Photo.query.filter(Photo.route_id==id).all()
    dropbox_folder_from_photos(user_photo) 
               
    photos_names=os.listdir('/home/webrgacv/webrobotapp/app/static/images/Temp/')
    files_names=photos_names
    return render_template('admin/routes/photo_route.html',title="Photos",files_names=files_names)
@admin.route('/display/<file_name>')
def display_image(file_name):

    return redirect(url_for('static', filename='images/Temp/' + file_name), code=301)
 
@admin.route('/routes/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_route(id):
    """
    Delete a route from the database
    """
    check_admin()
    route = Route.query.get_or_404(id)
    route_user=RouteUser.query.filter(id==RouteUser.route_id).one()
    route_station=RouteStation.query.filter(id==RouteStation.route_id).all()
    db.session.delete(route)
    print("Delete route")
    print("Delete route_user")
    db.session.delete(route_user)
    for routeS in route_station:
       db.session.delete(routeS)
    db.session.commit()
    flash('You have successfully deleted the route.')

    # redirect to the users page
    return redirect(url_for('admin.list_routes'))

@admin.route('/routes/delete/<int:route_id>,<int:station_id>', methods=['GET', 'POST'])
@login_required
def delete_station_route(route_id,station_id):
    """
    Delete a station from the route (db)
    """
    check_admin()
    id=route_id
    route_station=RouteStation.query.filter(RouteStation.route_id==route_id ,RouteStation.station_id==station_id).one()
    print(route_station)
    if(route_station is not None):
        db.session.delete(route_station)
        flash('You have successfully deleted the route.')
    check_status=RouteStation.query.filter(route_id== RouteStation.route_id).count()
    print(check_status)
    if(check_status >= 1):                                          
        check_status=RouteStation.query.filter(route_id== RouteStation.route_id
                                               ,RouteStation.is_Done==0).all()
        if(check_status is None):
           route_c=Route.query.get_or_404(id)
           route_c.status_id=1
           
        else:
            route_c=Route.query.get_or_404(id)
            route_c.status_id=4
          

           
    else:
        route_c=Route.query.get_or_404(id)
        db.session.delete(route_c)
       
    db.session.commit()                                               

    # redirect to the users page
    return redirect(url_for('admin.list_routes'))



