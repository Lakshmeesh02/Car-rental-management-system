from flask import Flask, render_template,request, redirect, url_for
import mysql.connector

app=Flask(__name__)

def create_sql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="coleadonis23#J",
        database="carrent"
    )

@app.route('/')
def home():
    return render_template("who.html")

@app.route('/askcred/<login_type>', methods=['GET','POST'])
def creds(login_type):
    if request.method=="POST" and login_type=="user":
        username=request.form.get('username')
        password=request.form.get('password')
        connection=create_sql_connection()
        cursor=connection.cursor()
        validate="select customer_id from customers where username=%s and password=%s"
        validate_data=(username,password)
        cursor.execute(validate,validate_data)
        existing_user=cursor.fetchone()
        cursor.close()
        connection.close()
        if not existing_user:
            return "No such user exists"
        else:
           return render_template("userhome.html")
            
    return render_template(f"askcred{login_type}.html")

@app.route('/register/<reg_type>', methods=['GET','POST'])
def register(reg_type):
    if request.method=="POST" and reg_type=="user":
        username=request.form.get("cusername")
        password=request.form.get("cpassword")
        fname=request.form.get("fname")
        lname=request.form.get("lname")
        contact=request.form.get("contact")

        connection=create_sql_connection()
        cursor=connection.cursor()
        check="select customer_id from customers where username=%s"
        check_data=(username,)
        cursor.execute(check,check_data)
        existing_users=cursor.fetchone()
        if existing_users:
            cursor.close()
            connection.close()
            return "Username already taken"
        
        query="insert into customers (fname, lname, username, password, contact) values (%s, %s, %s, %s, %s)"
        data=(fname, lname, username, password, contact)

        try:
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            connection.close()
            return redirect (url_for('home'))
        
        except Exception as e:
            print(e)
            cursor.close()
            connection.close()
            return "Try again"
        
    if request.method=="POST" and reg_type=="admin":
        username=request.form.get("ausername")
        password=request.form.get("apassword")

        connection=create_sql_connection()
        cursor=connection.cursor()
        check="select admin_id from admins where username=%s"
        check_data=(username,)
        cursor.execute(check,check_data)
        existing_admins=cursor.fetchone()
        if existing_admins:
            cursor.close()
            connection.close()
            return "Admin already exists"
        
        query="insert into admins (username, password) values (%s, %s)"
        data=(username, password)
        
        try:
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('home'))
        
        except Exception as e:
            print(e)
            cursor.close()
            connection.close()
            return "Try again"
        
    if request.method=="POST" and reg_type=="company":
        password=request.form.get("password")
        name=request.form.get("name")
        contact=request.form.get("contact")

        connection=create_sql_connection()
        cursor=connection.cursor()
        check="select company_id from companies where name=%s"
        check_data=(name,)
        cursor.execute(check,check_data)
        existing_companies=cursor.fetchone()
        if existing_companies:
            cursor.close()
            connection.close()
            return "Company exists already"
        
        query="insert into companies (name, password, contact) values (%s, %s, %s)"
        data=(name,password,contact)

        try:
            cursor.execute(query,data)
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('home'))
        
        except Exception as e:
            print(e)
            cursor.close()
            connection.close()
            return "Try again"
        
    return render_template(f"reg{reg_type}.html")

if __name__=="__main__":
    app.run(debug=True)