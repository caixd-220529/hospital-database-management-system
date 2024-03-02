export interface PrescriptionRough{
  prescriptionId: string
}

export interface ExaminationRough{
  examinationId: string
  examinationName: string
}

export interface SurgeryRough{
  surgeryId: string
  surgeryName: string
}

export interface RehabilitationRough{
  rehabilitationId: string
  rehabilitationName: string
}

export interface ConsultationRough{
  consultationId: string
  doctorName: string
}

export interface DoctorRough{
  doctorId: string
  doctorName: string
}

export interface NurseRough{
  nurseId: string
  nurseName: string
}

export interface HelpingStaffRough{
  helpingStaffId: string
  helpingStaffName: string
}

export interface PatientRough{
  patientId: string
  patientName: string
}

export interface SurgeryRelatedRecordRough{
  recordId: string
  recordTime: string
}

export interface PrescriptionMedicineRough{
  medicineId: string
  medicineName: string
  quantity: string
}

export interface HospitalizationRough { 
  hospitalizationId: string
  doctorName: string
}


export interface PrescriptionMedicineDetailed{
  prescriptionId: string
  medicineId: string
  medicineName: string
  medicineManufacturer: string
  courseOfMedication: string
  dosage: string
  frequency: string
  cost: string
  quantity: string
}
export type PrescriptionMedicineDetailedKey = keyof PrescriptionMedicineDetailed

export interface ConsultationDetailed{
  consultationId: string
  patientId: string
  patientName: string
  doctorRough: DoctorRough
  time: string
  selfReport: string
  medicalHistory: string
  medicationHistory: string
  medicalAdvice: string
  prescriptionRoughArr: PrescriptionRough[]
  examinationRoughArr: ExaminationRough[]
  rehabilitationRoughArr: RehabilitationRough[]
  surgeryRoughArr: SurgeryRough[]
  hospitalizationRoughArr: HospitalizationRough[]
  chargeId: string
}
export type ConsultationDetailedKey = keyof ConsultationDetailed

export interface RehabilitationDetailed {
  rehabilitationId: string
  consultationRough: ConsultationRough
  rehabilitationName: string
  beginTime: string
  endTime: string
  chargeId: string
  patientRough: PatientRough
  doctorRoughArr: DoctorRough[]
  nurseRoughArr: NurseRough[]
  helpingStaffRoughArr: HelpingStaffRough[]
}
export type RehabilitationDetailedKey = keyof RehabilitationDetailed

export interface ExaminationDetailed {  
  examinationId: string
  consultationRough: ConsultationRough
  timeOfExamination: string
  timeOfResult: string
  examinationName: string
  result: string
  chargeId: string
  patientRough: PatientRough
  doctorRoughArr: DoctorRough[]
  nurseRoughArr: NurseRough[]
  helpingStaffRoughArr: HelpingStaffRough[]
}
export type ExaminationDetailedKey = keyof ExaminationDetailed

export interface PrescriptionDetailed {
  prescriptionId: string
  consultationRough: ConsultationRough
  patientRough: PatientRough
  doctorRough: DoctorRough
  pharmacyWindow: string
  pharmacyPickupTime: string
  prescriptionMedicineRoughArr: PrescriptionMedicineRough[]
  chargeId: string
}
export type PrescriptionDetailedKey = keyof PrescriptionDetailed

export interface SurgeryDetailed {
  surgeryId: string
  consultationRough: ConsultationRough
  patientRough: PatientRough
  doctorRough: DoctorRough
  surgeryName: string
  surgeryDescription: string
  surgerySite: string
  surgeryType: string
  beginTime: string
  endTime: string
  chargeId: string
  doctorRoughArr: DoctorRough[]
  nurseRoughArr: NurseRough[]
  helpingStaffRoughArr: HelpingStaffRough[]
  recordRoughArr: SurgeryRelatedRecordRough[]
}
export type SurgeryDetailedKey = keyof SurgeryDetailed

export interface SurgeryRelatedRecordDetailed {
  surgeryId: string
  recordId: string
  recordTime: string
  recordDetail: string
}
export type SurgeryRelatedRecordDetailedKey = keyof SurgeryRelatedRecordDetailed

export interface ChargeDetailed {
  chargeId: string
  patientRough: PatientRough
  cost: string
  isCompleted: string
  chargeTime: string
  paymentMethod: string
  prescriptionRough: PrescriptionRough
  examinationRough: ExaminationRough
  surgeryRough: SurgeryRough
  rehabilitationRough: RehabilitationRough
  consultationRough: ConsultationRough
  hospitalizationRough: HospitalizationRough
}
export type ChargeDetailedKey = keyof ChargeDetailed

export interface HospitalizationDetailed { 
  hospitalizationId: string
  patientRough: PatientRough
  doctorRough: DoctorRough
  consultationRoughArr: ConsultationRough[]
  hospitalizationTime: string
  hospitalizationReason: string
  dischargeTime: string
  dischargeReason: string
  roomId: string
  bedNumber: string
  chargeId: string
}
export type HospitalizationDetailedKey = keyof HospitalizationDetailed

export interface RoomDetailed {
  roomId: string
  roomType: string
  numberOfBeds: string
  location: string
  description: string
}
export type RoomDetailedKey = keyof RoomDetailed

export enum DescribableItem{
  Consultation = 'Consultation',
  Prescription = 'Prescription',
  Examination = 'Examination',
  Rehabilitation = 'Rehabilitation',
  Surgery = 'Surgery',
  Charge = 'Charge',
  Hospitalization = 'Hospitalization',
  Patient = 'Patient',
  Doctor = 'Doctor',
  Nurse = 'Nurse',
  HelpingStaff = 'HelpingStaff',
  PrescriptionMedicine = 'PrescriptionMedicine',
  SurgeryRecord = 'SurgeryRecord',
  Room = 'Room',
}