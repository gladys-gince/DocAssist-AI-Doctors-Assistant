CREATE TABLE user_data (
    user_id SERIAL PRIMARY KEY,
    gmail VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
	CONSTRAINT unique_user_data UNIQUE (user_id, gmail)
);

drop TABLE user_data;
select * from user_data;
INSERT INTO user_data (gmail, password, type) VALUES ('admin', 'admin', 'admin');
DELETE FROM user_data WHERE user_id = 2;
UPDATE user_data
SET type = 'doctor'
WHERE user_id = 3;




CREATE TABLE doctor_timing (
    ID SERIAL PRIMARY KEY,
    specialist VARCHAR(255),
    Name VARCHAR(255),
    timing VARCHAR(255),
    day VARCHAR(255)
);

INSERT INTO doctor_timing (specialist, Name, timing, day)
VALUES
    ('Cardiologist', 'Dr. Abhishek Shah', '6pm - 8pm', 'Monday'),
    ('Cardiologist', 'Dr. Ajit R. Menon', '9am - 11am', 'Wednesday'),
    ('Cardiologist', 'Dr. Amit M. Vora', '2pm - 4pm', 'Tuesday'),
    ('Physiotherapist', 'Dr. Heena S. Garuda', '5pm - 7pm', 'Friday'),
    ('Psychiatrist', 'Dr. Bharat R. Shah', '6pm - 8pm', 'Monday'),
    ('Psychiatrist', 'Dr. Dilip K. Deshmukh', '9am - 11am', 'Wednesday'),
    ('Psychiatrist', 'Dr. Vihang N. Vahia', '2pm - 4pm', 'Tuesday');

INSERT INTO doctor_timing (specialist, Name, timing, day)
VALUES ('Neurologist', 'Dr. Pratham Kambli', '1:30pm - 3:30pm', 'Friday');

select * from doctor_timing;

CREATE TABLE user_demographic (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10),	
    contact VARCHAR(15),
    blood_group VARCHAR(5),
    dob VARCHAR(255),
    profile_photo BYTEA, 
    address TEXT
);


select * from user_demographic WHERE user_id = 2;
select * from user_demographic WHERE user_id = 2;
DELETE FROM user_demographic WHERE user_id = 2;

CREATE TABLE appointments (
    srno SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    doctor_type VARCHAR(50) NOT NULL,
    doctor_name VARCHAR(100) NOT NULL,
    doctor_date DATE NOT NULL
);

select * from appointments;
DELETE FROM appointments WHERE user_id = 2;

CREATE TABLE appointment_history (
    "Appointment ID" SERIAL PRIMARY KEY,
    "Patient ID" INT,
    "Doctor Name" VARCHAR(255),
    "Appointment Time" VARCHAR(255),
    "Regular Medicines" VARCHAR(255),
    "Last Prescribed Medicines" VARCHAR(255),
    "Current Prescribed Medicine" VARCHAR(255),
    "Immunization History" VARCHAR(255),
    "Detected Symptoms" VARCHAR(255),
    "Detected Diseases" VARCHAR(255),
    "Detected Surgery" VARCHAR(255),
    "Detected Tests" VARCHAR(255),
    "Conversation Tone" VARCHAR(255),
    "Voice Recording" BYTEA -- Assuming the voice recording is stored as binary data
);

delete from appointment_history where "Appointment ID" = 6;

select * from appointment_history;



