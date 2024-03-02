<script setup lang="ts">
import { EditPen, Files, Management } from '@element-plus/icons-vue'
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

const recordConsultation = '/doctor/record/consultation'
const recordPrescription = '/doctor/record/prescription'
const recordExamination = '/doctor/record/examination'
const recordRehabilitation = '/doctor/record/rehabilitation'
const recordSurgery = '/doctor/record/surgery'
const recordHospitalization = '/doctor/record/hospitalization'

const patientConsultationInformation = '/doctor/patient-information/consultation'
const patientPrescriptionInformation = '/doctor/patient-information/prescription'
const patientExaminationInformation = '/doctor/patient-information/examination'
const patientRehabilitationInformation = '/doctor/patient-information/rehabilitation'
const patientSurgeryInformation = '/doctor/patient-information/surgery'
const patientHospitalizationInformation = '/doctor/patient-information/hospitalization'

const doctorConsultationInformation = '/doctor/doctor-information/consultation'
const doctorPrescriptionInformation = '/doctor/doctor-information/prescription'
const doctorExaminationInformation = '/doctor/doctor-information/examination'
const doctorRehabilitationInformation = '/doctor/doctor-information/rehabilitation'
const doctorSurgeryInformation = '/doctor/doctor-information/surgery'
const doctorHospitalizationInformation = '/doctor/doctor-information/hospitalization'

</script>

<template>
  <el-scrollbar>
    <el-menu :router="true">
      <el-sub-menu index="record">
        <template #title>
          <el-icon><EditPen /></el-icon>Record
        </template>
        <el-menu-item :index="recordConsultation" :style="{color: (activeMenuItem===recordConsultation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
        <el-menu-item :index="recordPrescription" :style="{color: (activeMenuItem===recordPrescription)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
        <el-menu-item :index="recordExamination" :style="{color: (activeMenuItem===recordExamination)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
        <el-menu-item :index="recordRehabilitation" :style="{color: (activeMenuItem===recordRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
        <el-menu-item :index="recordSurgery" :style="{color: (activeMenuItem===recordSurgery)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
        <el-menu-item :index="recordHospitalization" :style="{color: (activeMenuItem===recordHospitalization)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="patientHistory">
        <template #title>
          <el-icon><Files /></el-icon>Patient Information
        </template>
        <el-menu-item :index="patientConsultationInformation" :style="{color: (activeMenuItem===patientConsultationInformation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
        <el-menu-item :index="patientPrescriptionInformation" :style="{color: (activeMenuItem===patientPrescriptionInformation)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
        <el-menu-item :index="patientExaminationInformation" :style="{color: (activeMenuItem===patientExaminationInformation)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
        <el-menu-item :index="patientRehabilitationInformation" :style="{color: (activeMenuItem===patientRehabilitationInformation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
        <el-menu-item :index="patientSurgeryInformation" :style="{color: (activeMenuItem===patientSurgeryInformation)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
        <el-menu-item :index="patientHospitalizationInformation" :style="{color: (activeMenuItem===patientHospitalizationInformation)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="doctorHistory">
        <template #title>
          <el-icon><Management /></el-icon>Doctor Information
        </template>
        <el-menu-item :index="doctorConsultationInformation" :style="{color: (activeMenuItem===doctorConsultationInformation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
        <el-menu-item :index="doctorPrescriptionInformation" :style="{color: (activeMenuItem===doctorPrescriptionInformation)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
        <el-menu-item :index="doctorExaminationInformation" :style="{color: (activeMenuItem===doctorExaminationInformation)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
        <el-menu-item :index="doctorRehabilitationInformation" :style="{color: (activeMenuItem===doctorRehabilitationInformation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
        <el-menu-item :index="doctorSurgeryInformation" :style="{color: (activeMenuItem===doctorSurgeryInformation)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
        <el-menu-item :index="doctorHospitalizationInformation" :style="{color: (activeMenuItem===doctorHospitalizationInformation)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>

</style>