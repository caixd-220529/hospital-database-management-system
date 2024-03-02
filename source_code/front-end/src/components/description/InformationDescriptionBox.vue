<script setup lang="ts">
import PatientPersonalInfoDescription from './user/PatientPersonalInfoDescription.vue'
import DoctorPersonalInfoDescription from "./user/DoctorPersonalInfoDescription.vue"
import ConsultationDescription from './other/ConsultationDescription.vue'
import RehabilitationDescription from './other/RehabilitationDescription.vue'
import ExaminationDescription from './other/ExaminationDescription.vue'
import PrescriptionDescription from './other/PrescriptionDescription.vue'
import SurgeryDescription from './other/SurgeryDescription.vue'
import PrescriptionMedicineDescription from './other/PrescriptionMedicineDescription.vue'
import SurgeryRecordDescription from './other/SurgeryRecordDescription.vue'
import ChargeDescription from './other/ChargeDescription.vue'
import HospitalizationDescription from './other/HospitalizationDescription.vue'
import RoomDescription from './other/RoomDescription.vue'
import NursePersonalInfoDescription from "./user/NursePersonalInfoDescription.vue";
import HelpingStaffPersonalInfoDescription from "./user/HelpingStaffPersonalInfoDescription.vue";
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import { DescribableItem } from '../../types/other'
import { ref } from 'vue'

const props = defineProps(
  {
    itemId: {
      type: String,
      required: true
    },

    itemType: {
      type: String,
      required: true
    }, 

    showEmployeeId: {
      type: Boolean,
      required: true,
    },

    showMedicineId: {
      type: Boolean,
      required: true,
    },

    showRoomDetail: {
      type: Boolean,
      required: false,
      default: false,
    },
  }
)
const itemId = ref<string>(props.itemId)
const currentItemType = ref<string>(props.itemType)

const emit = defineEmits<{
  changeTitle: [title: string]
}>()
const changeOuterDialogDialogTitle = (item: DescribableItem|string)=>{
  switch (item) {
    case DescribableItem.Charge:
      emit('changeTitle', 'Payment Detail')
      break
    case DescribableItem.Consultation:
      emit('changeTitle', 'Consultation Detail')
      break
    case DescribableItem.Examination:
      emit('changeTitle', 'Examination Detail')
      break
    case DescribableItem.Hospitalization:
      emit('changeTitle', 'Hospitalization Detail')
      break
    case DescribableItem.Prescription:
      emit('changeTitle', 'Prescription Detail')
      break
    case DescribableItem.Rehabilitation:
      emit('changeTitle', 'Rehabilitation Detail')
      break
    case DescribableItem.Surgery:
      emit('changeTitle', 'Surgery Detail')
      break
    case DescribableItem.Patient:
      emit('changeTitle', 'Patient Detail')
      break
    case DescribableItem.HelpingStaff:
      emit('changeTitle', 'Helping Staff Detail')
      break
    case DescribableItem.Doctor:
      emit('changeTitle', 'Doctor Detail')
      break
    case DescribableItem.PrescriptionMedicine:
      emit('changeTitle', 'Medicine Detail')
      break
    case DescribableItem.Nurse:
      emit('changeTitle', 'Nurse Detail')
      break
    case DescribableItem.SurgeryRecord:
      emit('changeTitle', 'Surgery Record Detail')
      break
    case DescribableItem.Room:
      emit('changeTitle', 'Room Detail')
      break
    default:
      console.error('Unknown item type')
  }
}
const changeContentHandler = (item: DescribableItem, id: string) => {
  console.log('InformationBox', item, id)
  historyDescriptionItemArr.push({ 'itemType': item, 'itemId': id })
  historyDescriptionItemArrStore.increaseIndexAndLengthByOne()
  // change the content of the outer box
  changeOuterDialogDialogTitle(item)
  itemId.value = id
  currentItemType.value = item
}

