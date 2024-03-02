import random
import fields
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS().init_app(app)  # allow CORS, so that the frontend can access the backend from a different domain


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/temp', methods=['GET'])
def temp():
    time.sleep(3)
    return {
        'message': f'success in loop {request.args.get("i")}',
    }


@app.route('/register-form-submit', methods=['POST'])
def register_form_submit():
    json = request.json
    print(json)
    response_correct = {
        'message': 'success',
        'results': {
            'userId': 114514,
        }
    }
    response_wrong = {
        'message': 'failed',
        'results': {
            'notice': 'The form is not filled correctly.',
            'invalidFormField': ['name', 'address'],
        }
    }
    # return jsonify(response_correct), 200
    return jsonify(response_wrong), 400


@app.route('/employee-supervisor-id-validate', methods=['GET'])
def validate_supervisor_id():
    form_name = request.args.get('formName')
    supervisor_id = request.args.get('supervisorId')
    print(form_name, supervisor_id)
    if supervisor_id == '123':
        print('hit')
        return {'message': ''}
    return {'message': 'The supervisor ID is invalid.'}


@app.route('/login', methods=['POST'])
def login():
    json = request.json
    print(json)
    if json['userId'] == 'p' or json['userId'] == 'patient':
        return {'message': 'success', 'results': {'userType': 'patient', 'userName': 'Phoebe'}}, 200
    elif json['userId'] == 'd' or json['userId'] == 'doctor':
        return {'message': 'success', 'results': {'userType': 'doctor', 'userName': 'Ross'}}, 200
    elif json['userId'] == 'n' or json['userId'] == 'nurse':
        return {'message': 'success', 'results': {'userType': 'nurse', 'userName': 'Monica'}}, 200
    elif json['userId'] == 'h' or json['userId'] == 'helpingStaff':
        return {'message': 'success', 'results': {'userType': 'helpingStaff', 'userName': 'Chandler'}}, 200  # R.I.P.
    elif json['userId'] == 'a' or json['userId'] == 'admin':
        return {'message': 'success', 'results': {'userType': 'admin', 'userName': 'Rachel'}}, 200
    return {'message': 'failed', 'results': 'The username or password is incorrect.'}, 400


@app.route('/get-patient-info', methods=['GET'])
def get_patient_info():
    return {
        'message': 'success',
        'results': {
            'patientId': '114514',
            'name': 'Phoebe',
            'gender': 'female',
            'birthdate': '2000-01-01',
            'martialStatus': 'single',
            'birthplace': 'USA',
            'nationality': '',
            'identificationDocumentType': 'ID',
            'identificationNumber': '1234567890',
            'phone': '1234567890',
            'address': 'Manhattan',
            'bloodType': 'A',
            'allergens': ['Pollen', 'Dust Mites', 'Pet Dander', 'Mold', 'Food', 'Insect Stings', 'Medications', ],
            'initialDiagnosisDate': '2020-01-01',
            'emergencyContact': 'Monica',
            'emergencyContactRelationship': 'friend',
            'emergencyContactPhone': '1234567890',
            'emergencyContactAddress': 'Manhattan',
            'occupation': 'massage therapist',
        }
    }, 200


@app.route('/edit-patient-info', methods=['POST'])
def edit_patient_info():
    json = request.json
    print(json)
    response_correct = {
        'message': 'success',
    }
    response_wrong = {
        'message': 'failed',
        'results': {
            'notice': 'The form is not filled correctly.',
            'invalidFormField': ['name', 'address'],
        }
    }
    # return jsonify(response_correct), 200
    return jsonify(response_wrong), 400


@app.route('/edit-password', methods=['POST'])
def edit_password():
    print(request.json)
    # return {'message': 'success'}, 200
    return {
        'message': 'failed',
        'results': 'Why failed?',
    }, 400


@app.route('/get-patient-consultation', methods=['GET'])
def get_patient_consultation():
    print([request.args.get('patientId'),
           request.args.get('isHistory'),
           request.args.getlist('doctorName[]'),
           request.args.getlist('department[]'),
           request.args.get('startTime'),
           request.args.get('endTime'),
           request.args.get('consultationId')])
    lst = []
    time.sleep(0.5)
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'time': fields.DatetimeField().random_data_generator(),
            'department': 'Cardiology',
            'doctorName': 'Ross',
            'consultationId': 'c' + str(i),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/get-patient-consultation/doctorName', methods=['GET'])
def get_patient_consultation_doctor_name():
    patient_id = request.args.get('patientId')
    doctor_name = request.args.get('doctorName')
    is_history = request.args.get('isHistory')
    print(patient_id, doctor_name, is_history)
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-patient-consultation/department', methods=['GET'])
def get_patient_consultation_department():
    result = {'message': 'success', 'results': []}
    ans = ['Cardiology', 'Dermatology', 'Endocrinology', 'Gastroenterology', 'Geriatric Medicine',
           'Hematology', 'a', 'b', 'c', 'd']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


long_sentence = 'In the beginning God created the heavens and the earth. Now the earth was formless and empty, ' \
                'darkness was over the surface of the deep, and the Spirit of God was hovering over the waters. ' \
                'And God said, "Let there be light," and there was light. God saw that the light was good, ' \
                'and he separated the light from the darkness. God called the light "day," and the darkness he ' \
                'called "night." And there was evening, and there was morning—the first day.'


@app.route('/get-consultation-detailed', methods=['GET'])
def get_consultation_detailed():
    return {
        'message': 'success',
        'results': {
            'consultationId': request.args.get('consultationId'),
            'patientId': '213123',
            'patientName': 'Phoebe',
            'doctorRough': {'doctorId': '123', 'doctorName': 'Ross'},
            'time': '2002-01-01 11:00:11',
            'selfReport': long_sentence,
            'medicalHistory': long_sentence,
            'medicationHistory': long_sentence,
            'medicalAdvice': long_sentence,
            'prescriptionRoughArr': [{'prescriptionId': 'p114'}, {'prescriptionId': 'p514'}],
            'examinationRoughArr': [{'examinationId': 'e4565', 'examinationName': 'Be your personal best'},
                                    {'examinationId': 'e4325', 'examinationName': 'But center around life'}],
            'rehabilitationRoughArr': [{'rehabilitationId': 'e4565', 'rehabilitationName': 'Be your personal best'},
                                       {'rehabilitationId': 'e4325', 'rehabilitationName': 'But center around life'}],
            'surgeryRoughArr': [{'surgeryId': 's4565', 'surgeryName': 'Hair transplant'}],
            'hospitalizationRoughArr': [{'hospitalizationId': 'h4565', 'doctorName': 'Ross'}],
            'chargeId': '456',
        }
    }, 200


