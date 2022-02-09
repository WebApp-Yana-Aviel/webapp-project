from flask import render_template,flash,request,abort,Response,jsonify,redirect,url_for,send_from_directory
from flask_login import login_required, current_user
from .cameraPi import execute_unix,turn_left,turn_right,forward,backward,stop,drive_stations
from . import home
import time
import datetime
import cv2
from .cameraPi import gen_frames,close_camera,tasks,delete_video_from_dropbox,dropbox_folder_from_photos,drive_station,dropbox_folder_from_videos,delete_files_from_images,delete_files_from_videos,delete_photo_from_dropbox
from .. import db
from ..models import Mode,Route,LogUser,Station,Photo,Video,RouteUser,RouteStation,StatusRoute
import os
from twilio.rest import Client
from time import sleep
import numpy as np
from sqlalchemy import func


# Camera sream in a manual and automatic states
@home.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(current_user.id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# manual state
@home.route('/profile_task', methods=['GET','POST'])
@login_required
def profile_task():
    clicked_id=""
    
    if request.method == 'POST':
        
        try:
            clicked_id=request.get_json()

            if clicked_id=='stopp':
               return tasks('stopL',current_user.id)
            elif clicked_id=='face':
              return tasks('face',current_user.id)
            elif clicked_id=='record':
              return tasks('record',current_user.id) 
            elif clicked_id=='grey':
              return tasks('grey',current_user.id)

            elif clicked_id=='capture':
              return tasks('capture',current_user.id)
  
            elif clicked_id=='aruco':
              return tasks('aruco',current_user.id)

            elif clicked_id=='facee':
              return tasks('face1',current_user.id)
          
            else:
              print('[INFO] Not task in a manual state')     
        except :
            print('[INFO] Not task in a manual state')  

    return render_template('home/manual.html',title='WebRobot')
  

#automatic state
@home.route('/automatic_state',methods=['POST','GET'])
@login_required
def automatic_state():
    if request.method=='POST':
        select_mode=request.form.get('modeSelect')
        select_station=request.form.getlist('stationSelect')
        ######
        # Add new Route  
        ###
        ### name of route
        timestamp = datetime.datetime.now()
        ts = timestamp.strftime("%A-%d-%B-%Y-%I:%M:%S%p")
        name_route=current_user.name+ts

        #delete duplicate from list
        select_station=list(dict.fromkeys(select_station))   
      
        route=Route(name=name_route,mode_id=select_mode,status_id=3)
        try:
            db.session.add(route)  # Adds new Route record to database
            db.session.commit()  # Commits all changes
            print('[INFO] Route :' + name_route+ 'add to the db (routes table)')
        except:
            # in case user name already exists
            print('[ERROR] Route :'+ name_route+ 'not add to the db (routes table)')
        ####
        #Add new stations
        ####
        for i in select_station:
            routes_stations=RouteStation(route_id=route.id,station_id=i)
 
            try:
                db.session.add(routes_stations)  # Adds new stations record to database
                db.session.commit()  # Commits all changes
                print('[INFO] Adds new stations in db')
            except:
                # in case station name already exists
                print('[ERROR] Stations of route:'+name_route+'not add to the db')
        
        #####
        #
        select_s = [int(x)-1 for x in select_station]
        select_s.sort() 
        
        #####
        # Add record to router_user
        ########      
        routeUser=RouteUser(route_id=route.id,user_id=current_user.id)
   
        try:
            db.session.add(routeUser)  # Adds new route_user record to database
            db.session.commit()  # Commits all changes
            print('[INFO] Adds new record in to route_user ')
        except:
            # in case already exists
            print('[ERROR]: Route_user:'+ current_user.name + 'not add to the db')         
        
        if 'select_route' in request.form: 
            route.status_id=2
            print('[INFO] Route :' +route.name+  '---start')
            try:
                db.session.commit()  # Commits all changes
                print('[INFO] Route in process -db- is successfully ')
            except:
                # in case  fault
                print('[ERROR]:Route is not change status in db ')
            os.system("espeak 'The quick brown fox'")
            a="Start a route ."
            message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
            execute_unix(message)
            time.sleep(0.1)
            drive_stations(select_s,route, (route.mode_id==3),current_user.id) 
            return automatic()
        elif 'save_route' in request.form: 
            print('[INFO] Route save in db....')
            return automatic()
            
    elif request.method=='GET':
            temp="Basic"
            modes = Mode.query.filter(Mode.name!=temp).all()
  
            stations = Station.query.filter(Station.name!=temp).all()  
            num_station=Station.query.with_entities(func.count(Station.id)).scalar()  
            print(num_station)
            return render_template('home/automatic.html',title='Automatic Mode',name=current_user.name,modes=modes,stations=stations,num_station=num_station)

@home.route('/automatic')
@login_required
def automatic():
       """
       List all mode
       """
       temp="Basic"
       modes = Mode.query.filter(Mode.name!=temp).all()
   
       """
       List all station
       """
       stations = Station.query.filter(Station.name!=temp).all() 
       num_station=Station.query.with_entities(func.count(Station.id)).scalar()  
       print(num_station)
       return render_template('home/automatic.html',title='Automatic Mode',name=current_user.name,modes=modes,stations=stations,num_station=num_station)


@home.route('/closeCamera', methods=['POST'])
def closeCamera():
    json = request.get_json()
    status = json['status']
    if status == "true":
        return close_camera('stop')
    else:
        return close_camera('open')
        
# home page that return 'index'
@home.route('/') 
def index():
    return render_template('home/index.html',title='WebRobot')

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)
    return render_template('home/admin_dashboard.html', title="Dashboard")

