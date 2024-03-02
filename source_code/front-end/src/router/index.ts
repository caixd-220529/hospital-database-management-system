// import {createRouter, createWebHistory} from 'vue-router'
import {createRouter, createWebHashHistory} from 'vue-router'
import {useConfigStore} from '../stores/config'
import { stringToUserType } from '../types/user'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login-or-register/login'
    },
    {
      path: '/login-or-register',
      name: 'login-or-register',
      component: () => import('../views/LoginOrRegisterView.vue'),
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('../views/LoginView.vue')
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('../views/RegisterView.vue')
        }
      ]
    },
    {
      path: '/patient',
      component: () => import('../views/MainView.vue'),
      children: [
        // path of history
        {
          path: 'history',
          children: [
            {
              path: 'consultation',
              component: () => import('../views/patient/ConsultationView.vue')
            },
            {
              path: 'prescription',
              component: () => import('../views/patient/PrescriptionView.vue')
            },
            {
              path: 'examination',
              component: () => import('../views/patient/ExaminationView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/patient/RehabilitationView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/patient/SurgeryView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/patient/HospitalizationView.vue')
            },
            {
              path: 'payment',
              component: () => import('../views/patient/ChargeView.vue')
            }
          ],
        },
        // path of inProcess
        {
          path: 'in-process',
          children: [
            {
              path: 'consultation',
              component: () => import('../views/patient/ConsultationView.vue')
            },
            {
              path: 'prescription',
              component: () => import('../views/patient/PrescriptionView.vue')
            },
            {
              path: 'examination',
              component: () => import('../views/patient/ExaminationView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/patient/RehabilitationView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/patient/SurgeryView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/patient/HospitalizationView.vue')
            },
            {
              path: 'payment',
              component: () => import('../views/patient/ChargeView.vue')
            }
          ]
        },
        // path of editing personal info
        {
          path: 'edit',
          component: () => import('../views/patient/EditPersonalInfoView.vue')
        },
        // path of making appointment
        {
          path: 'appointment/consultation',
          component: () => import('../views/patient/ConsultationAppointmentView.vue')
        },
        // path of editing password
        {
          path: 'edit-password',
          component: () => import('../views/EditPasswordView.vue')
        },
        // path of viewing personal info
        {
          path: 'view',
          component: () => import('../views/patient/ViewPersonalInfoView.vue')
        }
      ]
    },
    {
      path: '/doctor',
      component: () => import('../views/MainView.vue'),
      children: [
        {
          path: 'record',
          children: [
            {
              path: 'consultation',
              component: () => import('../views/doctor/ConsultationView.vue')
            },
            {
              path: 'prescription',
              component: () => import('../views/doctor/PrescriptionView.vue')
            },
            {
              path: 'examination',
              component: () => import('../views/doctor/ExaminationView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/doctor/RehabilitationView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/doctor/SurgeryView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/doctor/HospitalizationView.vue')
            },
          ]
        },
        {
          path: 'patient-information',
          children: [
            {
              path: 'consultation',
              component: () => import('../views/doctor/ConsultationView.vue')
            },
            {
              path: 'prescription',
              component: () => import('../views/doctor/PrescriptionView.vue')
            },
            {
              path: 'examination',
              component: () => import('../views/doctor/ExaminationView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/doctor/RehabilitationView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/doctor/SurgeryView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/doctor/HospitalizationView.vue')
            },
          ]
        },
        {
          path: 'doctor-information',
          children: [
            {
              path: 'consultation',
              component: () => import('../views/doctor/ConsultationView.vue')
            },
            {
              path: 'prescription',
              component: () => import('../views/doctor/PrescriptionView.vue')
            },
            {
              path: 'examination',
              component: () => import('../views/doctor/ExaminationView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/doctor/RehabilitationView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/doctor/SurgeryView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/doctor/HospitalizationView.vue')
            },
          ]
        },
        // path of editing password
        {
          path: 'edit-password',
          component: () => import('../views/EditPasswordView.vue')
        },
        // path of viewing personal info
        {
          path: 'view',
          component: () => import('../views/doctor/ViewPersonalInfoView.vue')
        },
        // path of editing personal info
        {
          path: 'edit',
          component: () => import('../views/doctor/EditPersonalInfoView.vue')
        },
      ]
    },
    {
      path: '/caregiver',
      component: () => import('../views/MainView.vue'),
      children: [
        // path of history
        {
          path: 'history',
          children: [
            {
              path: 'examination',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/caregiver/EventView.vue')
            },
          ],
        },
        // path of inProcess
        {
          path: 'in-process',
          children: [
            {
              path: 'examination',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'rehabilitation',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'surgery',
              component: () => import('../views/caregiver/EventView.vue')
            },
            {
              path: 'hospitalization',
              component: () => import('../views/caregiver/EventView.vue')
            },
          ]
        },
        {
          path: 'room',
          component: () => import('../views/caregiver/RoomView.vue')
        }
      ]
    },
    {
      path: '/nurse',
      component: () => import('../views/MainView.vue'),
      children:[
        {
          path: 'edit-password',
          component: () => import('../views/EditPasswordView.vue')
        },
        {
          path: 'view',
          component: () => import('../views/caregiver/ViewNurseInfo.vue')
        },
        {
          path: 'edit',
          component: () => import('../views/caregiver/EditNurseInfo.vue')
        }
      ]
    },
    {
      path: '/helpingStaff',
      component: () => import('../views/MainView.vue'),
      children:[
        {
          path: 'edit-password',
          component: () => import('../views/EditPasswordView.vue')
        },
        {
          path: 'view',
          component: () => import('../views/caregiver/ViewHelpingStaffInfo.vue')
        },
        {
          path: 'edit',
          component: () => import('../views/caregiver/EditHelpingStaffInfo.vue')
        }
      ]
    },
    {
      path: '/admin',
      component: () => import('../views/MainView.vue'),
      children:[
        {
          path: 'edit-password',
          component: () => import('../views/EditPasswordView.vue')
        },
        {
          path: 'view/:name',
          component: () => import('../views/admin/EventView.vue')
        },
        {
          path: 'manage/:name',
          component: () => import('../views/admin/EventView.vue')
        },
        {
          path: 'registration',
          component: () => import('../views/admin/UserRegistrationView.vue')
        }
      ]
    },
    {
      path: '/temp',
      component: () => import('../views/TempView.vue'),
    }

  ]
})

