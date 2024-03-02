<script setup lang="ts">
import axios from 'axios'
import {useConfigStore} from '../../stores/config'
import {DoctorInfoKey, DoctorInfo, PatientInfoKey} from '../../types/user'
import {ref, watch, onMounted} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const dataReady = ref(false)
const originalDoctorInfo = ref<DoctorInfo>({
  doctorId: '',
  name: '',
  gender: '',
  birthdate: '',
  position: '',
  department: '',
  supervisorId: '',
  supervisorName: '',
  phone: '',
  salary: '',
  dateOfHire: '',
  dateOfDismiss: '',
  licenseNumber: '',
  address: '',
})
const doctorEditForm = ref<DoctorInfo>({
  doctorId: '',
  name: '',
  gender: '',
  birthdate: '',
  position: '',
  department: '',
  supervisorId: '',
  supervisorName: '',
  phone: '',
  salary: '',
  dateOfHire: '',
  dateOfDismiss: '',
  licenseNumber: '',
  address: '',
})
const doctorEditFormRef = ref<FormInstance>()
const doctorEditFormRules = ref<FormRules<DoctorInfo>>({
  name: [
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  doctorId: [
    {required: true, message: 'Please enter doctor ID', trigger: 'change'}
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
  department: [
    {required: true, message: 'Please select department', trigger: 'change'}
  ],
  salary: [
    {required: true, message: 'Please enter salary', trigger: 'change'}
  ],
})

const doctorIdDisabled = true
const nameDisabled = true
const genderDisabled = true
const birthdateDisabled = true
const positionDisabled = true
const departmentDisabled = true
const supervisorIdDisabled = true
const supervisorNameDisabled = true
const phoneDisabled = false
const salaryDisabled = true
const dateOfHireDisabled = true
const dateOfDismissDisabled = true
const licenseNumberDisabled = true
const addressDisabled = false

const buttonDisabled = ref(false)
const failedMessage = ref('')
const failedDialogVisible = ref(false)

const birthdateDisabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const getDoctorOriginalInfo = async () => {
  axios.get(rootOfPath + `/get-doctor-info?doctorId=${config.userId}`)
    .then((res) => {
      for (const key in originalDoctorInfo.value) {
        if (res.data.results[key] === null || res.data.results[key] === undefined) {
          console.error(`key: ${key} is null`)
        }
        originalDoctorInfo.value[key as PatientInfoKey] = res.data.results[key]
        doctorEditForm.value[key as PatientInfoKey] = res.data.results[key]
      }
      dataReady.value = true
    })
    .catch((err) => {
      console.error(err)
    })
}

const submitForm = () => {
  buttonDisabled.value = true
  doctorEditFormRef.value.validate((valid) => {
    if (valid) {
      axios.post(rootOfPath + '/edit-doctor-info', doctorEditForm.value)
        .then(async () => {
          await getDoctorOriginalInfo()
          ElMessage.success('Edit successfully')
          buttonDisabled.value = false
        })
        .catch((err) => {
          failedMessage.value = err.response.data.results.notice
          failedDialogVisible.value = true
          err.response.data.results.invalidFormField.forEach((formField: string) => {
            doctorEditForm.value[formField as DoctorInfoKey] = originalDoctorInfo.value[formField as DoctorInfoKey]
          })
        })
        .finally(() => {
          buttonDisabled.value = false
        })
    } else {
      buttonDisabled.value = false
    }
  })
}

const resetForm = () => {
  for(const key in doctorEditForm.value) {
    doctorEditForm.value[key as DoctorInfoKey] = originalDoctorInfo.value[key as DoctorInfoKey]
  }
}

onMounted(() => {
  getDoctorOriginalInfo()
})

</script>

<template>
  <el-dialog
    title="Failed"
    v-model="failedDialogVisible"
  >
    <span>{{ failedMessage }}</span>
    <template #footer>
      <el-button type="primary" @click="failedDialogVisible = false">Confirm</el-button>
    </template>
  </el-dialog>

  <div v-loading="!dataReady" class="form-container">
    <el-form
      ref="doctorEditFormRef"
      :model="doctorEditForm"
      :rules="doctorEditFormRules"
      label-position="top"
    >
      <el-form-item label="Doctor ID" prop="doctorId">
        <el-input v-model="doctorEditForm.doctorId" :disabled="doctorIdDisabled"/>
      </el-form-item>

      <el-form-item label="Name" prop="name">
        <el-input v-model="doctorEditForm.name" :disabled="nameDisabled"/>
      </el-form-item>

      <el-form-item label="Gender" prop="gender">
        <el-select v-model="doctorEditForm.gender" :disabled="genderDisabled" placeholder="Select gender" style="width: 100%">
          <el-option label="Male" value="male"></el-option>
          <el-option label="Female" value="female"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Birthdate" prop="birthdate">
        <el-date-picker
          v-model="doctorEditForm.birthdate"
          :disabled="birthdateDisabled"
          type="date"
          placeholder="Select birthdate"
          style="width: 100%"
          :disabledDate="birthdateDisabledDate"
        />
      </el-form-item>

      <el-form-item label="Position" prop="position">
        <el-input v-model="doctorEditForm.position" :disabled="positionDisabled"/>
      </el-form-item>

      <el-form-item label="Department" prop="department">
        <el-input v-model="doctorEditForm.department" :disabled="departmentDisabled"/>
      </el-form-item>

      <el-form-item label="Supervisor ID" prop="supervisorId">
        <el-input v-model="doctorEditForm.supervisorId" :disabled="supervisorIdDisabled"/>
      </el-form-item>

      <el-form-item label="Supervisor Name" prop="supervisorName">
        <el-input v-model="doctorEditForm.supervisorName" :disabled="supervisorNameDisabled"/>
      </el-form-item>

      <el-form-item label="Phone" prop="phone">
        <el-input v-model="doctorEditForm.phone" :disabled="phoneDisabled"/>
      </el-form-item>

      <el-form-item label="Salary" prop="salary">
        <el-input v-model="doctorEditForm.salary" :disabled="salaryDisabled"/>
      </el-form-item>

      <el-form-item label="Date of Hire" prop="dateOfHire">
        <el-date-picker
          v-model="doctorEditForm.dateOfHire"
          :disabled="dateOfHireDisabled"
          type="date"
          placeholder="Select date of hire"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="Date of Dismiss" :disabled="dateOfDismissDisabled">
        <el-date-picker
          v-model="doctorEditForm.dateOfDismiss"
          :disabled="dateOfDismissDisabled"
          type="date"
          placeholder="Select date of dismiss"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="License Number" prop="licenseNumber">
        <el-input v-model="doctorEditForm.licenseNumber" :disabled="licenseNumberDisabled"/>
      </el-form-item>

      <el-form-item label="Address" prop="address">
        <el-input v-model="doctorEditForm.address" :disabled="addressDisabled"/>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm" :disabled="buttonDisabled">Submit</el-button>
        <el-button @click="resetForm" :disabled="buttonDisabled">Reset</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>

</style>