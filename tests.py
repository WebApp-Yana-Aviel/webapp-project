
import unittest

from flask_testing import TestCase
from flask import abort, url_for,jsonify
from app import create_app, db
from app.models import User,Mode,Station,Photo,Video,Route,Faults,StatusRoute,RouteStation,RouteUser,LogUser
import os

class TestBase(TestCase):

    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update()
        return app

    def setUp(self):
        """
        Will be called before every test
        """

        db.create_all()

        # create test admin user
        admin = User(name="admin",email="admin@admin.com",is_admin=True ,phone="+972549111254")
        admin.set_password("admin2021")
        # create test non-admin user
        user = User(name="test_user",email="test_user@admin.com",phone="+972549111254")
        user.set_password("test2021")

        # save users to database
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """

        db.session.remove()
        db.drop_all()


class TestModels(TestBase):

    def test_user_model(self):
        """
        Test number of records in User table
        """
        self.assertEqual(User.query.count(), 2)

    def test_mode_model(self):
        """
        Test number of records in mode table
        """

        # create test mode
        mode = Mode(name="Basic")

        # save mode to database
        db.session.add(mode)
        db.session.commit()

        self.assertEqual(Mode.query.count(), 1)

    def test_station_model(self):
        """
        Test number of records in station table
        """

        # create test role
        station = Station(name="Basic")

        # save station to database
        db.session.add(station)
        db.session.commit()

        self.assertEqual(Station.query.count(), 1)
  
    def test_fault_model(self):
        """
        Test number of records in fault table
        """

        # create test fault
        fault = Faults(name="Basic")

        # save fault to database
        db.session.add(fault)
        db.session.commit()

        self.assertEqual(Faults.query.count(), 1)
    
    def test_status_model(self):
        """
        Test number of records in status table
        """

        # create test status
        status = StatusRoute(name="Basic")

        # save status to database
        db.session.add(status)
        db.session.commit()

        self.assertEqual(StatusRoute.query.count(), 1)
    
    def test_route_model(self):
        """
        Test number of records in route table
        """

        # create test route
        route = Route(name="Basic",status_id=1,mode_id=1)

        # save route to database
        db.session.add(route)
        db.session.commit()

        self.assertEqual(Route.query.count(), 1)
    
    def test_Photo_model(self):
        """
        Test number of records in photo table
        """

        # create test photo
        photo = Photo(name="Basic",route_id=1,user_id=2)

        # save photo to database
        db.session.add(photo)
        db.session.commit()

        self.assertEqual(Photo.query.count(), 1)
    
    def test_video_model(self):
        """
        Test number of records in video table
        """

        # create test video
        video = Video(name="Basic",user_id=2,routeV_id=1)

        # save video to database
        db.session.add(video)
        db.session.commit()

        self.assertEqual(Video.query.count(), 1)
    
    
    def test_RouteStation_model(self):
        """
        Test number of records in RouteStation table
        """

        # create test RouteStation
        route_station = RouteStation(route_id=1,station_id=1)

        # save route_station to database
        db.session.add(route_station)
        db.session.commit()

        self.assertEqual(RouteStation.query.count(), 1)
    
    def test_LogUser_model(self):
        """
        Test number of records in LogUser table
        """

        # create test LogUser
        log_user = LogUser(route_id=1, fault_id=1)

        # save LogUser to database
        db.session.add(log_user)
        db.session.commit()

        self.assertEqual(LogUser.query.count(), 1)
        

class TestViews(TestBase):
                
    def test_reset_request_view(self):
        """
        Test that reaset_password is accessible without login
        """
        response = self.client.get(url_for('auth.reset_request'))
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('home.index'))
        self.assertEqual(response.status_code, 200) 

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test that logout link is inaccessible without login
        and redirects to login page then to logout
        """
        target_url = url_for('auth.logout')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_home_view(self):
        """
        Test that home is inaccessible without login
        and redirects to login page then to profile
        """
        target_url = url_for('home.profile')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
    

    def test_history_view(self):
        """
        Test that home is inaccessible without login
        and redirects to login page then to history
        """
        target_url = url_for('home.history')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
    def test_admin_dashboard_view(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page then to dashboard
        """
        target_url = url_for('home.admin_dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_user_view(self):
        """
        Test that departments page is inaccessible without login
        and redirects to login page then to user page
        """
        target_url = url_for('admin.list_users')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_mode_view(self):
        """
        Test that roles page is inaccessible without login
        and redirects to login page then to mode page
        """
        target_url = url_for('admin.list_modes')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_station_view(self):
        """
        Test that employees page is inaccessible without login
        and redirects to login page then to station page
        """
        target_url = url_for('admin.list_stations')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
    def test_fault_view(self):
        """
        Test that employees page is inaccessible without login
        and redirects to login page then to fault page
        """
        target_url = url_for('admin.list_faults')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
    def test_routes_view(self):
        """
        Test that employees page is inaccessible without login
        and redirects to login page then to routes page
        """
        target_url = url_for('admin.list_routes')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

class TestErrorPages(TestBase):

    def test_403_forbidden(self):
        # create route to abort the request with the 403 Error
        @self.app.route('/403')
        def forbidden_error():
            abort(403)

        response = self.client.get('/403')
        self.assertEqual(response.status_code, 403)
        #self.assertTrue("403 Forbidden" in response.data)

    def test_404_not_found(self):
        @self.app.route('/404')
        def forbidden_error():
            abort(404)

        response = self.client.get('/nothinghere')
        self.assertEqual(response.status_code, 404)
        #self.assertTrue(b'404 Forbidden' in response)

    def test_500_internal_server_error(self):
        # create route to abort the request with the 500 Error
        @self.app.route('/500')
        def internal_server_error():
            abort(500)

        response = self.client.get('/500')
        self.assertEqual(response.status_code, 500)
        #self.assertTrue(b'500 Forbidden' in response.data)

if __name__ == '__main__':
    unittest.main()
