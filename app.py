from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Initialize Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def checkPassword(self, password):
        return self.password == password
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self): 
        return f'<Task {self.id}>'

with app.app_context():
    db.create_all()
# Route for the home page

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Call checkPassword method from User class
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.checkPassword(password):
                print(user, user.checkPassword(password))
                return redirect(f'/tasks/{user.user_id}') # Redirect and include userID in the URL
            else:
                return render_template('login.html', error="Invalid credentials")
        except:
            return render_template('login.html', error="User not found")
    return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template('register.html', error="Username already exists")
        except:
            pass
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/') # Redirect and include userID in the URL
    return render_template('register.html')

@app.route('/tasks/<int:user_id>', methods=["POST", "GET"])
def tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()  # find tasks that belong to the user
    print(tasks)
    if request.method == "POST":
        task_content = request.form.get('content')
        new_task = Task(content=task_content, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(f'/tasks/{user_id}')
    return render_template('tasks.html', tasks=tasks, user_id=user_id)
    

@app.route('/tasks/delete/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(f'/tasks/{task.user_id}')

if __name__ == '__main__':
    app.run(debug=True)