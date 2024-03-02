<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ElCarousel } from 'element-plus'
import { useRouter } from 'vue-router'
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../stores/config'
import { ElScrollbar } from 'element-plus'
import {departmentRemoteMethod} from "../utils/remote.ts"

const config = useConfigStore()
const rootOfPath = config.rootOfPath


const identity = ref('patient')
const registerCarouselRef = ref<any>()
// scrollbar
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>()
const handleRegisterSwitch = (value: string) => {
  console.log(`switch to the form of ${value}`)
  if (value === 'patient') {
    registerCarouselRef.value.setActiveItem(0)
  } else if (value === 'doctor') {
    registerCarouselRef.value.setActiveItem(1)
  } else if (value === 'nurse') {
    registerCarouselRef.value.setActiveItem(2)
  } else if (value === 'helpingStaff') {
    registerCarouselRef.value.setActiveItem(3)
  }
  scrollbarRef.value?.setScrollTop(0)
}
const birthdateDisabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const registerSuccessMessageDialogVisible = ref(false)
const registerSubmitMessage = ref('')
const newUserId = ref('')
const router = useRouter()
const registerSuccessMessageDialogCloseHandle = () => {
  registerSuccessMessageDialogVisible.value = false
  newUserId.value = ''
  router.push('/login-or-register/login')
}
const registerFailedMessageDialogVisible = ref(false)
const registerFailedMessage = ref('')
const registerFailedMessageDialogCloseHandle = () => {
  registerFailedMessageDialogVisible.value = false
}
const resetInvalidFormField = (invalidFormFieldArr: Array<string>, formName: string) => {
  invalidFormFieldArr.forEach((formField: string) => {
    if (formName === 'patient') {
      patientRegisterForm.value[formField]=''
    } else if (formName === 'doctor') {
      doctorRegisterForm.value[formField]=''
    } else if (formName === 'nurse') {
      nurseRegisterForm.value[formField]=''
    } else if (formName === 'helpingStaff') {
      helpingStaffRegisterForm.value[formField]=''
    }
  })
}
const patientButtonDisabled = ref(false)
const doctorButtonDisabled = ref(false)
const nurseButtonDisabled = ref(false)
const helpingStaffButtonDisabled = ref(false)
// reset particular form
const resetRegisterForm = (form: FormInstance | undefined) => {
  if (!form) return
  form.resetFields()
}
const setFormButtonDisabledValue = (formName: string, value: boolean) => {
  if (formName === 'patient') {
    patientButtonDisabled.value = value
  } else if (formName === 'doctor') {
    doctorButtonDisabled.value = value
  } else if (formName === 'nurse') {
    nurseButtonDisabled.value = value
  } else if (formName === 'helpingStaff') {
    helpingStaffButtonDisabled.value = value
  }
}
// submit particular form
const submitRegisterForm = async (form: FormInstance | undefined, fromValue: PatientRegisterForm| DoctorRegisterForm | NurseRegisterForm | HelpingStaffRegisterForm | undefined , formName: string) => {
  if (!form || !fromValue) return
  setFormButtonDisabledValue(formName, true)
  await form.validate((valid, fields) => {
    if (valid) {
      const formValueCopy = JSON.parse(JSON.stringify(fromValue))
      formValueCopy.formName = formName
      axios.post(rootOfPath + `/register-form-submit`, formValueCopy).then((response: AxiosResponse) => {
        console.log(response)
        newUserId.value = response.data.results.userId
        registerSubmitMessage.value = 'Your account has already been created. Your user id is ' + newUserId.value + '.'
        registerSuccessMessageDialogVisible.value = true
      }).catch((err: any) => {
        console.log(err)
        registerFailedMessage.value = err.response.data.results.notice
        const invalidFormFieldArr: Array<string> = err.response.data.results.invalidFormField
        resetInvalidFormField(invalidFormFieldArr, formName)
        registerFailedMessageDialogVisible.value = true

      }).finally(() => {
        setFormButtonDisabledValue(formName, false)
      })
      console.log('submit! ')

    } else {
      console.log('error submit!',fields)
      setFormButtonDisabledValue(formName, false)
    }
  })
}
interface EmployeeRegisterForm{
  name: string
  gender: string
  position: string
  birthdate: string
  phone: string
  address: string
  dateOfHire: string
  // dateOfDismiss: string  // this should not be recorded when register
  supervisorId: string
  // salary: string  // this should not be decided by the employee
  password: string
  confirmPassword: string
  [key: string]: any
}


