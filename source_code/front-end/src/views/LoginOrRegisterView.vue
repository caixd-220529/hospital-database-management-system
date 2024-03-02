<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const buttonString = ref('')
const cardHeaderString = ref('')

const defineCardHeaderString = (path:string) => {
  if(path.endsWith('/register')){
    buttonString.value = 'Switch to login page'
    cardHeaderString.value = 'Register'
  } else {
    buttonString.value = 'Switch to register page'
    cardHeaderString.value = 'Login'
  }
}

defineCardHeaderString(router.currentRoute.value.fullPath)
watch(() => router.currentRoute.value.fullPath, (newVal) => {
  defineCardHeaderString(newVal)
})

const handleClick = () => {
  if(buttonString.value==='Switch to register page'){
    buttonString.value = 'Switch to login page'
    cardHeaderString.value = 'Register'
    router.push('/login-or-register/register')
  } else {
    buttonString.value = 'Switch to register page'
    cardHeaderString.value = 'Login'
    router.push('/login-or-register/login')
  }
}

</script>

<template>
  <div style="height: 1vh;"></div>
  <el-card class="box-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>{{ cardHeaderString }}</span>
        <el-button @click="handleClick">{{ buttonString }}</el-button>
      </div>
    </template>
    <div>
      <router-view />
    </div>
  </el-card>
  <div style="height: 1vh;"></div>
</template>


<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.box-card {
  width: 480px;
  margin: 0 auto;
}
</style>