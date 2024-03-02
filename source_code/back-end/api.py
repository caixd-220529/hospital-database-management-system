import random
import test.fields as fields
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from datetime import datetime, timezone
from dateutil.parser import *
from pytz import timezone
from hashlib import sha256
import mysql.connector

from SQLWrapper import SQLWrapper
from checker import *
from common import patient_fields, doctor_fields, nurse_fields, staff_fields, Register, employee_fields
from common import get_doctor_name, get_patient_name, convert_time
from CreateTable import createTable
from adminTableColumn import *
from adminForm import *
from adminGetData import *
from adminPutData import *
from nurseGetData import *

app = Flask(__name__)
CORS().init_app(app)  # allow CORS, so that the frontend can access the backend from a different domain

conn = mysql.connector.connect(host='localhost', user='dbcourse', password='DBcourse2023', database='hospital')


@app.route('/register-form-submit', methods=['POST'])
def register_form_submit():
    form = dict(request.json)
    _id = ''
    err = None
    if form['formName'] == 'patient':
        _id, err = Register.register_patient(form, conn)
    elif form['formName'] == 'doctor':
        _id, err = Register.register_doctor(form, conn)
    elif form['formName'] == 'nurse':
        _id, err = Register.register_nurse(form, conn)
    elif form['formName'] == 'helpingStaff':
        _id, err = Register.register_staff(form, conn)

    if not _id:
        response = {
            'message': 'failed',
            'results': {
                'notice': 'The form is not filled correctly.',
                'invalidFormField': err,
            }
        }
        return response, 400

    response = {
        'message': 'success',
        'results': {
            'userId': _id,
        }
    }
    return response, 200


@app.route('/employee-supervisor-id-validate', methods=['GET'])
def validate_supervisor_id():
    form_name = request.args.get('formName')
    if form_name == 'helpingStaff':
        form_name = 'helping_staff'
    supervisor_id = request.args.get('supervisorId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'], ['supervisor_id'])
    wrapper.where('employee_id', '=', supervisor_id, 'str')
    wrapper.run()
    res = wrapper.get()
    if res and not res[0][0] == supervisor_id:
        return {'message': ''}, 200
    return {'message': 'The supervisor ID is invalid.'}, 200


