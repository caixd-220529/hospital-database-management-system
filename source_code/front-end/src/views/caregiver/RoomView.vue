<script setup lang="ts">
import RoomDescription from '../../components/description/other/RoomDescription.vue'
import { useConfigStore } from '../../stores/config'
import {onBeforeMount, ref} from "vue";
import axios, {AxiosResponse} from "axios";
import {NurseInfoKey} from "../../types/user.ts";

const config = useConfigStore()
const userId = config.userId

const roomId = ref('')
onBeforeMount(() => {
  axios.get(config.rootOfPath + `/get-nurse-info?nurseId=${config.userId}`).then((response: AxiosResponse) => {
    roomId.value = response.data.results['roomId']
  }).catch((err: any) => {
    console.error(err)
  })
})

</script>

<template>
  <div class="view-personal-info-div">
    <RoomDescription v-if="roomId !== ''" :roomId="roomId" />
  </div>
</template>
<style scoped>

</style>