CREATE DATABASE if not exists carrent;
USE carrent;

create table customers
(customer_id int primary key auto_increment,
fname varchar(20) not null,
lname varchar(20) not null,
username varchar(20) not null,
password varchar(100) not null,
contact int not null
);

create table companies
(company_id int primary key auto_increment,
name varchar(20) not null,
password varchar(100) not null,
contact int not null,
location varchar(30) not null
);

create table cars
(car_id int primary key auto_increment,
name varchar(20) not null,
company_id int not null,
price_per_day float not null,
car_count int not null,
available int not null,
key fkcars1 (company_id),
constraint fkcars1 foreign key (company_id) references companies(company_id) on delete cascade,
constraint chk_price_per_day check ((price_per_day>0)),
constraint chk_count check((car_count>0)),
constraint chk_available check((available<=car_count))
);

create table reservations
(id int primary key auto_increment,
customer_id int not null,
company_id int not null,
price float not null,
pickup_date date not null,
return_date date not null,
car_id int not null,
car_count int not null,
key fkreservations1 (customer_id),
key fkreservations2 (company_id),
key fkreservations3 (car_id),
constraint fkreservations1 foreign key (customer_id) references customers(customer_id) on delete cascade,
constraint fkreservations2 foreign key (company_id) references companies(company_id) on delete cascade,
constraint fkreservations3 foreign key (car_id) references cars(car_id) on delete cascade,
constraint chk_car_count check((car_count>0))
);

-- Trigger to update available cars for a company when a customer who has reserved cars has deleted the account
DELIMITER //
CREATE TRIGGER before_delete_customer
BEFORE DELETE ON customers
FOR EACH ROW
BEGIN
    DECLARE car_id_var INT;
    DECLARE car_count_var INT;
    
    SELECT car_id, car_count
    INTO car_id_var, car_count_var
    FROM reservations
    WHERE customer_id = OLD.customer_id;

    UPDATE cars
    SET available = available + car_count_var
    WHERE car_id = car_id_var;
END;
//
DELIMITER ;


--Procedure to update car_availability when cars are booked by customers
DELIMITER //

CREATE PROCEDURE sp_UpdateCarAvailability(IN p_car_id INT, IN p_count INT)
BEGIN
    UPDATE cars SET available = available - p_count WHERE car_id = p_car_id;
END //

DELIMITER ;


--User roles and privileges
create user 'customers'@'localhost' identified by 'customers123';
create user 'companies'@'localhost' identified by 'companies123';
grant select, insert, delete on carrent.customers to 'customers'@'localhost';
grant select, update on carrent.cars to 'customers'@'localhost';
grant select, insert on carrent.reservations to 'customers'@'localhost';
grant select, insert, delete on carrent.companies to 'companies'@'localhost';
grant select, insert, delete, update on carrent.cars to 'companies'@'localhost';
grant select on carrent.reservations to 'companies'@'localhost';


--Values for companies page
INSERT INTO companies (company_id, name, password, contact, location) VALUES (1, 'bajaj', 'jabab', 90986, 'mumbai');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (2, 'ford', 'pass123', 98765, 'detroit');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (3, 'toyota', 'securepass', 87654, 'tokyo');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (4, 'honda', 'hondapass', 76543, 'osaka');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (5, 'audi', 'audipass', 54321, 'ingolstadt');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (6, 'mercedes', 'mercedespass', 43210, 'stuttgart');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (7, 'volkswagen', 'vwpass', 32109, 'wolfsburg');
INSERT INTO companies (company_id, name, password, contact, location) VALUES (8, 'bmw', 'bmwpass', 21098, 'munich');


--Values for customers page
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (1, 'likith', 'mc', 'likith', 'lik', 12345);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (2, 'John', 'Doe', 'john_doe', 'password123', 123456789);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (3, 'Alice', 'Smith', 'alice_smith', 'securepass', 987654321);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (4, 'Bob', 'Johnson', 'bob_johnson', 'pass1234', 555666777);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (5, 'Eva', 'Williams', 'eva_williams', 'mysecretpass', 111222333);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (6, 'Chris', 'Brown', 'chris_brown', 'brownpass', 999888777);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (7, 'Megan', 'Taylor', 'megan_taylor', 'taylorpass', 444555666);
INSERT INTO customers (customer_id, fname, lname, username, password, contact) VALUES (8, 'Ryan', 'Miller', 'ryan_miller', 'millerpass', 777888999);


--Values for cars page
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (1, 'Sedan A', 1, 50.0, 10, 8);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (2, 'SUV X', 2, 70.0, 15, 12);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (3, 'Compact B', 3, 45.0, 20, 18);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (4, 'Convertible C', 4, 90.0, 8, 6);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (5, 'Hatchback D', 5, 40.0, 12, 10);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (6, 'Truck E', 6, 80.0, 7, 5);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (7, 'Electric F', 7, 60.0, 14, 11);
INSERT INTO cars (car_id, name, company_id, price_per_day, car_count, available) VALUES (8, 'Luxury G', 8, 100.0, 5, 3);

