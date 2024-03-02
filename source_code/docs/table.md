# user
- <u>user_id</u>
- password
- role
- valid
- register_time

# patient
- <u>patient_id</u>
- name
- gender
- birthdate
- martial-status
- occupation
- birthplace
- nationality
- identification document type
- identification number
- phone
- address
- blood type
- allergens
- initial diagnosis date
- emergency contact
- emergency contact relationship
- emergency contact phone
- emergency contact address
- valid

# employee
- <u>employee_id</u>
- name
- gender
- position (the position in the hospital)
- birthdate
- phone
- address
- date of hire
- date of dismiss
- supervisor id
- salary
- valid

# doctor
- <u>doctor_id</u>
- department
- license number

# nurse
- <u>nurse_id</u>
- room_id
- license number

# helping_stuff
- <u>helping_stuff_id</u>

# room
- <u>room_id</u>
- room type (icu, operation theater, etc)
- number of beds
- description

# consultation
- <u>consultation_id</u>
- doctor_id
- patient_id
- date
- time
- self report
- medical history
- meidcation history
- medical advice
- charge_id

# prescription
- <u>prescription_id</u>
- consultation_id
- doctor_id (the doctor who prepare the medicine)
- pharmacy window (the pharmacy window where the patient can pick up the medication, can be null)
- pharmacy pickup date
- pharmacy pickup time
- charge_id

# medicine
- <u>medicine_id</u>
- name
- manufacturer

# prescription_medcine
- <u>prescription_id</u>
- <u>medicine_id</u>
- quantity
- course of medication
- dosage
- frequency
- cost

# examination
- <u>examination_id</u>
- consultation_id
- date of examination
- time of examination
- date of result
- time of result
- examination name
- result
- charge_id

# examination_doctor
- <u>examination_id</u>
- <u>doctor_id</u> (the doctor who performed the examination)

# examination_helping_staff
- <u>examination_id</u>
- <u>helping_staff_id</u>

# examination_nurse
- <u>examination_id</u>
- <u>nurse_id</u>
  
# rehabilitation
- <u>rehabilitation_id</u>
- consultation_id
- rehabilitation name
- begin date
- begin time
- end date
- end time
- charge id

# rehabilitation_doctor
- <u>rehabilitation_id</u>
- <u>doctor_id</u> (the doctor who performed the rehabilitation)

# rehabilitation_helping_staff
- <u>rehabilitation_id</u>
- <u>helping_staff_id</u>

# rehabilitation_nurse
- <u>rehabilitation_id</u>
- <u>nurse_id</u>

# surgery
- <u>surgery_id</u>
- consultation_id
- patient_id
- doctor_id of lead surgeon
- surgery name
- surgery description
- surgery site
- surgery type (emergency, elective, etc)
- begin date
- begin time
- end date
- end time
- charge_id
  
# surgery_related_record
- <u>surgery_id</u>
- <u>record_date</u>
- <u>record_time</u>
- record_id  (should be unique among all records)
- record_detail

# surgery_doctor
- <u>surgery_id</u>
- <u>doctor_id</u>

# surgery_nurse
- <u>surgery_id</u>
- <u>nurse_id</u>

# surgery_helping_staff
- <u>surgery_id</u>
- <u>helping_staff_id</u>

# hospitalization
- <u>hospitalization_id</u>
- patient_id
- doctor_id (doctor in charge)
- hospitalization date
- hospitalization time
- hospitalization reason
- discharge date
- discharge time
- discharge reason
- room_id
- bed number
- charge_id

# hospitalization_record
- <u>hospitalization_id</u>
- consultation_id

# charge
- <u>charge_id</u>
- patient_id
- cost
- is completed (whether the charge is completed)
- charge date
- charge time
- payment method