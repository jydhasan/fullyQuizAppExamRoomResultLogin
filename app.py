import base64
from datetime import datetime
from flask import Flask, Response, abort, jsonify, render_template, request, redirect, send_file, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import random
import sqlite3
import json
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# create an instance of the Flask class
app = Flask(__name__, static_url_path='/static', static_folder='static')

# add configurations and database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.secret_key = 'yoursecretkeyhere'


# initialize the database instance
db = SQLAlchemy(app)


# ===================================================================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Simple user model for demonstration purposes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    uname = db.Column(db.String(50),  nullable=False)
    role = db.Column(db.String(50),  nullable=False)
    subrole = db.Column(db.String(50),  nullable=False)
    schoolname = db.Column(db.String(50),  nullable=False)
    thana = db.Column(db.String(50),  nullable=False)
    district = db.Column(db.String(50),  nullable=False)
    email = db.Column(db.String(50),  nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


# Helper function to get a user from the database by username
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


# Helper function to add a new user to the database
# def add_user(username, password):
#     user = User(username=username, password=password)
def add_user(register_data):
    user = User(username=register_data['phone'],
                uname=register_data['uname'],
                role=register_data['role'],
                subrole=register_data['subcategory'],
                schoolname=register_data['schoolname'],
                thana=register_data['thana'],
                district=register_data['district'],
                email=register_data['email'])
    db.session.add(user)
    db.session.commit()


# Load a user given its ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['phone']
        user = get_user_by_username(username)
        # if user true then login
        if user:
            login_user(user)
            flash('Logged in successfully.', 'success')
            # return redirect(url_for('dashboard'))
            return redirect(url_for('home'))

        # if user and user.password == password:
        #     login_user(user)
        #     flash('Logged in successfully.', 'success')
        #     return redirect(url_for('dashboard'))
        else:
            flash('Unregister phone number register or Please try again.', 'error')

    return render_template('login.html')


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return f'Hello, {current_user.username}! This is your dashboard.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # request form data from register.html
        register_data = request.form
        username = request.form['phone']
    #     password = request.form['password']
        existing_user = get_user_by_username(username)

        if existing_user:
            flash(
                'Userphone already exists. Please choose a different username.', 'error')
        else:
            # add_user(username, password)
            # add register_data to add_user function
            add_user(register_data)
            flash('User registered successfully. You can now log in.', 'success')

    return redirect(url_for('login'))


# ===================================================================================================


# create students model
class QuestionList(db.Model):
    __tablename__ = 'QuestionList'
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    minutes = db.Column(db.String(100), nullable=False)
    tablename = db.Column(db.String(100), nullable=False)
    resulttable = db.Column(db.String(100), nullable=False)
    qstart = db.Column(db.String(100), nullable=False)
    qend = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Add more fields as needed

    def __init__(self, fid, title, minutes, tablename, resulttable, qstart, qend):
        self.fid = fid
        self.title = title
        self.minutes = minutes
        self.tablename = tablename
        self.resulttable = resulttable
        self.qstart = qstart
        self.qend = qend


# Assuming you have imported the required modules and set up the app and db instances.

# Define the model class following the Python naming convention


class CreateCategory(db.Model):
    __tablename__ = 'catagory_table'
    id = db.Column(db.Integer, primary_key=True)
    catagory = db.Column(db.String(100))
    catagoryLavel = db.Column(db.String(200))
    catagorySubject = db.Column(db.String(200))

    # Add a composite unique constraint for catagoryLavel and catagorySubject
    __table_args__ = (
        db.UniqueConstraint('catagoryLavel', 'catagorySubject'),
    )

    def __init__(self, catagory, catagoryLavel, catagorySubject):
        self.catagory = catagory
        self.catagoryLavel = catagoryLavel
        self.catagorySubject = catagorySubject

# Create a route to add a category


@app.route('/create_catagory', methods=['GET', 'POST'])
def create_catagory():
    if request.method == 'POST':
        def to_camel_case(input_string):
            # Split the string into words (removing any leading/trailing spaces)
            words = input_string.strip().split()

            # Remove any non-alphabetic characters from the beginning of the first word
            first_word = words[0]
            first_word = ''.join(filter(str.isalpha, first_word))

            # Capitalize the first letter of the first word
            first_word = first_word.capitalize()

            # Capitalize the first letter of each subsequent word
            camel_case_string = first_word + \
                ''.join(word.capitalize() for word in words[1:])

            return camel_case_string

        # Get the data from the form
        catagory_lavel = request.form['catagoryLavel']
        catagory_subject = request.form['catagorySubject']
        catagory = request.form['catagory_name']

        # Convert the catagoryLavel and catagorySubject to camel case
        catagory = to_camel_case(catagory)
        catagory_lavel = to_camel_case(catagory_lavel)
        catagory_subject = to_camel_case(catagory_subject)

        # Check if the combination of catagoryLavel and catagorySubject already exists
        check_subject = CreateCategory.query.filter_by(
            catagoryLavel=catagory_lavel, catagorySubject=catagory_subject).first()

        if check_subject:
            flash('This subject already exists within this category level.')
            return redirect(url_for('create_catagory'))
        else:
            catagory = CreateCategory(
                catagory=catagory,
                catagoryLavel=catagory_lavel,
                catagorySubject=catagory_subject
            )
            db.session.add(catagory)
            db.session.commit()
            flash('Record was successfully added')
    return render_template('create_catagory.html')


# Create a new route to show the data by alphabetical order
@app.route('/show_catagory', methods=['GET'])
def show_categories():
    categories = CreateCategory.query.order_by(
        CreateCategory.catagory, CreateCategory.catagoryLavel).all()
    return render_template('show_catagory.html', categories=categories)


# # show catagorySubject by catagoryLavel
@app.route('/show_catagory/<catagoryLavel>', methods=['GET'])
def show_catagory(catagoryLavel):
    categories = CreateCategory.query.filter(
        (CreateCategory.catagoryLavel == catagoryLavel) | (
            CreateCategory.catagory == catagoryLavel)
    ).order_by(CreateCategory.catagorySubject).all()

    return render_template('show_catagory_level.html', categories=categories)


# show catagorySubject by catagoryLavel
@app.route('/<id>')
def get_subject(id):
    subject = CreateCategory.query.filter_by(id=id).first()
    showQuestions = QuestionList.query.filter_by(fid=id).all()
    return render_template('subject.html', subject=subject, showQuestions=showQuestions)


# create a dynameic table
def create_dynamic_table(entry_id):
    table_name = f"new_table_{entry_id}"

    class DynamicTable(db.Model):
        __tablename__ = table_name
        id = db.Column(db.Integer, primary_key=True)
    return DynamicTable


def create_result_table(entry_id):
    result_table = f"result_table_{entry_id}"

    class DynamicTableResult(db.Model):
        __tablename__ = result_table
        id = db.Column(db.Integer, primary_key=True)
        uname = db.Column(db.String(100))
        uphone = db.Column(db.String(100), unique=True)
        schoolname = db.Column(db.String(100))
        matchcount = db.Column(db.String(100))
        mismatchcount = db.Column(db.String(100))
        totalcount = db.Column(db.String(100))
        grade = db.Column(db.String(100))

    return DynamicTableResult


# create excel quiz for catagorysubject


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # save excel data to database
    if request.method == 'POST':
        id = request.form['id']

        # another data for questionlist
        fid = request.form['id']
        title = request.form['title']
        minutes = request.form['minutes']

        entry_id = random.randrange(1, 9999999)
        DynamicTable = create_dynamic_table(entry_id)
        DynamicTableResult = create_result_table(entry_id)
        DynamicTableResult.__table__.create(db.engine)
        # Create the table in the database
        DynamicTable.__table__.create(db.engine)
        file = request.files['inputFile']
        # file.save(file.filename)
        df = pd.read_excel(file.filename)
        df.to_sql(DynamicTable.__tablename__, con=db.engine,
                  if_exists='replace', index=True)  # Fix here

        student = QuestionList(fid=fid, title=title,
                               minutes=minutes, tablename=DynamicTable.__tablename__, resulttable=DynamicTableResult.__tablename__, qstart='0', qend='0')
        db.session.add(student)
        db.session.commit()

        flash('Record was successfully added')
        return redirect(url_for('get_subject', id=id))
    else:
        return redirect(url_for('get_subject'))


# fetch data from questionlist table
@app.route('/get_data/<string:entry_id>', methods=['GET'])
@login_required
def get_data(entry_id):
    # use sqlite to get data from database
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {entry_id}")
    data = cursor.fetchall()
    conn.close()

    # new conn and cursor for timer
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT minutes FROM QuestionList WHERE qstart = 1")
    timerQ = cursor.fetchall()
    conn.close()
    # new conn and cursor for title
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT *FROM QuestionList WHERE qstart = 1")
    title_data = cursor.fetchall()
# print title_data
    for row in title_data:
        # print(row[1])
        title = row[2]
        fid = row[1]
        # print(title)
        cursor.execute(
            # select from catagory_table where id = fid
            f"SELECT * FROM catagory_table WHERE id = {fid}")
        rows = cursor.fetchall()
        for row in rows:
            # print(row[1])
            titleAc = row[1]
            titleLavel = row[2]
            titleSubject = row[3]
    # show notice here  for exam now
    cursor.execute(
        # select details from no_exam_now table
        "SELECT * FROM no_exam_now")
    quizNotice = cursor.fetchall()
    conn.close()
# show notice here  for exam now
    # show QuizImage
    files = QuizImage.query.all()
    for file in files:
        file.image_base64 = base64.b64encode(file.image).decode('utf-8')
    # return render_template('show_quiz_image.html', files=files)

    # return data
    return render_template('show_quiz.html', data=data, entry_id=entry_id, timerQ=timerQ, files=files, title=title, titleAc=titleAc, titleLavel=titleLavel, titleSubject=titleSubject, quizNotice=quizNotice)


@app.route('/get_data/quiz_ans', methods=['POST'])
def quiz_ans():
    # Access form data using request.form dictionary
    form_data = request.form
    entry_id = request.form['entry_id']

    # Establish connection to SQLite database
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()

    # Execute the SELECT query and fetch all data
    cursor.execute(f"SELECT * FROM {entry_id}")
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Converted extracted_data to a dictionary where each element is a key with value "zahid"
    extracted_data = {f"zahid_{i}": "zahid" for i in range(len(data))}

    matches = []
    mismatches = []
    for key, value in form_data.items():
        if value in extracted_data.values():
            matches.append(value)
        else:
            mismatches.append(value)

    # Count the number of matches and mismatches
    match_count = len(matches)
    mismatch_count = len(mismatches)-1
    extracted_data_count = len(extracted_data)

    # Count the number of elements in the extracted_data dictionary
    extracted_data_count = len(extracted_data)

    # Calculate the grade GPA based on match_count and extracted_data_count
    grade_percentage = (match_count / extracted_data_count) * 100

    # Calculate the corresponding grade based on the grade_percentage
    if grade_percentage < 50:
        grade = "Fail"
    elif grade_percentage < 60:
        grade = "Bellow 50"
    elif grade_percentage < 70:
        grade = "A-"
    elif grade_percentage < 80:
        grade = "A"
    else:
        grade = "A+"

    # Given input string
    input_string = entry_id

    # Removing the prefix "new_table_"
    number_part = input_string.replace("new_table_", "")

    # Converting the number_part to an integer (if needed)
    number = int(number_part)

    # Create the new string with "result_table" as prefix and the extracted number as suffix
    result_table_string = "result_table_" + str(number)

    # connect to sqlite
    # conn = sqlite3.connect('instance/db.sqlite')
    # cursor = conn.cursor()
    # # insert data to result table
    # cursor.execute(f"INSERT INTO {result_table_string} (uname,uphone,schoolname,matchcount,mismatchcount,totalcount,grade) VALUES (?,?,?,?,?,?,?)", (
    #     current_user.uname, current_user.username, current_user.schoolname, match_count, mismatch_count, extracted_data_count, grade))
    # conn.commit()
    # conn.close()

    try:
        # connect to sqlite
        conn = sqlite3.connect('instance/db.sqlite')
        cursor = conn.cursor()
        # insert data to result table
        cursor.execute(f"INSERT INTO {result_table_string} (uname,uphone,schoolname,matchcount,mismatchcount,totalcount,grade) VALUES (?,?,?,?,?,?,?)", (
            current_user.uname, current_user.username, current_user.schoolname, match_count, mismatch_count, extracted_data_count, grade))
        conn.commit()
        conn.close()

        # Redirect the user to a success URL or show a success message
        # For example, if you're using Flask web framework:
        # return redirect('/success_url')

    except sqlite3.IntegrityError as e:
        # Handle the UNIQUE constraint violation
        # Redirect the user to an error URL or show an error message
        # For example, if you're using Flask web framework:
        # return redirect('/error_url')
        return "<h1>You already Submit a Quiz</h1>"

        # If you're not using a web framework, you can print an error message
        # or handle the error in any way that suits your application's logic.
        # print("Error: UNIQUE constraint violation occurred.")

    # Return the matches count, mismatches count, extracted_data count, and grade GPA as JSON
    return jsonify({
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "extracted_data_count": extracted_data_count,
        "grade": grade,
        "entry_id": result_table_string,
        "current_user": current_user.username,
        "uname": current_user.uname,
        "collage_name": current_user.schoolname
    })

    # # calculate  grade GPA
    # grade = (match_count/extracted_data_count)*100

    # # Return the matches count, mismatches count, and extracted_data count as JSON
    # return jsonify({
    #     "match_count": match_count,
    #     "mismatch_count": mismatch_count,
    #     "extracted_data_count": extracted_data_count
    # })

    # Return the matches and mismatches count as JSON
    # return jsonify({"match_count": match_count, "mismatch_count": mismatch_count})

    # Check if each value in extracted_data is present in form_data values
    # matches = []
    # mismatches = []
    # for key, value in form_data.items():
    #     if value in extracted_data.values():
    #         matches.append(value)
    #     else:
    #         mismatches.append(value)

    # # Return the matches and mismatches as JSON
    # return jsonify({"matches": matches, "mismatches": mismatches})

    # Check if each value in extracted_data is present in form_data values
    # match_count = 0
    # for value in form_data.values():
    #     if value in extracted_data.values():
    #         match_count += 1

    # # Return the total number of matches as JSON
    # return jsonify({"match_count": match_count})


# def fetch_categories():
#     conn = sqlite3.connect('instance/db.sqlite')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM catagory_table")
#     data = cursor.fetchall()
#     conn.close()

    # categories = {}
    # for row in data:
    #     category = row[1]  # Assuming 'catagory' is the second column (index 1)
    #     # Assuming 'catagoryLavel' is the third column (index 2)
    #     category_level = row[2]

    #     if category in categories:
    #         categories[category].append(category_level)
    #     else:
    #         categories[category] = [category_level]

    # return categories


def fetch_categories():
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catagory_table")
    data = cursor.fetchall()
    conn.close()

    categories = {}
    for row in data:
        category = row[1]  # Assuming 'catagory' is the second column (index 1)
        # Assuming 'catagoryLavel' is the third column (index 2)
        category_level = row[2]

        if category in categories:
            if category_level not in categories[category]:
                categories[category].append(category_level)
        else:
            categories[category] = [category_level]

    return categories


@app.route('/login_register')
def login_register():
    categories = fetch_categories()
    return render_template('login_register.html', categories=categories)


@app.route('/get_subcategories/<category>')
def get_subcategories(category):
    categories = fetch_categories()
    subcategories = categories.get(category, [])
    return jsonify(subcategories)


# create route for resulttable page
@app.route('/result/<resulttable>')
@login_required
def result_table(resulttable):
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {resulttable}")
    data = cursor.fetchall()
    conn.close()
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Define the path for the Excel file
    excel_file_path = f'instance/{resulttable}.xlsx'

    # Export the DataFrame to Excel
    df.to_excel(excel_file_path, index=False)

    # Return the Excel file for download
    return send_file(excel_file_path, as_attachment=True)

    # return data
    # return render_template('result_table.html', data=data)


# create quiz exam hall room route
@app.route('/quiz_exam_hall_room')
def quiz_exam_hall_room():
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM QuestionList WHERE qstart = 1")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        entry_id = row[4]
        # if entry_id is found, redirect to the 'get_data' function
        if entry_id:
            return redirect(url_for('get_data', entry_id=entry_id))

    # If no entry_id is found in any row, return the "No exam now" message
    return redirect(url_for('no_exam_now'))


# create a model for no exam now
class NoExamNow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    noexamnow = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"NoExamNow('{self.noexamnow}')"


# create no exam now route
@app.route('/no_exam_now', methods=['GET', 'POST'])
def no_exam_now():
    # check method
    if request.method == 'POST':
        # Get data from form
        noexamnow = request.form['noexamnow']
        details = request.form['details']
 # Check if the row with the given 'noexamnow' value exists in the database
        existing_entry = NoExamNow.query.filter_by(noexamnow=noexamnow).first()

        if existing_entry:
            # If the row exists, update its 'details' attribute with the new value
            existing_entry.noexamnow = noexamnow
            existing_entry.details = details
            db.session.commit()
        else:
            # If the row doesn't exist, create a new entry in the 'NoExamNow' table
            new_entry = NoExamNow(noexamnow=noexamnow, details=details)
            db.session.add(new_entry)
            db.session.commit()
        return redirect(url_for('no_exam_now'))
    else:
        # fetch data from NoExamNow
        noexamnow = NoExamNow.query.all()
        return render_template('no_exam_now.html', noexamnow=noexamnow)


# create route for notice
@app.route('/notice')
def notice():
    return render_template('notice.html')


# create start_quiz route
@app.route('/start_quiz', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'POST':
        # Get data from form
        data = request.form['tablename']

        # Set qstart and qend values to 0 for all rows
        conn = sqlite3.connect('instance/db.sqlite')
        cursor = conn.cursor()
        cursor.execute("UPDATE QuestionList SET qstart = 0, qend = 0")
        conn.commit()

        # Update qstart to 1 for the specific tablename
        cursor.execute(
            "UPDATE QuestionList SET qstart = 1 WHERE tablename = ?", (data,))
        conn.commit()
        conn.close()

        return redirect(url_for('quiz_exam_hall_room'))

    # Handle GET request here if needed
    # ...


# end quiz exam hall room route


@app.route('/end_quiz', methods=['GET', 'POST'])
def end_quiz():
    if request.method == 'POST':
        # Get data from form
        data = request.form['tablename']

        # Set qstart and qend values to 0 for all rows
        conn = sqlite3.connect('instance/db.sqlite')
        cursor = conn.cursor()
        cursor.execute("UPDATE QuestionList SET qstart = 0, qend = 0")
        conn.commit()

        # # Update qstart to 1 for the specific tablename
        # cursor.execute(
        #     "UPDATE QuestionList SET qstart = 1 WHERE tablename = ?", (data,))
        # conn.commit()
        # conn.close()

        return redirect(url_for('quiz_exam_hall_room'))
    # test time count down


# @app.route('/test_time_count_down')
# def test_time_count_down():
#     conn = sqlite3.connect('instance/db.sqlite')
#     cursor = conn.cursor()
#     cursor.execute("SELECT minutes FROM QuestionList WHERE qstart = 1")
#     rows = cursor.fetchall()
#     conn.close()
#     return render_template('test.html', rows=rows)

#     test time count down


# create admin page route
@app.route('/admin')
@login_required
def admin():
    # get username
    username = current_user.username
    if username == '01713905601':
        return render_template('admin_page.html')
    else:
        return redirect(url_for('home'))
# create home page


@app.route('/')
def home():
    # create a QuerySet of all the rows in the 'QuestionList' table wheir qstart = 1
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM QuestionList WHERE qstart = 1")
    rows = cursor.fetchall()
    conn.close()
    if rows == []:
        rows = 'No exam now'
        ntitle = NoExamNow.query.all()
        title = ' '.join(row.noexamnow for row in ntitle)
        details = ' '.join(row.details for row in ntitle)
        noticedata = rows+" "+title+" "+details

        files = FileUpload.query.all()
        for file in files:
            file.image_base64 = base64.b64encode(file.image).decode('utf-8')

        return render_template('home_page.html', rows=noticedata, files=files)
    else:
        third_columns = ' '.join(row[2] for row in rows)
        fid = ' '.join(row[1] for row in rows)
        conn = sqlite3.connect('instance/db.sqlite')
        cursor = conn.cursor()
        # select from catagory_table where id = fid
        cursor.execute(
            "SELECT * FROM catagory_table WHERE id = ?", (fid,))
        rows = cursor.fetchall()
        id = ' '.join(row[1] for row in rows)
        id2 = ' '.join(row[2] for row in rows)
        message = "Exam going on "+" /"+id+"/ "+id2+"/"+third_columns
        conn.close()
        return render_template('home_page.html', rows=message)


# books upload
class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    file_data = db.Column(db.LargeBinary)
    image = db.Column(db.LargeBinary)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Integer)

    def __repr__(self):
        return f"FileUpload('{self.filename}')"


@app.route('/booksUpload', methods=['GET'])
def booksUpload():
    return render_template('upload.html')


@app.route('/uploadBooks', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # get form data
        form = request.form
        # save the fomr data to the database
        file_data = FileUpload(
            filename=request.files['file'].filename,
            file_data=request.files['file'].read(),
            image=request.files['image'].read(),
            title=form['title'],
            description=form['description'],
            price=form['price']
        )
        db.session.add(file_data)
        db.session.commit()
        return 'File saved to database successfully!'
    return 'Something went wrong'


@app.route('/show_data_all', methods=['GET'])
def show_data_all():
    files = FileUpload.query.all()
    for file in files:
        file.image_base64 = base64.b64encode(file.image).decode('utf-8')
    return render_template('show_data.html', files=files)


@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file_data = FileUpload.query.get_or_404(file_id)
    return Response(file_data.file_data, headers={
        'Content-Disposition': f'attachment; filename="{file_data.filename}"'
    })

# create route for details_books


@app.route('/details_books/<int:file_id>', methods=['GET'])
def details_books(file_id):
    file_data = FileUpload.query.get_or_404(file_id)
    file_data.image_base64 = base64.b64encode(file_data.image).decode('utf-8')
    return render_template('details_books.html', file_data=file_data)
# create aroute for studentlist


@app.route('/studentlist')
def studentlist():
    conn = sqlite3.connect('instance/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user")
    data = cursor.fetchall()
    conn.close()
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Define the path for the Excel file
    excel_file_path = f'instance/studentlist.xlsx'

    # Export the DataFrame to Excel
    df.to_excel(excel_file_path, index=False)

    # Return the Excel file for download
    return send_file(excel_file_path, as_attachment=True)

# create a route for upload quizimage


# books upload
class QuizImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)

    def __repr__(self):
        return f"FileUpload('{self.image}')"


# @app.route('/quizimage', methods=['GET', 'POST'])
# def upload_quiz_image():
#     if request.method == 'POST':
#         # Get form data
#         file = request.files['image']

#         if file:
#             # Save the form data to the database
#             file_data = QuizImage(image=file.read())
#             db.session.add(file_data)
#             db.session.commit()
#             return 'File saved to database successfully!'

#     return render_template('quizimage.html')


@app.route('/quizimage', methods=['GET', 'POST'])
def upload_quiz_image():
    if request.method == 'POST':
        # Get form data
        file = request.files['image']

        if file:
            # Check if there is an existing row in the table
            existing_data = QuizImage.query.first()

            if existing_data:
                # If there is existing data, update the image
                existing_data.image = file.read()
            else:
                # If no existing data, create a new row in the table
                file_data = QuizImage(image=file.read())
                db.session.add(file_data)

            # Commit the changes to the database
            db.session.commit()
            return 'File saved to database successfully!'

    return render_template('quizimage.html')


@app.route('/show_quiz_image', methods=['GET'])
def show_quiz_image():
    files = QuizImage.query.all()
    for file in files:
        file.image_base64 = base64.b64encode(file.image).decode('utf-8')
    return render_template('show_quiz_image.html', files=files)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
