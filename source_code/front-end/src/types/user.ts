export interface PatientInfo {
	patientId: string
	name: string
  gender: string
  birthdate: string
  maritalStatus: string
  occupation: string
  birthplace: string
  nationality: string
  identificationDocumentType: string
  identificationNumber: string
  phone: string
  address: string
  bloodType: string
  allergens: string[]
  initialDiagnosisDate: string
  emergencyContact: string
  emergencyContactRelationship: string
  emergencyContactPhone: string
  emergencyContactAddress: string
}
export type PatientInfoKey = keyof PatientInfo

export interface EmployeeInfo {
	name: string
  gender: string
  position: string
  birthdate: string
  phone: string
  address: string
  dateOfHire: string
  dateOfDismiss: string  // this should not be recorded when register
  supervisorId: string
  supervisorName: string
  salary: string  // this should not be decided by the employee
}

export interface DoctorInfo extends EmployeeInfo {
	doctorId: string
	department: string
	licenseNumber: string
}
export type DoctorInfoKey = keyof DoctorInfo

export interface NurseInfo extends EmployeeInfo {
	nurseId: string
	roomId: string
	licenseNumber: string
}

export type NurseInfoKey = keyof NurseInfo

export interface HelpingStaffInfo extends EmployeeInfo {
	helpingStaffId: string
}

export type HelpingStaffInfoKey = keyof HelpingStaffInfo

export enum UserType{
  Doctor = 'doctor',
  Nurse = 'nurse',
  HelpingStaff = 'helpingStaff',
  Patient = 'patient',
  Admin = 'admin'
}

export const stringToUserType = (str: string): UserType => {
  switch (str) {
    case 'doctor':
      return UserType.Doctor
    case 'nurse':
      return UserType.Nurse
    case 'helpingStaff':
      return UserType.HelpingStaff
    case 'patient':
      return UserType.Patient
    case 'admin':
      return UserType.Admin
    default:
      throw new Error('unknown user type')
  }
}