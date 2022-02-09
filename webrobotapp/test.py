
import unittest

from flask_testing import TestCase
from flask import abort, url_for
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



if __name__ == '__main__':
    unittest.main()
