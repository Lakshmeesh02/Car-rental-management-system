from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def home():
    return render_template("who.html")

@app.route('/askcred/<login_type>', methods=['GET','POST'])
def creds(login_type):
    return render_template(f"askcred{login_type}.html")

@app.route('/register/<reg_type>', methods=['GET','POST'])
def register(reg_type):
    return render_template(f"reg{reg_type}.html")

if __name__=="__main__":
    app.run(debug=True)