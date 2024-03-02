<script setup lang="ts">
import axios, { AxiosResponse } from 'axios'
import { useConfigStore } from '../../../stores/config.ts'
import { ChargeDetailed, ChargeDetailedKey } from '../../../types/other.ts'
import { ref, onMounted, watch, computed } from 'vue'
import { DescribableItem } from '../../../types/other.ts'
import ShowDetailButton from '../ShowDetailButton.vue'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const chargeDetailed: ChargeDetailed = {
  chargeId: '',
  patientRough: { patientId: '', patientName: '' },
  cost: '',
  isCompleted: '',
  chargeTime: '',
  paymentMethod: '',
  prescriptionRough: { prescriptionId: '', },
  examinationRough: { examinationId: '', examinationName: '' },
  surgeryRough: { surgeryId: '', surgeryName: '' },
  rehabilitationRough: { rehabilitationId: '', rehabilitationName: '' },
  consultationRough: { consultationId: '', doctorName: '' },
  hospitalizationRough: { hospitalizationId:'', doctorName: ''},
}
const props = defineProps(
  {
    chargeId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: false
    },
  }
)
const emit = defineEmits<{
  changeContent: [item: DescribableItem, id: string]
}>()
const getData = ref(false)
const chargedItemType = ref<DescribableItem>()
const isPrescription = computed(() => {
  return chargedItemType.value === DescribableItem.Prescription
})
const getCharge = () => {
  if (props.chargeId === '') {
    console.log('chargeId is empty')
  } else {
    console.log('chargeId:', props.chargeId)
  }
  getData.value = false
  axios.get(rootOfPath + `/get-charge-detailed?chargeId=${props.chargeId}`).then((response: AxiosResponse) => {
    console.log(response.data.results)
    for (const key in chargeDetailed) {
      if (key in response.data.results){
        chargeDetailed[key as ChargeDetailedKey] = response.data.results[key]
      } else {
        console.error(`Key ${key} does not exist in response`)
      }
    }
    let counter = 0
    if (chargeDetailed.consultationRough.consultationId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Consultation
    }
    if (chargeDetailed.examinationRough.examinationId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Examination
    }
    if (chargeDetailed.hospitalizationRough.hospitalizationId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Hospitalization
    }
    if (chargeDetailed.prescriptionRough.prescriptionId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Prescription
    }
    if (chargeDetailed.rehabilitationRough.rehabilitationId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Rehabilitation
    }
    if (chargeDetailed.surgeryRough.surgeryId !== '') {
      counter++
      chargedItemType.value = DescribableItem.Surgery
    }
    if (counter === 0) {
      console.error('No item type')
    }
    if (counter > 1) {
      console.error('More than one item type')
    }
  }).catch((err: any) => {
    console.error(err)
  }).finally(() => {
    getData.value = true
  })
}
onMounted(() => {
  getCharge()
})
watch(() => props.chargeId, () => {
  getCharge()
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
      <el-descriptions-item label="Charge ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ chargeDetailed.chargeId }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Cost" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ chargeDetailed.cost }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient ID" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>
          {{ chargeDetailed.patientRough.patientId }}
          <ShowDetailButton @click="handleShowDetail(DescribableItem.Patient, chargeDetailed.patientRough.patientId)"/>
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="Patient Name" label-align="center" align="center" :span="3" :min-width="250">
        <el-text>{{ chargeDetailed.patientRough.patientName }}</el-text>
      </el-descriptions-item>

      <div v-if="chargeDetailed.isCompleted==='true'">
        <el-descriptions-item label="Charge Time" label-align="center" align="center" :span="isPrescription?4:3">
          <el-text>{{ chargeDetailed.chargeTime }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Payment Method" label-align="center" align="center" :span="isPrescription?4:3">
          <el-text>{{ chargeDetailed.paymentMethod }}</el-text>
        </el-descriptions-item>
      </div>
      <div v-else>
        <el-descriptions-item label="Detailed Information" label-align="center" align="center" :span="isPrescription?6:4">
          <el-text>No payment records found</el-text>
        </el-descriptions-item>
      </div> 

      <div v-if="chargedItemType===DescribableItem.Consultation">
        <el-descriptions-item label="Related Consultation ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>
            {{ chargeDetailed.consultationRough.consultationId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Consultation, chargeDetailed.consultationRough.consultationId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Consultation Doctor Name" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>{{ chargeDetailed.consultationRough.doctorName }}</el-text>
        </el-descriptions-item>
      </div>

      <div v-else-if="chargedItemType === DescribableItem.Examination">
        <el-descriptions-item label="Related Examination ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>
            {{ chargeDetailed.examinationRough.examinationId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Examination, chargeDetailed.examinationRough.examinationId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Examination Name" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>{{ chargeDetailed.examinationRough.examinationName }}</el-text>
        </el-descriptions-item>
      </div>

      <div v-else-if="chargedItemType===DescribableItem.Hospitalization">
        <el-descriptions-item label="Related Hospitalization ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>
            {{ chargeDetailed.hospitalizationRough.hospitalizationId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Hospitalization, chargeDetailed.hospitalizationRough.hospitalizationId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Hospitalization Doctor Name" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>{{ chargeDetailed.hospitalizationRough.doctorName }}</el-text>
        </el-descriptions-item>
      </div>

      <div v-else-if="chargedItemType===DescribableItem.Rehabilitation">
        <el-descriptions-item label="Related Rehabilitation ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>
            {{ chargeDetailed.rehabilitationRough.rehabilitationId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Rehabilitation, chargeDetailed.rehabilitationRough.rehabilitationId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Rehabilitation Name" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>{{ chargeDetailed.rehabilitationRough.rehabilitationName }}</el-text>
        </el-descriptions-item>
      </div>
      
      <div v-else-if="chargedItemType===DescribableItem.Surgery">
        <el-descriptions-item label="Related Surgery ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>
            {{ chargeDetailed.surgeryRough.surgeryId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Surgery, chargeDetailed.surgeryRough.surgeryId)"/>
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="Surgery Name" label-align="center" align="center" :span="chargeDetailed.isCompleted?3:4">
          <el-text>{{ chargeDetailed.surgeryRough.surgeryName }}</el-text>
        </el-descriptions-item>
      </div>

      <div v-else-if="chargedItemType===DescribableItem.Prescription">
        <el-descriptions-item label="Related Prescription ID" label-align="center" align="center" :span="chargeDetailed.isCompleted?4:6">
          <el-text>
            {{ chargeDetailed.prescriptionRough.prescriptionId }}
            <ShowDetailButton @click="handleShowDetail(DescribableItem.Prescription, chargeDetailed.prescriptionRough.prescriptionId)"/>
          </el-text>
        </el-descriptions-item>
      </div>

      <div v-else><el-descriptions-item>SHOULD NOT REACH HERE!</el-descriptions-item></div>
    </el-descriptions>
  </el-scrollbar>
</template>

<style scoped>
</style>