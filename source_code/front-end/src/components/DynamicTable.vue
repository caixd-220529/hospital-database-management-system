<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue"
import {type TableInstance} from "element-plus"
import axios from "axios"
import {
  sortChargeId,
  sortConsultationId,
  sortCost,
  sortDepartment,
  sortDescribableItemId,
  sortDoctorId,
  sortExaminationId,
  sortHelpingStaffId,
  sortHospitalizationId,
  sortName,
  sortNurseId,
  sortPatientId,
  sortPharmacyPickWindow,
  sortPharmacyWindow,
  sortPosition,
  sortPrescriptionId,
  sortRehabilitationId,
  sortRoomId,
  sortSurgeryId,
  sortSurgerySite,
  sortTime,
} from "../utils/sort.ts"
import {useConfigStore} from "../stores/config.ts";
import {DescribableItem} from "../types/other.ts";

const props = defineProps({
  itemName: {
    type: String,
    required: true
  },
  tableData: {
    type: Array,
    required: true
  },
  tableDataReady: {
    type: Boolean,
    require: true,
  },
  restTableData: {
    type: String,
    required: true,
  }
})
const emit = defineEmits<{
  showDetailDialog: [itemType: DescribableItem, itemId: any]
  showEditDialog: [keyName: any, itemId: any]
  showDeleteDialog: [keyName: any, itemId: any]
}>()

interface ColumnItem {
  prop: string // must be unique
  label: string // the label of the item
  show: string // can only be 'true' or 'false', if it is 'false', then the column will not be shown

  // one of the attribute below must be true, if it needs to be shown
  sortConsultationId: string // can only be 'true' or 'false'
  sortDepartment: string // can only be 'true' or 'false'
  sortName: string // can only be 'true' or 'false'
  sortPrescriptionId: string // can only be 'true' or 'false'
  sortPharmacyWindow: string // can only be 'true' or 'false'
  sortExaminationId: string // can only be 'true' or 'false'
  sortRehabilitationId: string // can only be 'true' or 'false'
  sortSurgeryId: string // can only be 'true' or 'false'
  sortHospitalizationId: string // can only be 'true' or 'false'
  sortChargeId: string // can only be 'true' or 'false'
  sortDescribableItemId: string // can only be 'true' or 'false'
  sortCost: string // can only be 'true' or 'false'
  sortPosition: string // can only be 'true' or 'false'
  sortPatientId: string // can only be 'true' or 'false'
  sortDoctorId: string // can only be 'true' or 'false'
  sortNurseId: string // can only be 'true' or 'false'
  sortHelpingStaffId: string // can only be 'true' or 'false'
  sortPharmacyPickWindow: string // can only be 'true' or 'false'
  sortSurgerySite: string // can only be 'true' or 'false'
  sortTime: string // can only be 'true' or 'false'
  sortRoomId: string // can only be 'true' or 'false'
}
interface DetailInfo {
  canDelete: string // can only be 'true' or 'false'
  canEdit: string // can only be 'true' or 'false'

  canShowDetail: string // can only be 'true' or 'false', if it is 'true', then the detail button will be shown

  // is canShowDetail is True, one of the 'is...' attribute must be true
  isConsultation: string // can only be 'true' or 'false'
  propNameOfConsultationId: string // the prop name of consultationId

  isPrescription: string // can only be 'true' or 'false'
  propNameOfPrescriptionId: string // the prop name of prescriptionId

  isExamination: string // can only be 'true' or 'false'
  propNameOfExaminationId: string // the prop name of examinationId

  isRehabilitation: string // can only be 'true' or 'false'
  propNameOfRehabilitationId: string // the prop name of rehabilitationId

  isSurgery: string // can only be 'true' or 'false'
  propNameOfSurgeryId: string // the prop name of surgeryId

  isHospitalization: string // can only be 'true' or 'false'
  propNameOfHospitalizationId: string // the prop name of hospitalizationId

  isCharge: string // can only be 'true' or 'false'
  propNameOfChargeId: string // the prop name of chargeId

  isPatient: string // can only be 'true' or 'false'
  propNameOfPatientId: string // the prop name of patientId

  isDoctor: string // can only be 'true' or 'false'
  propNameOfDoctorId: string // the prop name of doctorId

  isNurse: string // can only be 'true' or 'false'
  propNameOfNurseId: string // the prop name of nurseId

  isHelpingStaff: string // can only be 'true' or 'false'
  propNameOfHelpingStaffId: string // the prop name of helpingStaffId

  isRoom: string // can only be 'true' or 'false'
  propNameOfRoomId: string // the prop name of roomId