@app.route('/get-rehabilitation-detailed', methods=['GET'])
def get_rehabilitation_detailed():
    return {
        'message': 'success',
        'results': {
            'rehabilitationId': request.args.get('rehabilitationId'),
            'consultationRough': {'consultationId': '12345', 'doctorName': 'Ross'},
            'beginTime': '2002-01-01 11:00:11',
            'endTime': '2002-01-01 11:00:11',
            'chargeId': '456',
            'rehabilitationName': 'Be your personal best',
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'doctorRoughArr': [{'doctorId': '123', 'doctorName': 'Ross'},
                               {'doctorId': '456', 'doctorName': 'Joey'}],
            'nurseRoughArr': [{'nurseId': 'n123', 'nurseName': 'Ben'},
                              {'nurseId': 'n456', 'nurseName': 'Emma'},
                              {'nurseId': 'n456', 'nurseName': 'Emma'}],
            'helpingStaffRoughArr': []
        }
    }, 200


@app.route('/get-examination-detailed', methods=['GET'])
def get_examination_detailed():
    return {
        'message': 'success',
        'results': {
            'examinationId': request.args.get('examinationId'),
            'consultationRough': {'consultationId': '54321', 'doctorName': 'Xi'},
            'timeOfExamination': '2002-01-01 11:00:11',
            'timeOfResult': '2002-01-01 11:00:11',
            'examinationName': 'Hello world',
            'result': long_sentence,
            'chargeId': '510080',
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'doctorRoughArr': [{'doctorId': 'e123', 'doctorName': 'Ross'},
                               {'doctorId': 'e456', 'doctorName': 'Joey'}],
            'nurseRoughArr': [{'nurseId': 'en123', 'nurseName': 'Ben'},
                              {'nurseId': 'en456', 'nurseName': 'Emma'},
                              {'nurseId': 'en456', 'nurseName': 'Emma'}],
            'helpingStaffRoughArr': []
        }
    }, 200


@app.route('/get-prescription-detailed', methods=['GET'])
def get_prescription_detailed():
    medicine_arr = []
    for i in range(int(random.random() * 10)):
        medicine_arr.append({
            'medicineId': 'm' + str(i),
            'medicineName': 'medicine' + str(i),
            'quantity': 'quantity' + str(i),
        })
    return {
        'message': 'success',
        'results': {
            'prescriptionId': request.args.get('prescriptionId'),
            'consultationRough': {'consultationId': '5201314', 'doctorName': 'Xi'},
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'doctorRough': {'doctorId': 'e123', 'doctorName': 'Ross'},
            'pharmacyWindow': '1',
            'pharmacyPickupTime': '2002-01-01 11:41:11',
            'prescriptionMedicineRoughArr': medicine_arr,
            'chargeId': '123456852',
        }
    }, 200


@app.route('/get-surgery-detailed', methods=['GET'])
def get_surgery_detailed():
    record_arr = []
    for i in range(int(random.random() * 10)):
        record_arr.append({
            'recordId': 'r' + str(i),
            'recordTime': '2002-01-01 11:00:11',
        })
    return {
        'message': 'success',
        'results': {
            'surgeryId': request.args.get('surgeryId'),
            'consultationRough': {'consultationId': '5201314', 'doctorName': 'Xi'},
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'doctorRough': {'doctorId': 'e123', 'doctorName': 'Ross'},
            'surgeryName': 'chick',
            'surgeryDescription': long_sentence,
            'surgerySite': 'wing',
            'surgeryType': 'elective',
            'beginTime': '2002-01-01 11:00:11',
            'endTime': '2002-01-01 11:22:11',
            'chargeId': 'c1234',
            'doctorRoughArr': [{'doctorId': 'e123', 'doctorName': 'Ross'},
                               {'doctorId': 'e456', 'doctorName': 'Joey'}],
            'nurseRoughArr': [{'nurseId': 'en123', 'nurseName': 'Ben'},
                              {'nurseId': 'en456', 'nurseName': 'Emma'},
                              {'nurseId': 'en456', 'nurseName': 'Emma'}],
            'helpingStaffRoughArr': [{'helpingStaffId': 'n123', 'helpingStaffName': 'Ben'},
                                     {'helpingStaffId': 'n456', 'helpingStaffName': 'Emma'},
                                     {'helpingStaffId': 'n456', 'helpingStaffName': 'Emma'}],
            'recordRoughArr': record_arr
        }
    }


@app.route('/patient/cancel-consultation', methods=['POST'])
def cancel_consultation():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-prescription-medicine-detailed', methods=['GET'])
def get_prescription_medicine_detailed():
    return {
        'message': 'success',
        'results': {
            'prescriptionId': request.args.get('prescriptionId'),
            'medicineId': request.args.get('medicineId'),
            'medicineName': 'medicine',
            'medicineManufacturer': 'manufacturer',
            'courseOfMedication': '1',
            'dosage': '1',
            'frequency': '1',
            'cost': '500',
            'quantity': 'qq',
        }
    }, 200


@app.route('/get-surgery-record-detailed', methods=['GET'])
def get_surgery_record_detailed():
    return {
        'message': 'success',
        'results': {
            'surgeryId': request.args.get('surgeryId'),
            'recordId': request.args.get('recordId'),
            'recordDate': '2002-01-01',
            'recordTime': '11:00:11',
            'recordDetail': long_sentence,
        }
    }


@app.route('/get-charge-detailed', methods=['GET'])
def get_charge_detailed():
    is_completed = 'true' if random.random() > 0.5 else 'false'
    res = {
        'message': 'success',
        'results': {
            'chargeId': request.args.get('chargeId'),
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'cost': '100',
            'isCompleted': is_completed,  # must be string 'true' or 'false'
            'chargeTime': '2002-01-01 11:00:11',
            'paymentMethod': 'cash',
            'prescriptionRough': {'prescriptionId': ''},
            'examinationRough': {'examinationId': '', 'examinationName': ''},
            'rehabilitationRough': {'rehabilitationId': '', 'rehabilitationName': ''},
            'surgeryRough': {'surgeryId': '', 'surgeryName': ''},
            'consultationRough': {'consultationId': '', 'doctorName': ''},
            'hospitalizationRough': {'hospitalizationId': '', 'doctorName': ''},
        }
    }
    temp = random.randint(0, 5)
    if temp == 0:
        res['results']['prescriptionRough'] = {'prescriptionId': 'p114'}
    elif temp == 1:
        res['results']['examinationRough'] = {'examinationId': 'e4565', 'examinationName': 'Be your personal best'}
    elif temp == 2:
        res['results']['rehabilitationRough'] = {'rehabilitationId': 'e4565',
                                                 'rehabilitationName': 'Be your personal best'}
    elif temp == 3:
        res['results']['surgeryRough'] = {'surgeryId': 's4565', 'surgeryName': 'Hair transplant'}
    elif temp == 4:
        res['results']['consultationRough'] = {'consultationId': 'c4565', 'doctorName': 'Ross'}
    elif temp == 5:
        res['results']['hospitalizationRough'] = {'hospitalizationId': 'h4565', 'doctorName': 'Ross'}
    return res, 200