// resources for patient
interface PatientRegisterForm {
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
  password: string
  confirmPassword: string
  [key: string]: any
}
const patientRegisterFormRef = ref<FormInstance>()
const patientRegisterForm = ref<PatientRegisterForm>({
  name: '',
  gender: '',
  birthdate: '',
  maritalStatus: '',
  occupation: '',
  birthplace: '',
  nationality: '',
  identificationDocumentType: '',
  identificationNumber: '',
  phone: '',
  address: '',
  bloodType: '',
  allergens: [],
  initialDiagnosisDate: '',
  emergencyContact: '',
  emergencyContactRelationship: '',
  emergencyContactPhone: '',
  emergencyContactAddress: '',
  password: '',
  confirmPassword: '',
})

// @ts-ignore
const patientValidatePassword = (rule: any, value: string, callback: any) => { 
  if (value === '') {
    callback(new Error('Please enter password'))
  } else {
    if (patientRegisterForm.value.confirmPassword !== '') {
      if (!patientRegisterFormRef.value) return
      patientRegisterFormRef.value.validateField('confirmPassword')
    }
    callback()
  }
}
// @ts-ignore
const patientValidateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please enter password again'))
  } else if (value !== patientRegisterForm.value.password) {
    callback(new Error('The two passwords do not match'))
  } else {
    callback()
  }
}
const patientRegisterRules = ref<FormRules<PatientRegisterForm>>({
  name :[
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  gender: [
    {required: true, message: 'Please select gender', trigger: 'change'}
  ],
  birthdate: [
    {required: true, message: 'Please select birthdate', trigger: 'change'}
  ],
  maritalStatus: [
    {required: true, message: 'Please select marital status', trigger: 'change'}
  ],
  initialDiagnosisDate: [
    {required: true, message: 'Please select the initial diagnosis date', trigger: 'change'}
  ],
  password: [
    {required: true, validator: patientValidatePassword, trigger: 'change'}
  ],
  confirmPassword: [
    {required: true, validator: patientValidateConfirmPassword, trigger: 'change'}
  ],
  identificationDocumentType: [
    {required: true, message: 'Please select or enter identification document type', trigger: 'change'}
  ],
  identificationNumber: [
    {required: true, message: 'Please enter identification number', trigger: 'change'}
  ],
  phone: [
    {required: true, message: 'Please enter phone number', trigger: 'change'}
  ],
  address: [
    {required: true, message: 'Please enter address', trigger: 'change'}
  ],
  bloodType: [
    {required: false}
  ],
  allergens: [
    {required: false}
  ],
  emergencyContact: [
    {required: false}
  ],
  emergencyContactRelationship: [
    {required: false}
  ],
  emergencyContactPhone: [
    {required: false}
  ],
  emergencyContactAddress: [
    {required: false}
  ],
})
// reset the initial diagnosis date when the birthdate change if necessary
watch(() => patientRegisterForm.value.birthdate, (newValue, oldValue) => {
  console.log('birthdate changed')
  console.log(newValue)
  console.log(oldValue)
  if (patientRegisterForm.value.initialDiagnosisDate === '') return
  if (patientRegisterForm.value.initialDiagnosisDate < newValue) {
    patientRegisterForm.value.initialDiagnosisDate = ''
  }
})
const patientInitialDiagnosisDisabledDate = (time: Date) => {
  if (time.getTime() > Date.now()) return true
  return time.getTime() < new Date(patientRegisterForm.value.birthdate).getTime();
}


// resources for doctor
interface DoctorRegisterForm extends EmployeeRegisterForm{
  department: string
  licenseNumber: string
}
const doctorRegisterFormRef = ref<FormInstance>()
const doctorRegisterForm = ref<DoctorRegisterForm>({
  name: '',
  gender: '',
  position: '',
  birthdate: '',
  phone: '',
  address: '',
  dateOfHire: '',
  supervisorId: '',
  // salary: '',
  department: '',
  licenseNumber: '',
  password: '',
  confirmPassword: '',
})

// @ts-ignore
const doctorValidatePassword = (rule: any, vale: string, callback: any) => {
  if (vale === '') {
    callback(new Error('Please enter password'))
  } else {
    if (doctorRegisterForm.value.confirmPassword !== '') {
      if (!doctorRegisterFormRef.value) return
      doctorRegisterFormRef.value.validateField('confirmPassword')
    }
    callback()
  }
}
// @ts-ignore
const doctorValidateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please enter password again'))
  } else if (value !== doctorRegisterForm.value.password) {
    callback(new Error('The two passwords do not match'))
  } else {
    callback()
  }
}
// @ts-ignore
const doctorValidateSupervisorId = (rule: any, value: string, callback: any) => {
  axios.get(rootOfPath + `/employee-supervisor-id-validate?formName=doctor&supervisorId=${value}`).then((response: AxiosResponse) => {
    console.log(response.data.message)
    if(response.data.message === '' || value=== '') {callback()}
    else {callback(response.data.message)}
  }).catch((err: any) => {
   console.log(err)
  })
}
const doctorRegisterRules = ref<FormRules<DoctorRegisterForm>>({
  name: [
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  gender: [
    {required: true, message: 'Please select gender', trigger: 'change'}
  ],
  birthdate: [
    {required: true, message: 'Please select birthdate', trigger: 'change'}
  ],
  dateOfHire: [
    {required: true, message: 'Please select date of hire', trigger: 'change'}
  ],
  licenseNumber: [
    {required: true, message: 'Please enter license number', trigger: 'change'}
  ],
  position: [
    {required: true, message: 'Please enter position', trigger: 'change'}
  ],
  phone: [
    {required: true, message: 'Please enter phone number', trigger: 'change'}
  ],
  address: [
    {required: true, message: 'Please enter address', trigger: 'change'}
  ],  
  password: [
    {required: true, validator: doctorValidatePassword, trigger: 'change'}
  ],
  confirmPassword: [
    {required: true, validator: doctorValidateConfirmPassword, trigger: 'change'}
  ],
  department: [
    {required: true, message: 'Please select department', trigger: 'change'}
  ],
  supervisorId: [
    {validator: doctorValidateSupervisorId}
  ],
})
// reset the date of hire when the birthdate change if necessary
watch(()=> doctorRegisterForm.value.birthdate, (newValue, oldValue) => {
  console.log('birthdate changed')
  console.log(newValue)
  console.log(oldValue)
  if (doctorRegisterForm.value.dateOfHire === '') return
  if (doctorRegisterForm.value.dateOfHire < newValue) {
    doctorRegisterForm.value.dateOfHire = ''
  }
})
const doctorDateOfHireDisabledDate = (time: Date) => {
  if (time.getTime() > Date.now()) return true
  return time.getTime() < new Date(doctorRegisterForm.value.birthdate).getTime();

}
const doctorDepartmentOptions = ref<string[]>([])
const doctorDepartmentLoading = ref(false)
const doctorDepartmentRemoteMethod = (query: string) => {
  departmentRemoteMethod(query, doctorDepartmentOptions, doctorDepartmentLoading)
}

// resources for nurse

interface NurseRegisterForm extends EmployeeRegisterForm{
  roomId: string, 
  licenseNumber: string,
}
const nurseRegisterFormRef = ref<FormInstance>()
const nurseRegisterForm = ref<NurseRegisterForm>({
  name: '',
  gender: '',
  position: '',
  birthdate: '',
  phone: '',
  address: '',
  dateOfHire: '',
  supervisorId: '',
  roomId: '',
  licenseNumber: '',
  password: '',
  confirmPassword: '',
})
// @ts-ignore
const nurseValidatePassword = (rule: any, vale: string, callback: any) => {
  if (vale === '') {
    callback(new Error('Please enter password'))
  } else {
    if (nurseRegisterForm.value.confirmPassword !== '') {
      if (!nurseRegisterFormRef.value) return
      nurseRegisterFormRef.value.validateField('confirmPassword')
    }
    callback()
  }
}
// @ts-ignore
const nurseValidateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please enter password again'))
  } else if (value !== nurseRegisterForm.value.password) {
    callback(new Error('The two passwords do not match'))
  } else {
    callback()
  }
}
// @ts-ignore
const nurseValidateSupervisorId = (rule: any, value: string, callback: any) => {
  axios.get(rootOfPath + `/employee-supervisor-id-validate?formName=nurse&supervisorId=${value}`).then((response: AxiosResponse) => {
    console.log(response.data.message)
    if(response.data.message === '' || value=== '') {callback()}
    else {callback(response.data.message)}
  }).catch((err: any) => {
   console.log(err)
  })
}
const nurseRegisterRules = ref<FormRules<NurseRegisterForm>>({
  name: [
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  gender: [
    {required: true, message: 'Please select gender', trigger: 'change'}
  ],
  birthdate: [
    {required: true, message: 'Please select birthdate', trigger: 'change'}
  ],
  dateOfHire: [
    {required: true, message: 'Please select date of hire', trigger: 'change'}
  ],
  licenseNumber: [
    {required: true, message: 'Please enter license number', trigger: 'change'}
  ],
  position: [
    {required: true, message: 'Please enter position', trigger: 'change'}
  ],
  phone: [
    {required: true, message: 'Please enter phone number', trigger: 'change'}
  ],
  address: [
    {required: true, message: 'Please enter address', trigger: 'change'}
  ],
  password: [
    {required: true, validator: nurseValidatePassword, trigger: 'change'}
  ],
  confirmPassword: [
    {required: true, validator: nurseValidateConfirmPassword, trigger: 'change'}
  ],
  roomId: [
    {required: true, message: 'Please select room', trigger: 'change'}
  ],
  supervisorId: [
    {validator: nurseValidateSupervisorId}
  ],
})
watch(()=> nurseRegisterForm.value.birthdate, (newValue, oldValue) => {
  console.log('birthdate changed')
  console.log(newValue)
  console.log(oldValue)
  if (nurseRegisterForm.value.dateOfHire === '') return
  if (nurseRegisterForm.value.dateOfHire < newValue) {
    nurseRegisterForm.value.dateOfHire = ''
  }
})
const nurseDateOfHireDisabledDate = (time: Date) => {
  if (time.getTime() > Date.now()) return true
  return time.getTime() < new Date(nurseRegisterForm.value.birthdate).getTime();

}


// resources for helping staff
interface HelpingStaffRegisterForm extends EmployeeRegisterForm{

}
const helpingStaffRegisterFormRef = ref<FormInstance>()
const helpingStaffRegisterForm = ref<HelpingStaffRegisterForm>({
  name: '',
  gender: '',
  position: '',
  birthdate: '',
  phone: '',
  address: '',
  dateOfHire: '',
  supervisorId: '',
  password: '',
  confirmPassword: '',
})
// @ts-ignore
const helpingStaffValidatePassword = (rule: any, vale: string, callback: any) => {
  if (vale === '') {
    callback(new Error('Please enter password'))
  } else {
    if (helpingStaffRegisterForm.value.confirmPassword !== '') {
      if (!helpingStaffRegisterFormRef.value) return
      helpingStaffRegisterFormRef.value.validateField('confirmPassword')
    }
    callback()
  }
}
// @ts-ignore
const helpingStaffValidateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please enter password again'))
  } else if (value !== helpingStaffRegisterForm.value.password) {
    callback(new Error('The two passwords do not match'))
  } else {
    callback()
  }
}
// @ts-ignore
const helpingStaffValidateSupervisorId = (rule: any, value: string, callback: any) => {
  axios.get(rootOfPath + `/employee-supervisor-id-validate?formName=helpingStaff&supervisorId=${value}`).then((response: AxiosResponse) => {
    console.log(response.data.message)
    if(response.data.message === '' || value=== '') {callback()}
    else {callback(response.data.message)}
  }).catch((err: any) => {
   console.log(err)
  })
}
const helpingStaffRegisterRules = ref<FormRules<HelpingStaffRegisterForm>>({
  name: [
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  gender: [
    {required: true, message: 'Please select gender', trigger: 'change'}
  ],
  birthdate: [
    {required: true, message: 'Please select birthdate', trigger: 'change'}
  ],
  dateOfHire: [
    {required: true, message: 'Please select date of hire', trigger: 'change'}
  ],
  position: [
    {required: true, message: 'Please enter position', trigger: 'change'}
  ],
  phone: [
    {required: true, message: 'Please enter phone number', trigger: 'change'}
  ],
  address: [
    {required: true, message: 'Please enter address', trigger: 'change'}
  ],
  password: [
    {required: true, validator: helpingStaffValidatePassword, trigger: 'change'}
  ],
  confirmPassword: [
    {required: true, validator: helpingStaffValidateConfirmPassword, trigger: 'change'}
  ],
  supervisorId: [
    {validator: helpingStaffValidateSupervisorId}
  ],
})
watch(()=> helpingStaffRegisterForm.value.birthdate, (newValue, oldValue) => {
  console.log('birthdate changed')
  console.log(newValue)
  console.log(oldValue)
  if (helpingStaffRegisterForm.value.dateOfHire === '') return
  if (helpingStaffRegisterForm.value.dateOfHire < newValue) {
    helpingStaffRegisterForm.value.dateOfHire = ''
  }
})
const helpingStaffDateOfHireDisabledDate = (time: Date) => {
  if (time.getTime() > Date.now()) return true
  return time.getTime() < new Date(helpingStaffRegisterForm.value.birthdate).getTime();

}

</script>

<template>
  <el-dialog
    title="Register Success"
    v-model="registerSuccessMessageDialogVisible"
    width="30%"
    :before-close="registerSuccessMessageDialogCloseHandle"
  >
    <span> {{ registerSubmitMessage }} </span>
    <template #footer>
      <el-button @click="registerSuccessMessageDialogCloseHandle">Confirm</el-button>
    </template>
  </el-dialog>

  <el-dialog
    title="Register Failed"
    v-model="registerFailedMessageDialogVisible"
    width="30%"
    :before-close="registerFailedMessageDialogCloseHandle"
  >
    <span> {{ registerFailedMessage }} </span>
    <template #footer>
      <el-button @click="registerFailedMessageDialogCloseHandle">Confirm</el-button>
    </template>
  </el-dialog>
  <div style="display: flex; justify-content: center;">
    <el-radio-group v-model="identity" style="margin-bottom: 18px;">
      <el-radio-button label="patient" @click="handleRegisterSwitch('patient')">Patient</el-radio-button>
      <el-radio-button label="doctor" @click="handleRegisterSwitch('doctor')">Doctor</el-radio-button>
      <el-radio-button label="nurse" @click="handleRegisterSwitch('nurse')">Nurse</el-radio-button>
      <el-radio-button label="helpingStaff" @click="handleRegisterSwitch('helpingStaff')">Helping Staff</el-radio-button>
    </el-radio-group>
  </div>

  <!-- <el-text type="info">Scroll through the table and fill in</el-text> -->

  <!-- <el-scrollbar height="500px" ref="scrollbarRef"> -->
    <el-carousel
      indicator-position="none"
      :autoplay=false
      :loop=false
      arrow="never"
      ref="registerCarouselRef"
      height="auto"
    >
      <el-carousel-item style="height: 1408px">
        <el-form
          ref="patientRegisterFormRef"
          :model="patientRegisterForm"
          label-position="top"
          label-width="80px"
          :rules="patientRegisterRules"
        >
          <el-form-item label="Name" prop="name">
            <el-input v-model="patientRegisterForm.name" placeholder="Enter name"></el-input>
          </el-form-item>
          
          <el-row>
            <el-col :span="12">
              <el-form-item label="Gender" prop="gender" class='left-input-select-box'>
                <el-select v-model="patientRegisterForm.gender" placeholder="Select gender">
                  <el-option label="Male" value="male"></el-option>
                  <el-option label="Female" value="female"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Birthdate" prop="birthdate">
                <el-date-picker
                  v-model="patientRegisterForm.birthdate"
                  type="date"
                  placeholder="Select birthdate"
                  :disabledDate="birthdateDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Marital Status" prop="maritalStatus" class='left-input-select-box'>
                <el-select v-model="patientRegisterForm.maritalStatus" placeholder="Select marital status">
                  <el-option label="Single" value="single"></el-option>
                  <el-option label="Married" value="married"></el-option>
                  <el-option label="Divorced" value="divorced"></el-option>
                  <el-option label="Widowed" value="widowed"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Initial Diagnosis Date" prop="initialDiagnosisDate">
                <el-date-picker
                  v-model="patientRegisterForm.initialDiagnosisDate"
                  type="date"
                  placeholder="Select initial diagnosis date"
                  :disabledDate="patientInitialDiagnosisDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Password" prop="password" class='left-input-select-box'>
                <el-input v-model="patientRegisterForm.password" placeholder="Enter password" type="password"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Confirm Password" prop="confirmPassword">
                <el-input v-model="patientRegisterForm.confirmPassword" placeholder="Enter password again" type="password"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Nationality" prop="nationality" class='left-input-select-box'>
                  <el-input v-model="patientRegisterForm.nationality" placeholder="Enter nationality"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Occupation" prop="occupation">
                <el-input v-model="patientRegisterForm.occupation" placeholder="Enter occupation"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Identification Document Type" prop="identificationDocumentType">
            <el-select 
              v-model="patientRegisterForm.identificationDocumentType" 
              placeholder="Select or enter your identification document type"
              filterable
              allow-create
              default-first-option
              class="long-select-box"
            >
              <el-option label="ID Card" value="idCard"></el-option>
              <el-option label="Mainland Travel Permit" value="mainlandTravelPermit"></el-option>
              <el-option label="Permanent Residency Card" value="permanentResidencyCard"></el-option>
              <el-option label="Passport" value="passport"></el-option>
            </el-select>
            <el-text type="info" size="small">Enter your document type and press "Enter" if you cannot find it in the list.</el-text>
          </el-form-item>

          <el-form-item label="Identification Number" prop="identificationNumber">
            <el-input v-model="patientRegisterForm.identificationNumber" placeholder="Enter identification number"></el-input>
          </el-form-item>

          <el-form-item label="Phone" prop="phone">
            <el-input v-model="patientRegisterForm.phone" placeholder="Enter phone number"></el-input>
          </el-form-item>

          <el-form-item label="Address" prop="address">
            <el-input v-model="patientRegisterForm.address" placeholder="Enter address"></el-input>
          </el-form-item>

          <el-form-item label="Birthplace" prop="birthplace">
            <el-input v-model="patientRegisterForm.birthplace" placeholder="Enter birthplace"></el-input>
          </el-form-item>

          <el-form-item label="Blood Type" prop="bloodType" class="long-select-box">
            <el-select 
              v-model="patientRegisterForm.bloodType" 
              placeholder="Select blood type"
              filterable
              allow-create
              default-first-option
              class="long-select-box"
            >
              <el-option label="A" value="a"></el-option>
              <el-option label="B" value="b"></el-option>
              <el-option label="AB" value="ab"></el-option>
              <el-option label="O" value="o"></el-option>
            </el-select>
            <el-text type="info" size="small">Enter your blood type and press "Enter" if you cannot find it in the list.</el-text>
          </el-form-item>
        
          <el-form-item label="Allergens" prop="allergens">
            <el-select 
              v-model="patientRegisterForm.allergens" 
              placeholder="Select or enter your allergens"
              filterable
              allow-create
              multiple
              default-first-option
              class="long-select-box"
              collapse-tags
              :max-collapse-tags="3"
            >
              <el-option label="Pollen" value="a"></el-option>
              <el-option label="Dust mite" value="dustMite"></el-option>
              <el-option label="Soy" value="soy"></el-option>
              <el-option label="Dairy product" value="dairyProduct"></el-option>
            </el-select>
            <el-text type="info" size="small">Enter your allergens and press "Enter" if you cannot find it in the list.</el-text>
          </el-form-item>

          <el-form-item label="Emergency Contact" prop="emergencyContact">
            <el-input v-model="patientRegisterForm.emergencyContact" placeholder="Enter emergency contact"></el-input>
          </el-form-item>

          <el-form-item label="Emergency Contact Relationship" prop="emergencyContactRelationship">
            <el-input v-model="patientRegisterForm.emergencyContactRelationship" placeholder="Enter emergency contact relationship"></el-input>
          </el-form-item>

          <el-form-item label="Emergency Contact Phone" prop="emergencyContactPhone">
            <el-input v-model="patientRegisterForm.emergencyContactPhone" placeholder="Enter emergency contact phone"></el-input>
          </el-form-item>

          <el-form-item label="Emergency Contact Address" prop="emergencyContactAddress">
            <el-input v-model="patientRegisterForm.emergencyContactAddress" placeholder="Enter emergency contact address"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitRegisterForm(patientRegisterFormRef, patientRegisterForm, 'patient')" :disabled="patientButtonDisabled">Register</el-button>
            <el-button @click="resetRegisterForm(patientRegisterFormRef)" :disabled="patientButtonDisabled">Reset</el-button>
          </el-form-item>
        </el-form>
      </el-carousel-item>

      <el-carousel-item style="height: 752px">
        <el-form
          ref="doctorRegisterFormRef"
          :model="doctorRegisterForm"
          label-position="top"
          label-width="80px"
          :rules="doctorRegisterRules"
        >
          <el-form-item label="Name" prop="name">
            <el-input v-model="doctorRegisterForm.name" placeholder="Enter name"></el-input>
          </el-form-item>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Gender" prop="gender" class="left-input-select-box">
                <el-select v-model="doctorRegisterForm.gender" placeholder="Select gender">
                  <el-option label="Male" value="male"></el-option>
                  <el-option label="Female" value="female"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Birthdate" prop="birthdate">
                <el-date-picker
                  v-model="doctorRegisterForm.birthdate"
                  type="date"
                  placeholder="Select birthdate"
                  :disabledDate="birthdateDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="License Number" prop="licenseNumber" class="left-input-select-box">
                <el-input v-model="doctorRegisterForm.licenseNumber" placeholder="Enter license number"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Date of Hire" prop="dateOfHire" class="left-input-select-box">
                <el-date-picker
                  v-model="doctorRegisterForm.dateOfHire"
                  type="date"
                  placeholder="Select date of hire"
                  :disabledDate="doctorDateOfHireDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Password" prop="password" class="left-input-select-box">
                <el-input v-model="doctorRegisterForm.password" placeholder="Enter password" type="password"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Confirm Password" prop="confirmPassword">
                <el-input v-model="doctorRegisterForm.confirmPassword" placeholder="Enter password again" type="password"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Department" prop="department">
            <el-select
              v-model="doctorRegisterForm.department"
              filterable
              remote
              reserve-keyword
              clearable
              placeholder="Enter department"
              :remote-method="doctorDepartmentRemoteMethod"
              :loading="doctorDepartmentLoading"
              class="long-select-box"
            >
              <el-option
                v-for="item in doctorDepartmentOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Position" prop="position">
            <el-input v-model="doctorRegisterForm.position" placeholder="Enter position"></el-input>
          </el-form-item>

          <el-form-item label="Supervisor ID" prop="supervisorId">
            <el-input v-model="doctorRegisterForm.supervisorId" placeholder="Enter supervisor ID"></el-input>
          </el-form-item>

          <el-form-item label="Phone" prop="phone">
            <el-input v-model="doctorRegisterForm.phone" placeholder="Enter phone number"></el-input>
          </el-form-item>

          <el-form-item label="Address" prop="address">
            <el-input v-model="doctorRegisterForm.address" placeholder="Enter address"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitRegisterForm(doctorRegisterFormRef, doctorRegisterForm, 'doctor')">Register</el-button>
            <el-button @click="resetRegisterForm(doctorRegisterFormRef)">Reset</el-button>
          </el-form-item>

        </el-form>
      </el-carousel-item>

      <el-carousel-item style="height: 752px">
        <el-form
          ref="nurseRegisterFormRef"
          :model="nurseRegisterForm"
          label-position="top"
          label-width="80px"
          :rules="nurseRegisterRules"
        >
          <el-form-item label="Name" prop="name">
            <el-input v-model="nurseRegisterForm.name" placeholder="Enter name"></el-input>
          </el-form-item>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Gender" prop="gender" class='left-input-select-box'>
                <el-select v-model="nurseRegisterForm.gender" placeholder="Select gender">
                  <el-option label="Male" value="male"></el-option>
                  <el-option label="Female" value="female"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Birthdate" prop="birthdate">
                <el-date-picker
                  v-model="nurseRegisterForm.birthdate"
                  type="date"
                  placeholder="Select birthdate"
                  :disabledDate="birthdateDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="License Number" prop="licenseNumber" class="left-input-select-box">
                <el-input v-model="nurseRegisterForm.licenseNumber" placeholder="Enter license number"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Date of Hire" prop="dateOfHire">
                <el-date-picker
                  v-model="nurseRegisterForm.dateOfHire"
                  type="date"
                  placeholder="Select date of hire"
                  :disabledDate="nurseDateOfHireDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Password" prop="password" class="left-input-select-box">
                <el-input v-model="nurseRegisterForm.password" placeholder="Enter password" type="password"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Confirm Password" prop="confirmPassword">
                <el-input v-model="nurseRegisterForm.confirmPassword" placeholder="Enter password again" type="password"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Room ID" prop="roomId">
            <el-input v-model="nurseRegisterForm.roomId" placeholder="Enter room ID"></el-input>
          </el-form-item>
    
          <el-form-item label="Position" prop="position">
            <el-input v-model="nurseRegisterForm.position" placeholder="Enter position"></el-input>
          </el-form-item>

          <el-form-item label="Supervisor ID" prop="supervisorId">
            <el-input v-model="nurseRegisterForm.supervisorId" placeholder="Enter supervisor ID"></el-input>
          </el-form-item>

          <el-form-item label="Phone" prop="phone">
            <el-input v-model="nurseRegisterForm.phone" placeholder="Enter phone number"></el-input>
          </el-form-item>

          <el-form-item label="Address" prop="address">
            <el-input v-model="nurseRegisterForm.address" placeholder="Enter address"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitRegisterForm(nurseRegisterFormRef, nurseRegisterForm, 'nurse')">Register</el-button>
            <el-button @click="resetRegisterForm(nurseRegisterFormRef)">Reset</el-button>
          </el-form-item>
        </el-form>
      </el-carousel-item>

      <el-carousel-item style="height: 592px">
        <el-form
          ref="helpingStaffRegisterFormRef"
          :model="helpingStaffRegisterForm"
          label-position="top"
          label-width="80px"
          :rules="helpingStaffRegisterRules"
        >
          <el-form-item label="Name" prop="name">
            <el-input v-model="helpingStaffRegisterForm.name" placeholder="Enter name"></el-input>
          </el-form-item>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Gender" prop="gender" class='left-input-select-box'>
                <el-select v-model="helpingStaffRegisterForm.gender" placeholder="Select gender">
                  <el-option label="Male" value="male"></el-option>
                  <el-option label="Female" value="female"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Birthdate" prop="birthdate">
                <el-date-picker
                  v-model="helpingStaffRegisterForm.birthdate"
                  type="date"
                  placeholder="Select birthdate"
                  :disabledDate="birthdateDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-form-item label="Position" prop="position" class="left-input-select-box">
                <el-input v-model="helpingStaffRegisterForm.position" placeholder="Enter position"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Date of Hire" prop="dateOfHire">
                <el-date-picker
                  v-model="helpingStaffRegisterForm.dateOfHire"
                  type="date"
                  placeholder="Select date of hire"
                  :disabledDate="helpingStaffDateOfHireDisabledDate"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row>
            <el-col :span="12">
              <el-form-item label="Password" prop="password" class="left-input-select-box">
                <el-input v-model="helpingStaffRegisterForm.password" placeholder="Enter password" type="password"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Confirm Password" prop="confirmPassword">
                <el-input v-model="helpingStaffRegisterForm.confirmPassword" placeholder="Enter password again" type="password"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Supervisor ID" prop="supervisorId">
            <el-input v-model="helpingStaffRegisterForm.supervisorId" placeholder="Enter supervisor ID"></el-input>
          </el-form-item>

          <el-form-item label="Phone" prop="phone">
            <el-input v-model="helpingStaffRegisterForm.phone" placeholder="Enter phone number"></el-input>
          </el-form-item>

          <el-form-item label="Address" prop="address">
            <el-input v-model="helpingStaffRegisterForm.address" placeholder="Enter address"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="submitRegisterForm(helpingStaffRegisterFormRef, helpingStaffRegisterForm, 'helpingStaff')">Register</el-button>
            <el-button @click="resetRegisterForm(helpingStaffRegisterFormRef)">Reset</el-button>
          </el-form-item>
        </el-form>
      </el-carousel-item>
    </el-carousel>
  <!-- </el-scrollbar> -->
  <!-- <el-text type="info">Scroll through the from and fill in</el-text> -->
  
</template>

<style scoped>
.left-input-select-box {
  width: 214px;
}
.long-select-box {
  width: 440px;
}
</style>
