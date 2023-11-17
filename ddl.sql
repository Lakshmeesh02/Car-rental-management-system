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

