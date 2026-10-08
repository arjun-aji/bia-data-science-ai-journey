CREATE DATABASE employee_data;
USE employee_data;
CREATE TABLE employee_data(emp_id INT PRIMARY KEY,f_name VARCHAR(50) NOT NULL,l_name VARCHAR(50),hire_date DATE NOT NULL,salary DECIMAL(10,2),is_active BOOL DEFAULT True);
INSERT INTO employee_data(emp_id,f_name,l_name,hire_date,salary) VALUES (1002,"Arjun","Shaju",'2026-08-22',65000.00);
INSERT INTO employee_data(emp_id,f_name,l_name,hire_date,salary) VALUES (1003,"Ajmal","A",'2026-08-22',55000.00),(1004,"Dhron","M",'2026-08-22',50000.00),(1005,"Febin","OP",'2026-08-22',55000.00);
select * from employee_data;
SELECT f_name AS "FIRST NAME" ,salary from employee_data;          
INSERT INTO employee_data (emp_id, f_name, l_name, hire_date, salary) VALUES
(1006, 'Arun', 'K', '2026-08-22', 48000.00),
(1007, 'Rahul', 'P', '2026-08-22', 52000.00),
(1008, 'Nihal', 'S', '2026-08-22', 45000.00),
(1009, 'Adithya', 'M', '2026-08-22', 57000.00),
(1010, 'Vishnu', 'R', '2026-08-22', 49000.00),
(1011, 'Akshay', 'T', '2026-08-22', 61000.00),
(1012, 'Fahad', 'N', '2026-08-22', 53000.00),
(1013, 'Naveen', 'B', '2026-08-22', 47000.00),
(1014, 'Amal', 'C', '2026-08-22', 56000.00),
(1015, 'Sanjay', 'V', '2026-08-22', 51000.00),
(1016, 'Rohan', 'D', '2026-08-22', 59000.00),
(1017, 'Akhil', 'J', '2026-08-22', 46000.00),
(1018, 'Joel', 'P', '2026-08-22', 54000.00),
(1019, 'Midhun', 'S', '2026-08-22', 62000.00),
(1020, 'Aswin', 'K', '2026-08-22', 50000.00),
(1021, 'Shahin', 'A', '2026-08-22', 58000.00),
(1022, 'Jithin', 'M', '2026-08-22', 55000.00),
(1023, 'Alan', 'T', '2026-08-22', 43000.00),
(1024, 'Sreehari', 'R', '2026-08-22', 60000.00),
(1025, 'Manu', 'P', '2026-08-22', 52000.00),
(1026, 'Kevin', 'J', '2026-08-22', 49000.00),
(1027, 'Gokul', 'N', '2026-08-22', 63000.00),
(1028, 'Irfan', 'H', '2026-08-22', 57000.00),
(1029, 'Roshan', 'C', '2026-08-22', 44000.00),
(1030, 'Sahil', 'V', '2026-08-22', 53000.00);
select * from employee_data where emp_id = 1001;
select f_name,l_name from employee_data where is_active = true;
select f_name,l_name from employee_data where salary>50000;
select f_name,l_name from employee_data where salary>50000 && is_active= true;
select * from employee_data order by f_name desc;
select * from employee_data order by salary,f_name;
cre