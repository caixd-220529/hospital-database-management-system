<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { HospitalizationDetailed, HospitalizationDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const hospitalizationDetailed: HospitalizationDetailed = {
  hospitalizationId: '',
  patientRough: { patientId: '', patientName: '' },
  doctorRough: { doctorId: '', doctorName: '' },
  consultationRoughArr: [],
  hospitalizationTime: '',
  hospitalizationReason: '',
  dischargeTime: '',
  dischargeReason: '',
  roomId: '',
  bedNumber: '',
  chargeId: '',
}

const props = defineProps(
  {
    hospitalizationId: {
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
const getDate = ref(false)
const getHospitalization = () => {
  if (props.hospitalizationId === '') {
    console.log('hospitalizationId is empty')
  } else {
    console.log('hospitalizationId:', props.hospitalizationId)
  }
  getDate.value = false
  axios.get(rootOfPath + `/get-hospitalization-detailed?hospitalizationId=${props.hospitalizationId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in hospitalizationDetailed) {
      if (key in response.data.results){
        hospitalizationDetailed[key as HospitalizationDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    getDate.value = true
  }).catch((error) => {
    console.log(error)
  })
}
onMounted(() => {
  getHospitalization()
})
watch(() => props.hospitalizationId, () => {
  getHospitalization()
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
      v-loading="!getDate"
      border
      direction="vertical"
      class="description-box"
    >
      <el-descriptions-item label="Hospitalization ID" align="center" label-align="center" :span="3" :min-width="250">
        <el-text>{{ hospitalizationDetailed.hospitalizationId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" align="center" label-align="center" :span="3" :min-width="250">
        <el-text>
          {{ hospitalizationDetailed.patientRough.patientId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, hospitalizationDetailed.patientRough.patientId)" />
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" align="center" label-align="center" :span="3" :min-width="250">
        <el-text>{{ hospitalizationDetailed.patientRough.patientName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Charge ID" align="center" label-align="center" :span="3" :min-width="250">
        <el-text>
          {{ hospitalizationDetailed.chargeId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, hospitalizationDetailed.chargeId)" />
        </el-text>
      </el-descriptions-item>

      <el-descriptions-item v-if="props.showEmployeeId" label="Attending Doctor ID" align="center" label-align="center" :span="3">
        <el-text>
          {{ hospitalizationDetailed.doctorRough.doctorId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, hospitalizationDetailed.doctorRough.doctorId)" />
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Attending Doctor Name" align="center" label-align="center" :span="props.showEmployeeId?3:4">
        <el-text>{{ hospitalizationDetailed.doctorRough.doctorName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Room ID" align="center" label-align="center" :span="props.showEmployeeId?3:4">
        <el-text>
          {{ hospitalizationDetailed.roomId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Room, hospitalizationDetailed.roomId)" />
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Bed Number" align="center" label-align="center" :span="props.showEmployeeId?3:4">
        <el-text>{{ hospitalizationDetailed.bedNumber }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Hospitalization Time" align="center" label-align="center" :span="6">
        <el-text>{{ hospitalizationDetailed.hospitalizationTime }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Discharge Time" align="center" label-align="center" :span="6">
        <el-text>{{ hospitalizationDetailed.dischargeTime }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Hospitalization Reason" label-align="center" :span="12">
        <el-text>{{ hospitalizationDetailed.hospitalizationReason }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Discharge Reason" label-align="center" :span="12">
        <el-text>{{ hospitalizationDetailed.dischargeReason }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Related Consultation Information" label-align="center" align="center" :span="12">
        <el-table :data="hospitalizationDetailed.consultationRoughArr" style="width: 100%">
          <el-table-column prop="consultationId" label="Consultation ID"  align="center"/>
          <el-table-column prop="doctorName" label="Doctor Name"  align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Consultation, row.consultationId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>