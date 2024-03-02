import mysql.connector
from SQLWrapper import SQLWrapper
from hashlib import sha256
from dateutil.parser import *
from datetime import datetime, date, time
from pytz import timezone
from typing import Union

from checker import check_patient_info, check_staff_info, check_nurse_info, check_doctor_info

patient_fields = {
    # front-end form to back-end database
    'patientId': 'patient_id',
    'name': 'name',
    'gender': 'gender',
    'birthdate': 'birthdate',
    'maritalStatus': 'marital_status',
    'occupation': 'occupation',
    'birthplace': 'birthplace',
    'nationality': 'nationality',
    'identificationDocumentType': 'identification_document_type',
    'identificationNumber': 'identification_number',
    'phone': 'phone',
    'address': 'address',
    'bloodType': 'blood_type',
    'allergens': 'allergens',
    'initialDiagnosisDate': 'initial_diagnosis_date',
    'emergencyContact': 'emergency_contact',
    'emergencyContactRelationship': 'emergency_contact_relationship',
    'emergencyContactPhone': 'emergency_contact_phone',
    'emergencyContactAddress': 'emergency_contact_address',
}

employee_fields = {
    'employeeId': 'employee_id',
    'name': 'name',
    'gender': 'gender',
    'position': 'position',
    'birthdate': 'birthdate',
    'phone': 'phone',
    'address': 'address',
    'dateOfHire': 'date_of_hire',
    'dateOfDismiss': 'date_of_dismiss',
    'supervisorId': 'supervisor_id',
    'salary': 'salary',
}

doctor_fields = {
    'doctorId': 'doctor_id',
    'department': 'department',
    'licenseNumber': 'license_number',
}

nurse_fields = {
    'nurseId': 'nurse_id',
    'roomId': 'room_id',
    'licenseNumber': 'license_number',
}

staff_fields = {
    'helpingStaffId': 'helping_staff_id',
}



def employee_preprocess(form: dict) -> str:
    form['birthdate'] = parse(form['birthdate']).strftime('%Y-%m-%d')
    form['dateOfHire'] = parse(form['dateOfHire']).strftime('%Y-%m-%d')
    psw_digest = sha256(form['password'].encode('utf-8')).hexdigest()
    form.pop('password')
    form.pop('confirmPassword')
    form.pop('formName')
    return psw_digest


