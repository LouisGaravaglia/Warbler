"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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
    

    def test_profile_page_with_POST(self):
        """ Making sure that the profile page renders the messages correctly after POST. """

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
                
            res = client.post("/messages/new", data={"text": "Hello"})
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 302)
            msg = Message.query.filter_by(text='Hello').first()
            self.assertEqual(msg.text, "Hello")
            
    
    def test_profile_page(self):
        """ Making sure that the profile page renders the messages correctly. """

        with self.client as client:
            msg = Message(text="My first post", timestamp="11 August 2020")
            self.u1.messages.append(msg)
            db.session.commit()
            
            res = self.client.get(f"/users/{self.uid1}")
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn("<p>My first post</p>", html)
            self.assertIn('<span class="text-muted">11 August 2020</span>', html)
            
    
    def test_add_no_session(self):
        with self.client as client:
            res = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))
            
            
    def test_add_invalid_user(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 43

            res = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))
            
            

            
    def test_invalid_message_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
            
            resp = c.get('/messages/99999999')

            self.assertEqual(resp.status_code, 404)
            
            
    def test_message_delete(self):
    
        m = Message(
            id=1234,
            text="a test message",
            user_id=self.uid1
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            m = Message.query.get(1234)
            self.assertIsNone(m)
    
    def test_unauthorized_message_delete(self):
    
        u = User.signup(username="unauthorized-user",
                        email="testtest@test.com",
                        password="password",
                        image_url=None)
        u.id = 76543

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.uid1
        )
        db.session.add_all([u, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.uid1
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m) 
            
    
  
            