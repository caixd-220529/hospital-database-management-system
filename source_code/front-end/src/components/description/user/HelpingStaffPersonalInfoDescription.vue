<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import {HelpingStaffInfo, HelpingStaffInfoKey} from '../../../types/user.ts'
import {ref, onMounted, watch} from 'vue'
import ShowDetailButton from "../ShowDetailButton.vue";
import { DescribableItem } from '../../../types/other.ts'


const config = useConfigStore()
const rootOfPath = config.rootOfPath
const helpingStaffInfo: HelpingStaffInfo = {
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
  helpingStaffId: '',
}
const props = defineProps(
  {
    helpingStaffId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const dataReady = ref(false)
const getHelpingStaffInfo = () => {
  if (props.helpingStaffId === '') {
    console.log('helpingStaffId is empty')
  }
  dataReady.value = false
  axios.get(rootOfPath + `/get-helping-staff-info?helpingStaffId=${props.helpingStaffId}`).then((response: AxiosResponse) => {
    for (const key in helpingStaffInfo) {
      if (key in response.data.results){
        helpingStaffInfo[key as HelpingStaffInfoKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    dataReady.value = true
  }).catch((err: any) => {
    console.error(err)
  })
}

const handleShowDetail = (item: DescribableItem, id: string) => {
  emit('changeContent', item, id)
}

onMounted(() => {
  getHelpingStaffInfo()
})
watch(() => props.helpingStaffId, () => {
  getHelpingStaffInfo()
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
      <el-descriptions-item label="HelpingStaff ID" align="center" :span="3" :min-width="250">
        <el-text>{{ helpingStaffInfo.helpingStaffId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Name" align="center" :span="3" :min-width="250">
        <el-text>{{ helpingStaffInfo.name }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Gender" align="center" :span="3" :min-width="250">
        <el-text>{{helpingStaffInfo.gender}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Birthdate" align="center" :span="3" :min-width="250">
        <el-text>{{helpingStaffInfo.birthdate}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Position" align="center" :span="4">
        <el-text>{{helpingStaffInfo.position}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor ID" align="center" :span="4">
        <el-text>{{helpingStaffInfo.supervisorId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor Name" align="center" :span="4">
        <el-text>{{helpingStaffInfo.supervisorId}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Phone" align="center" :span="3">
        <el-text>{{helpingStaffInfo.phone}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Salary" align="center" :span="3">
        <el-text>{{helpingStaffInfo.salary}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Hire" align="center" :span="3">
        <el-text>{{helpingStaffInfo.dateOfHire}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Dismiss" align="center" :span="3">
        <el-text>{{helpingStaffInfo.dateOfDismiss}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Address" align="center" :span="12">
        <el-text>{{helpingStaffInfo.address}}</el-text>
      </el-descriptions-item>

    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>