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
            return "Invalid credentials"
        else:
           return redirect(url_for('customerpage',customername=username))
        
    if request.method=="POST" and login_type=="company":
        username=request.form.get('cusername')
        password=request.form.get('cpassword')
        connection=create_sql_connection()
        cursor=connection.cursor()
        validate="select company_id from companies where name=%s and password=%s"
        validate_data=(username,password)
        cursor.execute(validate,validate_data)
        existing_company=cursor.fetchone()
        cursor.close()
        connection.close()
        if not existing_company:
            return "Invalid credentials"
        else:
            return redirect(url_for("companypage",companyname=username,company_id=existing_company[0]))
            
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
        
        
    if request.method=="POST" and reg_type=="company":
        password=request.form.get("password")
        name=request.form.get("name")
        contact=request.form.get("contact")
        location=request.form.get("location")

        connection=create_sql_connection()
        cursor=connection.cursor()
        check="select company_id from companies where name=%s"
        check_data=(name,)
        cursor.execute(check,check_data)
        existing_companies=cursor.fetchone()
        print(existing_companies)
        if existing_companies:
            cursor.close()
            connection.close()
            return "Company exists already"
        
        query="insert into companies (name, password, contact,location) values (%s, %s, %s, %s)"
        data=(name,password,contact,location)

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

@app.route('/customer/<customername>', methods=['GET','POST'])
def customerpage(customername):
    return render_template("userhome.html", username=customername)

@app.route('/company/<companyname>/<int:company_id>', methods=['GET','POST'])
def companypage(companyname,company_id):
    if request.method=="POST":
        carname=request.form.get("carname")
        price_per_day=request.form.get("price_per_day")
        action=request.form.get("action")
        limit=request.form.get("limit")

        if action=="add":
            if not price_per_day:
                return "Price per day required to perform this action"
            connection=create_sql_connection()
            cursor=connection.cursor()
            check="select car_id, car_count, available from cars where name=%s and company_id=%s"
            data=(carname,company_id)
            cursor.execute(check,data)
            existing_car=cursor.fetchone()
            if not existing_car:
                query="insert into cars (name,company_id,price_per_day,car_count,available) values (%s,%s,%s,%s,%s)"
                data=(carname,company_id,price_per_day,limit,limit)
                cursor.execute(query,data)
                connection.commit()
                cursor.close()
                connection.close()
                return "Car added successfully."
            else:
                print(existing_car)
                car_id=existing_car[0]
                car_count=existing_car[1]+int(limit)
                available=existing_car[2]+int(limit)
                query="update cars set price_per_day=%s, car_count=%s, available=%s where car_id=%s and company_id=%s"
                data=(price_per_day,car_count,available,car_id,company_id)
                cursor.execute(query,data)
                connection.commit()
                cursor.close()
                connection.close()
                return "updated info successfully"

        elif action=="remove":
            if not carname or not limit:
                return "Carname and limit field necessary to perform this action"
            connection=create_sql_connection()
            cursor=connection.cursor()
            check="select car_id, car_count, available from cars where name=%s and company_id=%s"
            data=(carname,company_id)
            cursor.execute(check,data)
            existing_car=cursor.fetchone()
            car_id=existing_car[0]
            car_count=existing_car[1]-int(limit)
            available=existing_car[2]-int(limit)
            if car_count<0:
                return "Invalid limit set"
            elif car_count==0:
                query="delete from cars where name=%s and company_id=%s"
                data=(carname,company_id)
                cursor.execute(query,data)
                connection.commit()
                cursor.close()
                connection.close()
                return "Car removed successfully"
            query="update cars set car_count=%s, available=%s where car_id=%s and company_id=%s"
            data=(car_count,available,car_id,company_id)
            cursor.execute(query,data)
            connection.commit()
            cursor.close()
            connection.close()
            return "Car removed successfully"

    return render_template("companyhome.html", companyname=companyname)

if __name__=="__main__":
    app.run(debug=True)