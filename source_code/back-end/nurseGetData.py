# for api: /caregiver/get-table-data
from SQLWrapper import SQLWrapper
from mysql.connector import MySQLConnection
from common import convert_time


def nurse_return(res: list):
    ret = []
    for t in res:
        ret.append({
            'itemId': t[0],
            'itemName': t[1],
            'patientId': t[2],
            'patientName': t[3],
            'time1': convert_time(t[4]),
            'time2': convert_time(t[5]),
            'caregiverId': t[6],
            'caregiverName': t[7],
            'consultationId': t[8],
        })
    return ret


def nurse_get_examination_data(conn: MySQLConnection, info: dict):
    wrapper = SQLWrapper(conn)
    query_fields = [
        'examination.examination_id',
        'examination.examination_name',
        'patient.patient_id',
        'patient.name',
        'examination.examination_date_time',
        'examination.time_of_result',
        'examination_nurse.nurse_id',
        'employee.name',
        'consultation.consultation_id',
    ]
    wrapper.query(['examination', 'consultation', 'patient', 'examination_nurse', 'employee'], query_fields)
    # for join
    wrapper.where('examination.examination_id', '=', 'examination_nurse.examination_id', 'field')
    wrapper.where('examination_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('examination.consultation_id', '=', 'consultation.consultation_id', 'field')

    wrapper.where('examination.examination_id', '=', info['id'], 'str')
    wrapper.where('examination.examination_name', '=', info['name'], 'str')
    wrapper.where('patient.patient_id', '=', info['patient_id'], 'str')
    wrapper.where('patient.name', '=', info['patient_name'], 'str')

    wrapper.where('examination.examination_date_time', '>=', info['begin_time1'], 'str')
    wrapper.where('examination.examination_date_time', '<=', info['end_time1'], 'str')

    if info['is_history'] == 'true':
        wrapper.where('examination.time_of_result', 'IS NOT', 'NULL', 'null')
        wrapper.where('examination.time_of_result', '>=', info['begin_time2'], 'str')
        wrapper.where('examination.time_of_result', '<=', info['end_time2'], 'str')
    else:
        wrapper.where('examination.time_of_result', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    return nurse_return(res)


def nurse_get_rehabilitation_data(conn: MySQLConnection, info: dict):
    wrapper = SQLWrapper(conn)
    query_fields = [
        'rehabilitation.rehabilitation_id',
        'rehabilitation.rehabilitation_name',
        'patient.patient_id',
        'patient.name',
        'rehabilitation.begin_date_time',
        'rehabilitation.end_date_time',
        'rehabilitation_nurse.nurse_id',
        'employee.name',
        'consultation.consultation_id',
    ]
    wrapper.query(['rehabilitation', 'consultation', 'patient', 'rehabilitation_nurse', 'employee'], query_fields)
    # for join
    wrapper.where('rehabilitation.rehabilitation_id', '=', 'rehabilitation_nurse.rehabilitation_id', 'field')
    wrapper.where('rehabilitation_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('rehabilitation.consultation_id', '=', 'consultation.consultation_id', 'field')

    wrapper.where('rehabilitation.rehabilitation_id', '=', info['id'], 'str')
    wrapper.where('rehabilitation.rehabilitation_name', '=', info['name'], 'str')
    wrapper.where('patient.patient_id', '=', info['patient_id'], 'str')
    wrapper.where('patient.name', '=', info['patient_name'], 'str')

    wrapper.where('rehabilitation.begin_date_time', '>=', info['begin_time1'], 'str')
    wrapper.where('rehabilitation.begin_date_time', '<=', info['end_time1'], 'str')

    if info['is_history'] == 'true':
        wrapper.where('rehabilitation.end_date_time IS NOT NULL', '', '', 'null')
        wrapper.where('rehabilitation.end_date_time', '>=', info['begin_time2'], 'str')
        wrapper.where('rehabilitation.end_date_time', '<=', info['end_time2'], 'str')
    else:
        wrapper.where('rehabilitation.end_date_time IS NULL', '', '', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    return nurse_return(res)


def nurse_get_surgery_data(conn: MySQLConnection, info: dict):
    wrapper = SQLWrapper(conn)
    query_fields = [
        'surgery.surgery_id',
        'surgery.surgery_name',
        'patient.patient_id',
        'patient.name',
        'surgery.begin_date_time',
        'surgery.end_date_time',
        'surgery_nurse.nurse_id',
        'employee.name',
        'consultation.consultation_id',
    ]
    wrapper.query(['surgery', 'consultation', 'patient', 'surgery_nurse', 'employee'], query_fields)
    # for join
    wrapper.where('surgery.surgery_id', '=', 'surgery_nurse.surgery_id', 'field')
    wrapper.where('surgery_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('surgery.consultation_id', '=', 'consultation.consultation_id', 'field')

    wrapper.where('surgery.surgery_id', '=', info['id'], 'str')
    wrapper.where('surgery.surgery_name', '=', info['name'], 'str')
    wrapper.where('patient.patient_id', '=', info['patient_id'], 'str')
    wrapper.where('patient.name', '=', info['patient_name'], 'str')

    wrapper.where('surgery.begin_date_time', '>=', info['begin_time1'], 'str')
    wrapper.where('surgery.begin_date_time', '<=', info['end_time1'], 'str')

    if info['is_history'] == 'true':
        wrapper.where('surgery.end_date_time', 'IS', 'NOT NULL', 'null')
        wrapper.where('surgery.end_date_time', '>=', info['begin_time2'], 'str')
        wrapper.where('surgery.end_date_time', '<=', info['end_time2'], 'str')
    else:
        wrapper.where('surgery.end_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    return nurse_return(res)


def nurse_get_hospitalization_data(conn: MySQLConnection, info: dict):
    wrapper = SQLWrapper(conn)
    query_fields = [
        'hospitalization.hospitalization_id',
        'patient.patient_id',
        'patient.name',
        'hospitalization.hospitalization_date_time',
        'hospitalization.discharge_date_time',
        'nurse.nurse_id',
        'employee.name',
        'NULL',
    ]
    wrapper.query(['hospitalization', 'patient', 'nurse', 'employee'], query_fields)
    # for join
    wrapper.where('hospitalization.room_id', '=', 'nurse.room_id', 'field')
    wrapper.where('nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('hospitalization.patient_id', '=', 'patient.patient_id', 'field')

    wrapper.where('hospitalization.hospitalization_id', '=', info['id'], 'str')
    wrapper.where('patient.patient_id', '=', info['patient_id'], 'str')
    wrapper.where('patient.name', '=', info['patient_name'], 'str')

    wrapper.where('hospitalization.hospitalization_date_time', '>=', info['begin_time1'], 'str')
    wrapper.where('hospitalization.hospitalization_date_time', '<=', info['end_time1'], 'str')

    if info['is_history'] == 'true':
        wrapper.where('hospitalization.discharge_date_time', 'IS NOT', 'NULL', 'null')
        wrapper.where('hospitalization.discharge_date_time', '>=', info['begin_time2'], 'str')
        wrapper.where('hospitalization.discharge_date_time', '<=', info['end_time2'], 'str')
    else:
        wrapper.where('hospitalization.discharge_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    return nurse_return(res)
