<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { ConsultationDetailed, ConsultationDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const consultationDetailed: ConsultationDetailed = {
  consultationId: '',
  patientId: '',
  patientName: '',
	doctorRough: { doctorId: '', doctorName: '' },
	time: '',
	selfReport: '',
	medicalHistory: '',
	medicationHistory: '',
	medicalAdvice: '',
	prescriptionRoughArr: [],
	examinationRoughArr: [],
	rehabilitationRoughArr: [],
  surgeryRoughArr: [],
  hospitalizationRoughArr: [],
	chargeId: '',
}

const props = defineProps(
  {
    consultationId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
    showEmployeeId: {
      type: Boolean,
      required: true,
    }
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const getData = ref(false)
const getConsultation = () => {
  if (props.consultationId === '') {
    console.log('consultationId is empty')
  } else {
    console.log('consultationId:', props.consultationId)
  }
  getData.value = false
  axios.get(rootOfPath + `/get-consultation-detailed?consultationId=${props.consultationId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in consultationDetailed) {
      if (key in response.data.results){
        consultationDetailed[key as ConsultationDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    getData.value = true
  }).catch((err: any) => {
    console.log(err)
  }).finally(() => {
    console.log(consultationDetailed)
  })
}
onMounted(() => {
  getConsultation()
})
watch(() => props.consultationId, () => {
  getConsultation()
})

const handleShowDetail = (item: DescribableItem, id: string) => {
  emit('changeContent', item, id)
}
</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions
      :column="12"
      :title=title
      v-loading="!getData"
      border
      direction="vertical"
      class="description-box"
    >
      <el-descriptions-item label="Consultation ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{consultationDetailed.consultationId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{consultationDetailed.patientId}}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, consultationDetailed.patientId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ consultationDetailed.patientName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="chargeId" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{consultationDetailed.chargeId}}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, consultationDetailed.chargeId)"/>
        </el-text>
      </el-descriptions-item>


      <el-descriptions-item v-if="props.showEmployeeId" label="Doctor Id" label-align="center" align="center" :span="4 ">
        <el-text>
          {{consultationDetailed.doctorRough.doctorId}}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, consultationDetailed.doctorRough.doctorId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Doctor Name" label-align="center" align="center" :span="props.showEmployeeId?4:6">
        {{consultationDetailed.doctorRough.doctorName}}
      </el-descriptions-item>
      <el-descriptions-item label="Time" label-align="center" align="center" :span="props.showEmployeeId?4:6">
        <el-text>{{consultationDetailed.time}}</el-text>
      </el-descriptions-item>
      
      <el-descriptions-item label="Self Report" label-align="center" :span="12">
        <el-text>{{consultationDetailed.selfReport}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Medical History" label-align="center" :span="12">
        <el-text>{{consultationDetailed.medicalHistory}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Medication History" label-align="center" :span="12">
        <el-text>{{consultationDetailed.medicationHistory}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Medical Advice" label-align="center" :span="12">
        <el-text>{{consultationDetailed.medicalAdvice}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Related Prescription Information" label-align="center" align="center" :span="12">
        <el-table :data="consultationDetailed.prescriptionRoughArr" style="width: 100%">
          <el-table-column prop="prescriptionId" label="Prescription ID"  align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Prescription, row.prescriptionId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Examination Information" label-align="center" align="center" :span="12">
        <el-table :data="consultationDetailed.examinationRoughArr" style="width: 100%">
          <el-table-column prop="examinationId" label="Examination ID" align="center"/>
          <el-table-column prop="examinationName" label="Examination Name" align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Examination, row.examinationId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    
      <el-descriptions-item label="Related Rehabilitation Information" label-align="center" align="center" :span="12">
        <el-table :data="consultationDetailed.rehabilitationRoughArr" style="width: 100%">
          <el-table-column prop="rehabilitationId" label="Rehabilitation ID" align="center"/>
          <el-table-column prop="rehabilitationName" label="Rehabilitation Name" align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Rehabilitation, row.rehabilitationId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Surgery Information" label-align="center" align="center" :span="12">
        <el-table :data="consultationDetailed.surgeryRoughArr" style="width: 100%">
          <el-table-column prop="surgeryId" label="Surgery ID" align="center"/>
          <el-table-column prop="surgeryName" label="Surgery Name" align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Surgery, row.surgeryId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Hospitalization Information" label-align="center" align="center" :span="12">
        <el-table :data="consultationDetailed.hospitalizationRoughArr" style="width: 100%">
          <el-table-column prop="hospitalizationId" label="Hospitalization ID" align="center"/>
          <el-table-column prop="doctorName" label="Attending Doctor Name" align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Hospitalization, row.hospitalizationId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>
</style>