@app.route('/get-hospitalization-detailed', methods=['GET'])
def get_hospitalization_detailed():
    return {
        'message': 'success',
        'results': {
            'hospitalizationId': request.args.get('hospitalizationId'),
            'consultationRoughArr': [{'consultationId': 'c123', 'doctorName': 'Xi'},
                                     {'consultationId': 'c456', 'doctorName': 'Xi'},
                                     {'consultationId': 'c789', 'doctorName': 'Xi'},
                                     {'consultationId': 'c246', 'doctorName': 'Xi'}, ],
            'patientRough': {'patientId': '213123', 'patientName': 'Phoebe'},
            'doctorRough': {'doctorId': 'e123', 'doctorName': 'Ross'},
            'hospitalizationTime': '2002-01-01 11:00:11',
            'hospitalizationReason': long_sentence,
            'dischargeTime': '2002-01-01 11:00:11',
            'dischargeReason': long_sentence,
            'roomId': '123',
            'bedNumber': '456',
            'chargeId': 'c1234',
        }
    }, 200


@app.route('/get-patient-prescription', methods=['GET'])
def get_patient_prescription():
    print([request.args.get('patientId'),
           request.args.get('isHistory'),
           request.args.get('prescriptionId'),
           request.args.get('consultationId'),
           request.args.get('beginTime'),
           request.args.get('endTime')])
    lst = []
    time.sleep(0.5)
    int_field_1 = fields.IntField(value_range=(0, 20))
    int_field_2 = fields.IntField(value_range=(0, 10000))

    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'prescriptionId': 'p' + str(i),
            'consultationId': 'c' + str(int_field_2.random_data_generator()),
            'pharmacyWindow': str(int_field_1.random_data_generator()),
            'pharmacyPickupTime': fields.DatetimeField().random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/patient/refuse-prescription', methods=['POST'])
