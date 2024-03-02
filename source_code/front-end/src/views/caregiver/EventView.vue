<script setup lang="ts">
import {useRouter} from 'vue-router'
import {computed, onMounted, ref, watch} from 'vue'
import {ElMessage, type FormInstance, type TableInstance} from 'element-plus'
import axios from 'axios';
import {useConfigStore} from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import {useDescriptionBoxHistoryArrStore} from '../../stores/descriptionBoxHistoryArr'
import {
  sortExaminationId,
  sortRehabilitationId,
  sortSurgeryId,
  sortHospitalizationId,
  sortName,
  sortPatientId,
  sortTime,
  sortConsultationId,
  sortNurseId,
  sortHelpingStaffId,
} from "../../utils/sort.ts"
import {
  examinationNameRemoteMethod,
  rehabilitationNameRemoteMethod,
  surgeryNameRemoteMethod,
  patientIdRemoteMethod,
  patientNameRemoteMethod,
} from "../../utils/remote.ts"
import {DescribableItem} from "../../types/other.ts"
import {UserType} from '../../types/user.ts'

interface TableData {
  consultationId: string
  itemId: string
  itemName: string
  time1: string
  time2: string
  patientId: string
  patientName: string
  caregiverId: string
  caregiverName: string
}

interface FilterForm {
  consultationId: string
  itemId: string
  itemName: string
  beginTime1: string
  beginTime2: string
  endTime1: string
  endTime2: string
  patientId: string
  patientName: string
  includeSubordinate: string
  isHistory?: boolean
  itemType?: DescribableItem
  inquirerId?: string
  inquirerType?: UserType
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()
const isHistory = computed(() => router.currentRoute.value.path.includes('history'))
const itemTypeOfPath = computed(() => {
  if (router.currentRoute.value.path.includes('examination')) return DescribableItem.Examination
  if (router.currentRoute.value.path.includes('rehabilitation')) return DescribableItem.Rehabilitation
  if (router.currentRoute.value.path.includes('surgery')) return DescribableItem.Surgery
  return DescribableItem.Hospitalization
})

const itemNameFieldLabel = computed(() => {
  switch (itemTypeOfPath.value) {
    case DescribableItem.Examination:
      return 'Examination Name'
    case DescribableItem.Rehabilitation:
      return 'Rehabilitation Name'
    case DescribableItem.Surgery:
      return 'Surgery Name'
    case DescribableItem.Hospitalization:
      return 'Hospitalization Name'
    default:
      return 'No match item type'
  }
})
const itemIdFieldLabel = computed(()=>{
  switch (itemTypeOfPath.value) {
    case DescribableItem.Examination:
      return 'Examination ID'
    case DescribableItem.Rehabilitation:
      return 'Rehabilitation ID'
    case DescribableItem.Surgery:
      return 'Surgery ID'
    case DescribableItem.Hospitalization:
      return 'Hospitalization ID'
    default:
      return 'No match item type'
  }
})
const caregiverIdFieldLabel = computed(() => {
  switch (config.userType) {
    case UserType.Nurse:
      return 'Nurse ID'
    case UserType.HelpingStaff:
      return 'Helping Staff ID'
    default:
      return 'No match user type'
  }
})
const caregiverNameFieldLabel = computed(() => {
  switch (config.userType) {
    case UserType.Nurse:
      return 'Nurse Name'
    case UserType.HelpingStaff:
      return 'Helping Staff Name'
    default:
      return 'No match user type'
  }
})
const time1FieldLabel = computed(()=>{
  switch (itemTypeOfPath.value) {
    case DescribableItem.Examination:
      return 'Examination Time'
    case DescribableItem.Rehabilitation:
      return 'Rehabilitation Begin Time'
    case DescribableItem.Surgery:
      return 'Surgery Begin Time'
    case DescribableItem.Hospitalization:
      return 'Hospitalization Time'
    default:
      return 'No match item type'
  }
})
const time2FieldLabel = computed(()=>{
  switch (itemTypeOfPath.value) {
    case DescribableItem.Examination:
      return 'Result Time'
    case DescribableItem.Rehabilitation:
      return 'Rehabilitation End Time'
    case DescribableItem.Surgery:
      return 'Surgery End Time'
    case DescribableItem.Hospitalization:
      return 'Hospitalization Time'
    default:
      return 'No match item type'
  }
})

const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const tableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: TableData[] = []
const orderedTableData = ref<TableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))
const showCareGiverInfo = ref(false)


