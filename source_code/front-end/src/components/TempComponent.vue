<script setup lang="ts">
import {watch} from "vue";

const props = defineProps(
  {
    count: {
      type: Number,
      require: true
    }
  }
)

watch(()=>props.count, (newVal, oldVal)=>{
  console.log(newVal, oldVal)
})

</script>

<template>
  <div>count in the component: {{props.count}}</div>
</template>

<style scoped>

</style>