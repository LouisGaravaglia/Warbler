"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()
        

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    def test_repr(self):
        """Testing to make sure repr method works"""
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        user = str(u)
        
        self.assertIn(": testuser, test@test.com>", user)
        
        
    def test_is_following(self):
        """Testing to make sure is_following successfully detect when user1 is following user2"""
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        
        self.assertEqual(self.u1.following[0].id, self.uid2)
        self.assertEqual(self.u2.followers[0].id, self.uid1)
        
        
        
        

    # Does is_following successfully detect when user1 is following user2?
    # Does is_following successfully detect when user1 is not following user2?
    # Does is_followed_by successfully detect when user1 is followed by user2?
    # Does is_followed_by successfully detect when user1 is not followed by user2?
    # Does User.create successfully create a new user given valid credentials?
    # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
    # Does User.authenticate successfully return a user when given a valid username and password?
    # Does User.authenticate fail to return a user when the username is invalid?
    # Does User.authenticate fail to return a user when the password is invalid?
