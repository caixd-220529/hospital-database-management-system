from typing import Dict
import re
import mysql.connector

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
    'roomId': 'room_id',
}

consultation_fields = {
    'consultationId': 'consultation_id',
    'patientId': 'patient_id',
    'patientName': 'patient.name',
    'time': 'date_time',
    'selfReport': 'self_report',
    'medicalHistory': 'medical_history',
    'medicationHistory': 'medication_history',
    'medicalAdvice': 'medical_advice',
    'chargeId': 'charge_id'
}

prescription_medicine_fields = {
    'prescriptionId': 'prescription_id',
    'medicineId': 'medicine_id',
    'quantity': 'quantity',
    'courseOfMedication': 'course_of_medication',
    'dosage': 'dosage',
    'frequency': 'frequency',
    'cost': 'cost',

}

examination_time_choose = ['09:00:00', '10:00:00', '11:00:00', '12:00:00', '13:00:00',
                           '14:00:00', '15:00:00', '16:00:00', '17:00:00' ]

rehabilitation_time_choose = examination_time_choose

surgery_time_choose = ['09:00:00', '13:00:00']
def check_number(number):
    # Check if the phone number contains any non-digit characters
    if re.search(r'[^0-9]', number):
        return False
    else:
        return True


def check_patient_info(info: dict):
    new_patient_fields = {v: k for k, v in patient_fields.items()}
    for field in info.keys():
        value = info[field]
        if value is not None:
            if field == 'patient_id' and len(value) > 10:
                return new_patient_fields[field]
            elif field == 'name' and len(value) > 255:
                return new_patient_fields[field]
            elif field == 'identification_number' and (len(value) > 255 or not check_number(value)):
                return new_patient_fields[field]
            elif field == 'phone' and (len(value) > 15 or not check_number(value)):
                return new_patient_fields[field]
            elif field == 'emergency_contact_phone' and (len(value) > 15 or not check_number(value)):
                return new_patient_fields[field]
    return ''


def check_employee_info(info: dict):
    new_employee_fields = {v: k for k, v in employee_fields.items()}
    for field in info.keys():
        value = info[field]
        if value is not None:
            if field == 'employee_id' and len(value) > 10:
                return new_employee_fields[field]
            elif field == 'name' and len(value) > 255:
                return new_employee_fields[field]
            elif field == 'phone' and (len(value) > 15 or not check_number(value)):
                return new_employee_fields[field]
    return ''


def check_doctor_info(info: dict):
    new_doctor_fields = {v: k for k, v in employee_fields.items()}
    for field in info.keys():
        value = info[field]
        if value is not None:
            if field == 'doctor_id' and len(value) > 10:
                return new_doctor_fields[field]
            elif field == 'department' and len(value) > 255:
                return new_doctor_fields[field]
            elif field == 'license_number' and len(value) > 255:
                return new_doctor_fields[field]
    return check_employee_info(info)


def check_nurse_info(info: dict):
    new_nurse_fields = {v: k for k, v in employee_fields.items()}
    for field in info.keys():
        value = info[field]
        if value is not None:
            if field == 'nurse_id' and len(value) > 10:
                return new_nurse_fields[field]
            elif field == 'room_id' and (len(value) > 4 or not check_number(value)):
                return new_nurse_fields[field]
            elif field == 'license_number' and len(value) > 255:
                return new_nurse_fields[field]
    return check_employee_info(info)


def check_staff_info(info: dict):
    new_staff_fields = {v: k for k, v in employee_fields.items()}
    for field in info.keys():
        value = info[field]
        if value is not None:
            if field == 'helping_staff_id' and len(value) > 10:
                return new_staff_fields[field]
            elif field == 'room_id' and (len(value) > 4 or not check_number(value)):
                return new_staff_fields[field]
    return check_employee_info(info)

def check_atomic(conn: mysql.connector.MySQLConnection):
    c = conn.cursor()
    delete = f'''DELETE FROM hospitalization_record WHERE tag = 0 '''
    c.execute(delete)
    delete = f'''DELETE FROM hospitalization WHERE tag = 0 '''
    c.execute(delete)
    delete = f'''DELETE FROM surgery WHERE tag = 0'''
    c.execute(delete)
    delete = f'''DELETE FROM rehabilitation WHERE tag = 0'''
    c.execute(delete)
    delete = f'''DELETE FROM examination WHERE tag = 0'''
    c.execute(delete)
    delete = f'''DELETE FROM prescription_medicine WHERE tag = 0'''
    c.execute(delete)
    delete = f'''DELETE FROM prescription WHERE tag = 0'''
    c.execute(delete)
    delete = f'''DELETE FROM charge WHERE tag = 0'''
    c.execute(delete)
    conn.commit()

