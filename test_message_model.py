"""Message model tests."""

# Using the following to run my tests: FLASK_ENV=production python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
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
        

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

        
    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(text="My first post", timestamp="11 August 2020")
        self.u1.messages.append(msg)
        db.session.commit()

        self.assertEqual("My first post", self.u1.messages[0].text)
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.uid1, self.u1.messages[0].user_id)
        self.assertEqual(msg.timestamp, self.u1.messages[0].timestamp)
        
    
    def test_message_likes(self):
        """Testing to see if likeing a message works."""

        msg = Message(text="My first post", timestamp="11 August 2020")
        self.u1.messages.append(msg)
        db.session.commit()
        
        self.u2.likes.append(msg)
        
        self.assertEqual("My first post", self.u2.likes[0].text)
        self.assertEqual(self.uid1, self.u2.likes[0].user_id)
        self.assertEqual(len(self.u2.likes), 1)
     
        
        