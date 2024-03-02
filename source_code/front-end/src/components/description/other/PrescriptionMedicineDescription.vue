<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { PrescriptionMedicineDetailed, PrescriptionMedicineDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const prescriptionMedicineDetailed: PrescriptionMedicineDetailed = {
  medicineId: '',
  prescriptionId: '',
  medicineName: '',
  medicineManufacturer: '',
  courseOfMedication: '',
  dosage: '',
  frequency: '',
  cost: '',
  quantity: ''
}
const props = defineProps(
  {
    prescriptionMedicineId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
    showMedicineId: {
      type: Boolean,
      required: true,
    },
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const getData = ref(false)
const getPrescriptionMedicine = () => {
  if (props.prescriptionMedicineId === '') {
    console.log('prescriptionMedicineId is empty')
  } else {
    console.log('prescriptionMedicineId:', props.prescriptionMedicineId)
  }
  getData.value = false
  const prescriptionId = props.prescriptionMedicineId.split('#')[0]
  const medicineId = props.prescriptionMedicineId.split('#')[1]
  axios.get(rootOfPath + `/get-prescription-medicine-detailed?prescriptionId=${prescriptionId}&medicineId=${medicineId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in prescriptionMedicineDetailed) {
      if (key in response.data.results){
        prescriptionMedicineDetailed[key as PrescriptionMedicineDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
  }).catch((err: any) => {
    console.error(err)
  }).finally(() => {
    getData.value = true
  })
}
onMounted(() => {
  getPrescriptionMedicine()
})
watch(() => props.prescriptionMedicineId, () => {
  getPrescriptionMedicine()
})
const handleShowDetail = (item: DescribableItem, id: string) => {
  emit('changeContent', item, id)
}
</script>

<template>
  <el-scrollbar class="description-scrollbar">
    <el-descriptions
      :column="12"
      :title="title"
      v-loading="!getData"
      border
      direction="vertical"
      class="description-box"
    >
      <div v-if="props.showMedicineId">
        <el-descriptions-item label="Prescription ID" label-align="center" align="center" :span="4" :min-width="333">
          <el-text>
            {{ prescriptionMedicineDetailed.prescriptionId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Prescription, prescriptionMedicineDetailed.prescriptionId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Medicine ID" label-align="center" align="center" :span="4" :min-width="334">
          <el-text>{{ prescriptionMedicineDetailed.medicineId }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Name" label-align="center" align="center" :span="4" :min-width="333">
          <el-text>{{ prescriptionMedicineDetailed.medicineName }}</el-text>
        </el-descriptions-item>

        <el-descriptions-item label="Manufacturer" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.medicineManufacturer }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Cost" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.cost }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Quantity" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.quantity }}</el-text>
        </el-descriptions-item>

        <el-descriptions-item label="Course" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.courseOfMedication }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Dosage" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.dosage }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Frequency" label-align="center" align="center" :span="4">
          <el-text>{{ prescriptionMedicineDetailed.frequency }}</el-text>
        </el-descriptions-item>
      </div>
      <div v-else>
        <el-descriptions-item label="Prescription ID" label-align="center" align="center" :span="3" :min-width="250">
          <el-text>
            {{ prescriptionMedicineDetailed.prescriptionId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Prescription, prescriptionMedicineDetailed.prescriptionId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Name" label-align="center" align="center" :span="3" :min-width="250">
          <el-text>{{ prescriptionMedicineDetailed.medicineName }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Manufacturer" label-align="center" align="center" :span="3" :min-width="250">
          <el-text>{{ prescriptionMedicineDetailed.medicineManufacturer }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Cost" label-align="center" align="center" :span="3" :min-width="250">
          <el-text>{{ prescriptionMedicineDetailed.cost }}</el-text>
        </el-descriptions-item>

        <el-descriptions-item label="Quantity" label-align="center" align="center" :span="3">
          <el-text>{{ prescriptionMedicineDetailed.quantity }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Course" label-align="center" align="center" :span="3">
          <el-text>{{ prescriptionMedicineDetailed.courseOfMedication }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Dosage" label-align="center" align="center" :span="3">
          <el-text>{{ prescriptionMedicineDetailed.dosage }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Frequency" label-align="center" align="center" :span="3">
          <el-text>{{ prescriptionMedicineDetailed.frequency }}</el-text>
        </el-descriptions-item>
      </div>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>
</style>