class Register:
    @staticmethod
    def register_patient(form: dict, conn: mysql.connector.MySQLConnection) -> (str, list):
        # pre-processing
        form['allergens'] = ','.join(form['allergens']) + ','
        form['birthdate'] = parse(form['birthdate']).strftime('%Y-%m-%d')
        form['initialDiagnosisDate'] = parse(form['initialDiagnosisDate']).strftime('%Y-%m-%d')
        psw_digest = sha256(form['password'].encode('utf-8')).hexdigest()
        form.pop('password')
        form.pop('confirmPassword')
        form.pop('formName')
        # substitute form key names with database field names
        for k in list(form.keys()):
            if not form[k]:
                form[k] = None
            form[patient_fields[k]] = form.pop(k)

        err = check_patient_info(form)
        if err:
            return '', err

        # insert into database
        wrapper = SQLWrapper(conn)
        wrapper.query(['patient'], ['MAX(patient_id)'])
        wrapper.run(limit=1)
        max_id = wrapper.get()
        max_id = 0 if max_id[0][0] is None else int(max_id[0][0][1:])
        new_id = 'p{:09d}'.format(max_id + 1)

        form['patient_id'] = new_id
        values = ', '.join([f'%({v})s' for v in patient_fields.values()]) + ', %(valid)s'
        form['valid'] = 1
        sql = f'INSERT INTO patient VALUES ({values});'
        wrapper.execute_raw(sql, False, form)

        # create user
        wrapper.clear()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wrapper.insert('user', [(new_id, psw_digest, 'patient', 1, now)])
        wrapper.commit()

        return new_id, []

    @staticmethod
    def register_employee(form: dict, wrapper: SQLWrapper):
        fields = list(set(employee_fields.values()) & set(form.keys()))
        fields_s = ', '.join(fields) + ', valid'
        values_s = ', '.join([f'%({f})s' for f in fields]) + ', %(valid)s'
        form['valid'] = 0
        sql = f'INSERT INTO employee ({fields_s}) VALUES ({values_s});'
        wrapper.execute_raw(sql, False, form)

    @staticmethod
    def register_doctor(form: dict, conn: mysql.connector.MySQLConnection) -> (str, list):
        # pre-processing
        psw_digest = employee_preprocess(form)
        # substitute form key names with database field names
        for k in list(form.keys()):
            if not form[k]:
                form[k] = None
            form[dict(employee_fields, **doctor_fields)[k]] = form.pop(k)

        err = check_doctor_info(form)
        if err:
            return '', err

        # insert into database
        wrapper = SQLWrapper(conn)
        wrapper.query(['doctor'], ['MAX(doctor_id)'])
        wrapper.run(limit=1)
        max_id = wrapper.get()
        max_id = 0 if max_id[0][0] is None else int(max_id[0][0][1:])
        new_id = 'd{:09d}'.format(max_id + 1)

        form['employee_id'] = new_id
        form['doctor_id'] = new_id

        Register.register_employee(form, wrapper)

        fields = list(doctor_fields.values())
        fields_s = ', '.join(fields)
        values_s = ', '.join([f'%({v})s' for v in doctor_fields.values()])
        sql = f'INSERT INTO doctor ({fields_s}) VALUES ({values_s});'
        wrapper.execute_raw(sql, False, form)

        # create user
        wrapper.clear()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wrapper.insert('user', [(new_id, psw_digest, 'doctor', 0, now)])
        wrapper.commit()

        return new_id, []

    @staticmethod
    def register_nurse(form: dict, conn: mysql.connector.MySQLConnection) -> (str, list):
        # pre-processing
        psw_digest = employee_preprocess(form)
        # substitute form key names with database field names
        for k in list(form.keys()):
            if not form[k]:
                form[k] = None
            form[dict(employee_fields, **nurse_fields)[k]] = form.pop(k)

        err = check_nurse_info(form)
        if err:
            return '', err

        # insert into database
        wrapper = SQLWrapper(conn)
        wrapper.query(['nurse'], ['MAX(nurse_id)'])
        wrapper.run(limit=1)
        max_id = wrapper.get()
        max_id = 0 if max_id[0][0] is None else int(max_id[0][0][1:])
        new_id = 'n{:09d}'.format(max_id + 1)

        form['employee_id'] = new_id
        form['nurse_id'] = new_id

        Register.register_employee(form, wrapper)

        fields = list(set(nurse_fields.values()) & set(form.keys()))
        fields_s = ', '.join(fields)
        values_s = ', '.join([f'%({v})s' for v in nurse_fields.values()])
        sql = f'INSERT INTO nurse ({fields_s}) VALUES ({values_s});'
        wrapper.execute_raw(sql, False, form)
        wrapper.commit()

        # create user
        wrapper.clear()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wrapper.insert('user', [(new_id, psw_digest, 'nurse', 0, now)])

        return new_id, []

    @staticmethod
    def register_staff(form: dict, conn: mysql.connector.MySQLConnection) -> (str, list):
        # pre-processing
        psw_digest = employee_preprocess(form)
        # substitute form key names with database field names
        for k in list(form.keys()):
            if not form[k]:
                form[k] = None
            form[dict(employee_fields, **staff_fields)[k]] = form.pop(k)

        err = check_staff_info(form)
        if err:
            return '', err

        # insert into database
        wrapper = SQLWrapper(conn)
        wrapper.query(['helping_staff'], ['MAX(helping_staff_id)'])
        wrapper.run(limit=1)
        max_id = wrapper.get()
        max_id = 0 if max_id[0][0] is None else int(max_id[0][0][1:])
        new_id = 's{:09d}'.format(max_id + 1)

        form['employee_id'] = new_id
        form['helping_staff_id'] = new_id

        Register.register_employee(form, wrapper)

        fields_s = ['helping_staff_id', 'room_id']
        values_s = ['%(helping_staff_id)s', '%(room_id)s']
        sql = f'INSERT INTO helping_staff ({fields_s}) VALUES ({values_s});'
        wrapper.execute_raw(sql, False, form)
        wrapper.commit()

        # create user
        wrapper.clear()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wrapper.insert('user', [(new_id, psw_digest, 'staff', 0, now)])

        return new_id, []


def convert_time(dt: Union[str, datetime, date], _format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    convert datetime to UTC+8, string in format 'YYYY-MM-DD HH:MM:SS'
    :param dt: datetime string or datetime object
    :return: string in format 'YYYY-MM-DD HH:MM:SS'
    """
    if not dt:
        return ''
    if isinstance(dt, date):
        # convert date object to datetime object
        dt = datetime.combine(dt, time())
    if isinstance(dt, datetime):
        tz = timezone('Asia/Shanghai')
        return dt.astimezone(tz).strftime(_format)
    tz = timezone('Asia/Shanghai')
    return parse(dt).astimezone(tz).strftime(_format)


def get_doctor_name(doctor_id: str, conn: mysql.connector.MySQLConnection):
    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'], ['name'])
    wrapper.where('employee_id', '=', doctor_id, 'str')
    wrapper.run(limit=1)
    doctor_name = ''
    if wrapper.get():
        doctor_name = wrapper.get()[0][0]
    return doctor_name


def get_patient_name(patient_id: str, conn: mysql.connector.MySQLConnection):
    wrapper = SQLWrapper(conn)
    wrapper.query(['patient'], ['name'])
    wrapper.where('patient_id', '=', patient_id, 'str')
    wrapper.run(limit=1)
    patient_name = ''
    if wrapper.get():
        patient_name = wrapper.get()[0][0]
    return patient_name