const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
historyDescriptionItemArrStore.increaseLengthByOne() // already have one item in the array
const historyDescriptionItemArr = [{
  'itemType': props.itemType,
  'itemId': props.itemId
}]
let lastHistoryDescriptionItemArrLength = 1
let lastHistoryDescriptionItemArrIndex = 0
let jump_subscribe = false
historyDescriptionItemArrStore.$subscribe((mutation, state) => {
  if (jump_subscribe) {
    jump_subscribe = false
    return
  }
  console.assert(mutation.type === 'direct')
  // user click the button in the description box
  if (lastHistoryDescriptionItemArrLength + 1 === state.descriptionBoxHistoryArrLength &&
      lastHistoryDescriptionItemArrIndex + 1 === state.descriptionBoxHistoryArrIndex) {
    // console.log('in description box', state.descriptionBoxHistoryArrIndex, state.descriptionBoxHistoryArrLength)
    if (lastHistoryDescriptionItemArrLength === lastHistoryDescriptionItemArrIndex + 1) {
      console.log('in description box, normal push')
      return
    } else {
      jump_subscribe = true
      console.log('in description box, maintain the arr')
      // refresh the history arr
      historyDescriptionItemArrStore.descriptionBoxHistoryArrLength = historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex + 1
      const lastArrItemId = historyDescriptionItemArr[historyDescriptionItemArr.length - 1].itemId
      const lastArrItemType = historyDescriptionItemArr[historyDescriptionItemArr.length - 1].itemType
      const splice_length = historyDescriptionItemArr.length - historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex
      historyDescriptionItemArr.splice(historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex, splice_length)
      historyDescriptionItemArr.push({ 'itemType': lastArrItemType, 'itemId': lastArrItemId })
      console.assert(historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex + 1 === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength)
    }

  } else {
    console.log('in outer box', state.descriptionBoxHistoryArrIndex, state.descriptionBoxHistoryArrLength)
    // user click the button in the dialog footer
    itemId.value = historyDescriptionItemArr[state.descriptionBoxHistoryArrIndex].itemId
    currentItemType.value = historyDescriptionItemArr[state.descriptionBoxHistoryArrIndex].itemType
    changeOuterDialogDialogTitle(currentItemType.value)
  }
  lastHistoryDescriptionItemArrLength = state.descriptionBoxHistoryArrLength
  lastHistoryDescriptionItemArrIndex = state.descriptionBoxHistoryArrIndex 
})
</script>

<template>
  <!-- <el-scrollbar style="display: flex; justify-content: center; height: 60vh;"> -->
  <div style="display: flex; justify-content: center; height: 60vh;">
    <ConsultationDescription 
      v-if="currentItemType===DescribableItem.Consultation" 
      :consultation-id="itemId" 
      @change-content="changeContentHandler"
      :show-employee-id="props.showEmployeeId"
    />
    <PatientPersonalInfoDescription 
      v-if="currentItemType===DescribableItem.Patient" 
      :patient-id="itemId"
    />
    <RehabilitationDescription 
      v-if="currentItemType===DescribableItem.Rehabilitation" 
      :rehabilitation-id="itemId" 
      @change-content="changeContentHandler"
      :show-employee-id="props.showEmployeeId"
    />
    <ExaminationDescription 
      v-if="currentItemType===DescribableItem.Examination" 
      :examination-id="itemId" 
      @change-content="changeContentHandler"
      :show-employee-id="props.showEmployeeId"
    />
    <PrescriptionDescription 
      v-if="currentItemType===DescribableItem.Prescription" 
      :prescription-id="itemId" 
      @change-content="changeContentHandler"
      :show-employee-id="props.showEmployeeId"
      :show-medicine-id="props.showMedicineId"
    />
    <SurgeryDescription 
      v-if="currentItemType===DescribableItem.Surgery" 
      :surgery-id="itemId" 
      @change-content="changeContentHandler"
      :show-employee-id="props.showMedicineId"
    />
    <PrescriptionMedicineDescription 
      v-if="currentItemType===DescribableItem.PrescriptionMedicine" 
      :prescription-medicine-id="itemId" 
      @change-content="changeContentHandler"
      :show-medicine-id="props.showMedicineId"
    />
    <SurgeryRecordDescription 
      v-if="currentItemType===DescribableItem.SurgeryRecord" 
      :surgery-record-id="itemId" 
      @change-content="changeContentHandler"
    />
    <ChargeDescription 
      v-if="currentItemType===DescribableItem.Charge" 
      :charge-id="itemId" 
      @change-content="changeContentHandler"
    />
    <HospitalizationDescription
      v-if="currentItemType===DescribableItem.Hospitalization"
      :hospitalization-id="itemId"
      @change-content="changeContentHandler"
      :show-employee-id="props.showEmployeeId"
    />
    <DoctorPersonalInfoDescription
      v-if="currentItemType===DescribableItem.Doctor"
      :doctor-id="itemId"
    />
    <RoomDescription
      v-if="currentItemType===DescribableItem.Room"
      :room-id="itemId"
    />
    <NursePersonalInfoDescription
      v-if="currentItemType===DescribableItem.Nurse"
      :nurse-id="itemId"
      :show-room-detail="props.showRoomDetail"
    />
    <HelpingStaffPersonalInfoDescription
      v-if="currentItemType===DescribableItem.HelpingStaff"
      :helping-staff-id="itemId"
    />

  </div>
  <!-- </el-scrollbar> -->
</template>

<style scoped>

</style>