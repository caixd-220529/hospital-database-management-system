import {Ref} from 'vue'
import {useConfigStore} from '../stores/config.ts'
import axios, {AxiosResponse} from "axios";
import {UserType} from '../types/user.ts'
import { DoctorRough, NurseRough, HelpingStaffRough} from "../types/other.ts";


const rootOfPath = useConfigStore().rootOfPath

const remoteMethodTemplate = (query: string, params: Object, path: string, options: Ref<string[]>|Ref<DoctorRough[]>|Ref<NurseRough[]>|Ref<HelpingStaffRough[]>, loading: Ref<boolean>) => {
  if (query) {
    loading.value = true
    axios.get(rootOfPath + path, {
      params: params
    }).then((response: AxiosResponse) => {
      options.value = response.data.results
    }).catch((err: any) => {
      console.log(err)
    }).finally(() => {
      loading.value = false
    })
  } else {
    options.value = []
  }
}

// get the department of the hospital
export const departmentRemoteMethod = (query: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'department': query}, '/get-department-arr', options, loading)
}


// get the name of doctor that the inquirer has the right to see
export const subordinateNameAndInquirerNameRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-subordinate-name-and-inquirer-name-arr', options, loading)
}

export const subordinateNameAndInquirerIdRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'Id': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-subordinate-id-and-inquirer-id-arr', options, loading)
}

export const patientNameRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-patient-name-arr', options, loading)
}

export const patientIdRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'Id': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-patient-id-arr', options, loading)
}

export const examinationNameRemoteMethod = (query: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'examinationName': query}, '/get-examination-name-arr', options, loading)
}

export const rehabilitationNameRemoteMethod = (query: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'rehabilitationName': query}, '/get-rehabilitation-name-arr', options, loading)
}

export const medicineInfoRemoteMethod = (query: string, options: any, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'medicineName': query}, '/get-medicine-info-arr', options, loading)
}

export const surgerySiteRemoteMethod = (query: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'surgerySite': query}, '/get-surgery-site-arr', options, loading)
}

export const surgeryNameRemoteMethod = (query: string, surgerySite: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'surgeryName': query, 'surgerySite': surgerySite}, '/get-surgery-name-arr', options, loading)
}

export const doctorInfoRemoteMethodUsedInAddCollaborator = (query: string, inquirerId: string, userType: UserType, options: Ref<DoctorRough[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'doctorName': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/add-collaborator/get-doctor-info-arr', options, loading)
}

export const nurseInfoRemoteMethodUsedInAddCollaborator = (query: string, inquirerId: string, userType: UserType, options: Ref<NurseRough[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'nurseName': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/add-collaborator/get-nurse-info-arr', options, loading)
}

export const helpingStaffInfoRemoteMethodUsedInAddCollaborator = (query: string, inquirerId: string, userType: UserType, options: Ref<HelpingStaffRough[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'helpingStaffName': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/add-collaborator/get-helping-staff-info-arr', options, loading)
}

export const doctorNameRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-doctor-name-arr', options, loading)
}

export const nurseNameRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-nurse-name-arr', options, loading)
}

export const helpingStaffNameRemoteMethod = (query: string, inquirerId: string, userType: UserType, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query, 'inquirerId': inquirerId, 'inquirerType': userType}, '/get-helping-staff-name-arr', options, loading)
}

export const medicineNameRemoteMethod = (query: string, options: any, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'name': query}, '/get-medicine-name-arr', options, loading)
}

export const roomTypeRemoteMethod = (query: string, options: Ref<string[]>, loading: Ref<boolean>) => {
  remoteMethodTemplate(query, {'roomType': query}, '/get-room-type-arr', options, loading)
}