const itemIdToShowDetail = ref('')
const itemTypeToShowDetail = ref<DescribableItem>()
const detailDialogVisible = ref(false)
const detailDialogTitle = ref('No initialization :(')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const filterFormRef = ref<FormInstance>()
const filterForm = ref<FilterForm>({
  consultationId: '',
  itemId: '',
  itemName: '',
  beginTime1: '',
  beginTime2: '',
  endTime1: '',
  endTime2: '',
  patientId: '',
  patientName: '',
  includeSubordinate: 'Show my and subordinate information',  // 'Show my and subordinate information' or 'Only show my information'
})
const formButtonDisabled = ref(false)

const patientIdOptions = ref<string[]>([])
const patientIdLoading = ref(false)
const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const itemNameOptions = ref<string[]>([])
const itemNameLoading = ref(false)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...filterForm.value}
  submitValue.isHistory = isHistory.value
  submitValue.itemType = itemTypeOfPath.value
  submitValue.inquirerId = config.userId
  submitValue.inquirerType = config.userType
  if(filterForm.value.includeSubordinate === 'Show my and subordinate information') {
    submitValue.includeSubordinate = 'true'
    showCareGiverInfo.value = true
  } else {
    submitValue.includeSubordinate = 'false'
    showCareGiverInfo.value = false
  }

  axios.get(rootOfPath + '/caregiver/get-table-data', {params: submitValue})
    .then((response)=>{
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      tableRef.value?.clearSort()
    })
    .catch((error)=>{
      ElMessage.error(error.response.data.message)
    })
    .finally(()=>{
      formButtonDisabled.value = false
      tableDataReady.value = true
    })
}

const handleTableSortChange = (param: any) => {
  const {prop, order} = param
  if (!order) {
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch (prop){
    case 'consultationId':
      orderedTableData.value.sort((a, b) => sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'itemId':
      switch(itemTypeOfPath.value){
        case DescribableItem.Examination:
          orderedTableData.value.sort((a, b) => sortExaminationId(a.itemId, b.itemId, order))
          break
        case DescribableItem.Rehabilitation:
          orderedTableData.value.sort((a, b) => sortRehabilitationId(a.itemId, b.itemId, order))
          break
        case DescribableItem.Surgery:
          orderedTableData.value.sort((a, b) => sortSurgeryId(a.itemId, b.itemId, order))
          break
        case DescribableItem.Hospitalization:
          orderedTableData.value.sort((a, b) => sortHospitalizationId(a.itemId, b.itemId, order))
          break
      }
      break
    case 'itemName':
      orderedTableData.value.sort((a, b) => sortName(a.itemName, b.itemName, order))
      break
    case 'time1':
      orderedTableData.value.sort((a, b) => sortTime(a.time1, b.time1, order))
      break
    case 'time2':
      orderedTableData.value.sort((a, b) => sortTime(a.time2, b.time2, order))
      break
    case 'patientId':
      orderedTableData.value.sort((a, b) => sortPatientId(a.patientId, b.patientId, order))
      break
    case 'patientName':
      orderedTableData.value.sort((a, b) => sortName(a.patientName, b.patientName, order))
      break
    case 'caregiverId':
      switch (config.userType){
        case UserType.Nurse:
          orderedTableData.value.sort((a, b) => sortNurseId(a.caregiverId, b.caregiverId, order))
          break
        case UserType.HelpingStaff:
          orderedTableData.value.sort((a, b) => sortHelpingStaffId(a.caregiverId, b.caregiverId, order))
          break
      }
      break
    case 'caregiverName':
      orderedTableData.value.sort((a, b) => sortName(a.caregiverName, b.caregiverName, order))
      break
  }
}

const resetFilterForm = () =>{
  filterForm.value = {
    consultationId: '',
    itemId: '',
    itemName: '',
    beginTime1: '',
    beginTime2: '',
    endTime1: '',
    endTime2: '',
    patientId: '',
    patientName: '',
    includeSubordinate: 'Show my and subordinate information',
  }
}

const itemNameRemoteMethod = (query: string) => {
  switch (itemTypeOfPath.value) {
    case DescribableItem.Examination:
      examinationNameRemoteMethod(query, itemNameOptions, itemNameLoading)
      break
    case DescribableItem.Rehabilitation:
      rehabilitationNameRemoteMethod(query, itemNameOptions, itemNameLoading)
      break
    case DescribableItem.Surgery:
      surgeryNameRemoteMethod(query, '', itemNameOptions, itemNameLoading)
      break
    case DescribableItem.Hospitalization:
      break
    default:
      console.error('Invalid itemType: ' + itemTypeOfPath.value)
  }

}
const _patientIdRemoteMethod = (query: string) => {
  patientIdRemoteMethod(query, config.userId, config.userType, patientIdOptions, patientIdLoading)
}
const _patientNameRemoteMethod = (query: string) => {
  patientNameRemoteMethod(query, config.userName, config.userType, patientNameOptions, patientNameLoading)
}

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleShowDetailButton = (itemId: string, itemType: DescribableItem) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  itemIdToShowDetail.value = itemId
  itemTypeToShowDetail.value = itemType
  switch (itemType) {
    case DescribableItem.Examination:
      handleChangeDetailDialogTitle('Examination Detail')
      break
    case DescribableItem.Rehabilitation:
      handleChangeDetailDialogTitle('Rehabilitation Detail')
      break
    case DescribableItem.Surgery:
      handleChangeDetailDialogTitle('Surgery Detail')
      break
    case DescribableItem.Hospitalization:
      handleChangeDetailDialogTitle('Hospitalization Detail')
      break
    default:
      console.error('Invalid itemType: ' + itemType)
  }
  detailDialogVisible.value = true
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetFilterForm()
  getTableData()
  tablePageSize.value = config.defaultPageSize
})
</script>

