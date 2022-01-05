# Movie-Website-Project

#Heading 

---
There would like to introduce my project I was preparing for last 2-3 weeks.
This is my concept of website for watching different movies.



Website is implemented with Python in relation with Django Framework,
also using a PostgreSQL as a main database. It contains some options you 
can use there: 

<h5>1: Sign up on Website</h5>
<h5>2: Sign in on Website</h5>
<h5>3: Get / Edit / Delete Your Profile </h5>

----
<h5>4: Get Single Movie / Category of Movies / All Movies</h5>
<h5>5: Add / Delete Review to Movie</h5>
<h5>6: Add / Remove Like to Movie</h5>
<h5>7: Create Your Movie </h5>

----

<h5>8: Confirm your email address </h5>
<h5>9:  Reset Your Password</h5>
<h5>10: Write Something to Support Email </h5>
----
<h5>11: Get Movie Price in rubles / dollars </h5>
<h5>12: Watch Movie</h5>


<h1>Tools:</h1>

<h5>1: Requests Lib</h5>
<h5>2: Logging </h5>
<h5>3: Bs4</h5>
<h5>4: Os lib</h5>
<h5>5: Datetime, etc....</h5>
---

<h1>Preparation:</h1>
 
<h5>1: Need to install env. variables I specified down below:
<h5>DB'S VARIABLES:
</h5>
<h5>DB_NAME - NAME OF YOUR DATABASE</h5>
<h5>DB_PASSWORD - PASSWORD YOU SET UP WHEN WERE CREATING YOUR DATABASE</h5>
<h5>DB_HOST - HOST FOR YOUR DATABASE</h5>

----
<h5>SMTP VARIABLES:
</h5>
<h5>EMAIL_HOST_USER - HOST FOR YOUR SMTP SERVER</h5>
<h5>EMAIL_HOST_PASSWORD - HOST'S PASSWORD</h5>
<h5>SUPPORT_EMAIL - EMAIL ADDRESS FOR SUPPORT</h5>
<h5>ALSO NEED TO CREATE A 'SECRET_KEY' ENV. VAR. AND PUT VALUE, OR JUST REPLACE IT WITH YOUR GENERATED KEY</h5>
----
<h5>2: Installing modules:</h5>
<h5>pip install requests</h5>
<h5>pip install django</h5>
<h5>pip install psycopg2</h5>
<h5>pip install bs4</h5>

try to run server with command:
python manage.py runserver
