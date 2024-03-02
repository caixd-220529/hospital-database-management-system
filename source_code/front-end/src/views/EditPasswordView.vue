<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useConfigStore } from '../stores/config'
import { ElMessage } from 'element-plus'

const rootOfPath = useConfigStore().rootOfPath

interface PasswordForm {
  oldPassword: string
  newPassword: string
  confirmNewPassword: string
}

const passwordFormRef = ref<FormInstance>()
const passwordForm = ref<PasswordForm>({
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})
// @ts-ignore
const validateNewPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please enter a new password'))
  } else {
    if (passwordForm.value.confirmNewPassword !== '') {
      passwordFormRef.value?.validateField('confirmNewPassword')
    }
    callback()
  }

}
// @ts-ignore
const validateConfirmNewPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('Please confirm your new password'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('The two passwords do not match'))
  } else {
    callback()
  }
}
const passwordFormRules = ref<FormRules<PasswordForm>>({
  oldPassword: [
    { required: true, message: 'Please enter your old password', trigger: 'change' }
  ],
  newPassword: [
    { required: true, validator: validateNewPassword, trigger: 'change' }
  ],
  confirmNewPassword: [
    { required: true, validator: validateConfirmNewPassword, trigger: 'change' }
  ]
})
const buttonDisabled = ref<boolean>(false)
const failedMessage = ref('')
const failedMessageDialogVisible = ref(false)
const submitPasswordForm = async (form: FormInstance | undefined) => {
  if (!form) return
  buttonDisabled.value = true
  await form.validate((valid: boolean) => {
    if (valid) {
      const submitValue:any = {...passwordForm.value}
      submitValue.userId = useConfigStore().userId
      axios.post(rootOfPath + '/edit-password', submitValue).then(() => {
        ElMessage({
          message: 'Edit password successfully',
          type: 'success'
        })
        resetPasswordForm(form)
      }).catch((error: any) => {
        console.log(error)
        failedMessageDialogVisible.value = true
        failedMessage.value = error.response.data.results
      }).finally(() => {
        buttonDisabled.value = false
      })
    } else {
      buttonDisabled.value = false
      console.log('error submit')
    }
  })
}
const resetPasswordForm = (form: FormInstance | undefined) => {
  if (!form) return
  form.resetFields()
}
</script>

<template>
  <el-dialog
    title="Failed"
    v-model="failedMessageDialogVisible"
    width="30%"
    :before-close="() => failedMessageDialogVisible = false"
  >
    <span>{{ failedMessage }}</span>
    <template #footer>
      <el-button type="primary" @click="failedMessageDialogVisible = false">Confirm</el-button>
    </template>
  </el-dialog>
  <div style="max-width: 500px; margin: 0 auto;">
    <el-form
      ref="passwordFormRef"
      :model="passwordForm"
      label-position="top"
      :rules="passwordFormRules"
    >
      <el-form-item label="Old Password" prop="oldPassword" >
        <el-input v-model="passwordForm.oldPassword" show-password />
      </el-form-item>

      <el-form-item label="New Password" prop="newPassword" >
        <el-input v-model="passwordForm.newPassword" show-password />
      </el-form-item>

      <el-form-item label="Confirm New Password" prop="confirmNewPassword" >
        <el-input v-model="passwordForm.confirmNewPassword" show-password />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :disabled="buttonDisabled" @click="submitPasswordForm(passwordFormRef)">Submit</el-button>
        <el-button :disabled="buttonDisabled" @click="resetPasswordForm(passwordFormRef)">Reset</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>

</style>
