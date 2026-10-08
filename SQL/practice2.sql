create database hr_system;
use hr_system;
create table master_dept( dept_id int primary key, dept_name varchar(25) );
create table naster_role( role_id int primary key, role_name varchar(25) );
insert into master_dept values(01,"DATA SCIENCE & AI "),(02,"WEB DEVELOPMENT"),(03,"UI/UX");
INSERT INTO naster_role values(11,"DATA SCIENTIST"),(12,"DATA ANALYST"),(13,"DATA ENGINEER"),(14,"AI ENGINEER"),
							(21,"FRONTENT DEVELOPER"),(22,"BACKEND DEVELOPER"),(23,"FULL STACK DEVELOPER"),(31,"DESIGNER");
CREATE TABLE employee_details(emp_id int primary key, name varchar(25) not null,hire_date date not null,salary decimal(12,2) not null,dept_id int,role_id int,
							foreign key(dept_id) references master_dept(dept_id),
                            foreign key(role_id) references naster_role(role_id));
drop table employee_details;
CREATE TABLE employee_details(emp_id int primary key, name varchar(25) not null,hire_date date not null,salary decimal(12,2) not null,dept_id int,role_id int,is_active bool default true,
							foreign key(dept_id) references master_dept(dept_id),
                            foreign key(role_id) references naster_role(role_id));
INSERT INTO employee_details
(emp_id, name, hire_date, salary, dept_id, role_id, is_active)
VALUES
(1001, 'Arjun Aji',     '2025-06-10', 65000.00, 01, 11, TRUE),
(1002, 'Rahul Menon',   '2025-07-15', 58000.00, 01, 12, TRUE),
(1003, 'Anjali Nair',   '2025-08-20', 72000.00, 01, 13, TRUE),
(1004, 'Vishnu Kumar',  '2025-09-05', 68000.00, 01, 14, TRUE),
(1005, 'Meera Joseph',  '2025-10-12', 55000.00, 01, 12, TRUE),

(1006, 'Adithya S',     '2025-05-18', 60000.00, 02, 21, TRUE),
(1007, 'Fahad Ali',     '2025-06-25', 62000.00, 02, 22, TRUE),
(1008, 'Neha Thomas',   '2025-07-30', 75000.00, 02, 23, TRUE),
(1009, 'Nikhil Raj',    '2025-08-14', 57000.00, 02, 21, FALSE),
(1010, 'Sneha Das',     '2025-09-22', 70000.00, 02, 23, TRUE),
(1011, 'Abhinav P',     '2025-11-01', 59000.00, 02, 22, TRUE),
(1012, 'Devika R',      '2026-01-10', 64000.00, 02, 21, TRUE),
(1013, 'Sanjay Kumar',  '2026-02-18', 78000.00, 02, 23, TRUE),

(1014, 'Amal George',   '2025-04-12', 52000.00, 03, 31, TRUE),
(1015, 'Diya Menon',    '2025-06-08', 56000.00, 03, 31, TRUE),
(1016, 'Riya Mathew',   '2025-08-16', 61000.00, 03, 31, FALSE),
(1017, 'Joel Thomas',   '2025-10-28', 54000.00, 03, 31, TRUE),
(1018, 'Akhil Babu',    '2026-01-15', 58000.00, 03, 31, TRUE),
(1019, 'Keerthi S',     '2026-03-05', 63000.00, 03, 31, TRUE),
(1020, 'Hari Krishnan', '2026-05-20', 67000.00, 03, 31, TRUE);

select * from employee_details;

select * from employee_details where dept_id in (01,02);

select * from employee_details where dept_id =01 and salary>60000 order by name ;

select sum(salary) AS "total salary" from employee_details;

select dept_id,sum(salary) AS "total salary" from employee_details group by dept_id;

select employee_details.name,master_dept.dept_name from employee_details inner join master_dept on employee_details.dept_id=master_dept.dept_id;
insert into master_dept values(04,"SCIENCE");
select employee_details.name,master_dept.dept_name from employee_details right join master_dept on employee_details.dept_id=master_dept.dept_id;

select master_dept.dept_name,sum(employee_details.salary) AS "total salary" from employee_details inner join master_dept on employee_details.dept_id=master_dept.dept_id group by employee_details.dept_id;

select employee_details.name,naster_role.role_name from employee_details inner join naster_role on employee_details.role_id=naster_role.role_id where employee_details.salary>(select avg(employee_details.salary) from employee_details);

update employee_details set salary= 75000 where emp_id=1001;

