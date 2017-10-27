from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'as8d7f98a!@qw546era#$#@$' 
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    content = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content= content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request

def require_login():
    allowed_routes = ['login', 'register','signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/newblog', methods=['POST', 'GET'])
def newblog():

    no_name=""
    no_content=""
    no_anything=""

    if request.method == 'POST':
        blog_name = request.form['new_blog_title']
        blog_content = request.form['new_blog_post']
        new_blog = Blog(blog_name, blog_content)

    

        if blog_name=="":
            no_name = "Please enter a title"
        if blog_content=="":
            no_content="Please make a blog to go with your beautiful title"

        if not no_name and not no_content:
            db.session.add(new_blog)
            db.session.commit()
            id=new_blog.id
            print(id)
            return redirect ('/blog?blogid='+str(id))
        else:
            return render_template('newblogpost.html', no_name=no_name, no_content=no_content)

    else:
        return render_template ('newblogpost.html', title="New Blog Post")
         



@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blogposts.html',title="Blogs!", 
        blogs=blogs)

@app.route('/blog', methods=['POST','GET'])
def blog():
    
    id=request.args.get ('blogid')
    blogs=Blog.query.filter_by(id=id).first()
    return render_template('blog.html',blogpost=blogs)



if __name__ == '__main__':
    app.run()