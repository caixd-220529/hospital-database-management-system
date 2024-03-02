<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { DoctorInfo, DoctorInfoKey } from '../../../types/user.ts'
import {ref, onMounted, watch} from 'vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const doctorInfo: DoctorInfo = {
  name: '',
  gender: '',
  position: '',
  birthdate: '',
  phone: '',
  address: '',
  dateOfHire: '',
  dateOfDismiss: '',
  supervisorId: '',
  supervisorName: '',
  salary: '',
  doctorId: '',
  department: '',
  licenseNumber: '',
}
const props = defineProps(
  {
    doctorId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    }
  }
)
const dataReady = ref(false)
const getDoctorInfo = () => {
  if (props.doctorId === '') {
    console.log('doctorId is empty')
  }
  dataReady.value = false
  axios.get(rootOfPath + `/get-doctor-info?doctorId=${props.doctorId}`).then((response: AxiosResponse) => {
    for (const key in doctorInfo) {
      if (key in response.data.results){
        doctorInfo[key as DoctorInfoKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    dataReady.value = true
  }).catch((err: any) => {
    console.error(err)
  })
}

onMounted(() => {
  getDoctorInfo()
})
watch(() => props.doctorId, () => {
  getDoctorInfo()
})
</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions
      :column="12"
      :title="title"
      v-loading="!dataReady"
      border
      direction="vertical"
      class="description-box"
    >
      <el-descriptions-item label="Doctor ID" align="center" :span="3" :min-width="250">
        <el-text>{{ doctorInfo.doctorId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Name" align="center" :span="3" :min-width="250">
        <el-text>{{ doctorInfo.name }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Gender" align="center" :span="3" :min-width="250">
        <el-text>{{doctorInfo.gender}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Birthdate" align="center" :span="3" :min-width="250">
        <el-text>{{doctorInfo.birthdate}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Position" align="center" :span="3">
        <el-text>{{doctorInfo.position}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Department" align="center" :span="3">
        <el-text>{{doctorInfo.department}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor ID" align="center" :span="3">
        <el-text>{{doctorInfo.supervisorId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor Name" align="center" :span="3">
        <el-text>{{doctorInfo.supervisorId}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Phone" align="center" :span="3">
        <el-text>{{doctorInfo.phone}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Salary" align="center" :span="3">
        <el-text>{{doctorInfo.salary}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Hire" align="center" :span="3">
        <el-text>{{doctorInfo.dateOfHire}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Dismiss" align="center" :span="3">
        <el-text>{{doctorInfo.dateOfDismiss}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="License Number" align="center" :span="12">
        <el-text>{{doctorInfo.licenseNumber}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Address" align="center" :span="12">
        <el-text>{{doctorInfo.address}}</el-text>
      </el-descriptions-item>

    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>