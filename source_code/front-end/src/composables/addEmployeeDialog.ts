import { UserType} from "../types/user.ts";
import {HelpingStaffRough, DoctorRough, NurseRough} from "../types/other.ts";
import {ElMessage, FormInstance, type FormRules} from 'element-plus'
import {useConfigStore} from '../stores/config'
import {ref, Ref, watch} from 'vue'
import axios from "axios";
import {
  doctorInfoRemoteMethodUsedInAddCollaborator, helpingStaffInfoRemoteMethodUsedInAddCollaborator,
  nurseInfoRemoteMethodUsedInAddCollaborator
} from "../utils/remote.ts";

export const useAddEmployeeDialog = (itemToRecord: Ref)=>{
  console.assert('doctorRoughArr' in itemToRecord.value)
  console.assert('nurseRoughArr' in itemToRecord.value)
  console.assert('helpingStaffRoughArr' in itemToRecord.value)
  const config = useConfigStore()
  const rootOfPath = config.rootOfPath

  const addEmployeeDialogVisible = ref(false)
  const employeeType = ref<UserType>(UserType.Doctor)
  const addEmployeeDialogTitle = ref('Add Doctor')
  const addEmployeeDialogButtonDisabled = ref(false)
  const doctorInfoToAdd = ref<DoctorRough>({doctorId: '', doctorName: ''})
  const nurseInfoToAdd = ref<NurseRough>({nurseId: '', nurseName: ''})
  const helpingStaffInfoToAdd = ref<HelpingStaffRough>({helpingStaffId: '', helpingStaffName: ''})
  const addDoctorFormRef = ref<FormInstance>()
  const addNurseFormRef = ref<FormInstance>()
  const addHelpingStaffFormRef = ref<FormInstance>()
  const doctorInfoOptions = ref<DoctorRough[]>([])
  const doctorInfoLoading = ref(false)
  const nurseInfoOptions = ref<NurseRough[]>([])
  const nurseInfoLoading = ref(false)
  const helpingStaffInfoOptions = ref<HelpingStaffRough[]>([])
  const helpingStaffInfoLoading = ref(false)
  const addDoctorFormRules = ref<FormRules<DoctorRough>>({
    doctorId: [
      {required: true, message: 'Please input the doctor name', trigger: 'change'}
    ],
    doctorName: [
      {required: true, message: 'Please input the doctor name', trigger: 'change'}
    ]
  })
  const addNurseFormRules = ref<FormRules<NurseRough>>({
    nurseId: [
      {required: true, message: 'Please input the nurse name', trigger: 'change'}
    ],
    nurseName: [
      {required: true, message: 'Please input the nurse name', trigger: 'change'}
    ]
  })
  const addHelpingStaffFormRules = ref<FormRules<HelpingStaffRough>>({
    helpingStaffId: [
      {required: true, message: 'Please input the helping staff name', trigger: 'change'}
    ],
    helpingStaffName: [
      {required: true, message: 'Please input the helping staff name', trigger: 'change'}
    ]
  })

  const handleAddEmployeeButton = (userType: UserType) => {
    employeeType.value = userType
    doctorInfoToAdd.value = {doctorId: '', doctorName: ''}
    nurseInfoToAdd.value = {nurseId: '', nurseName: ''}
    helpingStaffInfoToAdd.value = {helpingStaffId: '', helpingStaffName: ''}
    addEmployeeDialogButtonDisabled.value = false
    addEmployeeDialogVisible.value = true
  }
  const handleDeleteEmployeeButton = (userType: UserType, userId: string) => {
    switch (userType) {
      case UserType.Doctor:
        itemToRecord.value.doctorRoughArr = itemToRecord.value.doctorRoughArr.filter((item: DoctorRough) => item.doctorId !== userId)
        break
      case UserType.Nurse:
        itemToRecord.value.nurseRoughArr = itemToRecord.value.nurseRoughArr.filter((item: NurseRough) => item.nurseId !== userId)
        break
      case UserType.HelpingStaff:
        itemToRecord.value.helpingStaffRoughArr = itemToRecord.value.helpingStaffRoughArr.filter((item: HelpingStaffRough) => item.helpingStaffId !== userId)
        break
      default:
        console.error('Invalid user type: ' + userType)
    }
  }
  const handleAddEmployeeDialogConfirm = async () => {
    addEmployeeDialogButtonDisabled.value = true
    const submitValue = {
      userType: employeeType.value,
      doctorId: doctorInfoToAdd.value.doctorName,
      nurseId: nurseInfoToAdd.value.nurseName,
      helpingStaffId: helpingStaffInfoToAdd.value.helpingStaffName
    }
    let userName = ''
    await axios.get(rootOfPath + '/get-employee-name-by-id', {params: submitValue})
      .then((response)=>{
        userName = response.data.results
      })
    let formValid = false
    switch (employeeType.value) {
      case UserType.Doctor:
        submitValue.doctorId = doctorInfoToAdd.value.doctorId
        await addDoctorFormRef.value?.validate((valid)=>{
          formValid = valid
        })
        break
      case UserType.Nurse:
        submitValue.nurseId = nurseInfoToAdd.value.nurseId
        await addNurseFormRef.value?.validate((valid)=>{
          formValid = valid
        })
        break
      case UserType.HelpingStaff:
        submitValue.helpingStaffId = helpingStaffInfoToAdd.value.helpingStaffId
        await addHelpingStaffFormRef.value?.validate((valid)=>{
          formValid = valid
        })
        break
      default:
        console.error('Invalid employee type: ' + employeeType.value)
    }
    if(!formValid){
      addEmployeeDialogButtonDisabled.value = false
      return
    }
    switch (employeeType.value){
      case UserType.Doctor:
        itemToRecord.value.doctorRoughArr.forEach((item: DoctorRough) => {
          if(item.doctorId === submitValue.doctorId){
            ElMessage.error('This doctor has been added')
            addEmployeeDialogButtonDisabled.value = false
          }
        })
        if(!addEmployeeDialogButtonDisabled.value){
          return
        }
        itemToRecord.value.doctorRoughArr.push({doctorId: doctorInfoToAdd.value.doctorId, doctorName: userName})
        break
      case UserType.Nurse:
        itemToRecord.value.nurseRoughArr.forEach((item: NurseRough) => {
          if(item.nurseId === submitValue.nurseId){
            ElMessage.error('This nurse has been added')
            addEmployeeDialogButtonDisabled.value = false
          }
        })
        if(!addEmployeeDialogButtonDisabled.value){
          return
        }
        itemToRecord.value.nurseRoughArr.push({nurseId: nurseInfoToAdd.value.nurseId, nurseName: userName})
        break
      case UserType.HelpingStaff:
        itemToRecord.value.helpingStaffRoughArr.forEach((item: HelpingStaffRough) => {
          if(item.helpingStaffId === submitValue.helpingStaffId){
            ElMessage.error('This helping staff has been added')
            addEmployeeDialogButtonDisabled.value = false
          }
        })
        if(!addEmployeeDialogButtonDisabled.value){
          return
        }
        itemToRecord.value.helpingStaffRoughArr.push({helpingStaffId: helpingStaffInfoToAdd.value.helpingStaffId, helpingStaffName: userName})
        break
      default:
        console.error('Invalid employee type: ' + employeeType.value)
    }
    addEmployeeDialogVisible.value = false
    ElMessage.success('Add collaborator successfully')
  }
  const handleAddEmployeeDialogCancel = () => {
    addEmployeeDialogVisible.value = false
  }

  const doctorInfoRemoteMethod = (query: string) => {
    doctorInfoRemoteMethodUsedInAddCollaborator(query, config.userId, config.userType, doctorInfoOptions, doctorInfoLoading)
  }
  const nurseInfoRemoteMethod = (query: string) => {
    nurseInfoRemoteMethodUsedInAddCollaborator(query, config.userId, config.userType, nurseInfoOptions, nurseInfoLoading)
  }
  const helpingStaffInfoRemoteMethod = (query: string) => {
    helpingStaffInfoRemoteMethodUsedInAddCollaborator(query, config.userId, config.userType, helpingStaffInfoOptions, helpingStaffInfoLoading)
  }

  watch(employeeType, (newValue) => {
    switch (newValue) {
      case UserType.Doctor:
        addEmployeeDialogTitle.value = 'Add Doctor'
        break
      case UserType.Nurse:
        addEmployeeDialogTitle.value = 'Add Nurse'
        break
      case UserType.HelpingStaff:
        addEmployeeDialogTitle.value = 'Add Helping Staff'
        break
      default:
        console.error('Invalid employee type: ' + newValue)
    }
  })
  watch(() => doctorInfoToAdd.value.doctorName, () => {
    doctorInfoToAdd.value.doctorId = doctorInfoToAdd.value.doctorName
  })
  watch(() => nurseInfoToAdd.value.nurseName, () => {
    nurseInfoToAdd.value.nurseId = nurseInfoToAdd.value.nurseName
  })
  watch(() => helpingStaffInfoToAdd.value.helpingStaffName, () => {
    helpingStaffInfoToAdd.value.helpingStaffId = helpingStaffInfoToAdd.value.helpingStaffName
  })

  return {
    addEmployeeDialogVisible,
    employeeType,
    addEmployeeDialogTitle,
    addEmployeeDialogButtonDisabled,
    doctorInfoToAdd,
    nurseInfoToAdd,
    helpingStaffInfoToAdd,
    addDoctorFormRef,
    addNurseFormRef,
    addHelpingStaffFormRef,
    doctorInfoOptions,
    doctorInfoLoading,
    nurseInfoOptions,
    nurseInfoLoading,
    helpingStaffInfoOptions,
    helpingStaffInfoLoading,
    addDoctorFormRules,
    addNurseFormRules,
    addHelpingStaffFormRules,
    handleAddEmployeeButton,
    handleDeleteEmployeeButton,
    handleAddEmployeeDialogConfirm,
    handleAddEmployeeDialogCancel,
    doctorInfoRemoteMethod,
    nurseInfoRemoteMethod,
    helpingStaffInfoRemoteMethod
  }
}