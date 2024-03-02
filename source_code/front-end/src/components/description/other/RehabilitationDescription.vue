<script setup lang="ts">
import axois, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { RehabilitationDetailed, RehabilitationDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const rehabilitationDetailed: RehabilitationDetailed = {
  rehabilitationId: '',
  consultationRough: { consultationId: '', doctorName: '' },
  rehabilitationName: '',
  beginTime: '',
  endTime: '',
  chargeId: '',
  patientRough: { patientId: '', patientName: '' },
  doctorRoughArr: [],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
}
const props = defineProps(
  {
    rehabilitationId: {
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
const getRehabilitation = () => {
  if (props.rehabilitationId === '') {
    console.log('rehabilitationId is empty')
  } else {
    console.log('rehabilitationId:', props.rehabilitationId)
  }
  getData.value = false
  axois.get(rootOfPath + `/get-rehabilitation-detailed?rehabilitationId=${props.rehabilitationId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in rehabilitationDetailed) {
      if (key in response.data.results){
        rehabilitationDetailed[key as RehabilitationDetailedKey] = response.data.results[key]
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
  getRehabilitation()
})
watch(() => props.rehabilitationId, () => {
  getRehabilitation()
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
      <el-descriptions-item label="Rehabilitation ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{rehabilitationDetailed.rehabilitationId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Id" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ rehabilitationDetailed.patientRough.patientId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, rehabilitationDetailed.patientRough.patientId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ rehabilitationDetailed.patientRough.patientName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Charge ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ rehabilitationDetailed.chargeId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, rehabilitationDetailed.chargeId)"/>
        </el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Rehabilitation Name" label-align="center" align="center" :span="4">
        <el-text>{{rehabilitationDetailed.rehabilitationName}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation ID" label-align="center" align="center" :span="4">
        <el-text>
          {{ rehabilitationDetailed.consultationRough.consultationId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Consultation, rehabilitationDetailed.consultationRough.consultationId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation Doctor Name" label-align="center" align="center" :span="4">
        <el-text>{{ rehabilitationDetailed.consultationRough.doctorName }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Begin Time" label-align="center" align="center" :span="6">
        <el-text>{{rehabilitationDetailed.beginTime}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="End Time" label-align="center" align="center" :span="6">
        <el-text>{{rehabilitationDetailed.endTime}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Related Doctor Name" label-align="center" align="center" :span="12">
        <el-table :data="rehabilitationDetailed.doctorRoughArr" style="width: 100%">
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
        <el-table :data="rehabilitationDetailed.nurseRoughArr" style="width: 100%">
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
        <el-table :data="rehabilitationDetailed.helpingStaffRoughArr" style="width: 100%">
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
