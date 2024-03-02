<script setup lang="ts">
import {useConfigStore} from '../stores/config'
import {useRouter} from 'vue-router'
import {Moon, Setting, Sunny} from '@element-plus/icons-vue'
import PatientSidebar from '../components/sidebar/PatientSidebar.vue'
import DoctorSidebar from '../components/sidebar/DoctorSidebar.vue'
import CaregiverSidebar from "../components/sidebar/CaregiverSidebar.vue"
import AdminSidebar from "../components/sidebar/AdminSidebar.vue"
import {ref, watch} from 'vue'
import {UserType} from "../types/user.ts"
import {ElScrollbar} from 'element-plus'
import {useDark} from "@vueuse/core";

const config = useConfigStore()
const router = useRouter()
const mainScrollbarRef = ref<InstanceType<typeof ElScrollbar>>()


const routeToTitle = (route: string) => {
  const routeSplitArr = route.split('/')
  if(routeSplitArr.length===2){
    return 'Welcome'
  }else if (routeSplitArr[2] === 'view' && config.userType !== UserType.Admin) {
    return 'View Personal Information'
  } else if (routeSplitArr[2] === 'edit') {
    return 'Edit Personal Information'
  } else if (routeSplitArr[2] === 'edit-password') {
    return 'Edit Password'
  } else if (routeSplitArr[1]==='patient'){
    switch(routeSplitArr[2]){
      case 'history':
        switch(routeSplitArr[3]){
          case 'consultation':
            return 'History Consultation'
          case 'prescription':
            return 'History Prescription'
          case 'examination':
            return 'History Examination'
          case 'rehabilitation':
            return 'History Rehabilitation'
          case 'surgery':
            return 'History Surgery'
          case 'hospitalization':
            return 'History Hospitalization'
          case 'payment':
            return 'History Payment'
          default:
            return route
        }
      case 'in-process':
        switch(routeSplitArr[3]){
          case 'consultation':
            return 'In Process Consultation'
          case 'prescription':
            return 'In Process Prescription'
          case 'examination':
            return 'In Process Examination'
          case 'rehabilitation':
            return 'In Process Rehabilitation'
          case 'surgery':
            return 'In Process Surgery'
          case 'hospitalization':
            return 'In Process Hospitalization'
          case 'payment':
            return 'In Process Payment'
          default:
            return route
        }
      case 'appointment':
        return 'Appointment'
      default:
        return route
    }
  } else if (routeSplitArr[1]==='doctor'){
    switch(routeSplitArr[2]){
      case 'record':
        switch(routeSplitArr[3]){
          case 'consultation':
            return 'Record Consultation'
          case 'prescription':
            return 'Record Prescription'
          case 'examination':
            return 'Record Examination'
          case 'rehabilitation':
            return 'Record Rehabilitation'
          case 'surgery':
            return 'Record Surgery'
          case 'hospitalization':
            return 'Record Hospitalization'
          case 'payment':
            return 'Record Payment'
          default:
            return route
        }
      case 'patient-information':
        switch(routeSplitArr[3]){
          case 'consultation':
            return 'Patient Consultation Information'
          case 'prescription':
            return 'Patient Prescription Information'
          case 'examination':
            return 'Patient Examination Information'
          case 'rehabilitation':
            return 'Patient Rehabilitation Information'
          case 'surgery':
            return 'Patient Surgery Information'
          case 'hospitalization':
            return 'Patient Hospitalization Information'
          default:
            return route
        }
      case 'doctor-information':
        switch(routeSplitArr[3]){
          case 'consultation':
            return 'Doctor Consultation Information'
          case 'prescription':
            return 'Doctor Prescription Information'
          case 'examination':
            return 'Doctor Examination Information'
          case 'rehabilitation':
            return 'Doctor Rehabilitation Information'
          case 'surgery':
            return 'Doctor Surgery'
          case 'hospitalization':
            return 'Doctor Hospitalization Information'
          default:
            return route
        }
      default:
        return route
    }
  } else if (routeSplitArr[1]==='caregiver'){
    switch(routeSplitArr[2]){
      case 'history':
        switch(routeSplitArr[3]){
          case 'examination':
            return 'History Examination'
          case 'rehabilitation':
            return 'History Rehabilitation'
          case 'surgery':
            return 'History Surgery'
          case 'hospitalization':
            return 'History Hospitalization'
          default:
            return route
        }
      case 'in-process':
        switch(routeSplitArr[3]){
          case 'examination':
            return 'In Process Examination'
          case 'rehabilitation':
            return 'In Process Rehabilitation'
          case 'surgery':
            return 'In Process Surgery'
          case 'hospitalization':
            return 'In Process Hospitalization'
          default:
            return route
        }
      case 'room':
        return 'Assigned Room Information'
      default:
        return route
    }
  } else if (routeSplitArr[1]==='admin'){
    if (routeSplitArr.length === 3) {
      return 'Registration'
    } else {
      switch (routeSplitArr[3]){
        case 'patient':
          return 'Patient Management'
        case 'doctor':
          return 'Doctor Management'
        case 'nurse':
          return 'Nurse Management'
        case 'helping-staff':
          return 'Helping Staff Management'
        case 'medicine':
          return 'Medicine Management'
        case 'examination':
          return 'Examination Management'
        case 'rehabilitation':
          return 'Rehabilitation Management'
        case 'surgery':
          return 'Surgery Management'
        case 'department':
          return 'Department Management'
        case 'room':
          return 'Room Management'
      }
    }
  }
  else {
    return route
  }
}
const title = ref(routeToTitle(router.currentRoute.value.path))
watch(() => router.currentRoute.value.path, (newVal) => {
  title.value = routeToTitle(newVal)
  mainScrollbarRef.value!.setScrollTop(0)
})

