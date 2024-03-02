<script setup lang="ts">
import axios from 'axios'
import {useConfigStore} from '../../stores/config'
import {NurseInfoKey, NurseInfo, PatientInfoKey} from '../../types/user'
import {ref, watch, onMounted} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const dataReady = ref(false)
const originalNurseInfo = ref<NurseInfo>({
  nurseId: '',
  name: '',
  gender: '',
  birthdate: '',
  position: '',
  supervisorId: '',
  supervisorName: '',
  phone: '',
  salary: '',
  dateOfHire: '',
  dateOfDismiss: '',
  licenseNumber: '',
  address: '',
  roomId: '',
})
const nurseEditForm = ref<NurseInfo>({
  nurseId: '',
  name: '',
  gender: '',
  birthdate: '',
  position: '',
  roomId: '',
  supervisorId: '',
  supervisorName: '',
  phone: '',
  salary: '',
  dateOfHire: '',
  dateOfDismiss: '',
  licenseNumber: '',
  address: '',
})
const nurseEditFormRef = ref<FormInstance>()
const nurseEditFormRules = ref<FormRules<NurseInfo>>({
  name: [
    {required: true, message: 'Please enter name', trigger: 'change'}
  ],
  nurseId: [
    {required: true, message: 'Please enter nurse ID', trigger: 'change'}
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
  roomId: [
    {required: true, message: 'Please enter room ID', trigger: 'change'}
  ],
  salary: [
    {required: true, message: 'Please enter salary', trigger: 'change'}
  ],
})

const nurseIdDisabled = true
const nameDisabled = true
const genderDisabled = true
const birthdateDisabled = true
const positionDisabled = true
const roomIdDisabled = true
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

const getNurseOriginalInfo = async () => {
  axios.get(rootOfPath + `/get-nurse-info?nurseId=${config.userId}`)
    .then((res) => {
      for (const key in originalNurseInfo.value) {
        if (res.data.results[key] === null || res.data.results[key] === undefined) {
          console.error(`key: ${key} is null`)
        }
        originalNurseInfo.value[key as PatientInfoKey] = res.data.results[key]
        nurseEditForm.value[key as PatientInfoKey] = res.data.results[key]
      }
      dataReady.value = true
    })
    .catch((err) => {
      console.error(err)
    })
}

const submitForm = () => {
  buttonDisabled.value = true
  nurseEditFormRef.value.validate((valid) => {
    if (valid) {
      axios.post(rootOfPath + '/edit-nurse-info', nurseEditForm.value)
        .then(async () => {
          await getNurseOriginalInfo()
          ElMessage.success('Edit successfully')
          buttonDisabled.value = false
        })
        .catch((err) => {
          failedMessage.value = err.response.data.results.notice
          failedDialogVisible.value = true
          err.response.data.results.invalidFormField.forEach((formField: string) => {
            nurseEditForm.value[formField as NurseInfoKey] = originalNurseInfo.value[formField as NurseInfoKey]
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
  for(const key in nurseEditForm.value) {
    nurseEditForm.value[key as NurseInfoKey] = originalNurseInfo.value[key as NurseInfoKey]
  }
}

onMounted(() => {
  getNurseOriginalInfo()
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
      ref="nurseEditFormRef"
      :model="nurseEditForm"
      :rules="nurseEditFormRules"
      label-position="top"
    >
      <el-form-item label="Nurse ID" prop="nurseId">
        <el-input v-model="nurseEditForm.nurseId" :disabled="nurseIdDisabled"/>
      </el-form-item>

      <el-form-item label="Name" prop="name">
        <el-input v-model="nurseEditForm.name" :disabled="nameDisabled"/>
      </el-form-item>

      <el-form-item label="Gender" prop="gender">
        <el-select v-model="nurseEditForm.gender" :disabled="genderDisabled" placeholder="Select gender" style="width: 100%">
          <el-option label="Male" value="male"></el-option>
          <el-option label="Female" value="female"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Birthdate" prop="birthdate">
        <el-date-picker
          v-model="nurseEditForm.birthdate"
          :disabled="birthdateDisabled"
          type="date"
          placeholder="Select birthdate"
          style="width: 100%"
          :disabledDate="birthdateDisabledDate"
        />
      </el-form-item>

      <el-form-item label="Position" prop="position">
        <el-input v-model="nurseEditForm.position" :disabled="positionDisabled"/>
      </el-form-item>

      <el-form-item label="Room ID" prop="roomId">
        <el-input v-model="nurseEditForm.roomId" :disabled="roomIdDisabled"/>
      </el-form-item>

      <el-form-item label="Supervisor ID" prop="supervisorId">
        <el-input v-model="nurseEditForm.supervisorId" :disabled="supervisorIdDisabled"/>
      </el-form-item>

      <el-form-item label="Supervisor Name" prop="supervisorName">
        <el-input v-model="nurseEditForm.supervisorName" :disabled="supervisorNameDisabled"/>
      </el-form-item>

      <el-form-item label="Phone" prop="phone">
        <el-input v-model="nurseEditForm.phone" :disabled="phoneDisabled"/>
      </el-form-item>

      <el-form-item label="Salary" prop="salary">
        <el-input v-model="nurseEditForm.salary" :disabled="salaryDisabled"/>
      </el-form-item>

      <el-form-item label="Date of Hire" prop="dateOfHire">
        <el-date-picker
          v-model="nurseEditForm.dateOfHire"
          :disabled="dateOfHireDisabled"
          type="date"
          placeholder="Select date of hire"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="Date of Dismiss" :disabled="dateOfDismissDisabled">
        <el-date-picker
          v-model="nurseEditForm.dateOfDismiss"
          :disabled="dateOfDismissDisabled"
          type="date"
          placeholder="Select date of dismiss"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="License Number" prop="licenseNumber">
        <el-input v-model="nurseEditForm.licenseNumber" :disabled="licenseNumberDisabled"/>
      </el-form-item>

      <el-form-item label="Address" prop="address">
        <el-input v-model="nurseEditForm.address" :disabled="addressDisabled"/>
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