router.beforeEach((to, from) => {
  console.log(to, from)
  if (to.fullPath.includes('login-or-register') || to.fullPath.includes('temp')) {
    return true
  }
  const localStorageUserName = localStorage.getItem('userName')
  const localStorageUserId = localStorage.getItem('userId')
  const localStorageUserType = localStorage.getItem('userType')
  if (!localStorageUserName || !localStorageUserId || !localStorageUserType) {
    console.error('localStorage is not complete')
    return {name: 'login'}
  }
  const userTypeInRouter = to.fullPath.split('/')[1]
  const allUserTypeArr = ['patient', 'doctor', 'nurse', 'helpingStaff', 'caregiver', 'admin']
  if (!allUserTypeArr.includes(userTypeInRouter) || !allUserTypeArr.includes(localStorageUserType)){
    console.error('unknown userType in localStorage or router', userTypeInRouter, localStorageUserType)
    return {name: 'login'}
  }
  if (userTypeInRouter === localStorageUserType || (userTypeInRouter === 'caregiver' &&  ['nurse', 'helpingStaff'].includes(localStorageUserType))) {
    // write into the config store
    const config = useConfigStore()
    config.userType = stringToUserType(localStorageUserType)
    config.userId = localStorageUserId
    config.userName = localStorageUserName
    return true
  } else {
    console.log('user type unmatched', userTypeInRouter, localStorageUserType)
    return {name: 'login'}
  }
})

export default router