<template>
  <el-dialog
    v-model="detailDialogVisible"
    :title="detailDialogTitle"
    :width="config.showDetailDialogWidth"
    destroy-on-close
  >
    <InformationDescriptionBox
      :item-type="itemTypeOfPath"
      :item-id="itemIdToShowDetail"
      :show-employee-id="false"
      :show-medicine-id="false"
      @change-title="handleChangeDetailDialogTitle"
    />

    <template #footer>
      <el-button
        @click="historyDescriptionItemArrStore.decreaseIndexByOne"
        :disabled="detailedDialogPreviousButtonDisabled"
      >Previous</el-button>
      <el-button
        @click="historyDescriptionItemArrStore.increaseIndexByOne"
        :disabled="detailedDialogNextButtonDisabled"
      >Next</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="filterFormRef"
          :model="filterForm"
          label-position="top"
        >
          <el-form-item label="Mode" prop="includeSubordinate">
            <el-radio-group v-model="filterForm.includeSubordinate">
              <el-radio label="Show my and subordinate information"/>
              <el-radio label="Only show my information"/>
            </el-radio-group>
          </el-form-item>

          <el-form-item :label="itemIdFieldLabel" prop="itemId">
            <el-input
              v-model="filterForm.itemId"
              :placeholder="'Please input ' + itemTypeOfPath.toLowerCase() + ' ID'"
              clearable
            />
          </el-form-item>

          <el-form-item :label="itemNameFieldLabel" prop="itemName">
            <el-select
              v-model="filterForm.itemName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="itemNameRemoteMethod"
              :loading="itemNameLoading"
              :placeholder="'Please input ' + itemTypeOfPath.toLowerCase() + ' name'"
              style="width: 100%"
            >
              <el-option
                v-for="item in itemNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item :label="time1FieldLabel">
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="filterForm.beginTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="filterForm.endTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item :label="time2FieldLabel">
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="filterForm.beginTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="filterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId">
            <el-select
              v-model="filterForm.patientId"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_patientIdRemoteMethod"
              :loading="patientIdLoading"
              placeholder="Enter the patient ID"
              style="width: 100%"
            >
              <el-option
                v-for="item in patientIdOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Patient Name" prop="patientName">
            <el-select
              v-model="filterForm.patientName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_patientNameRemoteMethod"
              :loading="patientNameLoading"
              placeholder="Enter the patient Name"
              style="width: 100%"
            >
              <el-option
                v-for="item in patientNameOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              @click="getTableData"
              :disabled="formButtonDisabled"
            >
              Search
            </el-button>
            <el-button
              @click="resetFilterForm"
              :disabled="formButtonDisabled"
            >Reset
            </el-button>
          </el-form-item>

        </el-form>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <el-table
        class="table-container"
        :data="displayedTableData"
        @sort-change="handleTableSortChange"
        ref="tableRef"
        v-loading="!tableDataReady"
      >
        <el-table-column :label="itemIdFieldLabel" prop="itemId" sortable/>
        <el-table-column :label="itemNameFieldLabel" prop="itemName" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column :label="time1FieldLabel" prop="time1" sortable/>
        <el-table-column v-if="isHistory" :label="time2FieldLabel" prop="time2" sortable/>
        <el-table-column v-if="showCareGiverInfo" :label="caregiverIdFieldLabel" prop="caregiverId" sortable/>
        <el-table-column v-if="showCareGiverInfo" :label="caregiverNameFieldLabel" prop="caregiverName" sortable/>
        <el-table-column v-if="config.userType===UserType.Nurse" label="Action">
          <template #default="{row}">
            <el-button
              type="primary"
              size="small"
              @click="handleShowDetailButton(row.itemId, itemTypeOfPath)"
            >Show Detail</el-button>
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
    </el-scrollbar>
  </div>
</template>

<style scoped>

</style>