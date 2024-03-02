<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { SurgeryRelatedRecordDetailed, SurgeryRelatedRecordDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const surgeryRelatedRecordDetailed: SurgeryRelatedRecordDetailed = {
  surgeryId: '', 
  recordId: '',
  recordTime: '',
  recordDetail: '',
}
const props = defineProps(
  {
    surgeryRecordId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    }
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const getData = ref(false)
const getSurgeryRelatedRecord = () => {
  getData.value = false
  const surgeryId = props.surgeryRecordId.split('#')[0]
  const recordId = props.surgeryRecordId.split('#')[1]
  axios.get(rootOfPath + `/get-surgery-record-detailed?surgeryId=${surgeryId}&recordId=${recordId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in surgeryRelatedRecordDetailed) {
      if (key in response.data.results){
        surgeryRelatedRecordDetailed[key as SurgeryRelatedRecordDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
  }).catch((err: any) => {
    console.error(err)
  }).finally(() => {
    getData.value = true
  })
}
onMounted(() => {
  getSurgeryRelatedRecord()
})
watch(() => props.surgeryRecordId, () => {
  getSurgeryRelatedRecord()
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
      <el-descriptions-item label="Surgery ID" label-align="center" align="center" :span="4" :min-width="333">
        <el-text>
          {{surgeryRelatedRecordDetailed.surgeryId}}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Surgery, surgeryRelatedRecordDetailed.surgeryId)" />
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Record ID" label-align="center" align="center" :span="4" :min-width="333">
        <el-text>{{surgeryRelatedRecordDetailed.recordId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Record Time" label-align="center" align="center" :span="4" :min-width="333">
        <el-text>{{surgeryRelatedRecordDetailed.recordTime}}</el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Record Detail" label-align="center" align="left" :span="12">
        <el-text>{{surgeryRelatedRecordDetailed.recordDetail}}</el-text>
      </el-descriptions-item>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>