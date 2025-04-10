# project 1 DB init

-- Create New DB
CREATE DATABASE car_data;
-- Choose DB
USE car_data;

-- Init Tables
DROP TABLE IF EXISTS ev_specs;
DROP TABLE IF EXISTS engine_specs;
DROP TABLE IF EXISTS cars;
DROP TABLE IF EXISTS car_brands;

DROP TABLE IF EXISTS recalls;

-- Create Tables
CREATE TABLE car_brands (
	brand			VARCHAR(50) PRIMARY KEY,
	brand_img		TEXT
);
CREATE TABLE cars (
	model_id		INT		PRIMARY KEY,
	name			VARCHAR(100),
	brand			VARCHAR(50),
	car_type		VARCHAR(50),
	fuel_type		VARCHAR(100),
	release_date	VARCHAR(20),
	price			INT,		-- 가격 (만원 단위)
	image_url		TEXT,
	detail_url		TEXT,
	FOREIGN KEY (brand) REFERENCES car_brands(brand)
);
CREATE TABLE engine_specs (
	model_id			INT PRIMARY KEY,
	engine_displacement	VARCHAR(50),
	efficiency			VARCHAR(50),
	delivery_period		VARCHAR(50),
	FOREIGN KEY (model_id) REFERENCES cars(model_id)
);
CREATE TABLE ev_specs (
	model_id				INT PRIMARY KEY,
	efficiency_km_per_kwh	VARCHAR(255),
	total_range_km			VARCHAR(255),
	battery_capacity_kwh	VARCHAR(255),
	battery_manufacturer	VARCHAR(255),
	delivery_period			VARCHAR(50),
	FOREIGN KEY (model_id) REFERENCES cars(model_id)
);
CREATE TABLE recalls (
	brand				VARCHAR(20)		NOT NULL,
	name				VARCHAR(100)	NOT NULL,
	release_start		DATE,		-- 제조 시작일
	release_end			DATE,		-- 제조 일
	recall_type			VARCHAR(20),
	announcement_start	DATE,
	announcement_end	DATE,
	source				VARCHAR(50),
	defect_description	TEXT
);


CREATE TABLE test_car_brands (
	brand			VARCHAR(50) PRIMARY KEY,
	brand_img		TEXT
);
CREATE TABLE test_cars (
	model_id		INT		PRIMARY KEY,
	name			VARCHAR(100),
	brand			VARCHAR(50),
	brand_img		TEXT,
	car_type		VARCHAR(50),
	fuel_type		VARCHAR(100),
	release_date	VARCHAR(20),
	price			BIGINT,		-- 가격 (만원 단위)
	image_url		TEXT,
	detail_url		TEXT,
	FOREIGN KEY (brand) REFERENCES test_car_brands(brand)
);
CREATE TABLE test_engine_specs (
	model_id			INT PRIMARY KEY,
	engine_displacement	VARCHAR(50),
	efficiency			VARCHAR(50),
	delivery_period		VARCHAR(50),
	FOREIGN KEY (model_id) REFERENCES test_cars(model_id)
);
CREATE TABLE test_ev_specs (
	model_id				INT PRIMARY KEY,
	efficiency_km_per_kwh	VARCHAR(255),
	total_range_km			VARCHAR(255),
	battery_capacity_kwh	VARCHAR(255),
	battery_manufacturer	VARCHAR(255),
	delivery_period			VARCHAR(50),
	FOREIGN KEY (model_id) REFERENCES test_cars(model_id)
);