@app.route('/login', methods=['POST'])
def login():
    form = dict(request.json)
    _id = form['userId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['user'], ['password', 'role', 'valid'])
    wrapper.where('user_id', '=', _id, 'str')
    wrapper.run(limit=1)
    result = wrapper.get()
    if not result:
        return {'message': 'failed', 'results': 'User does not exist!'}, 400
    result = result[0]
    psw, role, valid = result
    if not valid:
        return {'message': 'failed', 'results': 'Your account has not been confirmed.'}, 400
    wrapper.clear()
    if role == 'patient':
        wrapper.query(['patient'], ['name'])
        wrapper.where('patient_id', '=', _id, 'str')
        wrapper.run(limit=1)
        name = wrapper.get()[0][0]
    elif role in ['doctor', 'nurse', 'helping_staff']:
        wrapper.query(['employee'], ['name'])
        wrapper.where('employee_id', '=', _id, 'str')
        wrapper.run(limit=1)
        name = wrapper.get()[0][0]
        if role == 'helping_staff':
            role = 'helpingStaff'   # 前端需要传入的字符串
    else:
        name = 'admin'

    _psw = form['password']
    _psw = sha256(_psw.encode('utf-8')).hexdigest()
    if psw == _psw:
        return {'message': 'success', 'results': {'userType': role, 'userName': name}}, 200
    else:
        return {'message': 'failed', 'results': 'The username or password is incorrect.'}, 400


@app.route('/get-patient-info', methods=['GET'])
def get_patient_info():
    pID = request.args.get('patientId')
    wrapper = SQLWrapper(conn)

    wrapper.query(['patient'], [])
    wrapper.where('patient_id', '=', pID, 'str')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    res = wrapper.get()[0]
    ret = {}
    if res:
        for idx, field in enumerate(patient_fields.keys()):
            ret[field] = str(res[idx]) if res[idx] is not None else ''
        ret['allergens'] = ret['allergens'].split(',')[:-1]
        ret = {'message': 'success', 'results': ret}
        return ret, 200
    else:
        ret = {'message': 'failed', 'results': 'The patient ID is invalid.'}
        return ret, 400


@app.route('/edit-patient-info', methods=['POST'])
def edit_patient_info():
    # pre-processing
    info = dict(request.json)
    info['allergens'] = ','.join(info['allergens']) + ','
    for k in list(info.keys()):
        if not info[k]:
            info[k] = None
        info[patient_fields[k]] = info.pop(k)

    err = check_patient_info(info)
    if err:
        response = {
            'message': 'failed',
            'results': {
                'notice': f'The {err} form is not filled correctly.',
                'invalidFormField': [err],
            }
        }
        return response, 400

    wrapper = SQLWrapper(conn)
    primary = {'patient_id': info['patient_id']}
    info.pop('patient_id')
    code = wrapper.update('patient', primary, info)
    if code != 0:
        response = {
            'message': 'failed',
            'results': {
                'notice': 'Database Error!',
                'invalidFormField': ['database'],
            }
        }
        return response, 400

    return {'message': 'success'}, 200


@app.route('/edit-password', methods=['POST'])
def edit_password():
    info = dict(request.json)
    old_psw = info['oldPassword']
    uid = info['userId']

    wrapper = SQLWrapper(conn)
    wrapper.query(['user'], ['password'])
    wrapper.where('user_id', '=', uid, 'str')
    wrapper.run(limit=1)
    psw_digest = wrapper.get()[0][0]
    if sha256(old_psw.encode('utf-8')).hexdigest() == psw_digest:
        new_psw = info['newPassword']
        wrapper.update('user', {'user_id': uid}, {'password': sha256(new_psw.encode('utf-8')).hexdigest()})
        return {'message': 'success'}, 200
    else:
        return {
            'message': 'failed',
            'results': 'Password not match!',
        }, 400


@app.route('/get-patient-consultation', methods=['GET'])
def get_patient_consultation():
    cid = request.args.get('consultationId')
    pid = request.args.get('patientId')
    doclst = request.args.getlist('doctorName[]')
    deplst = request.args.getlist('department[]')

    st, et, now = None, None, None
    try:
        st = parse(request.args.get('startTime')).timestamp()
        et = parse(request.args.get('endTime')).timestamp()
        now = datetime.now().timestamp()
    except Exception as e:
        pass

    wrapper = SQLWrapper(conn)
    wrapper.query(['consultation', 'doctor', 'employee'],
                  ['consultation.date_time', 'department', 'employee.name', 'consultation_id'])
    wrapper.where('patient_id', '=', pid, 'str')
    wrapper.where('consultation_id', '=', cid, 'int')
    wrapper.where('consultation.doctor_id', '=', 'doctor.doctor_id', 'field')
    wrapper.where('doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('datetime', '>=', st, 'str')
    wrapper.where('datetime', '<=', et, 'str')
    wrapper.where('datetime', '<=', now, 'str')

    wrapper.run(join_method='')
    res = wrapper.get()

    lst = []
    for t in res:
        tz = timezone('Asia/Shanghai')
        flag = True
        if deplst:
            flag = t[1] in deplst
        if doclst:
            flag = t[2] in doclst
        if flag:
            lst.append({
                'time': t[0].astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
                'department': t[1],
                'doctorName': t[2],
                'consultationId': t[3],
            })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/get-patient-consultation/doctorName', methods=['GET'])
def get_patient_consultation_doctor_name():
    doctor_name = request.args.get('doctorName').lower()

    wrapper = SQLWrapper(conn)
    wrapper.query(['doctor', 'employee'], ['DISTINCT name'])
    wrapper.where('doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.like('LOWER(name)', f'%{doctor_name}%', 'str')

    wrapper.run(join_method='')
    res = wrapper.get()

    result = {'message': 'success', 'results': []}
    for t in res:
        result['results'].append(t[0])

    return result, 200


@app.route('/get-patient-consultation/department', methods=['GET'])
def get_patient_consultation_department():
    department = request.args.get('department').lower()

    wrapper = SQLWrapper(conn)
    wrapper.query(['doctor'], ['DISTINCT department'])
    wrapper.like('LOWER(department)', f'%{department}%', 'str')
    wrapper.run()
    res = wrapper.get()

    result = {'message': 'success', 'results': []}
    for t in res:
        result['results'].append(t[0])

    return result, 200


long_sentence = 'In the beginning God created the heavens and the earth. Now the earth was formless and empty, ' \
                'darkness was over the surface of the deep, and the Spirit of God was hovering over the waters. ' \
                'And God said, "Let there be light," and there was light. God saw that the light was good, ' \
                'and he separated the light from the darkness. God called the light "day," and the darkness he ' \
                'called "night." And there was evening, and there was morning—the first day.'


@app.route('/get-consultation-detailed', methods=['GET'])
def get_consultation_detailed():
    cID = request.args.get('consultationId')
    wrapper = SQLWrapper(conn)

    wrapper.query(['consultation', 'patient',  'employee'],
                  ['consultation_id', 'patient.patient_id', 'patient.name', 'date_time',
                   'self_report', 'medical_history', 'medication_history', 'medical_advice',
                   'charge_id', 'doctor_id', 'employee.name'])
    wrapper.where('consultation_id', '=', cID, 'int')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    code = wrapper.run(limit=1, join_method='')

    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    query = f'''SELECT consultation_id, consultation.patient_id, patient.name, date_time, self_report, medical_history,
                medication_history, medical_advice, charge_id, consultation.doctor_id, employee.name
                FROM consultation JOIN patient ON consultation.patient_id = patient.patient_id
                JOIN doctor ON consultation.doctor_id = doctor.doctor_id
                JOIN employee ON doctor.doctor_id = employee.employee_id
                WHERE consultation_id = {cID} LIMIT 1;'''
    wrapper.execute_raw(query)
    res = wrapper.get()[0]
    ret = {}
    if res:
        for idx, field in enumerate(consultation_fields.keys()):
            ret[field] = str(res[idx]) if res[idx] is not None else ''
        ret['doctorRough'] = {'doctorID': res[9], 'doctorName': res[10]} if res[9] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The consultation ID is invalid'}
        return ret, 400
    wrapper.clear()
    query = f"""
            SELECT 'prescription' AS itemType, prescription_id AS itemId, NULL AS itemName
            FROM prescription
            WHERE consultation_id = {cID}
            UNION
            SELECT 'examination' AS itemType, examination_id AS itemId, examination_name AS itemName
            FROM examination
            WHERE consultation_id = {cID}
            UNION
            SELECT 'rehabilitation' AS itemType, rehabilitation_id AS itemId, rehabilitation_name AS itemName
            FROM rehabilitation
            WHERE consultation_id = {cID}
            UNION
            SELECT 'surgery' AS itemType, surgery_id AS itemId, surgery_name AS itemName
            FROM surgery
            WHERE consultation_id = {cID}
            UNION
            SELECT 'hospitalization' AS itemType, hospitalization_id AS itemId, employee.name AS itemName
            FROM hospitalization NATURAL JOIN employee NATURAL JOIN consultation
            WHERE consultation_id = {cID} and doctor_id = employee_id;
        """
    wrapper.execute_raw(query)
    res = wrapper.get()

    ret['prescriptionRoughArr'] = [{'prescriptionId': result[1]} for result in res if result[0] == 'prescription']
    ret['examinationRoughArr'] = [{'examinationId': result[1], 'examinationName': result[2]} for result in res if
                                  result[0] == 'examination']
    ret['rehabilitationRoughArr'] = [{'rehabilitationId': result[1], 'rehabilitationName': result[2]} for result in res
                                     if result[0] == 'rehabilitation']
    ret['surgeryRoughARR'] = [{'surgeryId': result[1], 'surgeryName': result[2]} for result in res if
                              result[0] == 'surgery']
    ret['hospitalizationRoughArr'] = [{'hospitalizationId': result[1], 'doctorName': result[2]} for result in res if
                                      result[0] == 'hospitalization']
    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/get-rehabilitation-detailed', methods=['GET'])
def get_rehabilitation_detailed():
    rID = request.args.get('rehabilitationId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitation'], [])
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        ret['rehabilitationId'] = str(rID)
        ret['rehabilitationName'] = res[2]
        ret['beginTime'] = convert_time(res[3])
        ret['endTime'] = convert_time(res[4])
        ret['chargeId'] = res[5] if res[5] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The consultation ID is invalid'}
        return ret, 400
    wrapper.clear()
    wrapper.query(['consultation', 'employee', 'patient'], ['employee.name', 'patient.patient_id', 'patient.name'])
    wrapper.where('consultation_id', '=', res[1], 'int')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('employee.valid', '=', 1, 'int')
    wrapper.where('patient.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['consultationRough'] = {'consultationId': str(res[1]), 'doctorName': result[0][0]}
        ret['patientRough'] = {'patientId': str(result[0][1]), 'patientName': result[0][2]}
    else:
        ret['consultationRough'] = {'consultationId': str(res[1]), 'doctorName': ''}
        ret['patientRough'] = {'patientId':'', 'patientName': ''}

    wrapper.clear()
    wrapper.query(['rehabilitation_doctor', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('rehabilitation_doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['doctorRoughArr'] = [{'doctorId': str(inf[0]), 'doctorName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['rehabilitation_nurse', 'employee'], ['rehabilitation_id', 'employee.name'])
    wrapper.where('rehabilitation_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['nurseRoughArr'] = [{'nurseId': str(inf[0]), 'nurseName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['rehabilitation_helping_staff', 'employee'], ['helping_staff_id', 'employee.name'])
    wrapper.where('rehabilitation_helping_staff.helping_staff_id', '=', 'employee.employee_id', 'field')
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['helpingStaffRoughArr'] = [{'helpingStaffId': str(inf[0]), 'helpingStaffName': inf[1]} for inf in infs]
    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/get-examination-detailed', methods=['GET'])
def get_examination_detailed():
    eID = request.args.get('examinationId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['examination'], [])
    wrapper.where('examination_id', '=', eID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        ret['examinationId'] = eID
        ret['timeOfExamination'] = convert_time(res[2])
        ret['timeOfResult'] = convert_time(res[3])
        ret['examinationName'] = res[4]
        ret['result'] = res[5]
        ret['chargeId'] = res[6] if res[6] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The examination ID is invalid'}
        return ret, 400
    wrapper.clear()
    wrapper.query(['consultation', 'employee', 'patient'], ['employee.name', 'patient.patient_id', 'patient.name'])
    wrapper.where('consultation_id', '=', res[1], 'int')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('employee.valid', '=', 1, 'int')
    wrapper.where('patient.valid', '=', 1, 'int')
    code = wrapper.run(limit=1, join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()[0]

    ret['consultationRough'] = {'consultationId': str(res[1]), 'doctorName': result[0]}
    ret['patientRough'] = {'patientId': str(result[1]), 'patientName': result[2]}
    wrapper.clear()
    wrapper.query(['examination_doctor', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('examination_doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('examination_id', '=', eID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['doctorRoughArr'] = [{'doctorId': str(inf[0]), 'doctorName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['examination_nurse', 'employee'], ['nurse_id', 'employee.name'])
    wrapper.where('examination_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('examination_id', '=', eID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['nurseRoughArr'] = [{'nurseId': str(inf[0]), 'nurseName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['examination_helping_staff', 'employee'], ['helping_staff_id', 'employee.name'])
    wrapper.where('examination_helping_staff.helping_staff_id', '=', 'employee.employee_id', 'field')
    wrapper.where('examination_id', '=', eID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['helpingStaffRoughArr'] = [{'helpingStaffId': str(inf[0]), 'helpingStaffName': inf[1]} for inf in infs]
    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/get-prescription-detailed', methods=['GET'])
def get_prescription_detailed():
    pID = request.args.get('prescriptionId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription'], [])
    wrapper.where('prescription_id', '=', pID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        ret['prescriptionId'] = pID
        ret['pharmacyWindow'] = res[3]
        ret['pharmacyPickupTime'] = convert_time(res[4])
        ret['chargeId'] = res[5] if res[5] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The examination ID is invalid'}
        return ret, 400
    wrapper.clear()
    wrapper.query(['consultation', 'employee', 'patient'], ['employee.name', 'patient.patient_id', 'patient.name'])
    wrapper.where('consultation_id', '=', res[1], 'int')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('employee.valid', '=', 1, 'int')
    wrapper.where('patient.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()[0]
    ret['consultationRough'] = {'consultationId': str(res[1]), 'doctorName': result[0]}
    ret['patientRough'] = {'patientId': str(result[1]), 'patientName': result[2]}

    wrapper.clear()
    wrapper.query(['prescription', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('prescription.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('prescription_id', '=', pID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    inf = wrapper.get()[0]
    ret['doctorRough'] = {'doctorId': str(inf[0]), 'doctorName': inf[1]}

    wrapper.clear()
    wrapper.query(['prescription_medicine', 'medicine'], ['medicine.medicine_id', 'name', 'quantity'])

    wrapper.where('prescription_id', '=', pID, 'int')
    wrapper.where('prescription_medicine.medicine_id', '=', 'medicine.medicine_id', 'field')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['prescriptionMedicineRoughArr'] = [{'medicineId': str(inf[0]), 'medicineName': inf[1],
                                            'quantity': inf[2]} for inf in infs]

    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/get-surgery-detailed', methods=['GET'])
def get_surgery_detailed():
    sID = request.args.get('surgeryId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery'], [])
    wrapper.where('surgery_id', '=', sID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        ret['surgeryId'] = str(sID)
        ret['surgeryName'] = res[4]
        ret['surgeryDescription'] = res[5]
        ret['surgerySite'] = res[6]
        ret['surgeryType'] = res[7]
        ret['beginTime'] = convert_time(res[8])
        ret['endTime'] = convert_time(res[9])
        ret['chargeId'] = res[10] if res[10] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The consultation ID is invalid'}
        return ret, 400
    wrapper.clear()
    wrapper.query(['consultation', 'employee', 'patient'], ['employee.name', 'patient.patient_id', 'patient.name'])
    wrapper.where('consultation_id', '=', res[1], 'int')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('consultation.patient_id', '=', 'patient.patient_id', 'field')
    wrapper.where('employee.valid', '=', 1, 'int')
    wrapper.where('patient.valid', '=', 1, 'int')
    code = wrapper.run(limit=1,join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()[0]
    ret['consultationRough'] = {'consultationId': str(res[1]), 'doctorName': result[0]}
    ret['patientRough'] = {'patientId': str(result[1]), 'patientName': result[2]}

    if res[3] != '':
        wrapper.clear()
        wrapper.query(['employee'], ['name'])
        wrapper.where('employee_id', '=', res[3], 'str')
        wrapper.where('employee.valid', '=', 1, 'int')
        code = wrapper.run(limit=1)
        if code != 0:
            ret = {'message': f'database error {code}', 'results': {}}
            return ret, 400
        result = wrapper.get()[0]
        ret['doctorRough'] = {'doctorId': str(res[3]), 'doctorName': str(result[0])}
    else:
        ret['doctorRough'] = {}
    wrapper.clear()
    wrapper.query(['surgery_doctor', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('surgery_doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('surgery_id', '=', sID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['doctorRoughArr'] = [{'doctorId': str(inf[0]), 'doctorName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['surgery_nurse', 'employee'], ['surgery_id', 'employee.name'])
    wrapper.where('surgery_nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('surgery_id', '=', sID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['nurseRoughArr'] = [{'nurseId': str(inf[0]), 'nurseName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['surgery_helping_staff', 'employee'], ['helping_staff_id', 'employee.name'])
    wrapper.where('surgery_helping_staff.helping_staff_id', '=', 'employee.employee_id', 'field')
    wrapper.where('surgery_id', '=', sID, 'int')
    wrapper.where('employee.valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['helpingStaffRoughArr'] = [{'helpingStaffId': str(inf[0]), 'helpingStaffName': inf[1]} for inf in infs]

    wrapper.clear()
    wrapper.query(['surgery_related_record'], ['record_id', 'record_date_time'])
    wrapper.where('surgery_id', '=', sID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    infs = wrapper.get()
    ret['recordRoughArr'] = [{'recordId': str(inf[0]), 'recordTime':convert_time(inf[1])} for inf in infs]
    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/patient/cancel-consultation', methods=['POST'])
def cancel_consultation():
    info = dict(request.json)
    cID = info['consultationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['consultation'], ['charge_id', 'doctor_id', 'date_time'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    dID = wrapper.get()[0][1]
    date_time = wrapper.get()[0][2]
    update = f'''UPDATE appointment SET available_slots = available_slots + 1 WHERE
                doctor_id  = '{dID}' AND datetime = '{date_time}' '''
    wrapper.execute_raw(update, False)
    delete = f'''DELETE FROM consultation WHERE consultation_id = {cID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-prescription-medicine-detailed', methods=['GET'])
def get_prescription_medicine_detailed():
    pID = request.args.get('prescriptionId')
    mID = request.args.get('medicineId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription_medicine'], [])
    wrapper.where('prescription_id', '=', pID, 'int')
    wrapper.where('medicine_id', '=', mID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        for idx, field in enumerate(prescription_medicine_fields.keys()):
            ret[field] = str(res[idx]) if res[idx] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The prescription ID or medicine ID is invalid'}
        return ret, 400

    wrapper.clear()
    wrapper.query(['medicine'], ['name', 'manufacturer'])
    wrapper.where('medicine_id', '=', mID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    if res:
        ret['medicineName'] = str(res[0]) if res[0] is not None else ''
        ret['medicineManufacturer'] = str(res[1]) if res[1] is not None else ''
        ret = {'message': 'success', 'results': ret}
        return ret, 200
    else:
        ret = {'message': 'failed', 'results': 'The medicine ID is invalid'}
        return ret, 400


@app.route('/get-surgery-record-detailed', methods=['GET'])
def get_surgery_record_detailed():
    sID = request.args.get('surgeryId')
    rID = request.args.get('recordId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery_related_record'], ['record_date_time', 'record_detail'])
    wrapper.where('surgery_id', '=', sID, 'int')
    wrapper.where('record_id', '=', rID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()[0]
    date_time = convert_time(result[0])
    detail = result[1]
    date_part = date_time.strftime('%Y-%m-%d')
    time_part = date_time.strftime('%H:%M:%S')
    return {
        'message': 'success',
        'results': {
            'surgeryId': request.args.get('surgeryId'),
            'recordId': request.args.get('recordId'),
            'recordDate': date_part,
            'recordTime': time_part,
            'recordDetail': detail,
        }
    }


@app.route('/get-charge-detailed', methods=['GET'])
def get_charge_detailed():
    charge_id = request.args.get('chargeId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['charge', 'patient'], ['patient_id', 'cost', 'is_completed', 'charge_date_time',
                                          'payment_method', 'name'])
    wrapper.where('charge_id', '=', charge_id, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    ret['chargeId'] = charge_id
    ret['cost'] = res[1]
    ret['isCompleted'] = 'true' if res[2] == 'YES' else 'false'
    ret['chargeTime'] = convert_time(res[3])
    ret['paymentMethod'] = res[4]
    ret['patientRough'] = {'patientId': str(res[0]), 'patientName': str(res[5])}

    wrapper.clear()
    wrapper.query(['consultation', 'employee'], ['consultation_id', 'employee.name'])
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('charge_id', '=', charge_id, 'int')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['consultationRough'] = {'consultationId': result[0][0], 'doctorName': result[0][1]}
    else:
        ret['consultationRough'] = {'consultationId': '', 'doctorName': ''}

    wrapper.clear()
    wrapper.query(['prescription'], ['prescription_id'])
    wrapper.where('charge_id', '=', charge_id, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['prescriptionRough'] = {'prescriptionId': result[0][0]}
    else:
        ret['prescriptionRough'] = {'prescriptionId': ''}

    wrapper.clear()
    wrapper.query(['examination'], ['examination_id', 'examination_name'])
    wrapper.where('charge_id', '=', charge_id, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['examinationRough'] = {'examinationId': result[0][0], 'examinationName': result[0][1]}
    else:
        ret['examinationRough'] = {'examinationId': '', 'examinationName': ''}

    wrapper.clear()
    wrapper.query(['rehabilitation'], ['rehabilitation_id', 'rehabilitation_name'])
    wrapper.where('charge_id', '=', charge_id, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['rehabilitationRough'] = {'rehabilitationId': result[0][0], 'rehabilitationName': result[0][1]}
    else:
        ret['rehabilitationRough'] = {'rehabilitationId': '', 'rehabilitationName': ''}

    wrapper.clear()
    wrapper.query(['surgery'], ['surgery_id', 'surgery_name'])
    wrapper.where('charge_id', '=', charge_id, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['surgeryRough'] = {'surgeryId': result[0][0], 'surgeryName': result[0][1]}
    else:
        ret['surgeryRough'] = {'surgeryId': '', 'surgeryName': ''}

    wrapper.clear()
    wrapper.query(['hospitalization', 'employee'], ['hospitalization_id', 'employee.name'])
    wrapper.where('hospitalization.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('charge_id', '=', charge_id, 'int')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    if result:
        ret['hospitalizationRough'] = {'hospitalizationId': result[0][0], 'doctorName': result[0][1]}
    else:
        ret['hospitalizationRough'] = {'hospitalizationId': '', 'doctorName': ''}

    ret = {'message': 'success', 'results': ret}
    return ret, 200
    is_completed = 'true' if random.random() > 0.5 else 'false'


@app.route('/get-hospitalization-detailed', methods=['GET'])
def get_hospitalization_detailed():
    hID = request.args.get('hospitalizationId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization'], [])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    ret = {}
    if res:
        ret['hospitalizationId'] = str(hID)
        ret['hospitalizationTime'] = convert_time(res[3])
        ret['hospitalizationReason'] = res[4]
        ret['dischargeTime'] = convert_time(res[5])
        ret['dischargeReason'] = res[6]
        ret['roomId'] = res[7]
        ret['bedNumber'] = res[8] if res[8] is not None else ''
        ret['chargeId'] = res[9] if res[9] is not None else ''
    else:
        ret = {'message': 'failed', 'results': 'The consultation ID is invalid'}
        return ret, 400
    wrapper.clear()
    wrapper.query(['employee', 'consultation', 'hospitalization_record'],
                  ['employee.name', 'hospitalization_record.consultation_id'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    wrapper.where('consultation.consultation_id', '=', 'hospitalization_record.consultation_id', 'field')
    wrapper.where('consultation.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    ret['consultationRoughArr'] = [{'consultationId': str(result[1]), 'doctorName': result[0]} for result in results]

    wrapper.clear()
    wrapper.query(['patient'], ['name'])
    wrapper.where('patient_id', '=', res[1], 'str')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()[0]
    ret['patientRough'] = {'patientId': str(res[0]), 'patientName': result[0]}

    wrapper.clear()
    wrapper.query(['hospitalization', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('hospitalization.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('hospitalization_id', '=', hID, 'int')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = wrapper.get()
    ret['doctorRough'] = {'doctorId': str(result[0][0]), 'doctorName': result[0][1]}

    ret = {'message': 'success', 'results': ret}
    return ret, 200


@app.route('/get-patient-prescription', methods=['GET'])
def get_patient_prescription():
    wrapper = SQLWrapper(conn)
    query_fields = [
        'prescription_id',
        'prescription.consultation_id',
        'pharmacy_window',
        'pharmacy_pickup_date_time',
    ]
    wrapper.query(['prescription', 'consultation'], query_fields)
    wrapper.where('prescription.consultation_id', '=', 'consultation.consultation_id', 'field')
    wrapper.where('patient_id', '=', request.args.get('patientId'), 'str')
    wrapper.where('prescription_id', '=', request.args.get('prescriptionId'), 'int')
    wrapper.where('consultation_id', '=', request.args.get('consultationId'), 'int')
    wrapper.where('pharmacy_window', '=', request.args.get('pharmacyWindow'), 'str')

    if request.args.get('isHistory') == 'true':
        wrapper.where('pharmacy_pickup_date_time', 'IS NOT', 'NULL', 'null')
        wrapper.where('pharmacy_pickup_date_time', '>=', request.args.get('beginTime'), 'str')
        wrapper.where('pharmacy_pickup_date_time', '<=', request.args.get('endTime'), 'str')
    else:
        wrapper.where('pharmacy_pickup_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    ret = []
    for t in res:
        ret.append({
            'prescriptionId': t[0],
            'consultationId': t[1],
            'pharmacyWindow': t[2],
            'pharmacyPickupTime': convert_time(t[3]),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/patient/refuse-prescription', methods=['POST'])
def refuse_prescription():
    info = dict(request.json)
    pID = info['prescriptionId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription'], ['charge_id'])
    wrapper.where('prescription_id', '=', pID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM prescription_medicine WHERE prescription_id = {pID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM prescription WHERE prescription_id = {pID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-patient-examination', methods=['GET'])
def get_patient_examination():
    wrapper = SQLWrapper(conn)
    query_fields = [
        'examination_id',
        'examination.consultation_id',
        'examination_name',
        'examination_date_time',
        'time_of_result',
    ]
    wrapper.query(['examination', 'consultation'], query_fields)
    wrapper.where('examination.consultation_id', '=', 'consultation.consultation_id', 'field')

    wrapper.where('examination_id', '=', request.args.get('examinationId'), 'int')
    wrapper.where('patient_id', '=', request.args.get('patientId'), 'str')
    wrapper.where('examination_name', '=', request.args.get('examinationName'), 'str')
    wrapper.where('consultation_id', '=', request.args.get('consultationId'), 'int')
    wrapper.where('examination_date_time', '>=', request.args.get('beginExaminationTime'), 'str')
    wrapper.where('examination_date_time', '<=', request.args.get('endExaminationTime'), 'str')

    if request.args.get('isHistory') == 'true':
        wrapper.where('time_of_result', 'IS NOT', 'NULL', 'null')
        wrapper.where('time_of_result', '>=', request.args.get('beginResultTime'), 'str')
        wrapper.where('time_of_result', '<=', request.args.get('endResultTime'), 'str')
    else:
        wrapper.where('time_of_result', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    ret = []
    for t in res:
        ret.append({
            'examinationId': t[0],
            'consultationId': t[1],
            'examinationName': t[2],
            'examinationTime': convert_time(t[3]),
            'resultTime': convert_time(t[4]),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/patient/cancel-examination', methods=['POST'])
def cancel_examination():
    info = dict(request.json)
    eID = info['examinationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['examination'], ['charge_id'])
    wrapper.where('examination_id', '=', eID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM examination WHERE examination_id = {eID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-patient-rehabilitation', methods=['GET'])
def get_patient_rehabilitation():
    wrapper = SQLWrapper(conn)
    query_fields = [
        'rehabilitation_id',
        'rehabilitation.consultation_id',
        'rehabilitation_name',
        'begin_date_time',
        'end_date_time',
    ]
    wrapper.query(['rehabilitation', 'consultation'], query_fields)
    wrapper.where('rehabilitation.consultation_id', '=', 'consultation.consultation_id', 'field')

    wrapper.where('rehabilitation_id', '=', request.args.get('rehabilitationId'), 'int')
    wrapper.where('patient_id', '=', request.args.get('patientId'), 'str')
    wrapper.where('rehabilitation_name', '=', request.args.get('rehabilitationName'), 'str')
    wrapper.where('consultation_id', '=', request.args.get('consultationId'), 'int')
    wrapper.where('begin_date_time', '>=', request.args.get('beginTime1'), 'str')
    wrapper.where('begin_date_time', '<=', request.args.get('endTime1'), 'str')

    if request.args.get('isHistory') == 'true':
        wrapper.where('end_date_time', 'IS NOT', 'NULL', 'null')
        wrapper.where('end_date_time', '>=', request.args.get('beginTime2'), 'str')
        wrapper.where('end_date_time', '<=', request.args.get('endTime2'), 'str')
    else:
        wrapper.where('end_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    ret = []

    for t in res:
        ret.append({
            'rehabilitationId': t[0],
            'consultationId': t[1],
            'rehabilitationName': t[2],
            'beginTime': convert_time(t[3]),
            'endTime': convert_time(t[4]),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/patient/cancel-rehabilitation', methods=['POST'])
def cancel_rehabilitation():
    info = dict(request.json)
    rID = info['rehabilitationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitation'], ['charge_id'])
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM rehabilitation WHERE rehabilitation_id = {rID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-patient-surgery', methods=['GET'])
def get_patient_surgery():
    wrapper = SQLWrapper(conn)
    query_fields = [
        'surgery_id',
        'consultation_id',
        'employee.name',
        'surgery_name',
        'begin_date_time',
        'end_date_time',
    ]
    wrapper.query(['surgery', 'employee', 'doctor'], query_fields)
    # for join
    wrapper.where('surgery.lead_surgeon_id', '=', 'employee.employee_id', 'field')
    wrapper.where('surgery.lead_surgeon_id', '=', 'doctor.doctor_id', 'field')

    wrapper.where('surgery_id', '=', request.args.get('surgeryId'), 'int')
    wrapper.where('patient_id', '=', request.args.get('patientId'), 'str')
    wrapper.where('surgery_name', '=', request.args.get('surgeryName'), 'str')
    wrapper.where('employee.name', '=', request.args.get('doctorName'), 'str')

    wrapper.where('begin_date_time', '>=', request.args.get('beginTime1'), 'str')
    wrapper.where('begin_date_time', '<=', request.args.get('endTime1'), 'str')

    if request.args.get('isHistory') == 'true':
        wrapper.where('end_date_time', 'IS NOT', 'NULL', 'null')
        wrapper.where('end_date_time', '>=', request.args.get('beginTime2'), 'str')
        wrapper.where('end_date_time', '<=', request.args.get('endTime2'), 'str')
    else:
        wrapper.where('end_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    ret = []
    for t in res:
        ret.append({
            'surgeryId': t[0],
            'consultationId': t[1],
            'doctorName': t[2],
            'surgeryName': t[3],
            'beginTime': convert_time(t[4]),
            'endTime': convert_time(t[5]),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/patient/cancel-surgery', methods=['POST'])
def cancel_surgery():
    info = dict(request.json)
    sID = info['surgeryId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery'], ['charge_id'])
    wrapper.where('surgery_id', '=', sID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM surgery_related_record WHERE surgery_id = {sID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM surgery WHERE surgery_id = {sID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/patient/cancel-hospitalization', methods=['POST'])
def cancel_hospitalization():
    info = dict(request.json)
    hID = info['hospitalizationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization'], ['charge_id', 'room_id'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    room_id = wrapper.get()[0][1]
    update = f'''UPDATE room SET available_beds = available_beds + 1 WHERE room_id = '{room_id}' '''
    wrapper.execute_raw(update, False)
    delete = f'''DELETE FROM hospitalization_record WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM hospitalization WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/patient/cancel-charge', methods=['POST'])
def cancel_charge():
    return {'message': 'success'}, 200


@app.route('/get-patient-hospitalization', methods=['GET'])
def get_patient_hospitalization():
    wrapper = SQLWrapper(conn)
    query_fields = [
        'hospitalization.hospitalization_id',
        'consultation_id',
        'employee.name',
        'hospitalization_date_time',
        'discharge_date_time',
    ]
    wrapper.query(['hospitalization', 'hospitalization_record', 'employee'], query_fields)
    wrapper.where('hospitalization.hospitalization_id', '=', 'hospitalization_record.hospitalization_id', 'field')
    wrapper.where('hospitalization.doctor_id', '=', 'employee.employee_id', 'field')

    wrapper.where('hospitalization.hospitalization_id', '=', request.args.get('hospitalizationId'), 'str')
    wrapper.where('consultation_id', '=', request.args.get('consultationId'), 'str')
    wrapper.where('patient_id', '=', request.args.get('patientId'), 'str')
    wrapper.where('employee.name', '=', request.args.get('doctorName'), 'str')
    wrapper.where('hospitalization_date_time', '>=', request.args.get('beginTime1'), 'str')
    wrapper.where('hospitalization_date_time', '<=', request.args.get('endTime1'), 'str')

    if request.args.get('isHistory') == 'true':
        wrapper.where('discharge_date_time', 'IS NOT', 'NULL', 'null')
        wrapper.where('discharge_date_time', '>=', request.args.get('beginTime2'), 'str')
        wrapper.where('discharge_date_time', '<=', request.args.get('endTime2'), 'str')
    else:
        wrapper.where('discharge_date_time', 'IS', 'NULL', 'null')

    wrapper.run(join_method='')
    res = wrapper.get()
    ret = []
    for t in res:
        ret.append({
            'hospitalizationId': t[0],
            'consultationId': t[1],
            'doctorName': t[2],
            'beginTime': convert_time(t[3]),
            'endTime': convert_time(t[4]),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/get-patient-charge', methods=['GET'])
def get_patient_charge():

    def filer_charge(wrapper: SQLWrapper):
        wrapper.where('charge.patient_id', '=', request.args.get('patientId'), 'str')
        wrapper.where('charge.charge_id', '=', request.args.get('chargeId'), 'int')
        wrapper.where('cost', '>=', request.args.get('beginCost'), 'int')
        wrapper.where('cost', '<=', request.args.get('endCost'), 'int')
        wrapper.where('charge_date_time', '>=', request.args.get('beginTime'), 'str')
        wrapper.where('charge_date_time', '<=', request.args.get('endTime'), 'str')

    wrapper = SQLWrapper(conn)
    query_fields = [
        'charge.charge_id',
        'cost',
        'charge_date_time',
        'payment_method',
    ]
    required_types = request.args.getlist('itemTypeList[]')
    if required_types:
        required_types = [t.lower() for t in required_types]
    else:
        required_types = ['consultation', 'examination', 'rehabilitation', 'surgery', 'prescription', 'hospitalization']

    ret = []
    for table in required_types:
        wrapper.clear()
        wrapper.query(['charge', table], query_fields + [f'{table}_id'])
        wrapper.where('charge.charge_id', '=', f'{table}.charge_id', 'field')
        if request.args.get('isHistory') == 'true':
            wrapper.where('is_completed', '=', 'yes', 'str')
        else:
            wrapper.where('is_completed', '=', 'no', 'str')

        filer_charge(wrapper)
        wrapper.run(join_method='')
        res = wrapper.get()
        for t in res:
            ret.append({
                'chargeId': t[0],
                'cost': t[1],
                'time': convert_time(t[2]),
                'paymentMethod': t[3],
                'itemId': t[4],
                'itemType': table[0].upper() + table[1:]
            })

    return {'message': 'success', 'results': ret}, 200


@app.route('/get-department-arr', methods=['GET'])
def get_department_arr():
    dname = request.args.get('department')

    wrapper = SQLWrapper(conn)
    wrapper.query(['departments'],
                  ['name'])
    wrapper.where('name', 'like', '%' + dname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pnames = wrapper.get()
        lis = []
        for item in pnames:
            lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-patient-appointment', methods=['GET'])
def get_patient_appointment():
    pID = request.args.get('patientId')
    department = request.args.get('department')
    docName = request.args.get('doctorName')
    begin = request.args.get('beginTime')
    end = request.args.get('endTime')
    wrapper = SQLWrapper(conn)

    wrapper.query(['appointment', 'doctor', 'employee'],
                  ['department', 'employee.name', 'position', 'datetime', 'cost', 'available_slots', 'doctor.doctor_id'])
    wrapper.where('appointment.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('appointment.doctor_id', '=', 'doctor.doctor_id', 'field')
    wrapper.where('valid', '=', 1, 'int')
    wrapper.where('available_slots', '>', 0, 'int')
    if department is not None:
        wrapper.where('department', '=', department, 'str')
    if docName is not None:
        wrapper.where('doctor_name', '=', docName, 'str')
    if begin is not None:
        wrapper.where('date_time', '>', begin, 'DATETIME')
    if end is not None:
        wrapper.where('date_time', '<', end, 'DATETIME')

    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'result': {}}
        return ret, 400

    res = wrapper.get()
    ret = [{'department': result[0],
            'doctorName': result[1],
            'doctorId': result[6],
            'time': convert_time(result[3]),
            'cost': str(result[4]),
            'position': result[2]} for result in res]

    return {
               'message': 'success',
               'results': ret,
           }, 200


@app.route('/patient/schedule-appointment', methods=['POST'])
def schedule_appointment():
    info = dict(request.json)
    wrapper = SQLWrapper(conn)
    insert = f'''INSERT INTO charge (patient_id, cost, is_completed, tag)
                VALUE ('{info['patientId']}', {info['cost']}, 'NO', 1)'''
    wrapper.execute_raw(insert, False)

    query = 'SELECT LAST_INSERT_ID();'
    wrapper.execute_raw(query, False)
    charge_id = wrapper.get()[0][0]

    date_time = info['time']
    insert = f'''INSERT INTO consultation (doctor_id, patient_id, date_time, charge_id)
                VALUE ('{info['doctorId']}', '{info['patientId']}','{date_time}', {charge_id});'''
    wrapper.execute_raw(insert, False)
    wrapper.execute_raw(query, False)
    cID = wrapper.get()[0][0]

    update = f'''UPDATE appointment
                SET available_slots = available_slots - 1
                WHERE doctor_id = '{info['doctorId']}'
                AND datetime = '{date_time}'
                AND cost = {info['cost']};'''
    wrapper.execute_raw(update)

    return {'message': 'success', 'results': {'consultationId': cID}}, 200


# below, doctor
@app.route('/get-subordinate-name-and-inquirer-name-arr', methods=['GET'])
def get_subordinate_name_and_inquirer_name_arr():
    inquirerId = request.args.get('inquirerId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'],
                  ['employee_id'])
    wrapper.where('supervisor_id', '=', inquirerId, 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    if wrapper.get():
        supervisor_ids = wrapper.get()
        name_lis = []
        for supervisor_id in supervisor_ids:
            name_lis.append(get_doctor_name(supervisor_id[0], conn))
        return {'message': 'success', 'results': name_lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-subordinate-id-and-inquirer-id-arr', methods=['GET'])
def get_subordinate_id_and_inquirer_id_arr():
    inquirerId = request.args.get('inquirerId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'],
                  ['employee_id'])
    wrapper.where('supervisor_id', '=', inquirerId, 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    if wrapper.get():
        supervisor_ids = wrapper.get()
        lis = []
        for supervisor_id in supervisor_ids:
            lis.append(supervisor_id[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-patient-name-arr', methods=['GET'])
def get_patient_name_arr():
    pname = request.args.get('name')
    rid = request.args.get('inquirerId')
    rtype = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['patient'],
                  ['name'])
    wrapper.where('name', 'like', pname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pnames = wrapper.get()
        lis = []
        for item in pnames:
            lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-patient-id-arr', methods=['GET'])
def get_patient_id_arr():
    pid = request.args.get('Id')
    rid = request.args.get('inquirerId')
    rtype = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['patient'],
                  ['patient_id'])
    wrapper.where('patient_id', 'like', pid + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pids = wrapper.get()
        lis = []
        for item in pids:
            lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-doctor-consultation', methods=['GET'])
def get_doctor_consultation():
    info = dict(request.args)
    logic = ('hasStarted' in info.keys())  # 不同界面的调用逻辑

    wrapper = SQLWrapper(conn)
    wrapper.query(['consultation', 'patient', 'doctor'],
                  ['consultation_id', 'date_time', 'patient_id', 'name', 'doctor_id', 'department', 'self_report'])
    wrapper.where('doctor_id', '=', info['inquirerId'], 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    id_name = {}
    if wrapper.get():
        consultation = wrapper.get()
        lst = []
        for i in range(len(consultation)):
            if logic and consultation[i][6]:
                continue
            else:
                doctor_name = 'error'
                if consultation[i][4] not in id_name.keys():
                    wrapper = SQLWrapper(conn)
                    wrapper.query(['employee'], ['name'])
                    wrapper.where('employee_id', '=', consultation[i][4], 'str')
                    code = wrapper.run()
                    if code != 0:
                        ret = {'message': f'database error {code}', 'results': {}}
                        return ret, 400
                    if wrapper.get():
                        doctor_name = wrapper.get()[0][0]
                else:
                    doctor_name = id_name[str(consultation[i][4])]
                if ((not info['patientName']) or str(consultation[i][3]) == info['patientName']) and \
                        ((not info['patientId']) or str(consultation[i][2]) == info['patientId']) and \
                        ((not info['consultationId']) or str(consultation[i][0]) == info['consultationId']) and \
                        ((not info['beginTime']) or str(consultation[i][1]) >= info['beginTime']) and \
                        ((not info['endTime']) or str(consultation[i][1]) <= info['endTime']):
                    id_name[str(consultation[i][4])] = doctor_name
                    lst.append({
                        'consultationId': str(consultation[i][0]),
                        'time': str(consultation[i][1]),
                        'patientId': str(consultation[i][2]),
                        'patientName': str(consultation[i][3]),
                        'doctorId': str(consultation[i][4]),
                        'department': str(consultation[i][5]),
                        'doctorName': doctor_name,
                        'hasStarted': 'true' if not logic and str(datetime.now()) > str(consultation[i][1]) else 'false',
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }


@app.route('/doctor/cancel-consultation', methods=['POST'])
def doctor_cancel_consultation():
    info = dict(request.json)
    cID = info['consultationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['consultation'], ['charge_id', 'doctor_id', 'date_time'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    dID = wrapper.get()[0][1]
    date_time = wrapper.get()[0][2]
    update = f'''UPDATE appointment SET available_slots = available_slots + 1 WHERE
                    doctor_id  = '{dID}' AND datetime = '{date_time}' '''
    wrapper.execute_raw(update, False)
    delete = f'''DELETE FROM consultation WHERE consultation_id = {cID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-doctor-info', methods=['GET'])
def get_doctor_info():
    pID = request.args.get('doctorId')
    wrapper = SQLWrapper(conn)

    wrapper.query(['employee'], [])
    wrapper.where('employee_id', '=', pID, 'str')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    res_employee = wrapper.get()[0]

    wrapper = SQLWrapper(conn)
    wrapper.query(['doctor'], [])
    wrapper.where('doctor_id', '=', pID, 'str')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    res_doctor = wrapper.get()[0]

    ret = {}
    if res_employee and res_doctor:
        for idx, field in enumerate(employee_fields.keys()):
            ret[field] = str(res_employee[idx]) if res_employee[idx] is not None else ''
        for idx, field in enumerate(doctor_fields.keys()):
            ret[field] = str(res_doctor[idx]) if res_doctor[idx] is not None else ''
        ret = {'message': 'success', 'results': ret}
        return ret, 200
    else:
        ret = {'message': 'failed', 'results': 'The patient ID is invalid.'}
        return ret, 400


@app.route('/get-examination-name-arr', methods=['GET'])
def get_examination_name_arr():
    ename = request.args.get('examinationName')
    wrapper = SQLWrapper(conn)
    wrapper.query(['examinations'],
                  ['name'])
    wrapper.where('name', 'like', '%' + ename + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    lis = []
    if wrapper.get():
        pnames = wrapper.get()
        for item in pnames:
            lis.append(item[0])
    return {'message': 'success', 'results': lis}, 200


@app.route('/appointment/examination/is-time-available', methods=['GET'])
def appointment_examination_is_time_available():
    name = request.args.get('examinationName')
    date = request.args.get('examinationDate')
    date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    extracted_date = date_object.date()
    wrapper = SQLWrapper(conn)
    query = f'''SELECT DATE_FORMAT(examination_date_time, '%H:%i:%s') AS time_category, COUNT(*)
                FROM examination
                WHERE DATE_FORMAT(examination_date_time, '%Y-%m-%d') = '{extracted_date}'
                AND examination_name = '{name}'
                GROUP BY time_category
                HAVING COUNT(*) >= 10;'''
    wrapper.execute_raw(query)
    results = wrapper.get()
    un_available = [str(result[0]) for result in results]
    ret = [{'examinationTime': t,
            'isAvailable': 'false' if t in un_available else 'true'} for t in examination_time_choose]
    return {'message': 'success',
            'results': ret
            }, 200


@app.route('/appointment/examination/pre-schedule', methods=['POST'])
def appointment_examination_pre_schedule():
    info = dict(request.json)
    cID = info['consultationId']
    name = info['examinationName']
    time = info['examinationTime']
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    wrapper.query(['consultation', 'patient'], ['patient_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0]
    if res:
        patient_id = res[0]
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400
    query = f'''SELECT cost FROM examinations WHERE examinations.name = '{name}' '''
    wrapper.execute_raw(query)
    res = wrapper.get()
    if res:
        cost = res[0][0]
    else:
        return {
                   'message': 'failed',
                   'results': 'examination_name is invalid'
               }, 400
    insert = f'''INSERT INTO charge (patient_id, cost, is_completed)
                VALUES ('{patient_id}', {cost}, 'NO')'''
    wrapper.execute_raw(insert)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    insert = f'''INSERT INTO examination (consultation_id, examination_date_time, examination_name, charge_id)
                VALUES ({cID}, '{time}', '{name}', {charge_id})'''
    wrapper.execute_raw(insert)
    wrapper.execute_raw(query)
    eID = wrapper.get()[0][0]
    if eID:
        return {
                   'message': 'success',
                   'results': {
                       'examinationId': str(eID),
                       'examinationName': name,
                   }
               }, 200
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400


@app.route('/appointment/examination/delete-pre-schedule', methods=['POST'])
def appointment_examination_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    eID = info['examinationId']
    wrapper = SQLWrapper(conn)
    query = f'''SELECT charge_id FROM examination WHERE examination_id = {eID}'''
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM examination WHERE
                examination_id = {eID} '''
    wrapper.execute_raw(delete)
    delete = f'''DELETE FROM charge
                WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-rehabilitation-name-arr', methods=['GET'])
def get_rehabilitation_name_arr():
    rname = request.args.get('rehabilitationName')

    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitations'],
                  ['name'])
    wrapper.where('name', 'like', '%' + rname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    lis = []
    if wrapper.get():
        pnames = wrapper.get()
        for item in pnames:
            lis.append(item[0])
    return {'message': 'success', 'results': lis}, 200



@app.route('/appointment/rehabilitation/is-time-available', methods=['GET'])  # 2023/10/19 already added in doc
def appointment_rehabilitation_is_time_available():
    name = request.args.get('rehabilitationName')
    date = request.args.get('beginDate')
    date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    extracted_date = date_object.date()
    wrapper = SQLWrapper(conn)
    query = f'''SELECT DATE_FORMAT(begin_date_time, '%H:%i:%s') AS time_category, COUNT(*)
                    FROM rehabilitation
                    WHERE DATE_FORMAT(begin_date_time, '%Y-%m-%d') = '{extracted_date}'
                    AND rehabilitation_name = '{name}'
                    GROUP BY time_category
                    HAVING COUNT(*) >= 10;'''
    wrapper.execute_raw(query)
    results = wrapper.get()
    un_available = [str(result[0]) for result in results]
    ret = [{'beginTime': t,
            'isAvailable': 'false' if t in un_available else 'true'} for t in rehabilitation_time_choose]
    return {'message': 'success',
            'results': ret
            }, 200


@app.route('/appointment/rehabilitation/pre-schedule', methods=['POST'])
def appointment_rehabilitation_pre_schedule():
    info = dict(request.json)
    cID = info['consultationId']
    name = info['rehabilitationName']
    time = info['beginTime']
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    query = f'''SELECT patient_id FROM consultation NATURAL JOIN patient
                 WHERE consultation_id = {cID} AND valid = 1 '''
    wrapper.execute_raw(query)
    res = wrapper.get()[0]
    if res:
        patient_id = res[0]
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400
    query = f'''SELECT cost FROM rehabilitations WHERE rehabilitations.name = '{name}' '''
    wrapper.execute_raw(query)
    res = wrapper.get()
    if res:
        cost = res[0][0]
    else:
        return {
                   'message': 'failed',
                   'results': 'rehabilitation_name is invalid'
               }, 400
    insert = f'''INSERT INTO charge (patient_id, cost, is_completed)
                VALUES ('{patient_id}', {cost}, 'NO')'''
    wrapper.execute_raw(insert)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    insert = f'''INSERT INTO rehabilitation (consultation_id, begin_date_time, rehabilitation_name, charge_id)
                VALUES ({cID}, '{time}', '{name}', {charge_id})'''
    wrapper.execute_raw(insert)
    wrapper.execute_raw(query)
    rID = wrapper.get()[0][0]
    if rID:
        return {
                   'message': 'success',
                   'results': {
                       'rehabilitationId': str(rID),
                       'rehabilitationName': name,
                   }
               }, 200
    else:
        return {
                   'message': 'failed',
                   'results': 'something wrong when insert into rehabilitation'
               }, 400


@app.route('/appointment/rehabilitation/delete-pre-schedule', methods=['POST'])
def appointment_rehabilitation_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    rID = info['rehabilitationId']
    wrapper = SQLWrapper(conn)
    query = f'''SELECT charge_id FROM rehabilitation WHERE rehabilitation_id = {rID}'''
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM rehabilitation WHERE
                rehabilitation_id = {rID} '''
    wrapper.execute_raw(delete)
    delete = f'''DELETE FROM charge
                WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/appointment/prescription/pre-schedule/ask-for-prescription-id', methods=['POST'])
def appointment_prescription_pre_schedule_ask_id():
    info = dict(request.json)
    cID = int(info['consultationId'])
    wrapper = SQLWrapper(conn)
    query = f'''SELECT doctor_id, patient_id FROM consultation WHERE consultation_id = {cID}'''
    wrapper.execute_raw(query)
    res = wrapper.get()[0]
    if res:
        doctor_id, patient_id = res
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400

    insert = f'''INSERT INTO charge (patient_id, cost, is_completed, tag)
                VALUES ('{patient_id}', 0, 'NO', 0)'''
    wrapper.execute_raw(insert)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    insert = f'''INSERT INTO prescription (consultation_id, doctor_id, charge_id)
                VALUES ({cID}, '{doctor_id}', {charge_id})'''
    wrapper.execute_raw(insert)
    wrapper.execute_raw(query)
    pID = wrapper.get()[0][0]
    if pID:
        return {
                   'message': 'success',
                   'results': {
                       'prescriptionId': str(pID),
                   }
               }, 200
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400


@app.route('/appointment/prescription/pre-schedule/confirm', methods=['POST'])
def appointment_prescription_pre_schedule_confirm():
    # should always return success!!!
    info = dict(request.json)
    pID = info['prescriptionId']
    wrapper = SQLWrapper(conn)
    query = f'SELECT cost FROM prescription_medicine WHERE prescription_id = {pID}'
    wrapper.execute_raw(query)
    costs = wrapper.get()
    total_cost = sum([cost[0] for cost in costs])
    query = f'SELECT charge_id FROM prescription WHERE prescription_id = {pID}'
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    update = f'UPDATE charge SET cost = cost + {total_cost} WHERE charge_id = {charge_id}'
    wrapper.execute_raw(update, False)
    window = random.randint(1, 10)
    update = f'''UPDATE prescription SET pharmacy_window = '{window}' WHERE prescription_id = {pID} '''
    wrapper.execute_raw(update)

    return {
        'message': 'success',
    }, 200


@app.route('/appointment/prescription/pre-schedule/cancel', methods=['POST'])
def appointment_prescription_pre_schedule_cancel():
    # should always return success!!!
    info = dict(request.json)
    wrapper = SQLWrapper(conn)
    delete = f'''DELETE FROM prescription_medicine WHERE
                    prescription_id = {info['prescriptionId']};'''
    wrapper.execute_raw(delete, False)
    query = f'''SELECT charge_id FROM prescription WHERE prescription_id = {info['prescriptionId']}'''
    wrapper.execute_raw(query, False)
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM prescription WHERE
                    prescription_id = {info['prescriptionId']};'''
    wrapper.execute_raw(delete,False)
    delete = f'''DELETE FROM charge
                    WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)


@app.route('/appointment/prescription/delete-pre-schedule', methods=['POST'])
def appointment_prescription_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    wrapper = SQLWrapper(conn)
    delete = f'''DELETE FROM prescription_medicine WHERE
                prescription_id = {info['prescriptionId']};'''
    wrapper.execute_raw(delete, False)
    query = f'''SELECT charge_id FROM prescription WHERE prescription_id = {info['prescriptionId']}'''
    wrapper.execute_raw(query, False)
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM prescription WHERE
                prescription_id = {info['prescriptionId']};'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge
                WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-medicine-info-arr', methods=['GET'])
def get_medicine_info_arr():
    pid = request.args.get('medicineName')

    wrapper = SQLWrapper(conn)
    wrapper.query(['medicine'],
                  ['medicine_id', 'name'])
    wrapper.where('name', 'like', '%' + pid + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    result = {'message': 'success', 'results': []}

    if wrapper.get():
        medicine_id_name = wrapper.get()
        for item in medicine_id_name:
            result['results'].append({
                'medicineId': item[0],
                'medicineName': item[1],
            })
        return result, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/appointment/prescription/pre-schedule/add-medicine', methods=['POST'])
def appointment_prescription_pre_schedule_add_medicine():
    info = dict(request.json)
    wrapper = SQLWrapper(conn)
    quantity = str(info['quantity'])
    if not quantity.isdigit():
        return {'message': 'failed', 'results': 'The quantity should be digital'}, 400
    query = f'''SELECT cost FROM medicine WHERE medicine_id = {info['medicineId']}'''
    wrapper.execute_raw(query)
    res = wrapper.get()[0][0]
    if res:
        cost = res*int(info['quantity'])
    else:
        return {'message': 'failed', 'results': 'The medicine ID is invalid'}, 400
    insert = f'''INSERT INTO prescription_medicine (prescription_id, medicine_id,
                quantity, course_of_medication, dosage, frequency, cost)
                VALUES ({info['prescriptionId']}, {info['medicineId']}, {info['quantity']},
                 '{info['courseOfMedication']}', '{info['dosage']}', '{info['frequency']}', {cost});'''
    wrapper.execute_raw(insert)
    return {'message': 'success'}, 200


@app.route('/appointment/prescription/pre-schedule/delete-medicine', methods=['POST'])
def appointment_prescription_pre_schedule_delete_medicine():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    wrapper = SQLWrapper(conn)
    delete = f'''DELETE FROM prescription_medicine
                where prescription_id = {info['prescriptionId']} AND
                medicine_id = {info['medicineId']};'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/get-medicine-name-by-id', methods=['GET'])
def get_medicine_name_by_id():
    medicine_id = request.args.get('medicineId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['medicine'], ['name'])
    wrapper.where('medicine_id', '=', medicine_id, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': ''}
        return ret, 400
    res = wrapper.get()[0]
    if res:
        return {'message': 'success', 'results': res[0]}, 200
    else:
        return {'message': 'failed', 'results': 'The medicine id is invalid'}


@app.route('/get-surgery-site-arr', methods=['GET'])
def get_surgery_site_arr():
    surgery_site = request.args.get('surgerySite')

    query = f'''SELECT DISTINCT surgery_site FROM surgeries WHERE surgery_site LIKE '%{surgery_site}%';'''
    wrapper = SQLWrapper(conn)
    wrapper.execute_raw(query)
    results = wrapper.get()
    ret = [result[0] for result in results]
    return {'message': 'success', 'results': ret}, 200


@app.route('/get-surgery-name-arr', methods=['GET'])
def get_surgery_name_arr():
    sname = request.args.get('surgeryName')
    site = request.args.get('surgerySite')

    wrapper = SQLWrapper(conn)
    wrapper.query(['surgeries'],
                  ['name'])
    wrapper.where('name', 'like', '%'+ sname + '%', 'str')
    wrapper.where('surgery_site', '=', site, 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    lis = []
    if wrapper.get():
        pnames = wrapper.get()

        for item in pnames:
            lis.append(item[0])
    return {'message': 'success', 'results': lis}, 200




@app.route('/get-surgery-type-arr', methods=['GET'])
def get_surgery_type_arr():
    return {'message': 'success', 'results': ['normal', 'emergency']}, 200


@app.route('/appointment/surgery/is-time-available', methods=['GET'])
def appointment_surgery_is_time_available():
    name = request.args.get('surgeryName')
    date = request.args.get('beginDate')
    date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    extracted_date = date_object.date()
    wrapper = SQLWrapper(conn)
    query = f'''SELECT DATE_FORMAT(begin_date_time, '%H:%i:%s') AS time_category, COUNT(*)
                        FROM surgery
                        WHERE DATE_FORMAT(begin_date_time, '%Y-%m-%d') = '{extracted_date}'
                        AND surgery_name = '{name}'
                        GROUP BY time_category
                        HAVING COUNT(*) >= 1;'''
    wrapper.execute_raw(query)
    results = wrapper.get()
    un_available = [str(result[0]) for result in results]
    ret = [{'beginTime': t,
            'isAvailable': 'false' if t in un_available else 'true'} for t in surgery_time_choose]
    return {'message': 'success',
            'results': ret
            }, 200


@app.route('/appointment/surgery/pre-schedule', methods=['POST'])
def appointment_surgery_pre_schedule():
    info = dict(request.json)
    cID = info['consultationId']
    site = info['surgerySite']
    time = info['beginTime']
    surgery_type = info['surgeryType']
    description = info['surgeryDescription']
    name = info['surgeryName']
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    query = f'''SELECT patient_id FROM consultation NATURAL JOIN patient
                  WHERE consultation_id = {cID} AND valid = 1'''
    wrapper.execute_raw(query)
    res = wrapper.get()
    if res:
        patient_id = res[0][0]
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400
    query = f'''SELECT cost FROM surgeries WHERE name = '{name}' '''
    wrapper.execute_raw(query)
    res = wrapper.get()[0]
    if res:
        cost = res[0]
    else:
        return {
                   'message': 'failed',
                   'results': 'examination_name is invalid'
               }, 400
    insert = f'''INSERT INTO charge (patient_id, cost, is_completed)
                VALUES ('{patient_id}', {cost}, 'NO')'''
    wrapper.execute_raw(insert, False)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query, False)
    charge_id = wrapper.get()[0][0]
    insert = f'''INSERT INTO surgery (consultation_id, patient_id, surgery_name, surgery_description,
                                    surgery_site, surgery_type, begin_date_time, charge_id)
                VALUES ({cID},'{patient_id}', '{name}', '{description}', '{site}', 
                '{surgery_type}',  '{time}', {charge_id})'''
    wrapper.execute_raw(insert)
    wrapper.execute_raw(query)
    sID = wrapper.get()[0][0]
    if sID:
        return {
                   'message': 'success',
                   'results': {
                       'surgeryId': str(sID),
                       'surgeryName': name,
                   }
               }, 200
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400


@app.route('/appointment/surgery/delete-pre-schedule', methods=['POST'])
def appointment_surgery_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    sID = info['surgeryId']
    wrapper = SQLWrapper(conn)
    query = f'''SELECT charge_id FROM surgery WHERE surgery_id = {sID}'''
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM surgery WHERE
                surgery_id = {sID} '''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge
                WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/appointment/hospitalization/is-time-available', methods=['GET'])
def appointment_hospitalization_is_time_available():
    ret = [{'hospitalizationTime': t,
            'isAvailable': 'true'} for t in examination_time_choose]
    return {'message': 'success',
            'results': ret
            }, 200


@app.route('/appointment/hospitalization/pre-schedule', methods=['POST'])
def appointment_hospitalization_pre_schedule():
    info = dict(request.json)
    cID = info['consultationId']
    reason = info['hospitalizationReason']
    time = info['hospitalizationTime']
    type = info['roomType']
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    query = f'''SELECT patient_id FROM consultation NATURAL JOIN patient
    #              WHERE consultation_id = {cID} AND valid = 1 '''
    wrapper.execute_raw(query)
    res = wrapper.get()[0]
    if res:
        patient_id = res[0]
    else:
        return {
                   'message': 'failed',
                   'results': 'consultation ID is invalid'
               }, 400

    insert = f'''INSERT INTO charge (patient_id, cost, is_completed)
                VALUES ('{patient_id}', 0, 'NO')'''
    wrapper.execute_raw(insert, False)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query, False)
    charge_id = wrapper.get()[0][0]
    query = '''SELECT room_id, number_of_beds FROM room WHERE available_beds > 0 ORDER BY RAND() LIMIT 1'''
    wrapper.execute_raw(query, False)
    res = wrapper.get()
    if res:
        room_id = res[0][0]
        number = res[0][1]
    else:
        return {
                       'message': 'failed',
                       'results': 'There is no available room.'
                   }, 400
    query = f'''SELECT doctor_id, employee.name FROM room JOIN employee
                WHERE room_id = '{room_id}' AND room.doctor_id = employee.employee_id AND valid = 1'''
    wrapper.execute_raw(query, False)
    doctor_id = wrapper.get()[0][0]
    doctor_name = wrapper.get()[0][1]
    query = f'''SELECT bed_number FROM hospitalization WHERE room_id = '{room_id}' AND discharge_date_time IS NULL'''
    wrapper.execute_raw(query, False)
    results = wrapper.get()
    bed_list = [result[0] for result in results]
    bed_number = 0
    for i in range(1, number+1):
        if i not in bed_list:
            bed_number = i
            break
    insert = f'''INSERT INTO hospitalization (patient_id, doctor_id, hospitalization_date_time,
                    hospitalization_reason, room_id, bed_number, charge_id)
                VALUES ('{patient_id}', '{doctor_id}', '{time}', '{reason}', '{room_id}', {bed_number}, {charge_id})'''
    wrapper.execute_raw(insert, False)
    query = 'SELECT LAST_INSERT_ID()'
    wrapper.execute_raw(query, False)
    hID = wrapper.get()[0][0]
    update = f'''UPDATE room SET available_beds = available_beds - 1 WHERE room_id = '{room_id}';'''
    wrapper.execute_raw(update, False)
    if hID:
        insert = f'''INSERT INTO hospitalization_record (hospitalization_id, consultation_id)
                    VALUES ({hID}, {cID})'''
        wrapper.execute_raw(insert)
        return {
                   'message': 'success',
                   'results': {
                       'hospitalizationId': str(hID),
                       'doctorName': doctor_name,
                   }
               }, 200
    else:
        return {
                   'message': 'failed',
                   'results': 'something wrong when insert into hospitalization'
               }, 400


@app.route('/appointment/hospitalization/delete-pre-schedule', methods=['POST'])
def appointment_hospitalization_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    info = dict(request.json)
    hID = info['hospitalizationId']
    wrapper = SQLWrapper(conn)
    query = f'''SELECT charge_id, room_id FROM hospitalization WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    room_id = wrapper.get()[0][1]
    update = f'''UPDATE room SET available_beds = available_beds + 1 WHERE room_id = '{room_id}';'''
    wrapper.execute_raw(update,False)
    delete = f'''DELETE FROM hospitalization_record WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(delete,False)
    delete = f'''DELETE FROM hospitalization WHERE
                hospitalization_id = {hID} '''
    wrapper.execute_raw(delete,False)
    delete = f'''DELETE FROM charge
                WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/appointment/consultation/submit', methods=['POST'])
def appointment_consultation_submit():
    # can only success!!!
    info = dict(request.json)
    cID = info['consultationId']
    report = info['selfReport']
    time = info['time']
    medical_history = info['medicalHistory']
    medication_history = info['medicationHistory']
    medical_advice = info['medicalAdvice']
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE consultation
                SET date_time = '{time}',
                    self_report = '{report}',
                    medical_history = '{medical_history}',
                    medication_history = '{medication_history}',
                    medical_advice = '{medical_advice}'
                WHERE consultation_id = {cID};'''
    wrapper.execute_raw(update, False)

    wrapper.clear()
    wrapper.query(['prescription'], ['prescription_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE prescription_medicine SET tag = 1 WHERE prescription_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE  prescription SET tag = 1 WHERE prescription_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE charge SET tag = 1 WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(update)

    wrapper.clear()
    wrapper.query(['examination'], ['examination_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE examination SET tag = 1 WHERE examination_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE charge SET tag = 1 WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(update)

    wrapper.clear()
    wrapper.query(['rehabilitation'], ['rehabilitation_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE rehabilitation SET tag = 1 WHERE rehabilitation_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE charge SET tag = 1 WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(update)

    wrapper.clear()
    wrapper.query(['surgery'], ['surgery_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE surgery SET tag = 1 WHERE surgery_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE charge SET tag = 1 WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(update)

    wrapper.clear()
    wrapper.query(['hospitalization', 'hospitalization_record'], ['hospitalization.hospitalization_id', 'charge_id', 'room_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE hospitalization_record SET tag = 1 WHERE hospitalization_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE hospitalization SET tag = 1 WHERE hospitalization_id = {result[0]}'''
        wrapper.execute_raw(update)
        update = f'''UPDATE charge SET tag = 1 WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(update)

    return {'message': 'success'}, 200


@app.route('/appointment/consultation/delete', methods=['POST'])
def appointment_consultation_delete():
    # can only success!!!
    # doctor abandon the consultation that he has already filled
    # should release the prescription, examination and so on that he has already filled
    info = dict(request.json)
    cID = info['consultationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription'], ['prescription_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        delete = f'''DELETE FROM prescription_medicine WHERE prescription_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM prescription WHERE prescription_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM charge WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(delete)

    wrapper.clear()
    wrapper.query(['examination'], ['examination_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        delete = f'''DELETE FROM examination WHERE examination_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM charge WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(delete)

    wrapper.clear()
    wrapper.query(['rehabilitation'], ['rehabilitation_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        delete = f'''DELETE FROM rehabilitation WHERE rehabilitation_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM charge WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(delete)

    wrapper.clear()
    wrapper.query(['surgery'], ['surgery_id', 'charge_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        delete = f'''DELETE FROM surgery WHERE surgery_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM charge WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(delete)

    wrapper.clear()
    wrapper.query(['hospitalization', 'hospitalization_record'], ['hospitalization.hospitalization_id', 'charge_id', 'room_id'])
    wrapper.where('consultation_id', '=', cID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    wrapper.clear()
    for result in results:
        update = f'''UPDATE room SET available_beds = available_beds + 1 WHERE room_id = {result[2]}'''
        wrapper.execute_raw(update)
        delete = f'''DELETE FROM hospitalization_record WHERE hospitalization_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM hospitalization WHERE hospitalization_id = {result[0]}'''
        wrapper.execute_raw(delete)
        delete = f'''DELETE FROM charge WHERE charge_id = {result[1]}'''
        wrapper.execute_raw(delete)

    return {'message': 'success'}, 200


@app.route('/get-doctor-prescription', methods=['GET'])
def get_doctor_prescription():
    info = dict(request.args)
    logic = ('hasStarted' in info.keys())  # 不同界面的调用逻辑

    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription'],
                  ['prescription_id', 'consultation_id', 'pharmacy_pickup_date_time', 'pharmacy_window'])
    wrapper.where('doctor_id', '=', info['inquirerId'], 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        prescription = wrapper.get()

        lst = []
        consultation_pid_did_pname_dname = {}
        for i in range(len(prescription)):
            if prescription[i][1] not in consultation_pid_did_pname_dname.keys():
                wrapper = SQLWrapper(conn)
                wrapper.query(['consultation'],
                              ['patient_id', 'doctor_id'])
                wrapper.where('consultation_id', '=', str(prescription[i][1]), 'str')
                code = wrapper.run(limit=1)
                if code != 0:
                    ret = {'message': f'database error {code}', 'results': {}}
                    return ret, 400
                if wrapper.get():
                    pid_did = wrapper.get()
                    patient_name = get_patient_name(pid_did[0][0], conn)
                    doctor_name = get_doctor_name(pid_did[0][1], conn)
                    consultation_pid_did_pname_dname[prescription[i][1]] = []
                    consultation_pid_did_pname_dname[prescription[i][1]].append(pid_did)
                    consultation_pid_did_pname_dname[prescription[i][1]].append(patient_name)
                    consultation_pid_did_pname_dname[prescription[i][1]].append(doctor_name)
            else:
                pid_did = consultation_pid_did_pname_dname[prescription[i][1]][0]
                patient_name = consultation_pid_did_pname_dname[prescription[i][1]][1]
                doctor_name = consultation_pid_did_pname_dname[prescription[i][1]][2]

            if not (logic and prescription[i][3]):
                if ((not info['patientName']) or str(patient_name) == info['patientName']) and \
                        ((not info['patientId']) or str(pid_did[0][0]) == info['patientId']) and \
                        ((not info['prescriptionId']) or str(prescription[i][0]) == info['prescriptionId']) and \
                        ((not info['beginTime']) or str(prescription[i][2]) >= info['beginTime']) and \
                        ((not info['endTime']) or str(prescription[i][2]) <= info['endTime']) and \
                        ((not info['consultationId']) or str(prescription[i][1]) == info['consultationId']):
                    lst.append({
                        'prescriptionId': str(prescription[i][0]),
                        'consultationId': str(prescription[i][1]),
                        'pharmacyPickupTime': convert_time(prescription[i][2]),
                        'pharmacyPickWindow': str(prescription[i][3]),
                        'hasStarted': 'true' if str(datetime.now()) > str(prescription[i][2]) else 'false',
                        'patientId': pid_did[0][0],
                        'patientName': patient_name,
                        'doctorId': pid_did[0][1],
                        'doctorName': doctor_name,
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }


@app.route('/doctor/cancel-prescription', methods=['POST'])
def doctor_cancel_prescription():
    info = dict(request.json)
    pID = info['prescriptionId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['prescription'], ['charge_id'])
    wrapper.where('prescription_id', '=', pID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]
    delete = f'''DELETE FROM prescription_medicine WHERE prescription_id = {pID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM prescription WHERE prescription_id = {pID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/prescription/finish', methods=['POST'])
def prescription_finish():
    info = dict(request.json)
    pID = info['prescriptionId']
    pick_up_time = info['pharmacyPickupTime']
    pick_up_time = datetime.strptime(pick_up_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE prescription SET pharmacy_pickup_date_time = '{pick_up_time}' WHERE prescription_id = {pID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-doctor-examination', methods=['GET'])
def get_doctor_examination():  # 这里数据库的自然连接有点啸问题，自己用了很屑的逻辑写了
    info = dict(request.args)
    logic = ('hasResult' in info.keys())  # 不同界面的调用逻辑
    examinationinfo = []
    wrapper = SQLWrapper(conn)
    wrapper.query(['examination'],
                  [])
    code = wrapper.run()

    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    if wrapper.get():
        examination_pid_did_pname_dname = {}
        examination = wrapper.get()
        for i in range(len(examination)):
            examinationinfo.append([])
            for item in examination[i]:
                examinationinfo[i].append(item)
            if examination[i][1] not in examination_pid_did_pname_dname.keys():
                wrapper.clear()
                wrapper.query(['consultation'],
                              ['doctor_id', 'patient_id'])
                wrapper.where('consultation_id', '=', str(examination[i][1]), 'int')
                code = wrapper.run()

                if code != 0:
                    ret = {'message': f'database error {code}', 'results': {}}
                    return ret, 400
                consultation = wrapper.get()
                if wrapper.get():
                    for j in range(len(consultation)):
                        for item in consultation[j]:
                            examinationinfo[i].append(item)
                    did = examinationinfo[i][8]
                    pid = examinationinfo[i][9]
                    patient_name = get_patient_name(pid, conn)
                    doctor_name = get_doctor_name(did, conn)
                    examination_pid_did_pname_dname[examination[i][1]] = []
                    examination_pid_did_pname_dname[examination[i][1]].append(pid)
                    examination_pid_did_pname_dname[examination[i][1]].append(did)
                    examination_pid_did_pname_dname[examination[i][1]].append(patient_name)
                    examination_pid_did_pname_dname[examination[i][1]].append(doctor_name)

        lst = []
        for i in range(len(examinationinfo)):
            pid = examination_pid_did_pname_dname[examination[i][1]][0]
            did = examination_pid_did_pname_dname[examination[i][1]][1]
            patient_name = examination_pid_did_pname_dname[examination[i][1]][2]
            doctor_name = examination_pid_did_pname_dname[examination[i][1]][3]
            if not (logic and examinationinfo[i][5] == '1'):
                if ((not info['examinationId']) or str(examinationinfo[i][0]) == info['examinationId']) and \
                        ((not info['examinationName']) or str(examinationinfo[i][4]) == info['examinationName']) and \
                        ((not info['patientName']) or str(patient_name) == info['patientName']) and \
                        ((not info['patientId']) or str(pid) == info['patientId']) and \
                        ((not info['beginExaminationTime']) or str(examinationinfo[i][2]) >= info['beginExaminationTime']) and \
                        ((not info['endExaminationTime']) or str(examinationinfo[i][2]) <= info['endExaminationTime']) and \
                        ((not info['consultationId']) or str(examinationinfo[i][1]) == info['consultationId']):
                    lst.append({
                        'examinationId': str(examinationinfo[i][0]),
                        'consultationId': str(examinationinfo[i][1]),
                        'examinationName': str(examinationinfo[i][4]),
                        'examinationTime': convert_time(examinationinfo[i][2]),
                        'resultTime': convert_time(examinationinfo[i][3]),
                        'patientId': pid,
                        'patientName': patient_name,
                        'doctorId': did,
                        'doctorName': doctor_name,
                        'hasConducted': 'true' if examinationinfo[i][5] == '1' else 'false',
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }


@app.route('/doctor/cancel-examination', methods=['POST'])
def doctor_cancel_examination():
    info = dict(request.json)
    eID = info['examinationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['examination'], ['charge_id'])
    wrapper.where('examination_id', '=', eID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]

    delete = f'''DELETE FROM examination WHERE examination_id = {eID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/doctor/examination/conduct', methods=['POST'])
def doctor_examination_conduct():
    info = dict(request.json)
    eID = info['examinationId']
    examination_time = info['examinationTime']
    examination_time = datetime.strptime(examination_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE examination SET examination_date_time = '{examination_time}' WHERE examination_id = {eID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/doctor/examination/record', methods=['POST'])
def doctor_examination_record():
    info = dict(request.json)
    eID = info['examinationId']
    examination_result = info['result']
    result_time = info['resultTime']
    result_time = datetime.strptime(result_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)

    doctor_arr = info['doctorRoughArr']
    for doctor_info in doctor_arr:
        insert = f'''INSERT INTO examination_doctor(examination_id, doctor_id)
                    VALUES ({eID}, '{doctor_info['doctorId']}')'''
        wrapper.execute_raw(insert, commit=False)

    nurse_arr = info['nurseRoughArr']
    for nurse_info in nurse_arr:
        insert = f'''INSERT INTO examination_nurse(examination_id, nurse_id)
                    VALUES ({eID}, '{nurse_info['nurseId']}')'''
        wrapper.execute_raw(insert, commit=False)

    helping_staff_arr = info['helpingStaffRoughArr']
    for helping_staff_info in helping_staff_arr:
        insert = f'''INSERT INTO examination_helping_staff(examination_id, helping_staff_id)
                    VALUES ({eID}, '{helping_staff_info['helpingStaffId']}')'''
        wrapper.execute_raw(insert, commit=False)

    update = f'''UPDATE examination SET time_of_result = '{result_time}', result =' {examination_result}'
                WHERE examination_id = {eID}'''
    wrapper.execute_raw(update)

    return {'message': 'success'}, 200


@app.route('/add-collaborator/get-doctor-info-arr', methods=['GET'])
def add_collaborator_get_doctor_info_arr():
    doctor_name = request.args.get('doctorName')
    wrapper = SQLWrapper(conn)
    wrapper.query(['doctor', 'employee'], ['doctor_id', 'employee.name'])
    wrapper.where('doctor.doctor_id', '=', 'employee.employee_id', 'field')
    wrapper.where('valid', '=', 1, 'int')
    wrapper.like('employee.name', doctor_name, 'str')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    doctor_info = [{'doctorName': result[1], 'doctorId': result[0]} for result in results]
    res = {'message': 'success', 'results': doctor_info}
    return res, 200


@app.route('/add-collaborator/get-nurse-info-arr', methods=['GET'])
def add_collaborator_get_nurse_info_arr():
    nurse_name = request.args.get('nurseName')
    wrapper = SQLWrapper(conn)
    wrapper.query(['nurse', 'employee'], ['nurse_id', 'employee.name'])
    wrapper.where('nurse.nurse_id', '=', 'employee.employee_id', 'field')
    wrapper.where('valid', '=', 1, 'int')
    wrapper.where('employee.name', 'like','%' + str(nurse_name) +'%', 'str')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    nurse_info = [{'nurseName': result[1], 'nurseId': result[0]} for result in results]
    res = {'message': 'success', 'results': nurse_info}
    return res, 200


@app.route('/add-collaborator/get-helping-staff-info-arr', methods=['GET'])
def add_collaborator_get_helping_staff_info_arr():
    _name = request.args.get('helpingStaffName')
    wrapper = SQLWrapper(conn)
    wrapper.query(['helping_staff', 'employee'], ['name', 'helping_staff_id'])
    wrapper.like('name', f'%{_name}%', 'str')
    wrapper.run()
    res = wrapper.get()
    result = {'message': 'success', 'results': []}
    for t in res:
        result['results'].append({
            'helpingStaffName': t[0],
            'helpingStaffId': t[1],
        })
    return result, 200


@app.route('/get-employee-name-by-id', methods=['GET'])
def get_employee_name_by_id():
    role = request.args.get('userType')
    _id = None
    if role == 'doctor':
        _id = request.args.get('doctorId')
    elif role == 'nurse':
        _id = request.args.get('nurseId')
    elif role == 'helpingStaff':
        _id = request.args.get('helpingStaffId')

    if role is not None:
        wrapper = SQLWrapper(conn)
        wrapper.query(['employee'], ['name'])
        wrapper.where('employee_id', '=', _id, 'str')
        wrapper.run(limit=1)
        res = wrapper.get()
        if res:
            _name = res[0][0]
            return {'message': 'success', 'results': _name}, 200
        else:
            return {'message': 'failed', 'results': 'employee not found!'}, 400
    else:
        return {'message': 'failed', 'results': 'Please provide id!'}, 400


@app.route('/get-doctor-rehabilitation', methods=['GET'])
def get_doctor_rehabilitation():
    info = dict(request.args)
    logic = ('isSearchingPatientInfo' not in info.keys())  # 不同界面的调用逻辑
    rehabilitationinfo = []
    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitation'],
                  [])
    code = wrapper.run()

    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        rehabilitation = wrapper.get()
        rehabilitation_pid_did_pname_dname = {}
        for i in range(len(rehabilitation)):
            rehabilitationinfo.append([])
            for item in rehabilitation[i]:
                rehabilitationinfo[i].append(item)
            if rehabilitation[i][1] not in rehabilitation_pid_did_pname_dname.keys():
                wrapper.clear()
                wrapper.query(['consultation'],
                              ['doctor_id', 'patient_id'])
                wrapper.where('consultation_id', '=', str(rehabilitation[i][1]), 'int')
                code = wrapper.run()

                if code != 0:
                    ret = {'message': f'database error {code}', 'results': {}}
                    return ret, 400

                consultation = wrapper.get()
                if wrapper.get():
                    for item in consultation[0]:
                        rehabilitationinfo[i].append(item)
                did = rehabilitationinfo[i][7]
                pid = rehabilitationinfo[i][8]
                patient_name = get_patient_name(pid, conn)
                doctor_name = get_doctor_name(did, conn)
                rehabilitation_pid_did_pname_dname[rehabilitation[i][1]] = []
                rehabilitation_pid_did_pname_dname[rehabilitation[i][1]].append(did)
                rehabilitation_pid_did_pname_dname[rehabilitation[i][1]].append(pid)
                rehabilitation_pid_did_pname_dname[rehabilitation[i][1]].append(patient_name)
                rehabilitation_pid_did_pname_dname[rehabilitation[i][1]].append(doctor_name)
        lst = []
        for i in range(len(rehabilitationinfo)):
            did = rehabilitation_pid_did_pname_dname[rehabilitation[i][1]][0]
            pid = rehabilitation_pid_did_pname_dname[rehabilitation[i][1]][1]
            patient_name = rehabilitation_pid_did_pname_dname[rehabilitation[i][1]][2]
            doctor_name = rehabilitation_pid_did_pname_dname[rehabilitation[i][1]][3]
            if not(logic and rehabilitationinfo[i][6] != 0):
                if ((not info['rehabilitationId']) or str(rehabilitationinfo[i][1]) == info['rehabilitationId']) and \
                   ((not info['rehabilitationName']) or str(rehabilitationinfo[i][2]) == info['rehabilitationName']) and \
                   ((not info['patientName']) or str(patient_name) == info['patientName']) and \
                   ((not info['patientId']) or str(pid) == info['patientId']) and \
                   ((not info['beginTime1']) or str(rehabilitationinfo[i][3]) >= info['beginTime1']) and \
                   ((not info['endTime1']) or str(rehabilitationinfo[i][4]) <= info['endTime1']) and \
                   ((not info['consultationId']) or str(rehabilitationinfo[i][0]) == info['consultationId']):
                    lst.append({
                        'rehabilitationId': str(rehabilitationinfo[i][0]),
                        'consultationId': str(rehabilitationinfo[i][1]),
                        'rehabilitationName': str(rehabilitationinfo[i][2]),
                        'beginTime': convert_time(rehabilitationinfo[i][3]),
                        'endTime': convert_time(rehabilitationinfo[i][4]),
                        'patientId': str(pid),
                        'patientName': str(patient_name),
                        'doctorId': str(did),
                        'doctorName': str(doctor_name),
                        'hasBegin': 'true' if rehabilitationinfo[i][6] == 1 else 'false',
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }


@app.route('/doctor/cancel-rehabilitation', methods=['POST'])
def doctor_cancel_rehabilitation():
    info = dict(request.json)
    rID = info['rehabilitationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['rehabilitation'], ['charge_id'])
    wrapper.where('rehabilitation_id', '=', rID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]

    delete = f'''DELETE FROM rehabilitation WHERE rehabilitation_id = {rID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/doctor/rehabilitation/begin', methods=['POST'])
def doctor_rehabilitation_conduct():
    info = dict(request.json)
    rID = info['rehabilitationId']
    rehabilitation_time = info['rehabilitationTime']
    rehabilitation_time = datetime.strptime(rehabilitation_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE rehabilitation SET begin_date_time = '{rehabilitation_time}' WHERE rehabilitation_id = {rID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/doctor/rehabilitation/end', methods=['POST'])
def doctor_rehabilitation_record():
    info = dict(request.json)
    rID = info['rehabilitationId']
    end_time = info['endTime']
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)

    doctor_arr = info['doctorRoughArr']
    for doctor_info in doctor_arr:
        insert = f'''INSERT INTO rehabilitation_doctor(rehabilitation_id, doctor_id)
                    VALUES ({rID}, '{doctor_info['doctorId']}')'''
        wrapper.execute_raw(insert, commit=False)

    nurse_arr = info['nurseRoughArr']
    for nurse_info in nurse_arr:
        insert = f'''INSERT INTO rehabilitation_nurse(rehabilitation_id, nurse_id)
                    VALUES ({rID}, '{nurse_info['nurseId']}')'''
        wrapper.execute_raw(insert, commit=False)

    helping_staff_arr = info['helpingStaffRoughArr']
    for helping_staff_info in helping_staff_arr:
        insert = f'''INSERT INTO rehabilitation_helping_staff(rehabilitation_id, helping_staff_id)
                    VALUES ({rID}, '{helping_staff_info['helpingStaffId']}')'''
        wrapper.execute_raw(insert, commit=False)

    update = f'''UPDATE rehabilitation SET end_date_time = '{end_time}'
                WHERE rehabilitation_id = {rID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/get-doctor-surgery', methods=['GET'])
def get_doctor_surgery():
    info = dict(request.args)
    logic = ('isSearchingPatientInfo' not in info.keys())  # 不同界面的调用逻辑
    surgeryinfo = []
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery'],
                  [])
    code = wrapper.run()

    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    if wrapper.get():
        surgery = wrapper.get()
        surgery_did_pid_dname_pname = {}
        for i in range(len(surgery)):
            surgeryinfo.append([])
            for item in surgery[i]:
                surgeryinfo[i].append(item)
            wrapper.clear()
            if surgery[i][1] not in surgery_did_pid_dname_pname.keys():
                wrapper.query(['consultation'],
                              ['doctor_id', 'patient_id'])
                wrapper.where('consultation_id', '=', str(surgery[i][1]), 'int')
                code = wrapper.run()

                if code != 0:
                    ret = {'message': f'database error {code}', 'results': {}}
                    return ret, 400

                consultation = wrapper.get()
                if wrapper.get():
                    for item in consultation[0]:
                        surgeryinfo[i].append(item)
                did = surgeryinfo[i][12]
                pid = surgeryinfo[i][13]
                patient_name = get_patient_name(pid, conn)
                doctor_name = get_doctor_name(did, conn)

                surgery_did_pid_dname_pname[surgery[i][1]] = []
                surgery_did_pid_dname_pname[surgery[i][1]].append(did)
                surgery_did_pid_dname_pname[surgery[i][1]].append(pid)
                surgery_did_pid_dname_pname[surgery[i][1]].append(doctor_name)
                surgery_did_pid_dname_pname[surgery[i][1]].append(patient_name)
        lst = []
        for i in range(len(surgeryinfo)):
            if not(logic and surgeryinfo[i][11]):
                did = surgery_did_pid_dname_pname[surgery[i][1]][0]
                pid = surgery_did_pid_dname_pname[surgery[i][1]][1]
                doctor_name = surgery_did_pid_dname_pname[surgery[i][1]][2]
                patient_name = surgery_did_pid_dname_pname[surgery[i][1]][3]
                if ((not info['surgeryId']) or str(surgeryinfo[i][1]) == info['surgeryId']) and \
                    ((not info['consultationId']) or str(surgeryinfo[i][0]) == info['consultationId']) and \
                    ((not info['surgerySite']) or str(surgeryinfo[i][6]) == info['surgerySite']) and \
                    ((not info['surgeryName']) or str(surgeryinfo[i][4]) == info['surgeryName']) and \
                    ((not info['patientId']) or pid == info['patientId']) and \
                    ((not info['patientName']) or patient_name == info['patientName']) and \
                    ((not info['beginTime1']) or str(surgeryinfo[i][8]) >= info['beginTime1']) and \
                    ((not info['endTime1']) or str(surgeryinfo[i][9]) <= info['endTime1']):
                    lst.append({
                        'surgeryId': str(surgeryinfo[i][0]),
                        'consultationId': str(surgeryinfo[i][1]),
                        'surgeryName': str(surgeryinfo[i][4]),
                        'surgerySite': str(surgeryinfo[i][6]),
                        'surgeryType': str(surgeryinfo[i][7]),
                        'beginTime': convert_time(surgeryinfo[i][8]),
                        'endTime': convert_time(surgeryinfo[i][9]),
                        'patientId': str(pid),
                        'patientName': str(patient_name),
                        'doctorId': str(did),
                        'doctorName': str(doctor_name),
                        'hasBegin': 'true' if surgeryinfo[i][11] == 1 else 'false',
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }


@app.route('/doctor/cancel-surgery', methods=['POST'])
def doctor_cancel_surgery():
    info = dict(request.json)
    sID = info['surgeryId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery'], ['charge_id'])
    wrapper.where('surgery_id', '=', sID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]

    delete = f'''DELETE FROM surgery WHERE surgery_id = {sID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/surgery/begin', methods=['POST'])
def doctor_surgery_conduct():
    info = dict(request.json)
    sID = info['surgeryId']
    surgery_time = info['surgeryTime']
    surgery_time = datetime.strptime(surgery_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE surgery SET begin_date_time = '{surgery_time}' WHERE surgery_id = {sID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/doctor/surgery/get-surgery-record-rough', methods=['GET'])
def doctor_surgery_get_surgery_record_rough():
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery_related_record'], ['record_id', 'record_date_time'])
    wrapper.where('surgery_id', '=', request.args.get('surgeryId'), 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()
    if not res:
        return {'message': 'failed', 'results': 'surgery not found!'}, 400
    res = res[0]
    return {
        'message': 'success',
        'results': {
            'recordId': res[0],
            'recordTime': convert_time(res[1]),
        }
    }, 200



@app.route('/doctor/surgery/end', methods=['POST'])
def doctor_surgery_end():
    info = dict(request.json)
    sID = info['surgeryId']
    end_time = info['endTime']
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)

    doctor_arr = info['doctorRoughArr']
    for doctor_info in doctor_arr:
        insert = f'''INSERT INTO surgery_doctor(surgery_id, doctor_id)
                    VALUES ({sID}, '{doctor_info['doctorId']}')'''
        wrapper.execute_raw(insert, commit=False)

    nurse_arr = info['nurseRoughArr']
    for nurse_info in nurse_arr:
        insert = f'''INSERT INTO surgery_nurse(surgery_id, nurse_id)
                    VALUES ({sID}, '{nurse_info['nurseId']}')'''
        wrapper.execute_raw(insert, commit=False)

    helping_staff_arr = info['helpingStaffRoughArr']
    for helping_staff_info in helping_staff_arr:
        insert = f'''INSERT INTO surgery_helping_staff(surgery_id, helping_staff_id)
                    VALUES ({sID}, '{helping_staff_info['helpingStaffId']}')'''
        wrapper.execute_raw(insert, commit=False)

    update = f'''UPDATE surgery SET end_date_time = '{end_time}'
                WHERE surgery_id = {sID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/doctor/surgery/record', methods=['POST'])
def doctor_surgery_record():
    info = dict(request.json)
    sID = info['surgeryId']
    record_detail = info['recordDetail']
    record_time = info['recordTime']
    record_time = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)

    insert = f'''INSERT INTO surgery_related_record (surgery_id, record_date_time, record_detail)
                VALUES ({sID}, '{record_time}', '{record_detail}')'''
    wrapper.execute_raw(insert)

    query = 'SELECT LAST_INSERT_ID();'
    wrapper.execute_raw(query)
    record_id = wrapper.get()[0][0]
    return {'message': 'success',
            'results': {
                'recordId': str(record_id),
            }}, 200


@app.route('/get-doctor-hospitalization', methods=['GET'])
def get_doctor_hospitalization():
    info = dict(request.args)
    logic = ('isSearchingPatientInfo' not in info.keys())  # 不同界面的调用逻辑
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization', 'hospitalization_record'],
                  [])
    code = wrapper.run()

    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    if wrapper.get():
        hospitalizationinfo = wrapper.get()
        lst = []
        p_d_name = {}
        for i in range(len(hospitalizationinfo)):
            if not(logic and hospitalizationinfo[i][1] != 0):
                did = hospitalizationinfo[i][3]
                pid = hospitalizationinfo[i][2]
                if pid not in p_d_name.keys():
                    patient_name = get_patient_name(pid, conn)
                    p_d_name[pid] = patient_name
                else:
                    patient_name = p_d_name[pid]
                if did not in p_d_name.keys():
                    doctor_name = get_doctor_name(did, conn)
                    p_d_name[did] = doctor_name
                else:
                    doctor_name = p_d_name[did]
                if ((not info['hospitalizationId']) or str(hospitalizationinfo[i][1]) == info['hospitalizationId']) and \
                   ((not info['patientId']) or str(pid) == info['patientId']) and \
                   ((not info['patientName']) or str(patient_name) == info['patientName']) and \
                   ((not info['beginHospitalizationTime']) or str(hospitalizationinfo[i][4]) >= info['beginHospitalizationTime']) and \
                   ((not info['endHospitalizationTime']) or str(hospitalizationinfo[i][4]) <= info['endHospitalizationTime']) and \
                   ((not info['beginDischargeTime']) or str(hospitalizationinfo[i][6]) >= info['beginDischargeTime']) and \
                   ((not info['endDischargeTime']) or str(hospitalizationinfo[i][6]) <= info['endDischargeTime']) and \
                   ((not info['consultationId']) or str(hospitalizationinfo[i][11]) == info['consultationId']):
                    lst.append({
                        'hospitalizationId': str(hospitalizationinfo[i][0]),
                        'consultationId': str(hospitalizationinfo[i][11]),
                        'hospitalizationTime': convert_time(hospitalizationinfo[i][4]),
                        'roomId': str(hospitalizationinfo[i][8]),
                        'bedNumber': str(hospitalizationinfo[i][9]),
                        'dischargeTime': convert_time(hospitalizationinfo[i][6]),
                        'patientId': str(pid),
                        'patientName': str(patient_name),
                        'doctorId': str(did),
                        'doctorName': str(doctor_name),
                        'hasBegin': 'true' if hospitalizationinfo[i][1] == 1 else 'false',
                    })
        return {
            'message': 'success',
            'results': lst,
        }, 200
    else:
        return {
            'message': 'failed',
            'results': 'Consultation not found.'
        }



@app.route('/doctor/cancel-hospitalization', methods=['POST'])
def doctor_cancel_hospitalization():
    info = dict(request.json)
    hID = info['hospitalizationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization'], ['charge_id'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    charge_id = wrapper.get()[0][0]

    delete = f'''DELETE FROM hospitalization_record WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM hospitalization WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(delete, False)
    delete = f'''DELETE FROM charge WHERE charge_id = {charge_id}'''
    wrapper.execute_raw(delete)
    return {'message': 'success'}, 200


@app.route('/doctor/hospitalization/get-hospitalization-record-rough', methods=['GET'])
def doctor_surgery_get_hospitalization_record_rough():
    hID = request.args.get('hospitalizationId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization_record', 'consultation', 'employee'], ['consultation.consultation_id', 'employee.name'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    wrapper.where('hospitalization_record.consultation_id', '=', 'consultation.consultation_id', 'field')
    wrapper.where('employee.employee_id', '=', 'consultation.doctor_id', 'field')
    wrapper.where('valid', '=', 1, 'int')
    code = wrapper.run(join_method='')
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    results = wrapper.get()
    res = [{'consultationId': result[0], 'doctorName': result[1]} for result in results]
    return {'message': 'success', 'results': res}, 200


@app.route('/doctor/hospitalization/begin', methods=['POST'])
def doctor_hospitalization_begin():
    info = dict(request.json)
    hID = info['hospitalizationId']
    hospitalization_time = info['hospitalizationTime']
    hospitalization_time = datetime.strptime(hospitalization_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)
    update = f'''UPDATE hospitalization SET hospitalization_date_time = '{hospitalization_time}' 
                WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200


@app.route('/doctor/hospitalization/record', methods=['POST'])
def doctor_hospitalization_record():
    info = dict(request.json)
    hID = info['hospitalizationId']
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization_record', 'consultation'], ['doctor_id', 'patient_id'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    doctor_id = wrapper.get()[0][0]
    patient_id = wrapper.get()[0][1]
    insert = f'''INSERT INTO charge (patient_id, cost, is_completed, tag)
                    VALUE ('{patient_id}', 100, 'NO', 1)'''
    wrapper.execute_raw(insert)

    query = 'SELECT LAST_INSERT_ID();'
    wrapper.execute_raw(query)
    charge_id = wrapper.get()[0][0]
    insert = f'''INSERT INTO consultation (doctor_id, patient_id, charge_id)
                    VALUE ('{doctor_id}', '{patient_id}', {charge_id});'''
    wrapper.execute_raw(insert)
    wrapper.execute_raw(query)
    cID = wrapper.get()[0][0]

    return {'message': 'success', 'results': {'consultationId': cID}}, 200


@app.route('/doctor/hospitalization/end', methods=['POST'])
def doctor_hospitalization_end():
    info = dict(request.json)
    hID = info['hospitalizationId']
    reason = info['dischargeReason']
    end_time = info['dischargeTime']
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
    wrapper = SQLWrapper(conn)

    update = f'''UPDATE hospitalization SET discharge_date_time = '{end_time}', discharge_reason = '{reason}'
                WHERE hospitalization_id = {hID}'''
    wrapper.execute_raw(update)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/edit-doctor-info', methods=['POST'])
def edit_doctor_info():
    info = dict(request.json)

    for k in list(info.keys()):
        if not info[k]:
            info[k] = None
        info[dict(employee_fields, **doctor_fields)[k]] = info.pop(k)

    err = check_doctor_info(info)
    if err:
        response = {
            'message': 'failed',
            'results': {
                'notice': f'The {err} form is not filled correctly.',
                'invalidFormField': [err],
            }
        }
        return response, 400

    wrapper = SQLWrapper(conn)
    code = wrapper.update('doctor JOIN employee',
                          {
                              'doctor_id': info['doctor_id'],
                              'employee_id': info['doctor_id'],
                          }, info)

    if code != 0:
        response = {
            'message': 'failed',
            'results': {
                'notice': 'Database error!',
                'invalidFormField': ['database'],
            }
        }
        return response, 400
    return {'message': 'success'}, 200


@app.route('/caregiver/permission', methods=['GET'])
def caregiver_permission():
    utype = request.args.get('userType')
    uid = request.args.get('userId')
    if utype == 'nurse':
        wrapper = SQLWrapper(conn)
        wrapper.query(['nurse', 'room'], ['room_type'])
        wrapper.where('nurse_id', '=', uid, 'str')
        wrapper.run()
        res = wrapper.get()
        ret = {
            'inExaminationRoom': 'false',
            'inRehabilitationRoom': 'false',
            'inSurgeryRoom': 'false',
            'inHospitalizationRoom': 'false',
        }
        for t in res:
            _type = t[0]
            if _type == 'examination':
                ret['inExaminationRoom'] = 'true'
            elif _type == 'rehabilitation':
                ret['inRehabilitationRoom'] = 'true'
            elif _type == 'surgery':
                ret['inSurgeryRoom'] = 'true'
            elif _type == 'VIP' or _type == 'normal':
                ret['inHospitalizationRoom'] = 'true'
        return {'message': 'success', 'results': ret}, 200

    elif utype == 'helpingStaff':
        wrapper = SQLWrapper(conn)
        wrapper.query(['helping_staff', 'room'], ['room_type'])
        wrapper.where('helping_staff_id', '=', uid, 'str')
        wrapper.run()
        res = wrapper.get()
        ret = {
            'inExaminationRoom': 'false',
            'inRehabilitationRoom': 'false',
            'inSurgeryRoom': 'false',
            'inHospitalizationRoom': 'false',
        }
        for t in res:
            _type = t[0]
            if _type == 'examination':
                ret['inExaminationRoom'] = 'true'
            elif _type == 'rehabilitation':
                ret['inRehabilitationRoom'] = 'true'
            elif _type == 'surgery':
                ret['inSurgeryRoom'] = 'true'
            elif _type == 'VIP' or _type == 'normal':
                ret['inHospitalizationRoom'] = 'true'
        return {'message': 'success', 'results': ret}, 200


@app.route('/caregiver/get-table-data', methods=['GET'])
def caregiver_get_table_data():
    info = {
        'id': request.args.get('userId'),
        'name': request.args.get('itemName'),
        'begin_time1': request.args.get('beginTime1'),
        'begin_time2': request.args.get('beginTime2'),
        'end_time1': request.args.get('endTime1'),
        'end_time2': request.args.get('endTime2'),
        'patient_id': request.args.get('patientId'),
        'patient_name': request.args.get('patientName'),
        'is_history': request.args.get('isHistory'),
    }
    _type = request.args.get('itemType')
    res = eval('nurse_get_' + _type.lower() + '_data')(conn, info)
    return {'message': 'success', 'results': res}


@app.route('/get-room-detailed', methods=['GET'])
def get_room_detailed():
    _id = request.args.get('roomId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['room'], ['room_type', 'number_of_beds'])
    wrapper.where('room_id', '=', _id, 'str')
    wrapper.run(limit=1)
    res = wrapper.get()
    if not res:
        return {'message': 'failed', 'results': 'room not found!'}, 400
    res = res[0]
    return {
        'message': 'success',
        'results': {
            'roomId': _id,
            'roomType': res[0],
            'numberOfBeds': res[1],
            'description': '',
            'location': '',
        }
    }, 200


@app.route('/doctor/get-surgery-description', methods=['GET'])
def doctor_get_surgery_description():
    sID = request.args.get('surgeryId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['surgery'], ['surgery_description'])
    wrapper.where('surgery_id', '=', sID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0][0]
    return {'message': 'success', 'results': res}, 200

    return {'message': 'success', 'results': long_sentence}, 200


@app.route('/doctor/get-hospitalization-reason', methods=['GET'])
def doctor_get_hospitalization_reason():
    hID = request.args.get('hospitalizationId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['hospitalization'], ['hospitalization_reason'])
    wrapper.where('hospitalization_id', '=', hID, 'int')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400
    res = wrapper.get()[0][0]
    return {'message': 'success', 'results': res}, 200
    # return {'message': 'success', 'results': long_sentence}, 200


@app.route('/get-nurse-info', methods=['GET'])
def get_nurse_info():
    _id = request.args.get('nurseId')
    wrapper = SQLWrapper(conn)
    wrapper.query(['employee', 'nurse'], [])
    wrapper.where('employee_id', '=', _id, 'str')
    wrapper.where('employee.employee_id', '=', 'nurse.nurse_id', 'field')
    wrapper.where('valid', '=', '1', 'int')
    wrapper.run(limit=1, join_method='')
    res = wrapper.get()
    if not res:
        return {'message': 'failed', 'results': 'nurse not found!'}, 400
    res = res[0]
    super_id = res[9]
    super_name = None
    if super_id is not None:
        wrapper.clear()
        wrapper.query(['employee'], ['name'])
        wrapper.where('employee', '=', super_id, 'str')
        wrapper.run(limit=1)
        res = wrapper.get()
        if res:
            super_name = res[0][0]

    return {
        'message': 'success',
        'results': {
            'name': res[1],
            'gender': res[2],
            'position': res[3],
            'birthdate': convert_time(res[4], '%Y-%m-%d'),
            'phone': res[5],
            'address': res[6],
            'dateOfHire': convert_time(res[7], '%Y-%m-%d'),
            'dateOfDismiss': convert_time(res[8], '%Y-%m-%d'),
            'supervisorId': super_id,
            'supervisorName': super_name,
            'salary': res[10],
            'nurseId': _id,
            'roomId': res[13],
            'licenseNumber': res[14],
        }
    }, 200


@app.route('/get-helping-staff-info', methods=['GET'])
def get_helping_staff_info():  # 未完待续
    pID = request.args.get('helpingStaffId')
    wrapper = SQLWrapper(conn)

    wrapper.query(['employee'], [])
    wrapper.where('employee_id', '=', pID, 'str')
    code = wrapper.run(limit=1)
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    res_employee = wrapper.get()[0]

    ret = {}
    if res_employee:
        for idx, field in enumerate(employee_fields.keys()):
            ret[field] = str(res_employee[idx]) if res_employee[idx] is not None else ''
        ret = {'message': 'success', 'results': ret}
        return ret, 200
    else:
        ret = {'message': 'failed', 'results': 'The patient ID is invalid.'}
        return ret, 400


@app.route('/edit-nurse-info', methods=['POST'])
def edit_nurse_info():
    info = dict(request.json)
    for k in list(info.keys()):
        if not info[k]:
            info[k] = None
        info[dict(employee_fields, **nurse_fields)[k]] = info.pop(k)

    err = check_nurse_info(info)
    if err:
        response = {
            'message': 'failed',
            'results': {
                'notice': f'The {err} form is not filled correctly.',
                'invalidFormField': [err],
            }
        }
        return response, 400

    wrapper = SQLWrapper(conn)
    code = wrapper.update('nurse NATURAL JOIN employee',
                   {'nurse_id': info['nurse_id'],
                    'employee_id': info['nurse_id']}, info)
    if code != 0:
        response = {
            'message': 'failed',
            'results': {
                'notice': 'Database error!',
                'invalidFormField': ['database'],
            }
        }
    return {'message': 'success'}, 200


@app.route('/edit-helping-staff-info', methods=['POST'])
def edit_helping_staff_info():
    info = dict(request.json)
    for k in list(info.keys()):
        if not info[k]:
            info[k] = None
        info[dict(employee_fields)[k]] = info.pop(k)

    err = check_staff_info(info)
    if err:
        response = {
            'message': 'failed',
            'results': {
                'notice': f'The {err} form is not filled correctly.',
                'invalidFormField': [err],
            }
        }
        return response, 400

    wrapper = SQLWrapper(conn)
    code = wrapper.update('employee',
                   {'employee_id': info['employee_id'], 'helping_staff_id': info['helping_staff_id']}, info)

    if code != 0:
        response = {
            'message': 'failed',
            'results': {
                'notice': 'Database Error!',
                'invalidFormField': ['database'],
            }
        }
        return response, 400
    return {'message': 'success'}, 200


@app.route('/get-doctor-name-arr', methods=['GET'])
def get_doctor_name_arr():
    dname = request.args.get('name')
    rid = request.args.get('inquirerId')
    rtpye = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'],
                  ['name', 'employee_id'])
    wrapper.where('name', 'like', '%' + dname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pnames = wrapper.get()
        lis = []
        for item in pnames:
            if item[1][0] == 'd':
                lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-nurse-name-arr', methods=['GET'])
def get_nurse_name_arr():
    dname = request.args.get('name')
    rid = request.args.get('inquirerId')
    rtpye = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'],
                  ['name', 'employee_id'])
    wrapper.where('name', 'like', dname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pnames = wrapper.get()
        lis = []
        for item in pnames:
            if item[1][0] == 'n':
                lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-helping-staff-name-arr', methods=['GET'])
def get_helping_staff_name_arr():
    dname = request.args.get('name')
    rid = request.args.get('inquirerId')
    rtpye = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['employee'],
                  ['name', 'employee_id'])
    wrapper.where('name', 'like', dname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pnames = wrapper.get()
        lis = []
        for item in pnames:
            if item[1][0] == 'h':
                lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/get-medicine-name-arr', methods=['GET'])
def get_medicine_name_arr():
    mname = request.args.get('name')
    rid = request.args.get('inquirerId')
    rtype = request.args.get('inquirerType')

    wrapper = SQLWrapper(conn)
    wrapper.query(['medicine'],
                  ['name'])
    wrapper.where('patient_id', 'like', mname + '%', 'str')
    code = wrapper.run()
    if code != 0:
        ret = {'message': f'database error {code}', 'results': {}}
        return ret, 400

    if wrapper.get():
        pids = wrapper.get()
        lis = []
        for item in pids:
            lis.append(item[0])
        return {'message': 'success', 'results': lis}, 200

    return {'message': 'failed', 'results': []}, 200


@app.route('/admin/get-form-info', methods=['GET'])
def admin_get_form_info():
    role = request.args.get('itemName')
    form_type = request.args.get('formType')  # three types: 'add', 'edit', 'search'
    result = []

    if form_type == 'search':
        if role == 'patient':
            result = admin_patient_form
        elif role == 'doctor':
            result = admin_doctor_form
        elif role == 'nurse':
            result = admin_nurse_form
        elif role == 'helping-staff':
            result = admin_staff_form
        else:
            result = eval('admin_' + role + '_search_form')

        return {'message': 'success', 'results': result}, 200

    elif form_type == 'add':
        if role not in ['patient', 'doctor', 'nurse', 'helping-staff']:
            result = eval('admin_' + role + '_add_form')
            return {'message': 'success', 'results': result}, 200
    else:
        return {}, 400


@app.route('/admin/get-table-data', methods=['GET'])
def admin_get_table_data():
    role = request.args.get('itemName')
    if role == 'helping-staff':
        role = 'helping_staff'
    ret = []
    if role in ['patient', 'nurse', 'doctor', 'helping_staff']:
        info = {}
        for k, v in personnel_info.items():
            if request.args.get(v) is not None:
                info[k] = request.args.get(v)
        if role == 'patient':
            ret = admin_get_patient_data(conn, info)
        elif role == 'doctor':
            info['department'] = request.args.get('form[4][value]')
            ret = admin_get_employee_data(conn, info, role)
        elif role == 'nurse' or role == 'helping_staff':
            info['room_id'] = request.args.get('form[4][value]')
            ret = admin_get_employee_data(conn, info, role)

    else:
        info = eval(role + '_search_info')
        for k, v in info.items():
            if request.args.get(v) is not None:
                info[k] = request.args.get(v)
        ret = eval('admin_get_' + role + '_data(conn, info)')

    return {'message': 'success', 'results': ret}, 200



@app.route('/admin/get-table-column', methods=['GET'])
def admin_get_table_column():
    role = request.args.get('itemName')
    if role == 'helping-staff':
        role = 'helping_staff'
    res = eval(role + '_table_column')
    return {
        'message': 'success',
        'results': res
    }


@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    info = dict(request.json)
    kind = info['itemName']
    wrapper = SQLWrapper(conn)
    if kind == 'patient':
        wrapper.update('user', {'user_id': info['itemId']}, {'valid': 0})
        wrapper.update('patient', {f'{kind}_id': info['itemId']}, {'valid': 0})
    elif kind in ['doctor', 'nurse', 'helping_staff']:
        wrapper.update('user', {'user_id': info['itemId']}, {'valid': 0})
        wrapper.update('employee', {'employee_id': info['itemId']}, {'valid': 0})
    elif kind == 'medicine':
        wrapper.execute_raw('DELETE FROM medicine WHERE medicine_id = %s;', True, (info['itemId'],))
    elif kind == 'examination':
        wrapper.execute_raw('DELETE FROM examinations WHERE examination_id = %s;', True, (info['itemId'],))
    elif kind == 'rehabilitation':
        wrapper.execute_raw('DELETE FROM rehabilitations WHERE rehabilitation_id = %s;', True, (info['itemId'],))
    elif kind == 'surgery':
        wrapper.execute_raw('DELETE FROM surgeries WHERE surgery_id = %s;', True, (info['itemId'],))
    elif kind == 'department':
        wrapper.execute_raw('DELETE FROM departments WHERE name = %s;', True, (info['itemId'],))
    elif kind == 'room':
        wrapper.execute_raw('DELETE FROM room WHERE room_id = %s;', True, (info['itemId'],))
    else:
        return {'message': 'fail', 'results': 'No such table.'}, 400
    return {'message': 'success', 'results': {'onlyRemoveOneRecord': 'true'}}, 200


@app.route('/admin/add-or-edit', methods=['POST'])
def admin_add_or_edit():
    kind = request.json['itemName']
    form = request.json['form']     # used in eval()

    info = dict.fromkeys(eval(kind + '_add_info').keys())
    for k in info.keys():
        r = eval(eval(kind + '_add_info')[k])
        info[k] = r if r is not None else ''
    code = eval('admin_put_' + kind + '_data')(conn, info)

    if code == 0:
        return {'message': 'success'}, 200
    else:
        return {'message': 'Please check your input'}, 400


@app.route('/admin/can-add', methods=['GET'])
def admin_can_add():
    kind = request.args.get('itemName')
    if kind in ['patient', 'doctor', 'nurse', 'helping-staff']:
        return {'message': 'success', 'results': 'false'}, 200
    return {'message': 'success', 'results': 'true'}, 200


@app.route('/admin/get-registration-waiting-list', methods=['GET'])
def admin_registration():
    info = dict(request.args)
    if info['userType'] == 'helping staff':
        info['userType'] = 'helping_staff'
    wrapper = SQLWrapper(conn)

    if info['userType'] == 'patient':
        wrapper.query(['user', 'patient'], ['user_id', 'name', 'role', 'register_time'])
        wrapper.where('patient_id', '=', 'user_id', 'field')
    else:
        wrapper.query(['user', 'employee'], ['user_id', 'name', 'role', 'register_time'])
        wrapper.where('employee_id', '=', 'user_id', 'field')

    wrapper.where('valid', '=', '0', 'int')
    wrapper.where('role', '=', info['userType'], 'str')
    wrapper.where('register_time', '>=', info['beginTime'], 'str')
    wrapper.where('register_time', '<=', info['endTime'], 'str')
    wrapper.run()
    res = wrapper.get()
    ret = []
    tz = timezone('Asia/Shanghai')
    for r in res:
        ret.append({
            'userId': r[0],
            'userName': r[1],
            'userType': r[2],
            'registerTime': r[3].astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
        })
    return {'message': 'success', 'results': ret}, 200


@app.route('/admin/registration/allow', methods=['POST'])
def admin_registration_allow():
    uid = request.json['userId']
    wrapper = SQLWrapper(conn)
    wrapper.update('user', {'user_id': uid}, {'valid': 1})
    return {'message': 'success'}, 200


@app.route('/admin/registration/disallow', methods=['POST'])
def admin_registration_disallow():
    info = dict(request.json)
    uid = info['userId']
    role = info['userType']
    if role == 'helping staff':
        role = 'helping_staff'
    wrapper = SQLWrapper(conn)
    wrapper.execute_raw('SET FOREIGN_KEY_CHECKS = 0;', True)
    wrapper.execute_raw('DELETE FROM user WHERE user_id = %s;', False, (uid,))
    wrapper.execute_raw('DELETE FROM employee WHERE employee_id = %s;', False, (uid,))
    wrapper.execute_raw(f'DELETE FROM {role} WHERE {role}_id = %s;', False, (uid,))
    wrapper.execute_raw('SET FOREIGN_KEY_CHECKS = 1;', True)

    return {'message': 'success'}, 200


@app.route('/admin/clear-deleted-users', methods=['POST'])
def admin_clear_deleted_user():
    role = request.json['itemName']

    wrapper = SQLWrapper(conn)
    if role == 'patient':
        wrapper.execute_raw('DELETE FROM user WHERE valid = 0;', False)
        wrapper.execute_raw('DELETE FROM patient WHERE valid = 0;', False)
    elif role in ['doctor', 'nurse', 'helping-staff']:
        if role == 'helping-staff':
            role = 'helping_staff'

        wrapper.query(['user', 'employee'], ['employee_id'])
        wrapper.where('role', '=', role, 'str')
        wrapper.where('vaild', '=', '0', 'int')
        wrapper.run()
        res = wrapper.get()
        wrapper.execute_raw('SET FOREIGN_KEY_CHECKS = 0;', True)
        for r in res:
            _id = r[0]
            wrapper.execute_raw(f'DELETE FROM {role} WHERE {role}_id = %s;', False, (_id,))
        wrapper.execute_raw('DELETE FROM user WHERE valid = 0;', False)
        wrapper.execute_raw('DELETE FROM employee WHERE valid = 0;', False)
        wrapper.execute_raw('SET FOREIGN_KEY_CHECKS = 1', True)

    return {'message': 'success'}, 200

@app.route('/get-room-type-arr')
def get_room_type_arr():
    return {'message': 'success', 'results': ['VIP',
                                              'normal']}, 200


if __name__ == '__main__':
    createTable(conn)
    check_atomic(conn)
    # use "flask init-database" to initialize the database
    app.run('0.0.0.0', debug=True, port=5000)
    conn.close()
