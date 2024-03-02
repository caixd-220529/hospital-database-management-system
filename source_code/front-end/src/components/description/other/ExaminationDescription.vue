<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { ExaminationDetailed, ExaminationDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const examinationDetailed: ExaminationDetailed = {
  examinationId: '',
  consultationRough: { consultationId: '', doctorName: '' },
  timeOfExamination: '',
  timeOfResult: '',
  examinationName: '',
  result: '',
  chargeId: '',
  patientRough: { patientId: '', patientName: '' },
  doctorRoughArr: [],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
}
const props = defineProps(
  {
    examinationId: {
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
const getExamination = () => {
  if (props.examinationId === '') {
    console.log('examinationId is empty')
  } else {
    console.log('examinationId:', props.examinationId)
  }
  getData.value = false
  axios.get(rootOfPath + `/get-examination-detailed?examinationId=${props.examinationId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in examinationDetailed) {
      if (key in response.data.results){
        examinationDetailed[key as ExaminationDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    getData.value = true
  })
}
onMounted(() => {
  getExamination()
})
watch(() => props.examinationId, () => {
  getExamination()
})
const handleShowDetail = (item: DescribableItem, id: string) => {
  emit('changeContent', item, id)
}
</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions
      :column="12"
      :title="title"
      v-loading="!getData"
      border
      direction="vertical"
      class="description-box"
    >
      <el-descriptions-item label="Examination ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ examinationDetailed.examinationId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ examinationDetailed.patientRough.patientId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, examinationDetailed.patientRough.patientId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ examinationDetailed.patientRough.patientName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Charge ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ examinationDetailed.chargeId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, examinationDetailed.chargeId)"/>
        </el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Examination Name" label-align="center" align="center" :span="6">
        <el-text>{{ examinationDetailed.examinationName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Examination Time" label-align="center" align="center" :span="6">
        <el-text>{{ examinationDetailed.timeOfExamination }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Consultation ID" label-align="center" align="center" :span="4">
        <el-text>
          {{ examinationDetailed.consultationRough.consultationId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Consultation, examinationDetailed.consultationRough.consultationId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation Doctor Name" label-align="center" align="center" :span="4">
        <el-text>{{ examinationDetailed.consultationRough.doctorName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Result Time" label-align="center" align="center" :span="4">
        <el-text>{{ examinationDetailed.timeOfResult }}</el-text>
      </el-descriptions-item>


      <el-descriptions-item label="Result" label-align="center" :span="12">
        <el-text>{{ examinationDetailed.result }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Related Doctor Information" label-align="center" align="center" :span="12">
        <el-table :data="examinationDetailed.doctorRoughArr" style="width: 100%">
          <el-table-column label="Doctor ID" align="center" prop="doctorId" v-if="props.showEmployeeId"/>
          <el-table-column label="Doctor Name" align="center" prop="doctorName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, row.doctorId)" />
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Nurse Information" label-align="center" align="center" :span="12">
        <el-table :data="examinationDetailed.nurseRoughArr" style="width: 100%">
          <el-table-column label="Nurse ID" align="center" prop="nurseId" v-if="props.showEmployeeId"/>
          <el-table-column label="Nurse Name" align="center" prop="nurseName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Nurse, row.nurseId)" />
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Helping Staff Information" label-align="center" align="center" :span="12">
        <el-table :data="examinationDetailed.helpingStaffRoughArr" style="width: 100%">
          <el-table-column label="Helping Staff ID" align="center" prop="helpingStaffId" v-if="props.showEmployeeId"/>
          <el-table-column label="Helping Staff Name" align="center" prop="helpingStaffName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.HelpingStaff, row.helpingStaffId)" />
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>