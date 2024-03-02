<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import {NurseInfo, NurseInfoKey} from '../../../types/user.ts'
import {ref, onMounted, watch} from 'vue'
import ShowDetailButton from "../ShowDetailButton.vue";
import { DescribableItem } from '../../../types/other.ts'


const config = useConfigStore()
const rootOfPath = config.rootOfPath
const nurseInfo: NurseInfo = {
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
  nurseId: '',
  licenseNumber: '',
  roomId: '',
}
const props = defineProps(
  {
    nurseId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
    showRoomDetail: {
      type: Boolean,
      required: true,
    }
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const dataReady = ref(false)
const getNurseInfo = () => {
  if (props.nurseId === '') {
    console.log('nurseId is empty')
  }
  dataReady.value = false
  axios.get(rootOfPath + `/get-nurse-info?nurseId=${props.nurseId}`).then((response: AxiosResponse) => {
    for (const key in nurseInfo) {
      if (key in response.data.results){
        nurseInfo[key as NurseInfoKey] = response.data.results[key]
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
  getNurseInfo()
})
watch(() => props.nurseId, () => {
  getNurseInfo()
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
      <el-descriptions-item label="Nurse ID" align="center" :span="3" :min-width="250">
        <el-text>{{ nurseInfo.nurseId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Name" align="center" :span="3" :min-width="250">
        <el-text>{{ nurseInfo.name }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Gender" align="center" :span="3" :min-width="250">
        <el-text>{{nurseInfo.gender}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Birthdate" align="center" :span="3" :min-width="250">
        <el-text>{{nurseInfo.birthdate}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Position" align="center" :span="3">
        <el-text>{{nurseInfo.position}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Room ID" align="center" :span="3">
        <el-text>
          {{nurseInfo.roomId}}
          <ShowDetailButton v-if="props.showRoomDetail" @click="handleShowDetail(DescribableItem.Room, nurseInfo.roomId);" />
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor ID" align="center" :span="3">
        <el-text>{{nurseInfo.supervisorId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Supervisor Name" align="center" :span="3">
        <el-text>{{nurseInfo.supervisorId}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Phone" align="center" :span="3">
        <el-text>{{nurseInfo.phone}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Salary" align="center" :span="3">
        <el-text>{{nurseInfo.salary}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Hire" align="center" :span="3">
        <el-text>{{nurseInfo.dateOfHire}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Date of Dismiss" align="center" :span="3">
        <el-text>{{nurseInfo.dateOfDismiss}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="License Number" align="center" :span="12">
        <el-text>{{nurseInfo.licenseNumber}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Address" align="center" :span="12">
        <el-text>{{nurseInfo.address}}</el-text>
      </el-descriptions-item>

    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>