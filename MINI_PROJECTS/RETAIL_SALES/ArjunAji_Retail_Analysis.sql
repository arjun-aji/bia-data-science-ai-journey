create database retailpro_db;
use retailpro_db;
select * from customers;
select * from orders;
select * from products;
select * from regions;

-- Q1  total revenue
select sum(quantity * unit_price * (1 - discount)) AS Total_Revenue FROM orders;

-- Q2 total number of distinct orders
select count(DISTINCT order_id) AS Total_Orders from orders;

-- Q3 Total quantity
select sum(quantity) AS Total_Quantity from orders;

select count(order_line_id) AS Total_Order_lines from orders;

-- Q4 average order value(TOTAL REVENUE/TOTAL ORDERS)
select SUM(quantity * unit_price * (1 - discount))/ COUNT(DISTINCT order_id) AS Average_Order_Value FROM orders;

-- Q5 MONTH BY MONTH
SELECT DATE_FORMAT(order_date, '%Y-%m') AS Month,COUNT(DISTINCT order_id) AS Total_Orders,
SUM(quantity * unit_price * (1 - discount)) AS Total_Revenue
FROM orders
GROUP BY Month
ORDER BY Total_Revenue;

-- Q6 TOP 10 PRODUCTS
SELECT products.product_name AS PRODUCTS, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN products on orders.product_id=products.product_id
GROUP BY orders.product_id, products.product_name
ORDER BY Total_Revenue DESC LIMIT 10;

-- Q7 CATEGORY HIGHEST REVENUE
SELECT products.category AS CATEGORY, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN products on orders.product_id=products.product_id
GROUP BY products.category
ORDER BY Total_Revenue DESC ;

-- Q8 PRODUCT HIGHEST SOLD PRODUCT
SELECT products.product_name AS PRODUCTS, SUM(orders.quantity) AS Total_Quantity
FROM orders INNER JOIN products on orders.product_id=products.product_id
GROUP BY orders.product_id, products.product_name
ORDER BY Total_Quantity DESC,products.product_name;

-- Q9 Identify the strongest-performing category
SELECT products.category AS CATEGORY, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue,
sum(orders.quantity) as Quantity_sold, count(distinct orders.order_id) as Number_of_orders 
FROM orders INNER JOIN products on orders.product_id=products.product_id
GROUP BY products.category
ORDER BY Total_Revenue DESC;

-- Q10 Which customer segments generate the highest revenue?
SELECT customers.customer_segment AS SEGMENT, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers on orders.customer_id=customers.customer_id
GROUP BY customers.customer_segment
ORDER BY Total_Revenue DESC;

-- Q11 Top 10 customers by revenue
SELECT customers.customer_name AS NAME, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers on orders.customer_id=customers.customer_id
GROUP BY customers.customer_id,customers.customer_name 
ORDER BY Total_Revenue DESC,customers.customer_name LIMIT 10;

-- Q12 average order value for each customer segment
SELECT customers.customer_segment AS SEGMENT, SUM(orders.quantity * orders.unit_price * (1 - orders.discount))/ COUNT(DISTINCT order_id) AS Average_Order_Value
FROM orders INNER JOIN customers on orders.customer_id=customers.customer_id
GROUP BY customers.customer_segment
ORDER BY Average_Order_Value DESC;

-- Q13 Which regions generate the highest revenue?
-- by region
SELECT regions.region_name AS REGION, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers ON orders.customer_id=customers.customer_id INNER JOIN regions on customers.region_id=regions.region_id
GROUP BY regions.region_name
ORDER BY Total_Revenue DESC;

-- by state
SELECT regions.state AS STATE, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers ON orders.customer_id=customers.customer_id INNER JOIN regions on customers.region_id=regions.region_id
GROUP BY regions.state
ORDER BY Total_Revenue DESC;

-- by city
SELECT customers.city AS city, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers on orders.customer_id=customers.customer_id
GROUP BY customers.city
ORDER BY Total_Revenue DESC;

-- Q14 Which region has the highest number of orders?
SELECT regions.region_name AS REGION, count(DISTINCT order_id) AS Total_Orders
FROM orders INNER JOIN customers ON orders.customer_id=customers.customer_id INNER JOIN regions on customers.region_id=regions.region_id
GROUP BY regions.region_name
ORDER BY Total_Orders DESC;

-- Q15 Identify the regions that appear to be underperforming based on revenue and order volume.
SELECT regions.region_name AS REGION, SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue,count(DISTINCT order_id) AS Total_Orders
FROM orders INNER JOIN customers ON orders.customer_id=customers.customer_id INNER JOIN regions on customers.region_id=regions.region_id
GROUP BY regions.region_name
ORDER BY Total_Revenue,Total_Orders;

-- Q16 Analyse orders by order_status.
SELECT order_status as STATUS , count(*) as COUNT,
(count(*)/(select count(*) from orders))*100 as PERCENTAGE from orders group by order_status
order by COUNT DESC;

-- Q17 Which payment methods are used most frequently?
SELECT payment_method AS PAYMENT,count(distinct order_id) as COUNT from orders group by payment_method order by COUNT DESC;

-- Product with highest price(max)
select product_name,unit_price from products where unit_price= (select max(unit_price) from products);

-- Product with lowest price(min)
select product_name,unit_price from products where unit_price= (select min(unit_price) from products);

-- AVERAGE PRODUCT PRICE PER CATOGORY
SELECT category,AVG(unit_price) AS Average_Price FROM products GROUP BY category ORDER BY Average_Price DESC;

-- USING LEFT JOIN TO COUNT NUMBER OF ORDERS PER CUSTOMER SO THAT IT SHOWS CUSTOMERS WITH 0 ORDERS TOO
SELECT customers.customer_name, COUNT(DISTINCT orders.order_id) AS Total_Orders
FROM customers LEFT JOIN orders
ON customers.customer_id = orders.customer_id
GROUP BY customers.customer_id, customers.customer_name;

-- Customers with revenue above 500,000
SELECT customers.customer_name AS NAME,SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) AS Total_Revenue
FROM orders INNER JOIN customers ON orders.customer_id = customers.customer_id
GROUP BY customers.customer_id, customers.customer_name
HAVING SUM(orders.quantity * orders.unit_price * (1 - orders.discount)) > 500000
ORDER BY Total_Revenue DESC;

-- Part C: Analysis-Ready Dataset

SELECT
    orders.order_id AS Order_ID,
    orders.order_date AS Order_Date,
    customers.customer_id AS Customer_ID,
    customers.customer_name AS Customer_Name,
    customers.customer_segment AS Customer_Segment,
    customers.city AS City,
    regions.region_name AS Region,
    regions.state AS State,
    products.product_id AS Product_ID,
    products.product_name AS Product_Name,
    products.category AS Category,
    products.subcategory AS Subcategory,
    orders.quantity AS Quantity,
    orders.unit_price AS Unit_Price,
    orders.discount AS Discount,
    orders.quantity * orders.unit_price * (1 - orders.discount) AS Revenue,
    orders.order_status AS Order_Status,
    orders.payment_method AS Payment_Method

FROM orders
INNER JOIN customers
    ON orders.customer_id = customers.customer_id
INNER JOIN products
    ON orders.product_id = products.product_id
INNER JOIN regions
    ON customers.region_id = regions.region_id
    order by Order_ID;