# profile page that return or manual state or automatic
@home.route('/profile',methods=['GET','POST']) 
@login_required
def profile_mode():
     if request.method == 'POST':
        try:       
  
            if request.form.get('mode') == 'ManualState':
                     
               return render_template('home/manual.html',title='WebRobot')
            elif request.form.get('mode') == 'AutomaticState' :
             
               temp="Basic"
               modes = Mode.query.filter(Mode.name!=temp).all()
           
               stations = Station.query.filter(Station.name!=temp).all()   
               num_station=Station.query.with_entities(func.count(Station.id)).scalar()  
               return render_template('home/automatic.html',title='Automatic Mode',name=current_user.name,modes=modes,stations=stations,num_station=num_station)
   
        except :
            print('[ERROR] not change mode (manual or automatic)')

     return render_template('home/profile.html',title='WebRobot')

# profile page that return 'profile'
@home.route('/profile') 
@login_required
def profile():
    check_routes()
    return render_template('home/profile.html', title='WebRobotApp', name=current_user.name)
  

def check_routes():
    print('[INFO ]check_routes and send sms')
    date_now=datetime.datetime.now()
    routes=Route.query.join(RouteStation,RouteUser).filter( Route.status_id==2 
                                                 ,Route.id==RouteStation.route_id
                                                 ,RouteUser.route_id==Route.id
                                                 ,RouteUser.user_id==current_user.id
                                                 ,RouteStation.is_Done == 0 or RouteStation.is_Open==0).all() 

    if (routes is not None):
        for route in routes:
            date_route=date_now-route.date_start
            min_in_day=24*60*60
            if(divmod(date_route.days*min_in_day+date_route.seconds,60)[0]>20):
                print(divmod(date_route.days*min_in_day+date_route.seconds,60)[0])
                route.status_id=4
                log_user=LogUser(fault_id=3,route_id=route.id)
                db.session.add(log_user) 
                db.session.commit()
 



                  
       
# history page that return 'history'
@home.route('/history',methods=['GET', 'POST']) 
@login_required
def history():
    return render_template('home/history.html',title='History')
       

@home.route('/history/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_route(id):
    """
    Delete a route from the database
  
    """
    route = Route.query.get_or_404(id)
    route_id=RouteUser.query.filter(RouteUser.route_id==id).one()
    route_user=RouteUser.query.get_or_404(route_id.id)
 
    route_id=RouteStation.query.filter(RouteStation.route_id==id).all()
    for route_i in route_id:
        db.session.delete(route_i)
    db.session.delete(route)
    db.session.delete(route_user)
    db.session.commit()
    flash('You have successfully deleted the route.')
    return redirect(url_for('home.history'))
    #return redirect(url_for('home.history_routes_all'))
 

@home.route('/history/start/<int:id>', methods=['GET'])
@login_required
def start_route(route_id):
    """
    Start a route from the database
  
    """
    route_id=id
    route_status=Route.query.get_or_404(route_id)
    route_status.status_id=2
    route_status.date_start=datetime.now()  
    db.session.commit()
    flash('You have successfully start the route.')
    select_stations=RouteStation.query.filter(RouteStation.route_id==route_id).all()

    select_s = []
    for r in select_stations:
        select_s.append(r.station_id-1)
   
    if len(select_s) > 1 :
         select_s.sort() 

    drive_stations(select_s,route_id,(route_status.mode_id==3),current_user.id)
 
    return redirect(url_for('home.history'))
    

@home.route('/history/delete/<string:file_name>', methods=['GET', 'POST'])
@login_required
def delete_photo(file_name):
    """
    Delete a photo from the database
  
    """
   
    id_photo=Photo.query.filter(Photo.name.ilike('%' + file_name + '%')).first()
  
    photo = Photo.query.get_or_404(id_photo.id)
    print('[INFO] Delete photo:'+photo.id)
    flash('You have successfully deleted the photo.')
    delete_photo_from_dropbox(file_name)
    db.session.delete(photo)
    db.session.commit()
    return redirect(url_for('home.history'))

@home.route('/download/<string:file_name>', methods=['GET', 'POST'])
def download_image(file_name):
    full_path ='/home/pi/webrobotapp/app/static/images/Temp'
    return send_from_directory(full_path, file_name) 

@home.route('/download/<string:file_name>', methods=['GET', 'POST'])
def download_video(file_name):
    full_path ='/home/pi/webrobotapp/app/static/video/Temp'
    return send_from_directory(full_path, file_name) 

@home.route('/history/delete_video/<string:file_name>', methods=['GET', 'POST'])
@login_required
def delete_video(file_name):
    """
    Delete a photo from the database
  
    """
    file_nameU=file_name.replace("mp4","avi")
    id_video=Video.query.filter(Video.name.ilike('%' + file_nameU + '%')).first()

    video = Video.query.get_or_404(id_video.id)
    print('[INFO] Delete video:' +video.id)
    flash('You have successfully deleted the video.')
    delete_video_from_dropbox(file_name)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('home.history'))
    

