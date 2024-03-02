<script setup lang="ts">
import HelpingStaffPersonalInfoDescription from "../../components/description/user/HelpingStaffPersonalInfoDescription.vue"
import { useConfigStore } from '../../stores/config'

const config = useConfigStore()
const userId = config.userId

</script>

<template>
  <div class="view-personal-info-div">
    <HelpingStaffPersonalInfoDescription :helping-staff-id="userId"  :show-room-id="false"/>
  </div>
</template>

<style scoped>

</style>