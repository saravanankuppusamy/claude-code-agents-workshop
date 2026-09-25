-- 2026_09_20_orders_cleanup.sql  (proposed)
ALTER TABLE orders DROP COLUMN legacy_status;
ALTER TABLE orders ADD COLUMN status TEXT NOT NULL;
UPDATE orders SET status = 'shipped' WHERE shipped_at IS NOT NULL;
CREATE INDEX idx_orders_customer ON orders(customer_id);
DELETE FROM customers WHERE last_login < '2020-01-01';