# search - history page
@home.route('/search',methods=['GET','POST']) 
@login_required
def search():
    files_names=""
    type_file=""
    if_all=0
    if request.method== "POST":
         try:
            select_option=request.form.get('selected_options','')
            dates_range=request.form.get('myCalendar','')
            if dates_range=="":
               print('[INFO] Not dates - history -search ')
               if_all=1
            else:          
               dates_array=dates_range.split(' - ')
               dates_array[0]=dates_array[0]+' 00:00:00.000000'
               dates_array[1]=dates_array[1]+' 59:59:59.999999'

            if select_option=='photos':
                type_file="images"
                if (if_all==1):
                    photo_user=Photo.query.filter(Photo.user_id==current_user.id).all()
                    if_all=0 
              
                else:    
                    photo_user=Photo.query.filter(Photo.user_id==current_user.id and (Photo.date_photo.between(dates_array[0],dates_array[1]))).all()

                dropbox_folder_from_photos(photo_user)
                 
                photos_names=os.listdir('/home/pi/webrobotapp/app/static/images/Temp/')
                files_names=photos_names
              
            elif select_option == 'videos':
                type_file="videos"
                if(if_all==1):
                    video_user=Video.query.filter(Video.user_id==current_user.id ).all()
                    if_all=0
                else:
                    video_user=Video.query.filter(Video.user_id==current_user.id , Video.date_video.between(dates_array[0],dates_array[1])).all()
             
                dropbox_folder_from_videos(video_user)
                 
                video_names=os.listdir('/home/pi/webrobotapp/app/static/videos/Temp/')
                files_names=video_names
                  
            elif select_option == 'routes':
                type_file="routes"
                temp="Basic"
                  
                if(if_all==1):   
                    routes_user=RouteUser.query.join(Route,Mode,StatusRoute).filter(RouteUser.user_id==current_user.id).all()
                
                    station_user=RouteStation.query.join(Station,Route,RouteUser).filter(RouteUser.user_id==current_user.id).all()  
                                                                                             
                    files_names=routes_user
                    photos=Photo.query.join(Route).filter(Photo.user_id==current_user.id,Photo.route_id != 1).all()
                    print(routes_user)
                    print(station_user)
                    print(photos)
                    if_all=0 
                else:
                      
                  
                    routes_user=RouteUser.query.join(Route,Mode,StatusRoute).filter(RouteUser.user_id==current_user.id
                                                                                 ,Route.date_route.between(dates_array[0],dates_array[1])).all()
                
                    station_user=RouteStation.query.join(Station,Route,RouteUser).filter(RouteUser.user_id==current_user.id
                                                                                 ,Route.date_route.between(dates_array[0],dates_array[1])).all()  
                  
                    files_names=routes_user
                    photos=Photo.query.join(Route).filter(Photo.user_id==current_user.id ,Photo.route_id != 1, Photo.date_photo.between(dates_array[0],dates_array[1])).all()
                    print(routes_user)
                    print(station_user)
                    print(photos)
              
                return render_template('home/history.html',title='History',file_names=files_names,type_file=type_file,stations=station_user,photos=photos)

         except:
           print('[ERROR] Search history page')
    return render_template('home/history.html',title='History',file_names=files_names,type_file=type_file)
 
@home.route('/routes/photo/<int:id>', methods=['GET', 'POST'])
@login_required
def show_picture(id):
    """
    Show photos in a route from the database
    """
    user_photo=Photo.query.filter(Photo.route_id==id).all()
    dropbox_folder_from_photos(user_photo)            
    photos_names=os.listdir('/home/pi/webrobotapp/app/static/images/Temp/')
    files_names=photos_names
    return render_template('home/show_photo.html',title="Photos",files_names=files_names)     
    
@home.route('/display/<file_name>')
def display_image(file_name):

    return redirect(url_for('static', filename='images/Temp/' + file_name), code=301)
              
@home.route('/display/<videoname>')
def display_video(videoname):
	
    return redirect(url_for('static', filename='videos/Temp/' + videoname), code=301)
         
@home.route('/left_side')
@login_required
def manual_left():
    #return drive_free("left")
    return turn_left()

@home.route('/right_side')
@login_required
def manual_right():
    #return drive_free("right")
    return turn_right()

@home.route('/up_side')
@login_required
def manual_up():
    return forward()

@home.route('/down_side')
@login_required
def manual_down():
    #return drive_free("backward")
    return backward()
    
@home.route('/stop')
@login_required
def manual_stop():
    return stop()
    #return drive_free("stop")
