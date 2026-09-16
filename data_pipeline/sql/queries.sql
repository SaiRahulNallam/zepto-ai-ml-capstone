-- Q1: SELECT / WHERE / ORDER BY
SELECT title, price_gbp FROM books WHERE rating >= 4 ORDER BY price_gbp DESC;

-- Q2: ORDER BY / LIMIT
SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 10;

-- Q3: DISTINCT + JOIN
SELECT DISTINCT c.category_name
FROM books b JOIN categories c ON b.category_id = c.category_id;

-- Q4: BETWEEN
SELECT title, rating, price_gbp
FROM books WHERE price_gbp BETWEEN 20 AND 40 ORDER BY price_gbp;

-- Q5: JOIN
SELECT c.category_name AS category, b.title, b.rating, b.price_gbp
FROM books b JOIN categories c ON b.category_id = c.category_id
ORDER BY c.category_name, b.rating DESC, b.title LIMIT 30;
