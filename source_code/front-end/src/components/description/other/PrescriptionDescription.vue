<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { PrescriptionDetailed, PrescriptionDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const prescriptionDetailed: PrescriptionDetailed = {
  prescriptionId: '',
  consultationRough: { 'consultationId': '', 'doctorName': '' },
  patientRough: { 'patientId': '', 'patientName': '' },
  doctorRough: { 'doctorId': '', 'doctorName': '' },
  pharmacyWindow: '',
  pharmacyPickupTime: '',
  prescriptionMedicineRoughArr: [],
  chargeId: '',
}
const props = defineProps(
  {
    prescriptionId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
    showEmployeeId: {
      type: Boolean,
      required: true,
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
const getPrescription = () => {
  if (props.prescriptionId === '') {
    console.log('prescriptionId is empty')
  } else {
    console.log('prescriptionId:', props.prescriptionId)
  }
  getData.value = false
  axios.get(rootOfPath + `/get-prescription-detailed?prescriptionId=${props.prescriptionId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in prescriptionDetailed) {
      if (key in response.data.results){
        prescriptionDetailed[key as PrescriptionDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    getData.value = true
  })
}
onMounted(() => {
  getPrescription()
})
watch(() => props.prescriptionId, () => {
  getPrescription()
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
      <el-descriptions-item label="Prescription ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{prescriptionDetailed.prescriptionId}}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ prescriptionDetailed.patientRough.patientId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, prescriptionDetailed.patientRough.patientId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ prescriptionDetailed.patientRough.patientName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Charge ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text></el-text>{{ prescriptionDetailed.chargeId }}
        <ShowDetailButton @click="handleShowDetail(DescribableItem.Charge, prescriptionDetailed.chargeId)"/>
      </el-descriptions-item>

      <el-descriptions-item label="Pharmacy Window" label-align="center" align="center" :span="6">
        <el-text>{{ prescriptionDetailed.pharmacyWindow }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Pharmacy Pickup Time" label-align="center" align="center" :span="6">
        <el-text>{{ prescriptionDetailed.pharmacyPickupTime }}</el-text>
      </el-descriptions-item>


      <el-descriptions-item label="Consultation ID" label-align="center" align="center" :span="props.showEmployeeId?3:4">
        <el-text>
          {{ prescriptionDetailed.consultationRough.consultationId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Consultation, prescriptionDetailed.consultationRough.consultationId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Consultation Doctor Name" label-align="center" align="center" :span="props.showEmployeeId?3:4">
        <el-text>{{ prescriptionDetailed.consultationRough.doctorName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Pharmaceutical Doctor Name" label-align="center" align="center" :span="props.showEmployeeId?3:4">
        <el-text>{{ prescriptionDetailed.doctorRough.doctorName }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item v-if="showEmployeeId" label="Pharmaceutical Doctor ID" label-align="center" align="center" :span="3">
        <el-text>
          {{ prescriptionDetailed.doctorRough.doctorId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Doctor, prescriptionDetailed.doctorRough.doctorId)"/>
        </el-text>
      </el-descriptions-item>


      <el-descriptions-item label="Medicine Information" label-align="center" align="center" :span="12">
        <el-table :data="prescriptionDetailed.prescriptionMedicineRoughArr" style="width: 100%">
          <el-table-column v-if="props.showMedicineId" prop="medicineId" label="Medicine ID" align="center"/>
          <el-table-column prop="medicineName" label="Medicine Name" align="center"/>
          <el-table-column prop="quantity" label="Quantity" align="center"/>
          <el-table-column label="Operation" align="center">
            <template #default="{row}">
              <ShowDetailButton @click="handleShowDetail(DescribableItem.PrescriptionMedicine, props.prescriptionId+'#'+row.medicineId)" />
            </template>
          </el-table-column>
        </el-table>
      </el-descriptions-item>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>

</style>