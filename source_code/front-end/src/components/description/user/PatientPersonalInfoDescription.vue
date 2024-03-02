<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { PatientInfo, PatientInfoKey } from '../../../types/user.ts'
import {ref, onMounted, watch} from 'vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const patientInfo: PatientInfo = {
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

const props = defineProps(
  {
    patientId: {
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
const getPatientInfo = () => {
  if (props.patientId === '') {
    console.log('patientId is empty')
  }
  dataReady.value = false
  axios.get(rootOfPath + `/get-patient-info?patientId=${props.patientId}`).then((response: AxiosResponse) => {
    for (const key in patientInfo) {
      if (key in response.data.results){
        patientInfo[key as PatientInfoKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    dataReady.value = true
  }).catch((err: any) => {
    console.error(err)
  }).finally(() => {
    console.log(patientInfo)
  })
}
onMounted(() => {
  getPatientInfo()
})
watch(() => props.patientId, () => {
  getPatientInfo()
})

</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions 
      :column="12" 
      :title=title
      v-loading="!dataReady" 
      border
      direction="vertical"
      class="description-box"
    >
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ patientInfo.patientId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ patientInfo.name }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Gender" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ patientInfo.gender }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Birthdate" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ patientInfo.birthdate }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Marital Status" label-align="center" align="center" :span="3">
        <el-text>{{ patientInfo.maritalStatus }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Initial Diagnosis Data" label-align="center" align="center" :span="3">
        <el-text>{{ patientInfo.initialDiagnosisDate }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Nationality" label-align="center" align="center" :span="3">
        <el-text v-if="patientInfo.nationality !== ''">{{ patientInfo.nationality }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Birthplace" label-align="center" align="center" :span="3">
        <el-text v-if="patientInfo.birthplace !== ''">{{ patientInfo.birthplace }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Blood Type" label-align="center" align="center" :span="4">
        <el-text v-if="patientInfo.bloodType !== ''">{{ patientInfo.bloodType }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Phone" label-align="center" align="center" :span="4">
        <el-text>{{ patientInfo.phone }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Occupation" label-align="center" align="center" :span="4">
        <el-text v-if="patientInfo.occupation !== ''">{{ patientInfo.occupation }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Identification Document Type" label-align="center" align="center" :span="6">
        <el-text>{{ patientInfo.identificationDocumentType }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Identification Number" label-align="center" align="center" :span="6">
        <el-text>{{ patientInfo.identificationNumber }}</el-text>
      </el-descriptions-item>
      
      <el-descriptions-item label="Allergens" label-align="center" align="center" :span="12">
        <div v-if="patientInfo.allergens.length !== 0">
          <el-tag v-for="item in patientInfo.allergens" style="margin: 5px;">{{ item }}</el-tag>
        </div>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>
        
      <el-descriptions-item label="Address" label-align="center" align="center" :span="12">
        <el-text>{{ patientInfo.address }}</el-text>
      </el-descriptions-item>
        
      <el-descriptions-item label="Emergency Contact" label-align="center" align="center" :span="4">
        <el-text v-if="patientInfo.emergencyContact !== ''">{{ patientInfo.emergencyContact }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Emergency Contact Relationship" label-align="center" align="center" :span="4">
        <el-text v-if="patientInfo.emergencyContactRelationship !== ''">{{ patientInfo.emergencyContactRelationship }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Emergency Contact Phone" label-align="center" align="center" :span="4">
        <el-text v-if="patientInfo.emergencyContactPhone !== ''">{{ patientInfo.emergencyContactPhone }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Emergency Contact Address" label-align="center" align="center" :span="12">
        <el-text v-if="patientInfo.emergencyContactAddress !== ''">{{ patientInfo.emergencyContactAddress }}</el-text>
        <el-text v-else type="info">No information</el-text>
      </el-descriptions-item>    
    </el-descriptions>
  </el-scrollbar>
</template>
<style scoped>
</style>
