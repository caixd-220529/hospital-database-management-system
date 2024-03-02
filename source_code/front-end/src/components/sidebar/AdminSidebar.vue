<script setup lang="ts">
import {View, EditPen, User} from '@element-plus/icons-vue'
import { watchEffect, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore} from "../../stores/config.ts"

const config = useConfigStore()
const menuItemActiveColor = config.sidebarMenuItemActiveColor
const menuItemInactiveColor = config.sidebarMenuItemInactiveColor

const router = useRouter()
const currentRoute = router.currentRoute
const activeMenuItem = ref<string>(currentRoute.value.path)
watchEffect(() => {
  activeMenuItem.value = currentRoute.value.path
})

const viewConsultation = '/admin/view/consultation'
const viewPrescription = '/admin/view/prescription'
const viewExamination = '/admin/view/examination'
const viewRehabilitation = '/admin/view/rehabilitation'
const viewSurgery = '/admin/view/surgery'
const viewHospitalization = '/admin/view/hospitalization'

const managePatient = '/admin/manage/patient'
const manageDoctor = '/admin/manage/doctor'
const manageNurse = '/admin/manage/nurse'
const manageHelpingStaff = '/admin/manage/helping-staff'
const manageMedicine = '/admin/manage/medicine'
const manageExamination = '/admin/manage/examination'
const manageRehabilitation = '/admin/manage/rehabilitation'
const manageSurgery = '/admin/manage/surgery'
const manageDepartment = '/admin/manage/department'
const manageRoom = '/admin/manage/room'

const userRegistration = '/admin/registration'

</script>

<template>
  <el-scrollbar>
    <el-menu :router="true">
      <el-sub-menu index="record" v-if="false">
        <template #title>
          <el-icon><View /></el-icon>Document
        </template>
          <el-menu-item :index="viewConsultation" :style="{color: (activeMenuItem===viewConsultation)? menuItemActiveColor: menuItemInactiveColor}">Consultation</el-menu-item>
          <el-menu-item :index="viewPrescription" :style="{color: (activeMenuItem===viewPrescription)? menuItemActiveColor: menuItemInactiveColor}">Prescription</el-menu-item>
          <el-menu-item :index="viewExamination" :style="{color: (activeMenuItem===viewExamination)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
          <el-menu-item :index="viewRehabilitation" :style="{color: (activeMenuItem===viewRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
          <el-menu-item :index="viewSurgery" :style="{color: (activeMenuItem===viewSurgery)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
          <el-menu-item :index="viewHospitalization" :style="{color: (activeMenuItem===viewHospitalization)? menuItemActiveColor: menuItemInactiveColor}">Hospitalization</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="manage">
        <template #title>
          <el-icon><EditPen /></el-icon>Management
        </template>
        <el-menu-item-group>
          <template #title>User</template>
          <el-menu-item :index="managePatient" :style="{color: (activeMenuItem===managePatient)? menuItemActiveColor: menuItemInactiveColor}">Patient</el-menu-item>
          <el-menu-item :index="manageDoctor" :style="{color: (activeMenuItem===manageDoctor)? menuItemActiveColor: menuItemInactiveColor}">Doctor</el-menu-item>
          <el-menu-item :index="manageNurse" :style="{color: (activeMenuItem===manageNurse)? menuItemActiveColor: menuItemInactiveColor}">Nurse</el-menu-item>
          <el-menu-item :index="manageHelpingStaff" :style="{color: (activeMenuItem===manageHelpingStaff)? menuItemActiveColor: menuItemInactiveColor}">Helping Staff</el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group>
          <template #title>Medical</template>
          <el-menu-item :index="manageMedicine" :style="{color: (activeMenuItem===manageMedicine)? menuItemActiveColor: menuItemInactiveColor}">Medicine</el-menu-item>
          <el-menu-item :index="manageExamination" :style="{color: (activeMenuItem===manageExamination)? menuItemActiveColor: menuItemInactiveColor}">Examination</el-menu-item>
          <el-menu-item :index="manageRehabilitation" :style="{color: (activeMenuItem===manageRehabilitation)? menuItemActiveColor: menuItemInactiveColor}">Rehabilitation</el-menu-item>
          <el-menu-item :index="manageSurgery" :style="{color: (activeMenuItem===manageSurgery)? menuItemActiveColor: menuItemInactiveColor}">Surgery</el-menu-item>
          <el-menu-item :index="manageDepartment" :style="{color: (activeMenuItem===manageDepartment)? menuItemActiveColor: menuItemInactiveColor}">Department</el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group>
          <template #title>Property</template>
          <el-menu-item :index="manageRoom" :style="{color: (activeMenuItem===manageRoom)? menuItemActiveColor: menuItemInactiveColor}">Room</el-menu-item>
        </el-menu-item-group>
      </el-sub-menu>
      <el-menu-item :index="userRegistration" :style="{color: (activeMenuItem===userRegistration)? menuItemActiveColor: menuItemInactiveColor}"><el-icon><User /></el-icon>Registration</el-menu-item>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>

</style>