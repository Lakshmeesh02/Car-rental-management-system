from flask import Flask, render_template,request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import plotly.express as px
import pandas as pd

app=Flask(__name__,static_folder='static')

def create_sql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="coleadonis23#J",
        database="carrent"
    )

def create_connection_customers():
    return mysql.connector.connect(
        host="localhost",
        username="customers",
        password="customers123",
        database="carrent"
    )

def create_connection_companies():
    return mysql.connector.connect(
        host="localhost",
        user="companies",
        password="companies123",
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
           return redirect(url_for("customerpage",customername=username,customer_id=existing_user[0]))
        
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
        contact=int(request.form.get("contact"))

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
        contact=int(request.form.get("contact"))
        location=request.form.get("location")

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

@app.route('/customer/<customername>/<int:customer_id>', methods=['GET','POST'])
def customerpage(customername,customer_id):
    if request.method=='POST':
        location=request.form.get("location")
        return redirect(url_for("viewcars",location=location))
    return render_template("userhome.html", username=customername, customer_id=customer_id)

@app.route('/availablecars/<location>',methods=['GET','POST'])
def viewcars(location):
    connection=create_sql_connection()
    cursor=connection.cursor()
    query="""select c.company_id, c.name, c.contact, c.location, cars.car_id, cars.name, cars.price_per_day, cars.available
    from companies as c
    inner join cars on cars.company_id=c.company_id 
    where substring_index(c.location,',',-1) = %s;"""
    cursor.execute(query,(location,))
    results=cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("searchcars.html", results=results, location=location)

@app.route('/reserve/<customername>/<int:customer_id>',methods=['GET','POST'])
def reserve(customername,customer_id):
    if request.method=='POST':
        companyid=int(request.form.get("companyid"))
        carid=int(request.form.get("carid"))
        carcount=int(request.form.get("carcount"))
        pickupdate=request.form.get("pickupdate")
        returndate=request.form.get("returndate")
        try:
            pickup_date=datetime.strptime(pickupdate,'%d-%m-%Y')
            return_date=datetime.strptime(returndate,'%d-%m-%Y')
        except ValueError:
            return "Enter valid dates"
        if not(companyid>0):
            return "Invalid company_id"
        if not(carid>0):
            return "Invalid car id"
        if return_date<pickup_date:
            return "Enter valid dates"
        if not(carcount>0):
            return "Invalid car count"
        total_days=(return_date-pickup_date).days
        connection=create_connection_customers()
        cursor=connection.cursor()
        check_car_exists="select car_id from cars where car_id=%s and company_id=%s"
        check_car_exists_data=(carid,companyid)
        cursor.execute(check_car_exists,check_car_exists_data)
        results=cursor.fetchall()
        if len(results)>1:
            return "Request redundant"
        check_availability="select available from cars where car_id=%s"
        check_availability_data=(carid,)
        cursor.execute(check_availability,check_availability_data)
        available_cars=cursor.fetchall()
        if carcount>available_cars[0][0]:
            return "Hold on, have some limit"
        calc_price="select price_per_day*%s*%s from cars where car_id=%s"
        calc_price_data=(carcount,total_days,carid)
        cursor.execute(calc_price,calc_price_data)
        price=cursor.fetchall()[0][0]
        insert_reservation="insert into reservations (customer_id,company_id, price, pickup_date, return_date, car_id, car_count) values (%s, %s, %s, %s, %s, %s, %s)"
        insert_reservation_data=(customer_id,companyid,price,pickup_date,return_date,carid,carcount)
        cursor.execute(insert_reservation,insert_reservation_data)
        connection.commit()
        cursor.callproc('sp_UpdateCarAvailability',(carid,carcount))
        connection.commit()
        cursor.close()
        connection.close()
        return f"Car booked successfully and price to pay(on pickup)={price}!"
    return render_template("reservecars.html", customer_id=customer_id, customername=customername)

@app.route('/customer/<customername>/<int:customer_id>/history',methods=['GET'])
def user_history(customername,customer_id):
    connection=create_connection_customers()
    cursor=connection.cursor()
    query="select id, company_id, price, pickup_date, return_date, car_id, car_count from reservations where customer_id=%s"
    data=(customer_id,)
    cursor.execute(query,data)
    reservations=cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("userhistory.html", reservations=reservations, customername=customername)

@app.route('/delete_customer/<int:customer_id>',methods=['GET'])
def deleteaccount(customer_id):
    connection=create_connection_customers()
    cursor=connection.cursor()
    query="delete from customers where customer_id=%s"
    data=(customer_id,)
    cursor.execute(query,data)
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('home'))

