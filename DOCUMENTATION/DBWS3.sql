--total payments made by VIP customers for vinyl purchases
SELECT c.CustomerID, c.Name, SUM(p.FinalAmount) AS TotalPaid
FROM Payments p
JOIN VIPCustomer v ON p.CustomerID = v.CustomerID
JOIN Customer c ON c.CustomerID = p.CustomerID
WHERE p.PaymentFor = 'Vinyl Purchase'
GROUP BY c.CustomerID;

--most expensive vinyl purchased by each customer along with the price
SELECT c.CustomerID, c.Name, v.Name AS VinylName, MAX(v.Price) AS MaxPrice
FROM Payments p
JOIN Vinyl v ON p.VinylID = v.VinylID
JOIN Customer c ON c.CustomerID = p.CustomerID
WHERE p.PaymentFor = 'Vinyl Purchase'
GROUP BY c.CustomerID;

--average price of vinyl purchases made by customers who applied any discounts
SELECT AVG(p.FinalAmount) AS AvgPriceWithDiscount
FROM Payments p
WHERE p.DiscountApplied > 0;

--names and total purchases of customers who bought vinyls in a specific genre

SELECT c.CustomerID, c.Name, COUNT(p.PaymentID) AS VinylPurchases
FROM Payments p
JOIN Vinyl v ON p.VinylID = v.VinylID
JOIN Customer c ON c.CustomerID = p.CustomerID
WHERE v.Genre = 'Rock'
GROUP BY c.CustomerID;

--customers who have not purchased any vinyls in the last 6 months
SELECT c.CustomerID, c.Name
FROM Customer c
LEFT JOIN Payments p ON c.CustomerID = p.CustomerID AND p.PaymentFor = 'Vinyl Purchase'
WHERE p.PaymentDate < NOW() - INTERVAL 6 MONTH OR p.PaymentID IS NULL;
