"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        u1 = User.signup("newtest1", "newemail1@email.com", "newpassword", None)
        uid1 = 1001
        u1.id = uid1

        u2 = User.signup("newtest2", "newemail2@email.com", "newpassword", None)
        uid2 = 2002
        u2.id = uid2
        
        u3 = User.signup("newtest3", "newemail3@email.com", "newpassword", None)
        uid3 = 3003
        u3.id = uid3

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)
        u3 = User.query.get(uid3)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2
        
        self.u3 = u3
        self.uid3 = uid3
         
        self.client = app.test_client()
        
        
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    

    def test_profile_page_no_following(self):
        """ Making sure that the profile page renders the correct users. """
        
        m1 = Message(
            id=1111,
            text="a test message1",
            user_id=self.uid1
        )

        db.session.add(m1)     
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
                
            res = client.get("/")
            html = res.get_data(as_text=True)
            
            msg1 = Message.query.get(1111)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f"<p>{msg1.text}</p>", html)
            
            
    # def test_profile_page_following(self):
    #     """ Making sure that the profile page renders the messages of those user is following. """
        
    #     m1 = Message(
    #         id=1111,
    #         text="a test message1",
    #         user_id=self.uid1
    #     )

        
    #     m2 = Message(
    #         id=2222,
    #         text="a test message2",
    #         user_id=self.uid2
    #     )

        
    #     m3 = Message(
    #         id=3333,
    #         text="a test message3",
    #         user_id=self.uid3
    #     )
    #     db.session.add(m1) 
    #     db.session.add(m2) 
    #     db.session.add(m3)      
    #     db.session.commit()

    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1
                
    #         res = client.get("/")
    #         html = res.get_data(as_text=True)
            
    #         msg1 = Message.query.get(1111)
    #         msg2 = Message.query.get(2222)
    #         msg3 = Message.query.get(3333)
            
    #         # user1 = User.query.get(self.uid1)
    #         # user2 = User.query.get(self.uid2)
    #         # user3 = User.query.get(self.uid3)
    #         self.u1.following.append(self.u2)
    #         db.session.commit()
    #         self.u1.following.append(self.u3)
    #         db.session.commit()

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn(f"<p>{msg1.text}</p>", html)
    #         self.assertIn(f"<p>{msg2.text}</p>", html)
    #         self.assertIn(f"<p>{msg3.text}</p>", html)
    #         # msg = Message.query.filter_by(text='Hello').first()
    #         # self.assertEqual(msg.text, "Hello")


    def test_users_page(self):
        """ Making sure that the profile page renders the correct users. """

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
                
            res = client.get("/users")
            html = res.get_data(as_text=True)
        

            self.assertEqual(res.status_code, 200)
            self.assertIn("@newtest1", html)
            self.assertIn("@newtest2", html)
            self.assertIn("@newtest3", html)
         
    