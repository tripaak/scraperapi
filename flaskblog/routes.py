from flask import render_template, flash, redirect, url_for,request,Response, send_from_directory
from flaskblog.forms import RegisterForm, LoginForm, UploadFileForm, RunScraper
from werkzeug.utils import secure_filename
from flaskblog.models import User, Post
from flaskblog import app, db
from flask_login import login_user, current_user, logout_user, login_required
import os



class DataStore():
    out_file_name = None

data = DataStore()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ('csv')

# Decorator route to add additional functionailty to function 
@app.route("/")
@app.route("/home")
def home():
    # render_template get html page and publish
    return render_template('home.html', title='Home')

@app.route("/manomano",methods=['POST','GET'])
def manomano():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],'manomano','in', secure_filename(file.filename)))
        flash("File is uploaded")
        return render_template('manomano.html', title='ManoMano Web Scraper',form=form) 
    return render_template('manomano.html', title='ManoMano Web Scraper',form=form) 

# @app.route("/upload",methods=['POST','GET'])
# def upload():
#     if request.method == 'POST':
#         print(request.files)

#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)

#         file = request.files['file']


#         if file.filename == '':
#             flash('No file selected for uploading')
#             return redirect(request.url)

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'],'manomano','in', filename))
#             flash('File successfully uploaded')
#             # return redirect('/')
#             return render_template('manomano.html')
#         else:
#             flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
#             return redirect(request.url)


@app.route("/run",methods=['POST','GET'])
def run_scraper():
    flash(f"running scraper for {os.listdir(app.config['UPLOAD_FOLDER'])}")
    from manomano import mano_scraper
    data.out_file_name = mano_scraper.run()
    flash(f'Scraping is done --> your file name is {data.out_file_name}')
    return render_template('manomano.html', title="SCraping Done")
    # return send_from_directory(os.path.join(os.getcwd(),'filesystem','manomano', 'out'),out_file_name ,as_attachment=True)
    # flash('Scraping Done !!')
    # return '''
    #     <html><body>
    #     <h>scraping is done </h>
    #     Hello. <a href="/downloadFile">Download File.</a>
    #     </body></html>
    #     '''

@app.route("/downloadFile")
def getPlotCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    print(os.path.join(os.getcwd(),'filesystem','manomano', 'out',data.out_file_name))
    csv = open(os.path.join(os.getcwd(),'filesystem','manomano', 'out',data.out_file_name))
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={data.out_file_name}.csv"})
       

@app.route("/about")
def about():
    # titile varibale is passed to html page
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User(username=form.username.data, email= form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(f"Account created for {form.username.data}", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and form.password.data == user.password:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccesful !', 'failure')    
    return render_template('login.html', form=form)   


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    image_file = url_for(f'static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file)