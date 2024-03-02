<script setup lang="ts">
import {ref} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import axios, {AxiosResponse} from 'axios'
import {useConfigStore} from '../stores/config'
import {useRouter} from 'vue-router'
import {stringToUserType, UserType} from "../types/user.ts"


const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()

interface LoginForm {
  userId: string
  password: string
}

const loginFormRef = ref<FormInstance>()
const loginForm = ref<LoginForm>({
  userId: '',
  password: '',
})
const loginRules = ref<FormRules<LoginForm>>({
  userId: [
    {required: true, message: 'Please enter your user ID', trigger: 'blur'},
  ],
  password: [
    {required: true, message: 'Please enter your password', trigger: 'blur'},
  ],
})

// the function that is called when the form is reset
const resetLoginForm = (form: FormInstance | undefined) => {
  if (!form) return
  console.log('reset the login form')
  form.resetFields()
}

const loginFailedDialogVisible = ref<boolean>(false)
const loginFailedMessage = ref<string>('')
// the function that is called when the form is submitted
const submitLoginForm = async (form: FormInstance | undefined, formValue: LoginForm) => {
  if (!form) return
  await form.validate((valid, fields) => {
    if (valid) {
      axios.post(rootOfPath + '/login', formValue).then((response: AxiosResponse) => {
        config.userType = stringToUserType(response.data.results.userType)
        config.userId = formValue.userId
        config.userName = response.data.results.userName
        localStorage.setItem('userId', config.userId)
        localStorage.setItem('userName', config.userName)
        localStorage.setItem('userType', config.userType)
        if (config.userType === UserType.Patient) {
          router.push('/patient')
        } else if (config.userType === UserType.Doctor) {
          router.push('/doctor')
        } else if (config.userType === UserType.Nurse) {
          router.push('/caregiver')
        } else if (config.userType === UserType.HelpingStaff) {
          router.push('/caregiver')
        } else if(config.userType === UserType.Admin) {
          router.push('/admin')
        } else {
          console.error('unknown userType')
        }
      })
        .catch((err: any) => {
        console.log(err)
        loginFailedDialogVisible.value = true
        loginFailedMessage.value = err.response.data.results
      })
    } else {
      console.log('error submit!', fields)
    }
  })
}
</script>

<template>
  <el-dialog
    title="Login Failed"
    v-model="loginFailedDialogVisible"
    width="30%"
  >
    <span>{{ loginFailedMessage }}</span>
    <template #footer>
      <el-button @click="loginFailedDialogVisible=false">Confirm</el-button>
    </template>
  </el-dialog>
  <el-form
    ref="loginFormRef"
    :model="loginForm"
    label-width="80px"
    :rules="loginRules"
  >
    <el-form-item label="User ID" prop="userId">
      <el-input v-model="loginForm.userId" placeholder="Enter ID"></el-input>
    </el-form-item>
    <el-form-item label="Password" prop="password">
      <el-input v-model="loginForm.password" placeholder="Enter password" type="password"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submitLoginForm(loginFormRef, loginForm)">Login</el-button>
      <el-button @click="resetLoginForm(loginFormRef)">Reset</el-button>
    </el-form-item>
  </el-form>
</template>

<style scoped>

</style>
