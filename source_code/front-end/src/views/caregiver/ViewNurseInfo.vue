<script setup lang="ts">
import NursePersonalInfoDescription from "../../components/description/user/NursePersonalInfoDescription.vue"
import { useConfigStore } from '../../stores/config'

const config = useConfigStore()
const userId = config.userId

</script>

<template>
  <div class="view-personal-info-div">
    <NursePersonalInfoDescription :nurse-id="userId"  :show-room-id="false"/>
  </div>
</template>

<style scoped>

</style>