import mysql.connector


def createTable(conn: mysql.connector.MySQLConnection):
    c = conn.cursor()
    # Check if the tables already exist

    c.execute('''CREATE TABLE IF NOT EXISTS user (
                        user_id VARCHAR(10) PRIMARY KEY,
                        password VARCHAR(256) NOT NULL,
                        role VARCHAR(10) CHECK (role IN ('patient', 'doctor', 'nurse', 'helping_staff', 'admin')),
                        valid INTEGER,
                        register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')


    c.execute('''CREATE TABLE IF NOT EXISTS patient (
                        patient_id VARCHAR(10) PRIMARY KEY CHECK (CHAR_LENGTH(patient_id) = 10),
                        name VARCHAR(255) NOT NULL,
                        gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
                        birthdate DATE DEFAULT '1900-01-01' NOT NULL,
                        marital_status VARCHAR(255),
                        occupation VARCHAR(255),
                        birthplace VARCHAR(255),
                        nationality VARCHAR(255),
                        identification_document_type VARCHAR(255),
                        identification_number VARCHAR(255),
                        phone VARCHAR(15),
                        address VARCHAR(255),
                        blood_type VARCHAR(10),
                        allergens VARCHAR(255),
                        initial_diagnosis_date DATE,
                        emergency_contact VARCHAR(255),
                        emergency_contact_relationship VARCHAR(255),
                        emergency_contact_phone VARCHAR(15),
                        emergency_contact_address VARCHAR(255),
                        valid INTEGER
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS employee (
                        employee_id VARCHAR(10) PRIMARY KEY CHECK (CHAR_LENGTH(employee_id) = 10),
                        name VARCHAR(255) NOT NULL,
                        gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
                        position VARCHAR(255),
                        birthdate DATE,
                        phone VARCHAR(15),
                        address VARCHAR(255),
                        date_of_hire DATE,
                        date_of_dismiss DATE,
                        supervisor_id VARCHAR(10),
                        salary REAL,
                        valid INTEGER
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS doctor (
                        doctor_id VARCHAR(10) PRIMARY KEY CHECK (CHAR_LENGTH(doctor_id) = 10),
                        department TEXT,
                        license_number TEXT,
                        FOREIGN KEY (doctor_id) REFERENCES employee(employee_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS room (
                        room_id VARCHAR(4) PRIMARY KEY,
                        room_type TEXT,
                        number_of_beds INTEGER,
                        additional_facility TEXT,
                        doctor_id VARCHAR(10),
                        available_beds INTEGER,
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS nurse (
                        nurse_id VARCHAR(10) PRIMARY KEY CHECK (CHAR_LENGTH(nurse_id) = 10),
                        room_id VARCHAR(4),
                        license_number TEXT,
                        FOREIGN KEY (nurse_id) REFERENCES employee(employee_id),
                        FOREIGN KEY (room_id) REFERENCES room(room_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS helping_staff (
                        helping_staff_id VARCHAR(10) PRIMARY KEY CHECK (CHAR_LENGTH(helping_staff_id) = 10),
                        room_id VARCHAR(4),
                        FOREIGN KEY (helping_staff_id) REFERENCES employee(employee_id),
                        FOREIGN KEY (room_id) REFERENCES room(room_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS charge (
                        charge_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        patient_id VARCHAR(10),
                        cost INTEGER,
                        is_completed VARCHAR(3) CHECK (is_completed IN ('YES', 'NO')),
                        charge_date_time TIMESTAMP,
                        payment_method TEXT,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS consultation (
                        consultation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        doctor_id VARCHAR(10),
                        patient_id VARCHAR(10),
                        date_time TIMESTAMP,
                        self_report TEXT,
                        medical_history TEXT,
                        medication_history TEXT,
                        medical_advice TEXT,
                        charge_id INTEGER,
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS prescription (
                        prescription_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        consultation_id INTEGER,
                        doctor_id VARCHAR(10),
                        pharmacy_window TEXT,
                        pharmacy_pickup_date_time TIMESTAMP,
                        charge_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (consultation_id) REFERENCES consultation(consultation_id),
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS medicine (
                        medicine_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        name TEXT NOT NULL,
                        manufacturer TEXT,
                        cost INTEGER
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS prescription_medicine (
                        prescription_id INTEGER,
                        medicine_id INTEGER,
                        quantity INTEGER,
                        course_of_medication TEXT,
                        dosage TEXT,
                        frequency TEXT,
                        cost INTEGER,
                        tag INTEGER DEFAULT 0,                        
                        PRIMARY KEY (prescription_id, medicine_id),
                        FOREIGN KEY (prescription_id) REFERENCES prescription(prescription_id),
                        FOREIGN KEY (medicine_id) REFERENCES medicine(medicine_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS examination (
                        examination_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        consultation_id INTEGER,
                        examination_date_time TIMESTAMP,
                        time_of_result TIMESTAMP,
                        examination_name VARCHAR(255) NOT NULL,
                        result TEXT,
                        charge_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (consultation_id) REFERENCES consultation(consultation_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS examination_doctor (
                        examination_id INTEGER,
                        doctor_id VARCHAR(10),
                        PRIMARY KEY (examination_id, doctor_id),
                        FOREIGN KEY (examination_id) REFERENCES examination(examination_id),
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS examination_helping_staff (
                        examination_id INTEGER,
                        helping_staff_id VARCHAR(10),
                        PRIMARY KEY (examination_id, helping_staff_id),
                        FOREIGN KEY (examination_id) REFERENCES examination(examination_id),
                        FOREIGN KEY (helping_staff_id) REFERENCES helping_staff(helping_staff_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS examination_nurse (
                        examination_id INTEGER,
                        nurse_id VARCHAR(10),
                        PRIMARY KEY (examination_id, nurse_id),
                        FOREIGN KEY (examination_id) REFERENCES examination(examination_id),
                        FOREIGN KEY (nurse_id) REFERENCES nurse(nurse_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rehabilitation (
                        rehabilitation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        consultation_id INTEGER,
                        rehabilitation_name VARCHAR(255) NOT NULL,
                        begin_date_time TIMESTAMP,
                        end_date_time TIMESTAMP,
                        charge_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (consultation_id) REFERENCES consultation(consultation_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rehabilitation_doctor (
                        rehabilitation_id INTEGER,
                        doctor_id VARCHAR(10),
                        PRIMARY KEY (rehabilitation_id, doctor_id),
                        FOREIGN KEY (rehabilitation_id) REFERENCES rehabilitation(rehabilitation_id),
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rehabilitation_helping_staff (
                        rehabilitation_id INTEGER,
                        helping_staff_id VARCHAR(10),
                        PRIMARY KEY (rehabilitation_id, helping_staff_id),
                        FOREIGN KEY (rehabilitation_id) REFERENCES rehabilitation(rehabilitation_id),
                        FOREIGN KEY (helping_staff_id) REFERENCES helping_staff(helping_staff_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rehabilitation_nurse (
                        rehabilitation_id INTEGER,
                        nurse_id VARCHAR(10),
                        PRIMARY KEY (rehabilitation_id, nurse_id),
                        FOREIGN KEY (rehabilitation_id) REFERENCES rehabilitation(rehabilitation_id),
                        FOREIGN KEY (nurse_id) REFERENCES nurse(nurse_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgery (
                        surgery_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        consultation_id INTEGER,
                        patient_id VARCHAR(10),
                        lead_surgeon_id VARCHAR(10),
                        surgery_name VARCHAR(255) NOT NULL,
                        surgery_description TEXT,
                        surgery_site TEXT,
                        surgery_type TEXT,
                        begin_date_time TIMESTAMP,
                        end_date_time TIMESTAMP,
                        charge_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (consultation_id) REFERENCES consultation(consultation_id),
                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                        FOREIGN KEY (lead_surgeon_id) REFERENCES doctor(doctor_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgery_related_record (
                        surgery_id INTEGER,
                        record_date_time TIMESTAMP,
                        record_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        record_detail TEXT,
                        UNIQUE (record_id),
                        FOREIGN KEY (surgery_id) REFERENCES surgery(surgery_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgery_doctor (
                        surgery_id INTEGER,
                        doctor_id VARCHAR(10),
                        role TEXT,
                        PRIMARY KEY (surgery_id, doctor_id),
                        FOREIGN KEY (surgery_id) REFERENCES surgery(surgery_id),
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgery_helping_staff (
                        surgery_id INTEGER,
                        helping_staff_id VARCHAR(10),
                        PRIMARY KEY (surgery_id, helping_staff_id),
                        FOREIGN KEY (surgery_id) REFERENCES surgery(surgery_id),
                        FOREIGN KEY (helping_staff_id) REFERENCES helping_staff(helping_staff_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgery_nurse (
                        surgery_id INTEGER,
                        nurse_id VARCHAR(10),
                        role TEXT,
                        PRIMARY KEY (surgery_id, nurse_id),
                        FOREIGN KEY (surgery_id) REFERENCES surgery(surgery_id),
                        FOREIGN KEY (nurse_id) REFERENCES nurse(nurse_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS hospitalization (
                        hospitalization_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        patient_id VARCHAR(10),
                        doctor_id VARCHAR(10),
                        hospitalization_date_time TIMESTAMP,
                        hospitalization_reason TEXT,
                        discharge_date_time TIMESTAMP,
                        discharge_reason TEXT,
                        room_id VARCHAR(4),
                        bed_number INTEGER,
                        charge_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
                        FOREIGN KEY (room_id) REFERENCES room(room_id),
                        FOREIGN KEY (charge_id) REFERENCES charge(charge_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS hospitalization_record (
                        hospitalization_id INTEGER,
                        consultation_id INTEGER,
                        tag INTEGER DEFAULT 0,
                        PRIMARY KEY (hospitalization_id, consultation_id),
                        FOREIGN KEY (hospitalization_id) REFERENCES hospitalization(hospitalization_id),
                        FOREIGN KEY (consultation_id) REFERENCES consultation(consultation_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointment (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        doctor_id VARCHAR(10),
                        datetime TIMESTAMP,
                        cost INTEGER,
                        available_slots INT,
                        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS departments (
                        name VARCHAR(255) PRIMARY KEY,
                        description TEXT
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS examinations (
                        examination_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(255),
                        cost INTEGER
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS surgeries (
                        name VARCHAR(255) PRIMARY KEY,
                        cost INTEGER,
                        surgery_site TEXT
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rehabilitations (
                        rehabilitation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(255),
                        cost INTEGER
                    )''')