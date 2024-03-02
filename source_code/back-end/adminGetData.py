# for api: /admin/get-table-data

from mysql.connector import MySQLConnection
from SQLWrapper import SQLWrapper
from pytz import timezone
from common import convert_time


def admin_get_patient_data(conn: MySQLConnection, info: dict) -> list:
    patient_name = info['name']
    patient_id = info['id']
    age_begin = info['age_begin']
    age_end = info['age_end']

    tz = timezone('Asia/Shanghai')
    time_begin = convert_time(info['time_begin']) if info['time_begin'] else ''
    time_end = convert_time(info['time_end']) if info['time_end'] else ''

    wrapper = SQLWrapper(conn)
    wrapper.query(['patient', 'user'], ['patient.name', 'patient_id', 'register_time'])

    wrapper.like('patient.name', f'%{patient_name}%', 'str')
    wrapper.where('patient_id', '=', 'user_id', 'field')
    wrapper.where('patient_id', '=', patient_id, 'str')
    wrapper.where('(YEAR(CURDATE()) - YEAR(birthdate))', '>=', age_begin, 'int')
    wrapper.where('(YEAR(CURDATE()) - YEAR(birthdate))', '<=', age_end, 'int')
    wrapper.where('register_time', '>=', time_begin, 'str')
    wrapper.where('register_time', '<=', time_end, 'str')
    wrapper.where('patient.valid', '=', '1', 'int')
    wrapper.run(join_method='')
    res = wrapper.get()

    ret = []
    tz = timezone('Asia/Shanghai')
    for p in res:
        ret.append({
            'patientName': p[0],
            'patientId': p[1],
            'registerTime': p[2].astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
        })
    return ret


def admin_get_employee_data(conn: MySQLConnection, info: dict, role: str) -> list:
    _name = info['name']
    _id = info['id']
    age_begin = info['age_begin']
    age_end = info['age_end']

    tz = timezone('Asia/Shanghai')
    time_begin = convert_time(info['time_begin']) if info['time_begin'] else ''
    time_end = convert_time(info['time_end']) if info['time_end'] else ''

    wrapper = SQLWrapper(conn)
    if role == 'doctor':
        wrapper.query([role, 'user', 'employee'], ['employee.name', f'{role}_id', 'department', 'register_time'])
        wrapper.where('department', '=', info['department'], 'str')
    else:
        wrapper.query([role, 'user', 'employee'], ['employee.name', f'{role}_id', 'room_id', 'register_time'])
        wrapper.where('room_id', '=', info['room_id'], 'str')

    wrapper.like('employee.name', f'%{_name}%', 'str')
    wrapper.where(f'{role}_id', '=', 'user_id', 'field')
    wrapper.where(f'{role}_id', '=', 'employee_id', 'field')
    wrapper.where('employee_id', '=', _id, 'str')
    wrapper.where('(YEAR(CURDATE()) - YEAR(birthdate))', '>=', age_begin, 'int')
    wrapper.where('(YEAR(CURDATE()) - YEAR(birthdate))', '<=', age_end, 'int')
    wrapper.where('register_time', '>=', time_begin, 'str')
    wrapper.where('register_time', '<=', time_end, 'str')
    wrapper.where('employee.valid', '=', '1', 'int')

    wrapper.run(join_method='')
    res = wrapper.get()

    ret = []
    tz = timezone('Asia/Shanghai')
    for p in res:
        if role == 'doctor':
            ret.append({
                'doctorName': p[0],
                'doctorId': p[1],
                'department': p[2],
                'registerTime': p[3].astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
            })
        else:
            if role == 'helping_staff':
                role = 'helpingStaff'
            ret.append({
                f'{role}Name': p[0],
                f'{role}Id': p[1],
                'roomId': p[2],
                'registerTime': p[3].astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
            })
    return ret