const handleLogOut = () => {
  localStorage.removeItem('userId')
  localStorage.removeItem('userName')
  localStorage.removeItem('userType')
  router.push('/login-or-register/login')
}

const isDark = useDark()
const toggleDark = ()=>{isDark.value = !isDark.value}
</script>

<template>
  <el-container style="height: 100vh;">
    <el-aside width="250px" class='sidebar'>
      <PatientSidebar v-if="config.userType===UserType.Patient" />
      <DoctorSidebar v-else-if="config.userType===UserType.Doctor"/>
      <CaregiverSidebar v-else-if="config.userType===UserType.Nurse || config.userType===UserType.HelpingStaff"/>
      <AdminSidebar v-else-if="config.userType===UserType.Admin"/>
    </el-aside>

    <el-container>
      <el-header class="header">
        <el-row style="height: 100%;">
          <el-col :span="12" style="text-align: left;">
            <span class="toolbar-left">
              <el-text size="large" tag="b">{{ title }}</el-text>
            </span>
          </el-col>
          <el-col :span="12" style="text-align: right;">
            <span class="toolbar-right">
              <span>
                <el-switch
                  v-model="isDark"
                  :active-action-icon="Moon"
                  :inactive-action-icon="Sunny"
                  style="margin-right: 8px;"
                />
              </span>
              <el-dropdown>
                <el-icon style="margin-right: 8px; margin-top: 2px"><setting/></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleLogOut">Log Out</el-dropdown-item>
                    <el-dropdown-item @click="router.push(`/${config.userType}/edit`)" v-if="config.userType !== UserType.Admin">Edit Personal Information</el-dropdown-item>
                    <el-dropdown-item @click="router.push(`/${config.userType}/edit-password`)">Edit Password</el-dropdown-item>
                    <el-dropdown-item @click="router.push(`/${config.userType}/view`)" v-if="config.userType !== UserType.Admin">View Personal Information</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <span><el-text> {{ config.userName }} </el-text></span>
            </span>
          </el-col>
        </el-row>
      </el-header>


      <el-main>
        <el-scrollbar ref="mainScrollbarRef">
          <router-view />
        </el-scrollbar>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.sidebar {
  background:  var(--el-color-primary-light-8);
  color: var(--el-text-color-primary);
}
.header {
  background-color: var(--el-color-primary-light-7);
  
}
.toolbar-left {
  display: inline-flex;
  align-items: center;
  justify-content: left;
  height: 100%;
  left: 20px;
}
.toolbar-right {
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: right;
  height: 100%;
  right: 20px;
}
</style>
