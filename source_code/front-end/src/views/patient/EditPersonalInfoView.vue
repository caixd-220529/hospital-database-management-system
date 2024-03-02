<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../stores/config'
import { PatientInfo, PatientInfoKey } from '../../types/user'
import { ref, watch, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const getData = ref(false)
const config = useConfigStore()
const rootOfPath = config.rootOfPath
const originalPatientInfo: PatientInfo = {
  patientId: '',
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
}

const getPatientOriginalInfo = async () => {
  axios.get(rootOfPath + `/get-patient-info?patientId=${config.userId}`).then((response: AxiosResponse) => {
    for (const key in originalPatientInfo) {
      if (response.data.results[key] === null|| response.data.results[key] === undefined) {
        console.error(`key: ${key} is null`)
      }
      originalPatientInfo[key as PatientInfoKey] = response.data.results[key]
      patientEditForm.value[key as PatientInfoKey] = response.data.results[key]
    }
    getData.value = true
    console.log('get patient original info successfully')
  }).catch((err: any) => {
    console.log(err)
  })
}
onMounted(() => {
  getPatientOriginalInfo()
})

// set whether the attributes are allowed to be edited
const patientIdDisabled = true
const nameDisabled = false
const genderDisabled = false
const birthdateDisabled = false
const maritalStatusDisabled = false
const occupationDisabled = false
const birthplaceDisabled = false
const nationalityDisabled = false
const identificationDocumentTypeDisabled = false
const identificationNumberDisabled = false
const phoneDisabled = false
const addressDisabled = false
const bloodTypeDisabled = false
const allergensDisabled = false
const initialDiagnosisDateDisabled = false
const emergencyContactDisabled = false
const emergencyContactRelationshipDisabled = false
const emergencyContactPhoneDisabled = false
const emergencyContactAddressDisabled = false

const patientEditForm = ref<PatientInfo>({
  patientId: '',
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
})
const patientEditFormRef = ref<FormInstance>()
const patientEditRules = ref<FormRules<PatientInfo>>({
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
})

watch(() => patientEditForm.value.birthdate, (newValue) => {
  if (patientEditForm.value.initialDiagnosisDate === '') return
  if (patientEditForm.value.initialDiagnosisDate < newValue) {
    patientEditForm.value.initialDiagnosisDate = ''
  }
})
const patientInitialDiagnosisDisabledDate = (time: Date) => {
  if (time.getTime() > Date.now()) return true
  return time.getTime() < new Date(patientEditForm.value.birthdate).getTime();

}
const birthdateDisabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}
const resetForm = (form: FormInstance | undefined) => {
  if (!form) return
  for (const key in originalPatientInfo) {
    //@ts-ignore
    patientEditForm.value[key] = originalPatientInfo[key]
  }
}
const buttonDisabled = ref(false)
const failedMessage = ref('')
const failedMessageDialogVisible = ref(false)
const submitForm = async (form: FormInstance | undefined) => {
  if (!form) return
  buttonDisabled.value = true
  await form.validate((valid: boolean) => {
    console.log(valid)
    if (valid) {
      axios.post(rootOfPath + '/edit-patient-info', patientEditForm.value).then(async () => {
        await getPatientOriginalInfo()
        ElMessage({
          message: 'Edit successfully',
          type: 'success',
        })
      }).catch((err: any) => {
        console.log(err)
        failedMessage.value = err.response.data.results.notice
        const invalidFormFieldArr: Array<string> = err.response.data.results.invalidFormField
        invalidFormFieldArr.forEach((formField: string) => {
          //@ts-ignore
          patientEditForm.value[formField] = originalPatientInfo[formField]
        })
        failedMessageDialogVisible.value = true
      }).finally(() => {
        buttonDisabled.value = false
      })
    } else {
      console.log('error submit')
      buttonDisabled.value = false
    }
  })
}
</script>

