INSERT INTO user (id, email, password) VALUES
(1, 'admin@example.com', 'pbkdf2:sha256:150000$w0mLxLJU$e6f21a4b45a0d10286766f33057834949148eb2b3ecc4ec1a136d619f82034d0'); -- password

INSERT INTO company (id, created_at, name, slogan) VALUES 
(1, datetime(), "Soap Subscription "|| DATE(), "Sqeaky clean!");

INSERT INTO category(id, uuid, created_at, name) VALUES
(1, "7085d61d-c84d-4951-a824-aa27c7e21086", datetime(), "Make your choice");

INSERT INTO plan 
(id, created_at, archived, uuid, title, interval_unit, interval_amount, sell_price, days_before_first_charge, trial_period_days, category_uuid, private)
VALUES(1, datetime(), 0,  '840500cb-c663-43e6-a632-d8521bb14c42', 'Hair Gel', 'weekly', 599, 100, 0, 0, '7085d61d-c84d-4951-a824-aa27c7e21086', 0);

INSERT INTO plan 
(id, created_at, archived, uuid, title, interval_unit, interval_amount, days_before_first_charge, trial_period_days, description, category_uuid, private)
VALUES(2, datetime(), 0,  '5813b05b-9031-45b3-b120-8fc6b1b3082e', 'Bath Soaps', 'monthly', 1099, 0, 0, 'This plan has a description', '7085d61d-c84d-4951-a824-aa27c7e21086', 0);

INSERT INTO plan 
(id, created_at, archived, uuid, title, sell_price, days_before_first_charge, trial_period_days, category_uuid, private)
VALUES(3, datetime(), 0,  '58921f7a-3371-4ccf-aeee-e2b8af5cca3a', 'One-Off Soaps', 566, 0, 0, '7085d61d-c84d-4951-a824-aa27c7e21086', 0);

INSERT INTO plan
(id, created_at, archived, uuid, title, sell_price, days_before_first_charge, trial_period_days, category_uuid, private)
VALUES(4, datetime(), 0,  '20921f7a-3371-4ccf-aeee-e2b8af5cca20', 'Free plan', 0, 0, 0, '7085d61d-c84d-4951-a824-aa27c7e21086', 0);

INSERT INTO plan_requirements (
id, created_at, plan_id, instant_payment, subscription)
VALUES
(1, datetime(), 1, 1, 1),
(2, datetime(), 2, 0, 1),
(3, datetime(), 3, 1, 0),
(4, datetime(), 4, 0, 0);

INSERT INTO plan_selling_points (
id, created_at, point, plan_id
)
VALUES
( 1, datetime(), "Homemade", 1),
( 2, datetime(), "High Quality", 1),
( 3, datetime(), "Smooth", 1),
( 4, datetime(), "Pack of 5", 2),
( 5, datetime(), "Luxury soaps", 2),
( 6, datetime(), "Assorted scents", 2),
( 7, datetime(), "One off purchase", 3),
( 8, datetime(), "Luxury soaps", 3),
( 9, datetime(), "Assorted scents", 3);


INSERT INTO integration (
tawk_active, tawk_property_id)
VALUES (0, 'example');


CREATE TABLE IF NOT EXISTS builder_sites
    (
      site_url text,
      email text
);

INSERT INTO setting (id, charge_vat, shop_activated, default_currency, default_country_code) 
VALUES (1,0,0,'GBP','GB');
