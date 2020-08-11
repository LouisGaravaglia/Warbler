"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from bs4 import BeautifulSoup
import urllib as request
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

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
        
        u4 = User.signup("weirdname", "weirdemail@email.com", "newpassword", None)
        uid4 = 4004
        u4.id = uid4

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)
        u3 = User.query.get(uid3)
        u4 = User.query.get(uid4)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2
        
        self.u3 = u3
        self.uid3 = uid3
        
        self.u4 = u4
        self.uid4 = uid4
         
        self.client = app.test_client()
        
        
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    

    # def test_profile_page_no_following(self):
    #     """ Making sure that the profile page renders the correct users. """
        
    #     m1 = Message(
    #         id=1111,
    #         text="a test message1",
    #         user_id=self.uid1
    #     )

    #     db.session.add(m1)     
    #     db.session.commit()

    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1
                
    #         res = client.get("/")
    #         html = res.get_data(as_text=True)
            
    #         msg1 = Message.query.get(1111)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn(f"<p>{msg1.text}</p>", html)
            
            
    # def test_users_page(self):
    #     """ Making sure that the users page renders all users. """

    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1  
        
    #         res = client.get("/users")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("@newtest1", html)
    #         self.assertIn("@newtest2", html)
    #         self.assertIn("@newtest3", html)
            
    
    # def test_users_page_posts(self):
    #     """ Making sure that the users page only renders their posts. """

    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1
            
    #         m2 = Message(
    #         id=2222,
    #         text="a test message2",
    #         user_id=self.uid2
    #     )
    #         db.session.add(m2)      
    #         db.session.commit() 
          
    #         res = client.get(f"/users/{self.uid2}")
    #         html = res.get_data(as_text=True)
        
    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("a test message2", html)
    
    
    # def test_is_following_users(self):
    #     """Testing to make sure the users appear of those their following"""
        
    #     self.u1.following.append(self.u2)
    #     db.session.commit()
        
    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1
        
    #         res = client.get(f"/users/{self.uid1}/following")
    #         html = res.get_data(as_text=True)
    
    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("@newtest2", html)
    #         self.assertIn("@newtest1", html)
            
    
    # def test_followers(self):
    #     """Testing to make sure the users appear for those who are following user"""
        
    #     self.u1.followers.append(self.u2)
    #     db.session.commit()
        
    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.uid1
        
    #         res = client.get(f"/users/{self.uid1}/followers")
    #         html = res.get_data(as_text=True)
    
    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("@newtest2", html)
    #         self.assertIn("@newtest1", html)
            
            
    # def test_users_search(self):
        
    #     with self.client as client:
            
    #         res = client.get("/users?q=test")
    #         html = res.get_data(as_text=True)

    #         self.assertIn("@newtest1", html)
    #         self.assertIn("@newtest2", html)
    #         self.assertIn("@newtest3", html)               

    #         self.assertNotIn("@weirdname", html)


    def setup_likes(self):
        m1 = Message(text="message1", user_id=self.uid2)
        m2 = Message(text="message2", user_id=self.uid2)
        m3 = Message(id=9876, text="message3", user_id=self.uid1)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.uid1, message_id=9876)

        db.session.add(l1)
        db.session.commit()

    def test_user_show_with_likes(self):
        self.setup_likes()

        with self.client as client:
            res = client.get(f"/users/{self.uid1}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn("@newtest1", html)
            soup = BeautifulSoup(html, 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("1", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

         
    