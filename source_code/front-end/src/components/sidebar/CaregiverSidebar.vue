<script setup lang="ts">
import {Finished, Stopwatch, House} from '@element-plus/icons-vue'
import {onMounted, ref, watchEffect} from 'vue'
import {useRouter} from 'vue-router'
import {useConfigStore} from "../../stores/config.ts"
import {UserType} from "../../types/user.ts";
import axios from "axios";

const config = useConfigStore()
const menuItemActiveColor = config.sidebarMenuItemActiveColor
const menuItemInactiveColor = config.sidebarMenuItemInactiveColor

const router = useRouter()
const currentRoute = router.currentRoute
const activeMenuItem = ref<string>(currentRoute.value.path)

watchEffect(() => {
  activeMenuItem.value = currentRoute.value.path
})

const historyExamination = '/caregiver/history/examination'
const historyRehabilitation = '/caregiver/history/rehabilitation'
const historySurgery = '/caregiver/history/surgery'
const historyHospitalization = '/caregiver/history/hospitalization'

const inProcessExamination = '/caregiver/in-process/examination'
const inProcessRehabilitation = '/caregiver/in-process/rehabilitation'
const inProcessSurgery = '/caregiver/in-process/surgery'
const inProcessHospitalization = '/caregiver/in-process/hospitalization'

const sidebarReady = ref(false)
const inExaminationRoom = ref(false)
const inRehabilitationRoom = ref(false)
const inSurgeryRoom = ref(false)
const inHospitalizationRoom = ref(false)

const room = '/caregiver/room'

onMounted(() => {
  axios.get(config.rootOfPath + '/caregiver/permission', {
  params:
    {userId: config.userId,
    userType: config.userType}
  })
  .then((res)=>{
    console.log(res)
    inExaminationRoom.value = res.data.results.inExaminationRoom === 'true'
    inRehabilitationRoom.value = res.data.results.inRehabilitationRoom === 'true'
    inSurgeryRoom.value = res.data.results.inSurgeryRoom === 'true'
    inHospitalizationRoom.value = res.data.results.inHospitalizationRoom === 'true'
    sidebarReady.value = true
  })
})
</script>

<template>
  <el-scrollbar>
    <el-menu :router="true" v-loading="!sidebarReady">
      <el-menu-item v-if="inExaminationRoom" :index="historyExamination" :style="{color: (activeMenuItem === historyExamination)? menuItemActiveColor: menuItemInactiveColor}">History Examination</el-menu-item>
      <el-menu-item v-if="inRehabilitationRoom" :index="historyRehabilitation" :style="{color: (activeMenuItem === historyRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">History Rehabilitation</el-menu-item>
      <el-menu-item v-if="inSurgeryRoom" :index="historySurgery" :style="{color: (activeMenuItem === historySurgery)? menuItemActiveColor: menuItemInactiveColor}">History Surgery</el-menu-item>
      <el-menu-item v-if="inHospitalizationRoom" :index="historyHospitalization" :style="{color: (activeMenuItem === historyHospitalization)? menuItemActiveColor: menuItemInactiveColor}">History Hospitalization</el-menu-item>

      <el-menu-item v-if="inExaminationRoom" :index="inProcessExamination" :style="{color: (activeMenuItem === inProcessExamination)? menuItemActiveColor: menuItemInactiveColor}">In Process Examination</el-menu-item>
      <el-menu-item v-if="inRehabilitationRoom" :index="inProcessRehabilitation" :style="{color: (activeMenuItem === inProcessRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">In Process Rehabilitation</el-menu-item>
      <el-menu-item v-if="inSurgeryRoom" :index="inProcessSurgery" :style="{color: (activeMenuItem === inProcessSurgery)? menuItemActiveColor: menuItemInactiveColor}">In Process Surgery</el-menu-item>
      <el-menu-item v-if="inHospitalizationRoom" :index="inProcessHospitalization" :style="{color: (activeMenuItem === inProcessHospitalization)? menuItemActiveColor: menuItemInactiveColor}">In Process Hospitalization</el-menu-item>

      <el-menu-item v-if="config.userType===UserType.Nurse" :index="room" :style="{color: (activeMenuItem === room)? menuItemActiveColor: menuItemInactiveColor}">Assigned Room Information</el-menu-item>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>

</style>