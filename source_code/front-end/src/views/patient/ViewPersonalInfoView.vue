<script setup lang="ts">
import PatientPersonalInfoDescription from '../../components/description/user/PatientPersonalInfoDescription.vue'
import { useConfigStore } from '../../stores/config'

const config = useConfigStore()
const userId = config.userId
</script>

<template>
  <div class="view-personal-info-div">
    <PatientPersonalInfoDescription :patientId="userId" />
  </div>
</template>
<style scoped>

</style>
