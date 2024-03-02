# for api: /admin/add-or-edit
from mysql.connector import MySQLConnection
from SQLWrapper import SQLWrapper


def admin_put_medicine_data(conn: MySQLConnection, info: dict) -> int:
    name = info['name']
    manufacturer = info['manufacturer']
    cost = info['cost']
    if not name:
        return -1
    try:
        cost = int(cost)
    except:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('medicine', [(None, name, manufacturer, cost)])
    wrapper.commit()
    return code


def admin_put_examination_data(conn: MySQLConnection, info: dict) -> int:
    name = info['name']
    cost = info['cost']
    if not name:
        return -1
    try:
        cost = int(cost)
    except:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('examinations', [(None, name, cost)])
    wrapper.commit()
    return code


def admin_put_rehabilitation_data(conn: MySQLConnection, info: dict) -> int:
    name = info['name']
    cost = info['cost']
    if not name:
        return -1
    try:
        cost = int(cost)
    except:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('rehabilitations', [(None, name, cost)])
    wrapper.commit()
    return code

def admin_put_surgery_data(conn: MySQLConnection, info: dict) -> int:
    name = info['name']
    cost = info['cost']
    if not name:
        return -1
    try:
        cost = int(cost)
    except:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('surgeries', [(None, name, cost)])
    wrapper.commit()
    return code

def admin_put_department_data(conn: MySQLConnection, info: dict) -> int:
    name = info['name']
    if not name:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('departments', [(name,)])
    wrapper.commit()
    return code

def admin_put_room_data(conn: MySQLConnection, info: dict) -> int:
    _id = info['id']
    _type = info['type'] if info['type'] else None
    number = info['bed_number'] if info['bed_number'] else None
    additional = info['additional_facility'] if info['additional_facility'] else None

    if not _id:
        return -1
    try:
        number = int(number)
    except:
        return -1
    wrapper = SQLWrapper(conn)
    code = wrapper.insert('room', [(_id, _type, number, additional)])
    wrapper.commit()
    return code