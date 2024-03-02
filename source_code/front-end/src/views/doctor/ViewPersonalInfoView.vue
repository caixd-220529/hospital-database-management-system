<script setup lang="ts">
import DoctorPersonalInfoDescription from "../../components/description/user/DoctorPersonalInfoDescription.vue"
import { useConfigStore } from '../../stores/config'

const config = useConfigStore()
const userId = config.userId

</script>

<template>
  <div class="view-personal-info-div">
    <DoctorPersonalInfoDescription :doctorId="userId" />
  </div>
</template>

<style scoped>

</style>