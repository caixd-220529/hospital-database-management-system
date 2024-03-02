<script setup lang="ts">
import { Stopwatch, Finished, Service } from '@element-plus/icons-vue'
import { watchEffect, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore} from "../../stores/config.ts"

const menuItemActiveColor = useConfigStore().sidebarMenuItemActiveColor
const menuItemInactiveColor = useConfigStore().sidebarMenuItemInactiveColor

const router = useRouter()
const currentRoute = router.currentRoute
const activeMenuItem = ref<string>(currentRoute.value.path)

watchEffect(() => {
  activeMenuItem.value = currentRoute.value.path
})

const historyConsultation = '/patient/history/consultation'
const historyPrescription = '/patient/history/prescription'
const historyExamination = '/patient/history/examination'
const historyRehabilitation = '/patient/history/rehabilitation'
const historySurgery = '/patient/history/surgery'
const historyHospitalization = '/patient/history/hospitalization'
const historyPayment = '/patient/history/payment'

const inProcessConsultation= '/patient/in-process/consultation'
const inProcessPrescription = '/patient/in-process/prescription'
const inProcessExamination = '/patient/in-process/examination'
const inProcessRehabilitation = '/patient/in-process/rehabilitation'
const inProcessSurgery = '/patient/in-process/surgery'
const inProcessHospitalization = '/patient/in-process/hospitalization'
const inProcessPayment = '/patient/in-process/payment'

const appointmentConsultation = '/patient/appointment/consultation'
</script>

<template>
  <el-scrollbar>
    <el-menu :router="true">
      <el-sub-menu index="history">
        <template #title>
          <el-icon><Finished /></el-icon>History
        </template>
        <el-menu-item-group>
          <template #title>Medical</template>
          <el-menu-item :index="historyConsultation" :style="{color: (activeMenuItem === historyConsultation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
          <el-menu-item :index="historyPrescription" :style="{color: (activeMenuItem === historyPrescription)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
          <el-menu-item :index="historyExamination" :style="{color: (activeMenuItem === historyExamination)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
          <el-menu-item :index="historyRehabilitation" :style="{color: (activeMenuItem === historyRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
          <el-menu-item :index="historySurgery" :style="{color: (activeMenuItem === historySurgery)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
          <el-menu-item :index="historyHospitalization" :style="{color: (activeMenuItem === historyHospitalization)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group>
          <template #title>Financial</template>
          <el-menu-item :index="historyPayment" :style="{color: (activeMenuItem === historyPayment)? menuItemActiveColor: menuItemInactiveColor}">Payment</el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>
      <el-sub-menu index="inProcess">
        <template #title>
          <el-icon><Stopwatch /></el-icon>In Process
        </template>
        <el-menu-item-group>
          <template #title>Medical</template>
          <el-menu-item :index="inProcessConsultation" :style="{color: (activeMenuItem === inProcessConsultation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
          <el-menu-item :index="inProcessPrescription" :style="{color: (activeMenuItem === inProcessPrescription)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
          <el-menu-item :index="inProcessExamination" :style="{color: (activeMenuItem === inProcessExamination)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
          <el-menu-item :index="inProcessRehabilitation" :style="{color: (activeMenuItem === inProcessRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
          <el-menu-item :index="inProcessSurgery" :style="{color: (activeMenuItem === inProcessSurgery)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
          <el-menu-item :index="inProcessHospitalization" :style="{color: (activeMenuItem === inProcessHospitalization)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group>
          <template #title>Financial</template>
          <el-menu-item :index="inProcessPayment" :style="{color: (activeMenuItem === inProcessPayment)? menuItemActiveColor: menuItemInactiveColor}">Payment</el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>
      <el-sub-menu index="appointment">
        <template #title>
          <el-icon><Service /></el-icon>Appointment
        </template>
        <el-menu-item :index="appointmentConsultation" :style="{color: (activeMenuItem === appointmentConsultation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>
</style>