<template>
  <el-dialog
    title="Failed"
    v-model="failedMessageDialogVisible"
  >
    <span>{{ failedMessage }}</span>
    <template #footer>
      <el-button type="primary" @click="failedMessageDialogVisible = false">Confirm</el-button>
    </template>
  </el-dialog>

  <div v-loading="!getData" class="form-container">
    <el-form
      ref="patientEditFormRef"
      :model="patientEditForm"
      :rules="patientEditRules"
      label-position="top"
    >
      <el-form-item label="Patient ID" prop="patientId">
        <el-input v-model="patientEditForm.patientId" :disabled="patientIdDisabled"></el-input>
      </el-form-item>

      <el-form-item label="Name" prop="name">
        <el-input v-model="patientEditForm.name" :disabled="nameDisabled" placeholder="Enter name"></el-input>
      </el-form-item>

      <el-form-item label="Gender" prop="gender">
        <el-select v-model="patientEditForm.gender" :disabled="genderDisabled" placeholder="Select gender" style="width: 100%">
          <el-option label="Male" value="male"></el-option>
          <el-option label="Female" value="female"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Birthdate" prop="birthdate">
        <el-date-picker
          v-model="patientEditForm.birthdate"
          type="date"
          placeholder="Select birthdate"
          :disabled="birthdateDisabled"
          style="width: 100%"
          :disabledDate="birthdateDisabledDate"
        ></el-date-picker>
      </el-form-item>

      <el-form-item label="Marital Status" prop="maritalStatus">
        <el-select 
          v-model="patientEditForm.maritalStatus" 
          :disabled="maritalStatusDisabled" 
          placeholder="Select marital status"
          style="width: 100%"
        >
          <el-option label="Single" value="single"></el-option>
          <el-option label="Married" value="married"></el-option>
          <el-option label="Divorced" value="divorced"></el-option>
          <el-option label="Widowed" value="widowed"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Initial Diagnosis Date" prop="initialDiagnosisDate">
        <el-date-picker
          v-model="patientEditForm.initialDiagnosisDate"
          type="date"
          placeholder="Select initial diagnosis date"
          :disabled="initialDiagnosisDateDisabled"
          style="width: 100%"
          :disabledDate="patientInitialDiagnosisDisabledDate"
        ></el-date-picker>
      </el-form-item>

      <el-form-item label="Identification Document Type" prop="identificationDocumentType">
        <el-select 
          v-model="patientEditForm.identificationDocumentType" 
          placeholder="Select or enter your identification document type"
          filterable
          allow-create
          default-first-option
          style="width: 100%"
          :disabled="identificationDocumentTypeDisabled"
        >
          <el-option label="ID Card" value="idCard"></el-option>
          <el-option label="Mainland Travel Permit" value="mainlandTravelPermit"></el-option>
          <el-option label="Permanent Residency Card" value="permanentResidencyCard"></el-option>
          <el-option label="Passport" value="passport"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Identification Number" prop="identificationNumber">
        <el-input v-model="patientEditForm.identificationNumber" :disabled="identificationNumberDisabled" placeholder="Enter identification number"></el-input>
      </el-form-item>

      <el-form-item label="Phone" prop="phone">
        <el-input v-model="patientEditForm.phone" :disabled="phoneDisabled" placeholder="Enter phone number"></el-input>
      </el-form-item>

      <el-form-item label="Address" prop="address">
        <el-input v-model="patientEditForm.address" :disabled="addressDisabled" placeholder="Enter address"></el-input>
      </el-form-item>

      <el-form-item label="Occupation" prop="occupation">
        <el-input v-model="patientEditForm.occupation" :disabled="occupationDisabled" placeholder="Enter occupation"></el-input>
      </el-form-item>

      <el-form-item label="Birthplace" prop="birthplace">
        <el-input v-model="patientEditForm.birthplace" :disabled="birthplaceDisabled" placeholder="Enter birthplace"></el-input>
      </el-form-item>

      <el-form-item label="Nationality" prop="nationality">
        <el-input v-model="patientEditForm.nationality" :disabled="nationalityDisabled" placeholder="Enter nationality"></el-input>
      </el-form-item>

      <el-form-item label="Blood Type" prop="bloodType">
        <el-select 
          v-model="patientEditForm.bloodType" 
          placeholder="Select blood type"
          filterable
          allow-create
          default-first-option
          style="width: 100%"
          :disabled="bloodTypeDisabled"
        >
          <el-option label="A" value="a"></el-option>
          <el-option label="B" value="b"></el-option>
          <el-option label="AB" value="ab"></el-option>
          <el-option label="O" value="o"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Allergens" prop="allergens">
        <el-select 
          v-model="patientEditForm.allergens" 
          placeholder="Select or enter your allergens"
          filterable
          allow-create
          multiple
          default-first-option
          style="width: 100%"
          collapse-tags
          :max-collapse-tags="3"
          :disabled="allergensDisabled"
        >
          <el-option label="Pollen" value="pollen"></el-option>
          <el-option label="Dust mite" value="dustMite"></el-option>
          <el-option label="Soy" value="soy"></el-option>
          <el-option label="Dairy product" value="dairyProduct"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Emergency Contact" prop="emergencyContact">
        <el-input v-model="patientEditForm.emergencyContact" placeholder="Enter emergency contact" :disabled="emergencyContactDisabled"></el-input>
      </el-form-item>

      <el-form-item label="Emergency Contact Relationship" prop="emergencyContactRelationship">
        <el-input v-model="patientEditForm.emergencyContactRelationship" placeholder="Enter emergency contact relationship" :disabled="emergencyContactRelationshipDisabled"></el-input>
      </el-form-item>

      <el-form-item label="Emergency Contact Phone" prop="emergencyContactPhone">
        <el-input v-model="patientEditForm.emergencyContactPhone" placeholder="Enter emergency contact phone" :disabled="emergencyContactPhoneDisabled"></el-input>
      </el-form-item>

      <el-form-item label="Emergency Contact Address" prop="emergencyContactAddress">
        <el-input v-model="patientEditForm.emergencyContactAddress" placeholder="Enter emergency contact address" :disabled="emergencyContactAddressDisabled"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm(patientEditFormRef)" :disabled="buttonDisabled">Submit</el-button>
        <el-button @click="resetForm(patientEditFormRef)" :disabled="buttonDisabled">Reset</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>

</style>