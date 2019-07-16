# MultiUserBlog
Part of the Udacity Nanodegree Program "Fullstack Web Developer". Browse a live version on gcloud: http://multi-user-blog-164807.appspot.com/

# User experience
This is a very basic version of a webblog. Users can
  - register, login, logout
  - write new posts
  - comment on posts
  - delete, like, edit posts
  - delete, edit comments

The website uses cookies to store the username safely locally. Passwords are only stored encrypted in the database.

# Code
The Code is written in Python and HTML, as well as very little CSS.
It uses the GoogleAppEngine's database together with the jinja2 template (webapp2).
One global variable "session" stores the user name, if the user is loged in and the according cookie is set correctly. This
is used to verify if liking/editing/commenting/etc. is allowed for the current user.

## - python

### main.py
  imports all the submodules, handles the routing, and defines the classes for the landingpage
  as well as for signup/login/logout
  
### app/handler.py
  defines most used functions for rendering html, setting/reading cookies, fetching user object for verifying login-cookie
  
### app/secure/secure.py
  very short module providing all necessary functionality for encryption (cookie, password)
  
### app/blog/blogpost.py
  - defines the database model for a blogpost
  - create/edit/delete existing post
  - renders single/all post(s), handle the like-action on blogposts
  
### app/blog/comments.py
  - defines database model for a comment
  - create/edit/delete existing comment

### app/blog/postlikes.py
  defines database model for a postlike
  
### app/blog/timestamp.py
  small helper modul for creating a current timestamp which is used when users edit their post/comment ("last edited")
  
### app/blog/user.py
  - defines database model for a user
  - register/login user
  - function for liking a post (only loged in users can like)
  
### app/blog/uservalidator.py
  provides a bunch of functios used in the registry/login process to verify that..
  - usernames are uniqe
  - usernames/password/email are apropiate values (regex check for length and characters)
  - passwords do match
  
## - HTML
all templates are located in app/templates. Files that start with an underscore are loaded into the html via "include", all the others are complete html files following the structure of the base.html file, utilizing the jinja2 template system.

### base.html
This is the basic structure, also noted down in base_skeleton.html Every pages renders this document, which has the following exchangable parts..
- title: title of the blog
- head: contains the title, could contain more meta tages
- header: contains login/logout/signup links, greeting message for loged in users
- htmlcontent: main part of the website
- footer: copyright, year, ...