  isPrescriptionMedicine: string // can only be 'true' or 'false'
  propOfPrescriptionMedicineId: string // the prop name of medicineId. format of the data: prescriptionId#medicineId

  isSurgeryRecord: string // can only be 'true' or 'false'
  propOfSurgeryRecordId: string // the prop name of surgeryRecordId. format of the data: surgeryId#recordId
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const tableRef = ref<TableInstance>()
const tableColumns = ref<ColumnItem[]>([])
const tableColumnReady = ref(false)
const tableSortReady = ref(false)
const tableDetailInfo = ref<DetailInfo>({
  canDelete: 'false',
  canEdit: 'false',
  canShowDetail: 'false',
  isConsultation: 'false',
  propNameOfConsultationId: '',
  isPrescription: 'false',
  propNameOfPrescriptionId: '',
  isExamination: 'false',
  propNameOfExaminationId: '',
  isRehabilitation: 'false',
  propNameOfRehabilitationId: '',
  isSurgery: 'false',
  propNameOfSurgeryId: '',
  isHospitalization: 'false',
  propNameOfHospitalizationId: '',
  isCharge: 'false',
  propNameOfChargeId: '',
  isPatient: 'false',
  propNameOfPatientId: '',
  isDoctor: 'false',
  propNameOfDoctorId: '',
  isNurse: 'false',
  propNameOfNurseId: '',
  isHelpingStaff: 'false',
  propNameOfHelpingStaffId: '',
  isRoom: 'false',
  propNameOfRoomId: '',
  isPrescriptionMedicine: 'false',
  propOfPrescriptionMedicineId: '',
  isSurgeryRecord: 'false',
  propOfSurgeryRecordId: '',
})
const tableKeyColumnPropName = ref('')

const orderedTableData = ref<any[]>(props.tableData)
let originalTableData: any[] = []
const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const isTrue = (str: string) => str === 'true'
const resetTableData = () => {
  tableSortReady.value = false
  orderedTableData.value = props.tableData.slice()
  originalTableData = props.tableData.slice()
  totalDataNumber.value = originalTableData.length
  currentTablePage.value = 1
  tableRef.value?.clearSort()
  tableSortReady.value = true
}
const getTableColumn = () => {
  tableColumnReady.value = false
  axios.get(rootOfPath + '/admin/get-table-column', {params: {itemName: props.itemName}})
    .then((res)=>{
      tableColumns.value = res.data.results.columns
      tableDetailInfo.value = res.data.results.detailInfo
      tableKeyColumnPropName.value = res.data.results.keyColumnPropName
      tableColumnReady.value = true
    })
    .catch((err)=>{
      console.log(err)
    })
}

const handleTableSortChange = (param: any) => {
  const {prop, order} = param
  const index = tableColumns.value.findIndex((item) => item.prop === prop)
  if (index === -1) {
    console.log('error: can not find the prop in tableColumns')
    return
  }
  if (!order) {
    orderedTableData.value = originalTableData.slice()
    return
  }
  if (isTrue(tableColumns.value[index]['sortConsultationId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortConsultationId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortDepartment'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortDepartment(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortName'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortName(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortPrescriptionId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortPrescriptionId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortPharmacyWindow'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortPharmacyWindow(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortExaminationId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortExaminationId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortRehabilitationId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortRehabilitationId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortSurgeryId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortSurgeryId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortHospitalizationId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortHospitalizationId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortChargeId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortChargeId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortDescribableItemId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortDescribableItemId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortCost'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortCost(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortPosition'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortPosition(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortPatientId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortPatientId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortDoctorId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortDoctorId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortNurseId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortNurseId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortHelpingStaffId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortHelpingStaffId(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortPharmacyPickWindow'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortPharmacyPickWindow(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortSurgerySite'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortSurgerySite(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortTime'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortTime(a[prop], b[prop], order))
  } else if (isTrue(tableColumns.value[index]['sortRoomId'])) {
    orderedTableData.value = orderedTableData.value.sort((a, b) => sortRoomId(a[prop], b[prop], order))
  } else {
    console.log('error: can not find the sort function')
  }
}
const handleShowDetailButton = (row: any) => {
  if (isTrue(tableDetailInfo.value.isConsultation)) {
    emit('showDetailDialog', DescribableItem.Consultation, row[tableDetailInfo.value.propNameOfConsultationId])
  } else if(isTrue(tableDetailInfo.value.isPrescription)) {
    emit('showDetailDialog', DescribableItem.Prescription, row[tableDetailInfo.value.propNameOfPrescriptionId])
  } else if(isTrue(tableDetailInfo.value.isExamination)) {
    emit('showDetailDialog', DescribableItem.Examination, row[tableDetailInfo.value.propNameOfExaminationId])
  } else if(isTrue(tableDetailInfo.value.isRehabilitation)) {
    emit('showDetailDialog', DescribableItem.Rehabilitation, row[tableDetailInfo.value.propNameOfRehabilitationId])
  } else if(isTrue(tableDetailInfo.value.isSurgery)) {
    emit('showDetailDialog', DescribableItem.Surgery, row[tableDetailInfo.value.propNameOfSurgeryId])
  } else if(isTrue(tableDetailInfo.value.isHospitalization)) {
    emit('showDetailDialog', DescribableItem.Hospitalization, row[tableDetailInfo.value.propNameOfHospitalizationId])
  } else if(isTrue(tableDetailInfo.value.isCharge)) {
    emit('showDetailDialog', DescribableItem.Charge, row[tableDetailInfo.value.propNameOfChargeId])
  } else if(isTrue(tableDetailInfo.value.isPatient)) {
    emit('showDetailDialog', DescribableItem.Patient, row[tableDetailInfo.value.propNameOfPatientId])
  } else if(isTrue(tableDetailInfo.value.isDoctor)) {
    emit('showDetailDialog', DescribableItem.Doctor, row[tableDetailInfo.value.propNameOfDoctorId])
  } else if(isTrue(tableDetailInfo.value.isNurse)) {
    emit('showDetailDialog', DescribableItem.Nurse, row[tableDetailInfo.value.propNameOfNurseId])
  } else if(isTrue(tableDetailInfo.value.isHelpingStaff)) {
    emit('showDetailDialog', DescribableItem.HelpingStaff, row[tableDetailInfo.value.propNameOfHelpingStaffId])
  } else if(isTrue(tableDetailInfo.value.isRoom)) {
    emit('showDetailDialog', DescribableItem.Room, row[tableDetailInfo.value.propNameOfRoomId])
  } else if(isTrue(tableDetailInfo.value.isPrescriptionMedicine)) {
    emit('showDetailDialog', DescribableItem.PrescriptionMedicine, row[tableDetailInfo.value.propOfPrescriptionMedicineId])
  } else if(isTrue(tableDetailInfo.value.isSurgeryRecord)) {
    emit('showDetailDialog', DescribableItem.SurgeryRecord, row[tableDetailInfo.value.propOfSurgeryRecordId])
  } else {
    console.log('error: can not find the detail function')
  }
}
const handleDeleteButton = (row: any) => {
  emit('showDeleteDialog', tableKeyColumnPropName.value, row[tableKeyColumnPropName.value])
}
const handleEditButton = (row: any) => {
  emit('showEditDialog', tableKeyColumnPropName.value, row[tableKeyColumnPropName.value])
}

onMounted(()=>{
  getTableColumn()
  resetTableData()
})
watch(()=>props.restTableData,()=>{
  resetTableData()
})
watch(()=>props.tableData, ()=>{
  // simply add, delete or edit a record in the table
  orderedTableData.value = props.tableData.slice()
  originalTableData = props.tableData.slice()
  totalDataNumber.value = originalTableData.length
})
watch(()=>props.itemName, ()=>{
  getTableColumn()
  resetTableData()
})

</script>

<template>
  <el-table
    :data="displayedTableData"
    v-loading="!(props.tableDataReady&&tableColumnReady&&tableSortReady)"
    @sort-change="handleTableSortChange"
    ref="tableRef"
  >
    <template v-for="column in tableColumns" :key="column.prop">
      <el-table-column :prop="column.prop" :label="column.label" v-if="isTrue(column.show)" sortable/>
    </template>
    <el-table-column label="Action">
      <template #default="scope">
        <el-button
          size="small"
          type="primary"
          v-if="isTrue(tableDetailInfo.canShowDetail)"
          @click="handleShowDetailButton(scope.row)"
        >Show Detail
        </el-button>
        <el-button
          size="small"
          v-if="isTrue(tableDetailInfo.canEdit)"
          @click="handleEditButton(scope.row)"
        >Edit
        </el-button>
        <el-button
          size="small"
          type="danger"
          v-if="isTrue(tableDetailInfo.canDelete)"
          @click="handleDeleteButton(scope.row)"
        >Delete
        </el-button>
      </template>
    </el-table-column>
  </el-table>
  <el-pagination
    v-model:current-page="currentTablePage"
    v-model:page-size="tablePageSize"
    :page-sizes="config.tablePageSizeArr"
    layout="total, sizes, prev, pager, next, jumper"
    :total="totalDataNumber"
    class="pagination-container"
  />
</template>

<style scoped>

</style>