def refuse_prescription():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-patient-examination', methods=['GET'])
def get_patient_examination():
    print([request.args.get('examinationId'),
           request.args.get('examinationName'),
           request.args.get('beginExaminationTime'),
           request.args.get('endExaminationTime'),
           request.args.get('consultationId'),
           request.args.get('beginResultTime'),
           request.args.get('endResultTime'),
           request.args.get('isHistory'),
           request.args.get('patientId')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    date_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 10) + 20):
        lst.append({
            'examinationId': 'e' + str(i),
            'consultationId': 'c' + str(int_field.random_data_generator()),
            'examinationName': str_field.random_data_generator(),
            'examinationTime': date_field.random_data_generator(),
            'resultTime': date_field.random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/patient/cancel-examination', methods=['POST'])
def cancel_examination():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-patient-rehabilitation', methods=['GET'])
def get_patient_rehabilitation():
    print([request.args.get('rehabilitationId'),
           request.args.get('rehabilitationName'),
           request.args.get('beginTime'),
           request.args.get('endTime'),
           request.args.get('consultationId'),
           request.args.get('isHistory'),
           request.args.get('patientId')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))

    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'rehabilitationId': 'r' + str(i),
            'consultationId': 'c' + str(int_field.random_data_generator()),
            'rehabilitationName': 'check it out',
            'beginTime': fields.DatetimeField().random_data_generator(),
            'endTime': fields.DatetimeField().random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/patient/cancel-rehabilitation', methods=['POST'])
def cancel_rehabilitation():
    print(request.json)
    # return {'message': 'success'}, 200
    return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-patient-surgery', methods=['GET'])
def get_patient_surgery():
    print([request.args.get('surgeryId'),
           request.args.get('surgeryName'),
           request.args.get('beginTime1'),
           request.args.get('doctorName'),
           request.args.get('endTime1'),
           request.args.get('beginTime2'),
           request.args.get('endTime2'),
           request.args.get('consultationId'),
           request.args.get('isHistory'),
           request.args.get('patientId')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    string_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'surgeryId': 's' + str(i),
            'consultationId': 'c' + str(int_field.random_data_generator()),
            'doctorName': string_field.random_data_generator(),
            'surgeryName': string_field.random_data_generator(),
            'beginTime': fields.DatetimeField().random_data_generator(),
            'endTime': fields.DatetimeField().random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/patient/cancel-surgery', methods=['POST'])
def cancel_surgery():
    return {'message': 'success'}, 200


@app.route('/patient/cancel-hospitalization', methods=['POST'])
def cancel_hospitalization():
    return {'message': 'success'}, 200


@app.route('/patient/cancel-charge', methods=['POST'])
def cancel_charge():
    return {'message': 'success'}, 200


@app.route('/get-patient-hospitalization', methods=['GET'])
def get_patient_hospitalization():
    print([request.args.get('hospitalizationId'),
           request.args.get('consultationId'),
           request.args.get('isHistory'),
           request.args.get('patientId'),
           request.args.get('doctorName'),
           request.args.get('beginTime1'),
           request.args.get('endTime1'),
           request.args.get('beginTime2'),
           request.args.get('endTime2')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    string_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'hospitalizationId': 'h' + str(i),
            'consultationId': 'c' + str(int_field.random_data_generator()),
            'doctorName': string_field.random_data_generator(),
            'beginTime': fields.DatetimeField().random_data_generator(),
            'endTime': fields.DatetimeField().random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/get-patient-charge', methods=['GET'])
def get_patient_charge():
    print([request.args.get('isHistory'),
           request.args.get('patientId'),
           request.args.getlist('itemTypeList[]'),
           request.args.get('chargeId'),
           request.args.get('itemId'),
           request.args.get('beginTime'),
           request.args.get('endTime'),
           request.args.get('beginCost'),
           request.args.get('endCost')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    string_field = fields.StringField(length_range=(2, 50),
                                      dictionary=['Prescription', 'Examination', 'Rehabilitation',
                                                  'Surgery', 'Consultation', 'Hospitalization'])
    pay_string_field = fields.StringField(length_range=(2, 50),
                                          dictionary=['cash', 'credit card', 'debit card', 'Alipay', 'WeChat Pay'])
    item_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'time': fields.DatetimeField().random_data_generator(),
            'cost': str(int_field.random_data_generator()),
            'chargeId': 'c' + str(i),
            'itemType': string_field.random_data_generator(),
            'itemId': 'p' + str(i),
            'paymentMethod': pay_string_field.random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/get-department-arr', methods=['GET'])
def get_department_arr():
    print(request.args.get('department'))
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-patient-appointment', methods=['GET'])
def get_patient_appointment():
    print([request.args.get('patientId'),
           request.args.get('department'),
           request.args.get('doctorName'),
           request.args.get('beginTime'),
           request.args.get('endTime')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 500))
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'department': string_field.random_data_generator(),
            'doctorName': string_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'time': fields.DatetimeField().random_data_generator(),
            'cost': str(int_field.random_data_generator()),
            'position': string_field.random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/patient/schedule-appointment', methods=['POST'])
def schedule_appointment():
    print(request.json)
    return {'message': 'success', 'results': {'consultationId': 'c12'}}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


# below, doctor
@app.route('/get-subordinate-name-and-inquirer-name-arr', methods=['GET'])
def get_subordinate_name_and_inquirer_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-subordinate-id-and-inquirer-id-arr', methods=['GET'])
def get_subordinate_id_and_inquirer_id_arr():
    print([request.args.get('Id'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-patient-name-arr', methods=['GET'])
def get_patient_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-patient-id-arr', methods=['GET'])
def get_patient_id_arr():
    print([request.args.get('Id'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-doctor-consultation', methods=['GET'])
def get_doctor_consultation():
    print([request.args.get('consultationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('department'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginTime'),
           request.args.get('endTime'),
           request.args.get('inquirerId'),
           request.args.get('hasStarted'),
           request.args.get('isSearchingPatientInfo')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'consultationId': 'c' + str(i),
            'time': time_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'department': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasStarted': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-consultation', methods=['POST'])
def doctor_cancel_consultation():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-doctor-info', methods=['GET'])
def get_doctor_info():
    print(request.args.get('doctorId'))
    return {
        'message': 'success',
        'results': {
            'name': 'Jack',
            'gender': 'male',
            'position': 'pos',
            'birthdate': '2003-01-01',
            'phone': '5998745987456',
            'address': 'America',
            'dateOfHire': '2003-01-01',
            'dateOfDismiss': '',
            'supervisorId': '1325',
            'supervisorName': 'yang',
            'salary': '1545',
            'doctorId': 'd4565465',
            'department': 'asdf',
            'licenseNumber': 'asdfasdf',
        }
    }, 200


@app.route('/get-examination-name-arr', methods=['GET'])
def get_examination_name_arr():
    print([request.args.get('examinationName')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 500)):
        result['results'].append(string_field.random_data_generator())
    random.shuffle(result['results'])
    return result, 200


@app.route('/appointment/examination/is-time-available', methods=['GET'])
def appointment_examination_is_time_available():
    print([request.args.get('examinationName'), request.args.get('examinationDate')])
    lst = []
    time_field = fields.DatetimeField(force_format='{H}:{M}:{S}')
    for i in range(20):
        lst.append({'examinationTime': time_field.random_data_generator(),
                    'isAvailable': 'true' if random.random() > 0.5 else 'false'})
    return {'message': 'success',
            'results': lst
            }, 200


@app.route('/appointment/examination/pre-schedule', methods=['POST'])
def appointment_examination_pre_schedule():
    print(request.json)
    return {
        'message': 'success',
        'results': {
            'examinationId': str(fields.IntField([100, 999]).random_data_generator()),
            'examinationName': 'check it out' + str(int(random.random() * 1000)),
        }
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/examination/delete-pre-schedule', methods=['POST'])
def appointment_examination_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-rehabilitation-name-arr', methods=['GET'])
def get_rehabilitation_name_arr():
    print([request.args.get('rehabilitationName')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 500)):
        result['results'].append(string_field.random_data_generator())
    random.shuffle(result['results'])
    return result, 200


@app.route('/appointment/rehabilitation/is-time-available', methods=['GET'])  # 2023/10/19 already added in doc
def appointment_rehabilitation_is_time_available():
    print([request.args.get('rehabilitationName'), request.args.get('beginDate')])
    lst = []
    time_field = fields.DatetimeField(force_format='{H}:{M}:{S}')
    for i in range(20):
        lst.append({'beginTime': time_field.random_data_generator(),
                    'isAvailable': 'true' if random.random() > 0.5 else 'false'})
    return {'message': 'success',
            'results': lst
            }, 200


@app.route('/appointment/rehabilitation/pre-schedule', methods=['POST'])
def appointment_rehabilitation_pre_schedule():
    print(request.json)
    return {
        'message': 'success',
        'results': {
            'rehabilitationId': str(fields.IntField([100, 999]).random_data_generator()),
            'rehabilitationName': 'check it out' + str(int(random.random() * 1000)),
        }
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/rehabilitation/delete-pre-schedule', methods=['POST'])
def appointment_rehabilitation_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/appointment/prescription/pre-schedule/ask-for-prescription-id', methods=['POST'])
def appointment_prescription_pre_schedule_ask_id():
    print(request.json)
    return {
        'message': 'success',
        'results': {
            'prescriptionId': 'p' + str(fields.IntField([100, 999]).random_data_generator()),
        }
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/prescription/pre-schedule/confirm', methods=['POST'])
def appointment_prescription_pre_schedule_confirm():
    # should always return success!!!
    print(request.json)
    return {
        'message': 'success',
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/prescription/pre-schedule/cancel', methods=['POST'])
def appointment_prescription_pre_schedule_cancel():
    # should always return success!!!
    print(request.json)
    return {
        'message': 'success',
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/prescription/delete-pre-schedule', methods=['POST'])
def appointment_prescription_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-medicine-info-arr', methods=['GET'])
def get_medicine_info_arr():
    print([request.args.get('medicineName')])
    result = {'message': 'success', 'results': []}
    string_field = fields.StringField(length_range=(2, 15))
    int_field = fields.IntField(value_range=(0, 10000))
    for i in range(int(random.random() * 500)):
        result['results'].append({
            'medicineName': string_field.random_data_generator(),
            'medicineId': 'm' + str(int_field.random_data_generator()),
        }
        )
    random.shuffle(result['results'])
    return result, 200


@app.route('/appointment/prescription/pre-schedule/add-medicine', methods=['POST'])
def appointment_prescription_pre_schedule_add_medicine():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/prescription/pre-schedule/delete-medicine', methods=['POST'])
def appointment_prescription_pre_schedule_delete_medicine():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-medicine-name-by-id', methods=['GET'])
def get_medicine_name_by_id():
    print([request.args.get('medicineId')])
    return {'message': 'success', 'results': 'i am new name' + str(random.randint(1, 100))}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-surgery-site-arr', methods=['GET'])
def get_surgery_site_arr():
    print([request.args.get('surgerySite')])
    result = {'message': 'success', 'results': []}
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 500)):
        result['results'].append(string_field.random_data_generator())
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-surgery-name-arr', methods=['GET'])
def get_surgery_name_arr():
    print([request.args.get('surgeryName'), request.args.get('surgerySite')])
    result = {'message': 'success', 'results': []}
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 500)):
        result['results'].append(string_field.random_data_generator())
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-surgery-type-arr', methods=['GET'])
def get_surgery_type_arr():
    result = {'message': 'success', 'results': []}
    string_field = fields.StringField(length_range=(2, 15))
    for i in range(int(random.random() * 500)):
        result['results'].append(string_field.random_data_generator())
    random.shuffle(result['results'])
    return result, 200


@app.route('/appointment/surgery/is-time-available', methods=['GET'])
def appointment_surgery_is_time_available():
    print([request.args.get('surgeryName'),
           request.args.get('surgerySite'),
           request.args.get('beginDate'),
           request.args.get('surgeryType')])
    lst = []
    time_field = fields.DatetimeField(force_format='{H}:{M}:{S}')
    for i in range(20):
        lst.append({'beginTime': time_field.random_data_generator(),
                    'isAvailable': 'true' if random.random() > 0.5 else 'false'})
    return {'message': 'success',
            'results': lst
            }, 200


@app.route('/appointment/surgery/pre-schedule', methods=['POST'])
def appointment_surgery_pre_schedule():
    print(request.json)
    return {
        'message': 'success',
        'results': {
            'surgeryId': fields.IntField([100, 999]).random_data_generator(),
            'surgeryName': 'check it out' + str(int(random.random() * 1000)),
        }
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/surgery/delete-pre-schedule', methods=['POST'])
def appointment_surgery_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/appointment/hospitalization/is-time-available', methods=['GET'])
def appointment_hospitalization_is_time_available():
    print([
        request.args.get('hospitalizationDate'),
        request.args.get('roomType'),
    ])
    lst = []
    time_field = fields.DatetimeField(force_format='{H}:{M}:{S}')
    for i in range(20):
        lst.append({'hospitalizationTime': time_field.random_data_generator(),
                    'isAvailable': 'true' if random.random() > 0.5 else 'false'})
    return {'message': 'success',
            'results': lst
            }, 200


@app.route('/appointment/hospitalization/pre-schedule', methods=['POST'])
def appointment_hospitalization_pre_schedule():
    print(request.json)
    return {
        'message': 'success',
        'results': {
            'hospitalizationId': str(fields.IntField([100, 999]).random_data_generator()),
            'doctorName': 'check it out' + str(int(random.random() * 1000)),
        }
    }, 200
    # return {'message': 'failed', 'results': 'reason why the pre-schedule failed'}, 400


@app.route('/appointment/hospitalization/delete-pre-schedule', methods=['POST'])
def appointment_hospitalization_delete_pre_schedule():
    # pre-schedule must can be canceled!!!
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/appointment/consultation/submit', methods=['POST'])
def appointment_consultation_submit():
    # can only success!!!
    print(request.json)
    return {'message': 'success'}, 200


@app.route('/appointment/consultation/delete', methods=['POST'])
def appointment_consultation_delete():
    # can only success!!!
    # doctor abandon the consultation that he has already filled
    # should release the prescription, examination and so on that he has already filled
    print(request.json)
    return {'message': 'success'}, 200


@app.route('/get-doctor-prescription', methods=['GET'])
def get_doctor_prescription():
    print([request.args.get('prescriptionId'),
           request.args.get('consultationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginTime'),
           request.args.get('endTime'),
           request.args.get('inquirerId'),
           request.args.get('hasStarted')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'prescriptionId': 'p' + str(i),
            'consultationId': 'c' + str(int_field.random_data_generator()),
            'pharmacyPickupTime': time_field.random_data_generator(),
            'pharmacyPickWindow': str_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasStarted': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-prescription', methods=['POST'])
def doctor_cancel_prescription():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/prescription/finish', methods=['POST'])
def prescription_finish():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-doctor-examination', methods=['GET'])
def get_doctor_examination():
    print([request.args.get('examinationId'),
           request.args.get('examinationName'),
           request.args.get('consultationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginExaminationTime'),
           request.args.get('endExaminationTime'),
           request.args.get('beginResultTime'),
           request.args.get('endResultTime'),
           request.args.get('inquirerId'),
           request.args.get('hasConducted'),
           request.args.get('hasResult'),
           request.args.get('inquirerId')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'examinationId': 'e' + str(i),
            'consultationId': 'c' + str(i),
            'examinationName': str_field.random_data_generator(),
            'examinationTime': time_field.random_data_generator(),
            'resultTime': time_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasConducted': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-examination', methods=['POST'])
def doctor_cancel_examination():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/examination/conduct', methods=['POST'])
def doctor_examination_conduct():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/examination/record', methods=['POST'])
def doctor_examination_record():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/add-collaborator/get-doctor-info-arr', methods=['GET'])
def add_collaborator_get_doctor_info_arr():
    print([request.args.get('doctorName'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append({
            'doctorName': ans[i],
            'doctorId': 'd' + str(i),
        })
    random.shuffle(result['results'])
    return result, 200


@app.route('/add-collaborator/get-nurse-info-arr', methods=['GET'])
def add_collaborator_get_nurse_info_arr():
    print([request.args.get('nurseName'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append({
            'nurseName': ans[i],
            'nurseId': 'n' + str(i),
        })
    random.shuffle(result['results'])
    return result, 200


@app.route('/add-collaborator/get-helping-staff-info-arr', methods=['GET'])
def add_collaborator_get_helping_staff_info_arr():
    print([request.args.get('helpingStaffName'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append({
            'helpingStaffName': ans[i],
            'helpingStaffId': 'h' + str(i),
        })
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-employee-name-by-id', methods=['GET'])
def get_employee_name_by_id():
    print([request.args.get('userType'), request.args.get('doctorId'),
           request.args.get('nurseId'), request.args.get('helpingStaffId'), ])
    return {'message': 'success', 'results': 'i am new name' + str(random.randint(1, 100))}, 200


@app.route('/get-doctor-rehabilitation', methods=['GET'])
def get_doctor_rehabilitation():
    print([request.args.get('rehabilitationId'),
           request.args.get('rehabilitationName'),
           request.args.get('consultationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginTime1'),
           request.args.get('endTime1'),
           request.args.get('beginTime2'),
           request.args.get('endTime2'),
           request.args.get('inquirerId'),
           request.args.get('hasBegin'),
           request.args.get('hasEnd')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'rehabilitationId': 'r' + str(i),
            'consultationId': 'c' + str(i),
            'rehabilitationName': str_field.random_data_generator(),
            'beginTime': time_field.random_data_generator(),
            'endTime': time_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasBegin': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-rehabilitation', methods=['POST'])
def doctor_cancel_rehabilitation():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/rehabilitation/begin', methods=['POST'])
def doctor_rehabilitation_conduct():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/rehabilitation/end', methods=['POST'])
def doctor_rehabilitation_record():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-doctor-surgery', methods=['GET'])
def get_doctor_surgery():
    print([request.args.get('surgeryId'),
           request.args.get('surgeryName'),
           request.args.get('surgerySite'),
           request.args.get('consultationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginTime1'),
           request.args.get('endTime1'),
           request.args.get('beginTime2'),
           request.args.get('endTime2'),
           request.args.get('inquirerId'),
           request.args.get('hasBegin'),
           request.args.get('hasEnd')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'surgeryId': 'ss' + str(i),
            'consultationId': 'c' + str(i),
            'surgeryName': str_field.random_data_generator(),
            'surgerySite': str_field.random_data_generator(),
            'surgeryType': str_field.random_data_generator(),
            'beginTime': time_field.random_data_generator(),
            'endTime': time_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasBegin': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-surgery', methods=['POST'])
def doctor_cancel_surgery():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/surgery/begin', methods=['POST'])
def doctor_surgery_conduct():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/surgery/get-surgery-record-rough', methods=['GET'])
def doctor_surgery_get_surgery_record_rough():
    print([request.args.get('surgeryId')])
    res = []
    for i in range(5):
        res.append({
            'recordId': 'r' + str(i),
            'recordTime': '2021-10-19 12:12:12',
        })
    return {'message': 'success', 'results': res}, 200


@app.route('/doctor/surgery/end', methods=['POST'])
def doctor_surgery_end():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/surgery/record', methods=['POST'])
def doctor_surgery_record():
    print(request.json)
    return {'message': 'success',
            'results': {
                'recordId': 'r' + str(int(random.random() * 1000)),
            }}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/get-doctor-hospitalization', methods=['GET'])
def get_doctor_hospitalization():
    print([request.args.get('consultationId'),
           request.args.get('hospitalizationId'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('doctorName'),
           request.args.get('doctorId'),
           request.args.get('beginHospitalizationTime'),
           request.args.get('endHospitalizationTime'),
           request.args.get('beginDischargeTime'),
           request.args.get('endDischargeTime'),
           request.args.get('inquirerId'),
           request.args.get('hasBegin'),
           request.args.get('hasEnd')])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'hospitalizationId': 'hh' + str(i),
            'consultationId': 'c' + str(i),
            'hospitalizationTime': time_field.random_data_generator(),
            'roomId': 'r' + str(int_field.random_data_generator()),
            'bedNumber': str(int_field.random_data_generator()),
            'dischargeTime': time_field.random_data_generator(),
            'patientId': 'p' + str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'doctorId': 'd' + str(int_field.random_data_generator()),
            'doctorName': str_field.random_data_generator(),
            'hasBegin': 'true' if random.random() > 0.5 else 'false',
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/doctor/cancel-hospitalization', methods=['POST'])
def doctor_cancel_hospitalization():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/hospitalization/get-hospitalization-record-rough', methods=['GET'])
def doctor_surgery_get_hospitalization_record_rough():
    print([request.args.get('hospitalizationId')])
    res = []
    for i in range(5):
        res.append({
            'consultationId': 'r' + str(i),
            'doctorName': 'wow' + str(random.randint(1, 100)),
        })
    return {'message': 'success', 'results': res}, 200


@app.route('/doctor/hospitalization/begin', methods=['POST'])
def doctor_hospitalization_begin():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/hospitalization/record', methods=['POST'])
def doctor_hospitalization_record():
    print(request.json)
    return {'message': 'success',
            'results': {'consultationId': 'c' + str(int(random.random() * 1000))}
            }, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/doctor/hospitalization/end', methods=['POST'])
def doctor_hospitalization_end():
    print(request.json)
    return {'message': 'success'}, 200
    # return {'message': 'failed', 'results': 'reason why the submission failed'}, 400


@app.route('/edit-doctor-info', methods=['POST'])
def edit_doctor_info():
    json = request.json
    print(json)
    response_correct = {
        'message': 'success',
    }
    response_wrong = {
        'message': 'failed',
        'results': {
            'notice': 'The form is not filled correctly.',
            'invalidFormField': ['address'],
        }
    }
    return jsonify(response_correct), 200
    # return jsonify(response_wrong), 400


@app.route('/caregiver/permission', methods=['GET'])
def caregiver_permission():
    print([request.args.get('userId'), request.args.get('userType')])
    return {'message': 'success',
            'results': {
                # nurse can only in one room (specified by the room id)
                # helping staff can in multiple rooms
                'inExaminationRoom': 'true',
                'inRehabilitationRoom': 'true',
                'inSurgeryRoom': 'true',
                'inHospitalizationRoom': 'true',
            }}, 200


@app.route('/caregiver/get-table-data', methods=['GET'])
def caregiver_get_table_data():
    print([request.args.get('consultationId'),
           request.args.get('itemId'),
           request.args.get('itemName'),
           request.args.get('beginTime1'),
           request.args.get('beginTime2'),
           request.args.get('endTime1'),
           request.args.get('endTime2'),
           request.args.get('patientId'),
           request.args.get('patientName'),
           request.args.get('isHistory'),
           request.args.get('itemType'),
           request.args.get('inquirerId'),
           request.args.get('inquirerType'),
           request.args.get('includeSubordinate'),
           ])
    lst = []
    time.sleep(0.5)
    int_field = fields.IntField(value_range=(0, 10000))
    time_field = fields.DatetimeField()
    str_field = fields.StringField(length_range=(2, 10))
    for i in range(int(random.random() * 1000) + 2000):
        lst.append({
            'consultationId': 'c' + str(i),
            'itemId': 'i' + str(i),
            'itemName': str_field.random_data_generator(),
            'time1': time_field.random_data_generator(),
            'time2': time_field.random_data_generator(),
            'patientId': str(int_field.random_data_generator()),
            'patientName': str_field.random_data_generator(),
            'caregiverId': 'id' + str(int_field.random_data_generator()),
            'caregiverName': str_field.random_data_generator(),
        })
    return {
        'message': 'success',
        'results': lst,
    }, 200


@app.route('/get-room-detailed', methods=['GET'])
def get_room_detailed():
    return {
        'message': 'success',
        'results': {
            'roomId': request.args.get('roomId'),
            'roomType': 'VIP',
            'numberOfBeds': '10',
            'description': long_sentence,
            'location': long_sentence,
        }
    }, 200


@app.route('/doctor/get-surgery-description', methods=['GET'])
def doctor_get_surgery_description():
    print([request.args.get('surgeryId')])
    return {'message': 'success', 'results': long_sentence}, 200


@app.route('/doctor/get-hospitalization-reason', methods=['GET'])
def doctor_get_hospitalization_reason():
    print([request.args.get('hospitalizationId')])
    return {'message': 'success', 'results': long_sentence}, 200


@app.route('/get-nurse-info', methods=['GET'])
def get_nurse_info():
    print(request.args.get('nurseId'))
    return {
        'message': 'success',
        'results': {
            'name': 'Jack',
            'gender': 'male',
            'position': 'pos',
            'birthdate': '2003-01-01',
            'phone': '5998745987456' + str(random.randint(1, 100)),
            'address': 'America',
            'dateOfHire': '2003-01-01',
            'dateOfDismiss': '',
            'supervisorId': '1325',
            'supervisorName': 'yang',
            'salary': '1545',
            'nurseId': request.args.get('nurseId'),
            'roomId': 'asdf',
            'licenseNumber': 'asdfasdf',
        }
    }, 200


@app.route('/get-helping-staff-info', methods=['GET'])
def get_helping_staff_info():
    print(request.args.get('helpingStaffId'))
    return {
        'message': 'success',
        'results': {
            'name': 'Jack',
            'gender': 'male',
            'position': 'pos',
            'birthdate': '2003-01-01',
            'phone': '5998745987456',
            'address': 'America',
            'dateOfHire': '2003-01-01',
            'dateOfDismiss': '',
            'supervisorId': '1325',
            'supervisorName': 'yang',
            'salary': '1545',
            'helpingStaffId': request.args.get('helpingStaffId'),
        }
    }, 200


@app.route('/edit-nurse-info', methods=['POST'])
def edit_nurse_info():
    json = request.json
    print(json)
    response_correct = {
        'message': 'success',
    }
    response_wrong = {
        'message': 'failed',
        'results': {
            'notice': 'The form is not filled correctly.',
            'invalidFormField': ['address'],
        }
    }
    return jsonify(response_correct), 200
    # return jsonify(response_wrong), 400


@app.route('/edit-helping-staff-info', methods=['POST'])
def edit_helping_staff_info():
    json = request.json
    print(json)
    response_correct = {
        'message': 'success',
    }
    response_wrong = {
        'message': 'failed',
        'results': {
            'notice': 'The form is not filled correctly.',
            'invalidFormField': ['address'],
        }
    }
    return jsonify(response_correct), 200
    # return jsonify(response_wrong), 400


@app.route('/get-doctor-name-arr', methods=['GET'])
def get_doctor_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-nurse-name-arr', methods=['GET'])
def get_nurse_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-helping-staff-name-arr', methods=['GET'])
def get_helping_staff_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/get-medicine-name-arr', methods=['GET'])
def get_medicine_name_arr():
    print([request.args.get('name'), request.args.get('inquirerId'), request.args.get('inquirerType')])
    result = {'message': 'success', 'results': []}
    ans = ['Ben', 'Ross', 'Joey', 'Chandler', 'Monica', 'Rachel', 'Phoebe', 'Gunther', 'Janice', 'Richard']
    for i in range(int(random.random() * 10)):
        result['results'].append(ans[i])
    random.shuffle(result['results'])
    return result, 200


@app.route('/admin/get-form-info', methods=['GET'])
def admin_get_form_info():
    print([
        request.args.get('itemName'),
        request.args.get('formType')  # three types: 'add', 'edit', 'search'
    ])
    if request.args.get('formType') == 'search':
        result = [
            {
                'prop': 'patientName',
                'label': 'Patient Name',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'true',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'patientId',
                'label': 'Patient ID',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'age',
                'label': 'Age',
                'type': 'string',
                'disabled': 'false',
                'isInterval': 'true',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleEnumValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'dateField1',
                'label': 'Data Field 1',
                'type': 'date',
                'disabled': 'false',
                'isInterval': 'true',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'dateField2',
                'label': 'Data Field 2',
                'type': 'date',
                'disabled': 'false',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'eField',
                'label': 'E Field ' + request.args.get('itemName'),
                'disabled': 'false',
                'type': 'enumerate',
                'isInterval': 'false',
                'enumerateValue': ['wow', 'wow2', 'wow3'],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'eFieldM',
                'label': 'E Field M' + request.args.get('itemName'),
                'disabled': 'false',
                'type': 'enumerate',
                'isInterval': 'false',
                'enumerateValue': ['wow', 'wow2', 'wow3'],
                'isMultiple': 'true',
                'minNum': '0',
                'maxNum': '2',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': ['wow2', 'wow3'],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'examinationName',
                'label': 'Examination Name',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'true',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'true',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': 'm',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
        ]
        return {'message': 'success', 'results': result}, 200
    elif request.args.get('formType') == 'edit':
        result = [
            {
                'prop': 'patientName',
                'label': 'Patient Name',
                'disabled': 'true',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'true',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': 'q',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'patientId',
                'label': 'Patient ID',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': 'w',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'age',
                'label': 'Age',
                'type': 'string',
                'disabled': 'false',
                'isInterval': 'true',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '12',
                'endValue': '32',
                'multipleEnumValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'dateField1',
                'label': 'Data Field 1',
                'type': 'date',
                'disabled': 'false',
                'isInterval': 'true',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '2002-05-02 12:12:12',
                'endValue': '2002-05-02 12:12:12',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'dateField2',
                'label': 'Data Field 2',
                'type': 'date',
                'disabled': 'false',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '2002-05-02 12:12:12',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'eField',
                'label': 'E Field ' + request.args.get('itemName'),
                'disabled': 'false',
                'type': 'enumerate',
                'isInterval': 'false',
                'enumerateValue': ['wow', 'wow2', 'wow3'],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': 'wow',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'eFieldM',
                'label': 'E Field M' + request.args.get('itemName'),
                'disabled': 'false',
                'type': 'enumerate',
                'isInterval': 'false',
                'enumerateValue': ['wow', 'wow2', 'wow3'],
                'isMultiple': 'true',
                'minNum': '0',
                'maxNum': '2',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': 'wow',
                'beginValue': '',
                'endValue': '',
                'multipleValue': ['wow2', 'wow3'],

                'rules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
        ]
        return {'message': 'success', 'results': result}, 200
    elif request.args.get('formType') == 'add':
        result = [
            {
                'prop': 'patientName',
                'label': 'Patient Name',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'false',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'true',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'true',
                    'message': 'm',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'eFieldM',
                'label': 'E Field M' + request.args.get('itemName'),
                'disabled': 'false',
                'type': 'enumerate',
                'isInterval': 'false',
                'enumerateValue': ['wow', 'wow2', 'wow3'],
                'isMultiple': 'true',
                'minNum': '0',
                'maxNum': '2',

                'needRemoteMethod': 'false',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': 'wow',
                'beginValue': '',
                'endValue': '',
                'multipleValue': ['wow2', 'wow3'],

                'rules': {
                    'required': 'true',
                    'message': 'multiple checkbox err',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'examinationName',
                'label': 'Examination Name',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'true',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'true',
                'isRehabilitationName': 'false',
                'isMedicineName': 'false',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': ['wow', 'ww'],

                'rules': {
                    'required': 'true',
                    'message': 'm',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
            {
                'prop': 'medicineName',
                'label': 'Medicine Name',
                'disabled': 'false',
                'type': 'string',
                'isInterval': 'false',
                'enumerateValue': [],
                'isMultiple': 'true',
                'minNum': '',
                'maxNum': '',

                'needRemoteMethod': 'true',
                'isPatientName': 'false',
                'isDoctorName': 'false',
                'isNurseName': 'false',
                'isHelpingStaffName': 'false',
                'isExaminationName': 'false',
                'isRehabilitationName': 'false',
                'isMedicineName': 'true',
                'isSurgerySite': 'false',
                'isSurgeryName': 'false',
                'isDepartment': 'false',

                'value': '',
                'beginValue': '',
                'endValue': '',
                'multipleValue': [],

                'rules': {
                    'required': 'true',
                    'message': 'm',
                    'trigger': 'change',
                },
                'beginRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                },
                'endRules': {
                    'required': 'false',
                    'message': '',
                    'trigger': 'change',
                }
            },
        ]
        return {'message': 'success', 'results': result}, 200
    else:
        return {}, 400


@app.route('/admin/get-table-data', methods=['GET'])
def admin_get_table_data():
    print([request.args])
    str_field = fields.StringField(length_range=(2, 10))
    data_field = fields.DatetimeField()
    result = []
    time.sleep(0.5)
    for i in range(int(random.random() * 10) + 20):
        result.append({
            # format 'prop': 'value'
            # not all the prop here should exist in admin_get_table_column()
            # but all the prop in admin_get_table_column() need to exist here
            'patientName': str_field.random_data_generator(),
            'patientId': 'p' + str(i),
            'consultationId': 'c' + str(i),
            'testTime': data_field.random_data_generator(),
        })
    return {'message': 'success', 'results': result}, 200


@app.route('/admin/get-table-column', methods=['GET'])
def admin_get_table_column():
    print([request.args.get('itemName')])
    return {
        'message': 'success',
        'results': {
            'columns': [
                {
                    'prop': 'patientName',
                    'label': 'Patient Name',
                    'show': 'true',

                    'sortConsultationId': 'false',
                    'sortDepartment': 'false',
                    'sortName': 'true',
                    'sortPrescriptionId': 'false',
                    'sortPharmacyWindow': 'false',
                    'sortExaminationId': 'false',
                    'sortRehabilitationId': 'false',
                    'sortSurgeryId': 'false',
                    'sortHospitalizationId': 'false',
                    'sortChargeId': 'false',
                    'sortDescribableItemId': 'false',
                    'sortCost': 'false',
                    'sortPosition': 'false',
                    'sortPatientId': 'false',
                    'sortDoctorId': 'false',
                    'sortNurseId': 'false',
                    'sortHelpingStaffId': 'false',
                    'sortPharmacyPickWindow': 'false',
                    'sortSurgerySite': 'false',
                    'sortTime': 'false',
                    'sortRoomId': 'false',
                },
                {
                    'prop': 'patientId',
                    'label': 'Patient ID',
                    'show': 'true',

                    'sortConsultationId': 'false',
                    'sortDepartment': 'false',
                    'sortName': 'false',
                    'sortPrescriptionId': 'false',
                    'sortPharmacyWindow': 'false',
                    'sortExaminationId': 'false',
                    'sortRehabilitationId': 'false',
                    'sortSurgeryId': 'false',
                    'sortHospitalizationId': 'false',
                    'sortChargeId': 'false',
                    'sortDescribableItemId': 'false',
                    'sortCost': 'false',
                    'sortPosition': 'false',
                    'sortPatientId': 'true',
                    'sortDoctorId': 'false',
                    'sortNurseId': 'false',
                    'sortHelpingStaffId': 'false',
                    'sortPharmacyPickWindow': 'false',
                    'sortSurgerySite': 'false',
                    'sortTime': 'false',
                    'sortRoomId': 'false',
                },
                {
                    'prop': 'testTime',
                    'label': 'Test Time ' + request.args.get('itemName'),
                    'show': 'true',

                    'sortConsultationId': 'false',
                    'sortDepartment': 'false',
                    'sortName': 'false',
                    'sortPrescriptionId': 'false',
                    'sortPharmacyWindow': 'false',
                    'sortExaminationId': 'false',
                    'sortRehabilitationId': 'false',
                    'sortSurgeryId': 'false',
                    'sortHospitalizationId': 'false',
                    'sortChargeId': 'false',
                    'sortDescribableItemId': 'false',
                    'sortCost': 'false',
                    'sortPosition': 'false',
                    'sortPatientId': 'false',
                    'sortDoctorId': 'false',
                    'sortNurseId': 'false',
                    'sortHelpingStaffId': 'false',
                    'sortPharmacyPickWindow': 'false',
                    'sortSurgerySite': 'false',
                    'sortTime': 'true',
                    'sortRoomId': 'false',
                }
            ],
            'detailInfo': {
                'canDelete': 'true',
                'canEdit': 'true',
                'canShowDetail': 'true',

                'isConsultation': 'true',
                'propNameOfConsultationId': 'consultationId',
                'isPrescription': 'false',
                'propNameOfPrescriptionId': 'prescriptionId',
                'isExamination': 'false',
                'propNameOfExaminationId': 'examinationId',
                'isRehabilitation': 'false',
                'propNameOfRehabilitationId': 'rehabilitationId',
                'isSurgery': 'false',
                'propNameOfSurgeryId': 'surgeryId',
                'isHospitalization': 'false',
                'propNameOfHospitalizationId': 'hospitalizationId',
                'isCharge': 'false',
                'propNameOfChargeId': 'chargeId',
                'isPatient': 'false',
                'propNameOfPatientId': 'patientId',
                'isDoctor': 'false',
                'propNameOfDoctorId': 'doctorId',
                'isNurse': 'false',
                'propNameOfNurseId': 'nurseId',
                'isHelpingStaff': 'false',
                'propNameOfHelpingStaffId': 'helpingStaffId',
                'isRoom': 'false',
                'propNameOfRoomId': 'roomId',
                'isPrescriptionMedicine': 'false',
                'propOfPrescriptionMedicineId': 'prescriptionId#medicineId',
                'isSurgeryRecord': 'false',
                'propOfSurgeryRecordId': 'surgeryId#recordId',
            },
            'keyColumnPropName': 'patientId',  # must be unique
        }
    }


@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    print(request.json)
    return {'message': 'success', 'results': {'onlyRemoveOneRecord': 'true'}}, 200
    # return {'message': 'fail', 'results': 'why fail'}, 400


@app.route('/admin/add-or-edit', methods=['POST'])
def admin_add_or_edit():
    print(request.json)
    return {'message': 'success'}, 200


@app.route('/admin/can-add', methods=['GET'])
def admin_can_add():
    print([request.args.get('itemName')])
    return {'message': 'success', 'results': 'true'}, 200


@app.route('/admin/get-registration-waiting-list', methods=['GET'])
def admin_registration():
    print([request.args.get('userType'), request.args.get('beginTime'), request.args.get('endTime')])
    lst = []
    name_field = fields.StringField(length_range=(2, 10))
    time_field = fields.DatetimeField()
    type_field = fields.StringField(length_range=(2, 1000), dictionary=['doctor', 'nurse', 'helping staff'])
    for i in range(0, random.randint(0, 10) * 100 + random.randint(0, 1000)):
        lst.append({
            'userId': 'u' + str(i),
            'userName': name_field.random_data_generator(),
            'userType': type_field.random_data_generator(),
            'registerTime': time_field.random_data_generator(),
        })
    return {'message': 'success', 'results': lst}, 200


@app.route('/admin/registration/allow', methods=['POST'])
def admin_registration_allow():
    print(request.json)
    return {'message': 'success'}, 200


@app.route('/admin/registration/disallow', methods=['POST'])
def admin_registration_disallow():
    print(request.json)
    return {'message': 'success'}, 200


# functions below are added after the document is created
@app.route('/get-room-type-arr')
def get_room_type_arr():
    print([request.args.get('roomType')])
    return {'message': 'success', 'results': ['VIP',
                                              'normal',
                                              fields.StringField(length_range=(2, 1000)).random_data_generator()]}, 200


# clear all deleted users
@app.route('/admin/clear-deleted-users', methods=['POST'])
def clear_deleted_users():
    print(request.json)
    return {'message': 'success'}, 200


if __name__ == '__main__':
    # use "flask init-database" to initialize the database
    app.run('0.0.0.0', debug=True, port=5000)
