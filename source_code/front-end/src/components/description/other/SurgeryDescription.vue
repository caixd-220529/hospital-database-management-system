<script setup lang="ts">
import axios, {AxiosResponse} from 'axios'
import {useConfigStore} from '../../../stores/config.ts'
import {SurgeryDetailed, SurgeryDetailedKey} from '../../../types/other.ts'
import {ref, onMounted, watch} from 'vue'
import {DescribableItem} from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const surgeryDetailed: SurgeryDetailed = {
  surgeryId: '',
  consultationRough: {'consultationId': '', 'doctorName': ''},
  patientRough: {'patientId': '', 'patientName': ''},
  doctorRough: {'doctorId': '', 'doctorName': ''},
  surgeryName: '',
  surgeryDescription: '',
  surgerySite: '',
  surgeryType: '',
  beginTime: '',
  endTime: '',
  chargeId: '',
  doctorRoughArr: [],
  helpingStaffRoughArr: [],
  nurseRoughArr: [],
  recordRoughArr: [],
}
const props = defineProps(
    {
      surgeryId: {
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
      },
    }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const getData = ref(false)
const getSurgery = () => {
  if (props.surgeryId === '') {
    console.log('surgeryId is empty')
  } else {
    console.log('surgeryId:', props.surgeryId)
  }
  getData.value = false
  axios.get(rootOfPath + `/get-surgery-detailed?surgeryId=${props.surgeryId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in surgeryDetailed) {
      if (key in response.data.results) {
        surgeryDetailed[key as SurgeryDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    getData.value = true
  }).catch((err: any) => {
    console.error(err)
  })
}
onMounted(() => {
  getSurgery()
})
watch(() => props.surgeryId, () => {
  getSurgery()
})
const handleShowDetail = (item: DescribableItem, id: string) => {
  emit('changeContent', item, id)
}
</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions
        :column="12"
        :title="props.title"
        v-loading="!getData"
        border
        direction="vertical"
        class="description-box"
    >
      <el-descriptions-item label="Surgery ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ surgeryDetailed.surgeryId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text></el-text>
        {{ surgeryDetailed.patientRough.patientId }}
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text></el-text>
        {{ surgeryDetailed.patientRough.patientName }}
      </el-descriptions-item>
      <el-descriptions-item label="Charge ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ surgeryDetailed.chargeId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, surgeryDetailed.chargeId)"/>
        </el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Surgery Name" label-align="center" align="center" :span="4">
        <el-text>{{ surgeryDetailed.surgeryName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Surgery Site" label-align="center" align="center" :span="4">
        <el-text>{{ surgeryDetailed.surgerySite }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Surgery Type" label-align="center" align="center" :span="4">
        <el-text>{{ surgeryDetailed.surgeryType }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item v-if="showEmployeeId" label="Operating Surgeon ID" label-align="center" align="center"
                            :span="3">
        <el-text>
          {{ surgeryDetailed.doctorRough.doctorId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, surgeryDetailed.doctorRough.doctorId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Operating Surgeon Name" label-align="center" align="center"
                            :span="props.showEmployeeId?3:4">
        <el-text>
          {{ surgeryDetailed.doctorRough.doctorName }}
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation ID" label-align="center" align="center" :span="props.showEmployeeId?3:4">
        <el-text>
          {{ surgeryDetailed.consultationRough.consultationId }}
          <ShowDetailButton
              @click="handleShowDetail(DescribableItem.Consultation, surgeryDetailed.consultationRough.consultationId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation Doctor Name" label-align="center" align="center" :span="props.showEmployeeId?3:4">
        <el-text>{{ surgeryDetailed.consultationRough.doctorName }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Begin Time" label-align="center" align="center" :span="6">
        <el-text>{{ surgeryDetailed.beginTime }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="End Time" label-align="center" align="center" :span="6">
        <el-text>{{ surgeryDetailed.endTime }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Description" label-align="center" align="left" :span="12">
        <el-text>{{ surgeryDetailed.surgeryDescription }}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Surgery Record" label-align="center" align="center" :span="12">
        <el-table :data="surgeryDetailed.recordRoughArr" style="width: 100%">
          <el-table-column label="Record ID" align="center" prop="recordId"/>
          <el-table-column label="Record Time" align="center" prop="recordTime"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton
                  @click="handleShowDetail(DescribableItem.SurgeryRecord, surgeryDetailed.surgeryId+'#'+row.recordId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Doctor Information" label-align="center" align="center" :span="12">
        <el-table :data="surgeryDetailed.doctorRoughArr" style="width: 100%">
          <el-table-column label="Doctor ID" align="center" prop="doctorId" v-if="props.showEmployeeId"/>
          <el-table-column label="Doctor Name" align="center" prop="doctorName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, row.doctorId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Nurse Information" label-align="center" align="center" :span="12">
        <el-table :data="surgeryDetailed.nurseRoughArr" style="width: 100%">
          <el-table-column label="Nurse ID" align="center" prop="nurseId" v-if="props.showEmployeeId"/>
          <el-table-column label="Nurse Name" align="center" prop="nurseName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.Nurse, row.nurseId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>

      <el-descriptions-item label="Related Helping Staff Information" label-align="center" align="center" :span="12">
        <el-table :data="surgeryDetailed.helpingStaffRoughArr" style="width: 100%">
          <el-table-column label="Helping Staff ID" align="center" prop="helpingStaffId" v-if="props.showEmployeeId"/>
          <el-table-column label="Helping Staff Name" align="center" prop="helpingStaffName"/>
          <el-table-column label="Operation" align="center" v-if="props.showEmployeeId">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.HelpingStaff, row.helpingStaffId)"/>
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    </el-descriptions>

  </el-scrollbar>
</template>

<style scoped>

</style>
