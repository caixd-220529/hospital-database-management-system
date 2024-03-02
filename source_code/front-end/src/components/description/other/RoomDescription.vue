<script setup lang="ts">
import axois, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import {RoomDetailedKey, RoomDetailed} from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const roomDetailed: RoomDetailed = {
  roomId: '',
  roomType: '',
  numberOfBeds: '',
  location: '',
  description: '',
}
const props = defineProps(
  {
    roomId: {
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
const getData = ref(false)
const getRoom = () => {
  if (props.roomId === '') {
    console.log('roomId is empty')
  } else {
    console.log('roomId:', props.roomId)
  }
  getData.value = false
  axois.get(rootOfPath + `/get-room-detailed?roomId=${props.roomId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in roomDetailed) {
      if (key in response.data.results){
        roomDetailed[key as RoomDetailedKey] = response.data.results[key]
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
  getRoom()
})
watch(() => props.roomId, () => {
  getRoom()
})
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
      <el-descriptions-item label="Room ID" align="center" :span="4" min-width="333">
        <el-text>
          {{ roomDetailed.roomId }}
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Room Type" align="center" :span="4" min-width="333">
        <el-text>
          {{ roomDetailed.roomType }}
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Number of Beds" align="center" :span="4" min-width="333">
        <el-text>
          {{ roomDetailed.numberOfBeds }}
        </el-text>
      </el-descriptions-item>

      <el-descriptions-item label="Location" label-align="center" :span="12">
        <el-text>
          {{ roomDetailed.location }}
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Description" label-align="center" :span="12">
        <el-text>
          {{ roomDetailed.description }}
        </el-text>
      </el-descriptions-item>

    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>