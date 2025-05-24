CREATE TABLE urls (
    url_id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    page_num INT
);


CREATE TABLE cars (
    car_id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    brand TEXT,
    model TEXT,
    price TEXT,
    post_code TEXT,
    prod_year TEXT,
    mileage TEXT,
    gearbox TEXT,
    energy TEXT,
    attrs JSONB,
    crawled_at TIMESTAMP DEFAULT NOW()
);