def admin_get_medicine_data(conn: MySQLConnection, info: dict):
    _name = info['name']
    _id = info['id']
    manufacturer = info['manufacturer']
    cost_begin = info['cost_begin']
    cost_end = info['cost_end']

    wrapper = SQLWrapper(conn)
    wrapper.query(['medicine'], ['name', 'medicine_id', 'manufacturer', 'cost'])
    wrapper.like('name', f'%{_name}%', 'str')
    wrapper.where('medicine_id', '=', _id, 'str')
    wrapper.where('manufacturer', '=', manufacturer, 'str')
    wrapper.where('cost', '>=', cost_begin, 'int')
    wrapper.where('cost', '<=', cost_end, 'int')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'medicineName': p[0],
            'medicineId': p[1],
            'manufacturer': p[2],
            'cost': p[3],
        })
    return ret


def admin_get_examination_data(conn: MySQLConnection, info: dict):
    _name = info['name']
    _id = info['id']
    cost_begin = info['cost_begin']
    cost_end = info['cost_end']

    wrapper = SQLWrapper(conn)
    wrapper.query(['examinations'], ['name', 'examination_id', 'cost'])
    wrapper.like('name', f'%{_name}%', 'str')
    wrapper.where('examination_id', '=', _id, 'str')
    wrapper.where('cost', '>=', cost_begin, 'int')
    wrapper.where('cost', '<=', cost_end, 'int')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'examinationName': p[0],
            'examinationId': p[1],
            'cost': p[2],
        })
    return ret


def admin_get_rehabilitation_data(conn: MySQLConnection, info: dict):
    _name = info['name']
    _id = info['id']
    cost_begin = info['cost_begin']
    cost_end = info['cost_end']

    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitations'], ['name', 'rehabilitation_id', 'cost'])
    wrapper.like('name', f'%{_name}%', 'str')
    wrapper.where('rehabilitation_id', '=', _id, 'str')
    wrapper.where('cost', '>=', cost_begin, 'int')
    wrapper.where('cost', '<=', cost_end, 'int')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'rehabilitationName': p[0],
            'rehabilitationId': p[1],
            'cost': p[2],
        })
    return ret


def admin_get_surgery_data(conn: MySQLConnection, info: dict):
    _name = info['name']
    _id = info['id']
    cost_begin = info['cost_begin']
    cost_end = info['cost_end']

    wrapper = SQLWrapper(conn)
    wrapper.query(['surgeries'], ['name', 'surgery_id', 'cost'])
    wrapper.like('name', f'%{_name}%', 'str')
    wrapper.where('surgery_id', '=', _id, 'str')
    wrapper.where('cost', '>=', cost_begin, 'int')
    wrapper.where('cost', '<=', cost_end, 'int')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'surgeryName': p[0],
            'surgeryId': p[1],
            'cost': p[2],
        })
    return ret


def admin_get_department_data(conn: MySQLConnection, info: dict):
    _name = info['name']

    wrapper = SQLWrapper(conn)
    wrapper.query(['departments'], ['name'])
    wrapper.like('name', f'%{_name}%', 'str')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'departmentName': p[0],
        })
    return ret


def admin_get_room_data(conn: MySQLConnection, info: dict):
    _id = info['id']
    _type = info['type']
    number_begin = info['bed_number_begin']
    number_end = info['bed_number_end']
    additional = info['additional_facility']

    wrapper = SQLWrapper(conn)
    wrapper.query(['room'], ['room_id', 'room_type', 'number_of_beds', 'additional_facility'])
    wrapper.like('room_id', f'%{_id}%', 'str')
    wrapper.like('type', f'%{_type}%', 'str')
    wrapper.where('bed_number', '>=', number_begin, 'int')
    wrapper.where('bed_number', '<=', number_end, 'int')
    wrapper.like('additional_facility', f'%{additional}%', 'str')

    wrapper.run()
    res = wrapper.get()

    ret = []
    for p in res:
        ret.append({
            'roomId': p[0],
            'roomType': p[1],
            'bedNumber': p[2],
            'additionalFacility': p[3],
        })
    return ret