@app.route('/company/<companyname>/<int:company_id>', methods=['GET','POST'])
def companypage(companyname,company_id):
    if request.method=="POST":
        carname=request.form.get("carname")
        price_per_day=int(request.form.get("price_per_day"))
        limit=int(request.form.get("limit"))

        if not price_per_day or price_per_day<0:
            return "Price per day required and needs to be valid"
        connection=create_connection_companies()
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
    return render_template("companyhome.html", companyname=companyname,company_id=company_id)

@app.route('/company/<companyname>/<int:company_id>/stats', methods=['GET'])
def companystats(companyname,company_id):
    if request.method=='GET':
        connection=create_connection_companies()
        cursor=connection.cursor()
        query="""
        select count(cars.car_id),
        avg(price_per_day),
        sum(available),
        sum(reservations.price)
        from cars left join reservations on cars.car_id=reservations.car_id 
        where cars.company_id=%s
        """
        data=(company_id,)
        cursor.execute(query,data)
        statistics=cursor.fetchone()

        query="""
        select cars.name, count(reservations.id) as rental_count
        from cars left join reservations on cars.car_id=reservations.car_id
        where cars.company_id=%s
        group by cars.name
        order by rental_count desc
        limit 1
        """
        cursor.execute(query,data)
        most_rented=cursor.fetchone()

        query="""
        select cars.name, count(reservations.id) as rental_count
        from cars left join reservations on cars.car_id=reservations.car_id
        where cars.company_id=%s
        group by cars.name
        order by rental_count asc
        limit 1
        """
        cursor.execute(query,data)
        least_rented=cursor.fetchone()

        availability_pie="select sum(car_count) as count, available from cars where company_id=%s group by available"
        cursor.execute(availability_pie,data)
        availability_data=cursor.fetchall()
        print(availability_data)

        price_bar="select name, avg(price_per_day) as price_per_day from cars where company_id=%s group by name"
        cursor.execute(price_bar,data)
        price_data=cursor.fetchall()
        cursor.close()
        connection.close()

        if availability_data:
            total_cars, available_cars=availability_data[0]
            percentage_available=(available_cars/total_cars)*100
            data={'count':[percentage_available, 100-percentage_available], 'available':['Available','Unavailable']}
            df=pd.DataFrame(data)
            pie_chart=px.pie(df, names='available', values='count', title='Car availability distribution')
            pie_html=pie_chart.to_html(full_html=False)
        else:
            pie_html = "No data available for car availability distribution."
        df_price=pd.DataFrame(price_data, columns=['name','price_per_day'])
        bar_graph=px.bar(df_price, x='name', y='price_per_day', title='price for each car')
        bar_html=bar_graph.to_html(full_html=False)
    return render_template("companystats.html",companyname=companyname,company_id=company_id,statistics=statistics, most_rented=most_rented, least_rented=least_rented, pie_html=pie_html, bar_html=bar_html)

@app.route('/company/<int:company_id>/cars',methods=['GET'])
def company_cars(company_id):
    connection=create_connection_companies()
    cursor=connection.cursor()
    query="select car_id, name, price_per_day, car_count, available from cars where company_id=%s"
    data=(company_id,)
    cursor.execute(query,data)
    cars=cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("carlist.html",company_id=company_id,cars=cars)

@app.route('/company/bookings/<int:company_id>',methods=['GET'])
def bookings(company_id):
    connection=create_connection_companies()
    cursor=connection.cursor()
    query="select * from reservations where company_id=%s"
    data=(company_id,)
    cursor.execute(query,data)
    reserves=cursor.fetchall()
    reserves=reserves[::-1]
    cursor.close()
    connection.close()
    return render_template("companybookings.html",reserves=reserves,company_id=company_id)

if __name__=="__main__":
    app.run(debug=True)