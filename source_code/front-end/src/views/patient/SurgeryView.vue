<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import {sortConsultationId, sortSurgeryId, sortName, sortTime} from "../../utils/sort.ts"

interface SurgeryTableData {
  surgeryId: string
  surgeryName: string
  doctorName: string
  beginTime: string
  endTime: string
  consultationId: string
}

interface SurgeryFilterForm {
  surgeryId: string
  surgeryName: string
  doctorName: string
  beginTime1: string
  endTime1: string
  beginTime2: string
  endTime2: string
  consultationId: string
  isHistory?: boolean
  patientId?: string
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()
const isHistory = computed(() => router.currentRoute.value.path.includes('history'))

const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const surgeryTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: SurgeryTableData[] = []
const orderedTableData = ref<SurgeryTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelSurgeryDialogVisible = ref(false)
const surgeryIdToCancel = ref('')
const cancelSurgeryDialogButtonDisabled = ref(false)
const surgeryIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Surgery Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const surgeryFilterFormRef = ref<FormInstance>()
const surgeryFilterForm = ref<SurgeryFilterForm>({
  surgeryId: '',
  surgeryName: '',
  doctorName: '',
  beginTime1: '',
  endTime1: '',
  beginTime2: '',
  endTime2: '',
  consultationId: '',
})
const formButtonDisabled = ref(false)

const getTableData = () =>{
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = { ...surgeryFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-surgery', { params: submitValue })
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      surgeryTableRef.value?.clearSort()
    })
    .catch((error) => {
      console.log(error)
    }).finally(() => {
    formButtonDisabled.value = false
    tableDataReady.value = true
  })
}

const handleTableSortChange = (param:any)=>{
  const { prop, order } = param
  if (!order){
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch (prop) {
    case 'surgeryId':
      orderedTableData.value.sort((a, b)=>sortSurgeryId(a.surgeryId, b.surgeryId, order))
      break
    case 'surgeryName':
      orderedTableData.value.sort((a, b)=>sortName(a.surgeryName, b.surgeryName, order))
      break
    case 'beginTime':
      orderedTableData.value.sort((a, b)=>sortTime(a.beginTime, b.beginTime, order))
      break
    case 'endTime':
      orderedTableData.value.sort((a, b)=>sortTime(a.endTime, b.endTime, order))
      break
    case 'consultationId':
      orderedTableData.value.sort((a, b)=>sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'doctorName':
      orderedTableData.value.sort((a, b)=>sortName(a.doctorName, b.doctorName, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableCancelButton = (row: SurgeryTableData)=>{
  cancelSurgeryDialogButtonDisabled.value = false
  surgeryIdToCancel.value = row.surgeryId
  cancelSurgeryDialogVisible.value = true
}

const handleConfirmCancelSurgeryButton = () => {
  cancelSurgeryDialogButtonDisabled.value = true
  cancelSurgeryDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-surgery', {surgeryId: surgeryIdToCancel.value})
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.surgeryId !== surgeryIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.surgeryId !== surgeryIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel surgery successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: SurgeryTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  surgeryIdToShowDetail.value = row.surgeryId
  handleChangeDetailDialogTitle('Surgery Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetSurgeryFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetSurgeryFilterForm(surgeryFilterFormRef.value)
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
      :item-type="DescribableItem.Surgery"
      :item-id="surgeryIdToShowDetail"
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

  <el-dialog
    v-model="cancelSurgeryDialogVisible"
    title="Cancel Surgery"
  >
    <span>Are you sure to cancel surgery with ID <el-text tag="b">{{ surgeryIdToCancel }}</el-text> ?</span>

    <template #footer>
      <el-button
        @click="cancelSurgeryDialogVisible = false"
        :disabled="cancelSurgeryDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelSurgeryButton"
        :disabled="cancelSurgeryDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="surgeryFilterFormRef"
          :model="surgeryFilterForm"
          label-position="top"
        >
          <el-form-item label="Surgery ID" prop="surgeryId">
            <el-input v-model="surgeryFilterForm.surgeryId" placeholder="Enter the surgery ID"></el-input>
          </el-form-item>

          <el-form-item label="Surgery Name" prop="surgeryName">
            <el-input v-model="surgeryFilterForm.surgeryName" placeholder="Enter surgery name"></el-input>
          </el-form-item>

          <el-form-item label="Lead Surgeon Name" prop="doctorName">
            <el-input v-model="surgeryFilterForm.doctorName" placeholder="Enter lead surgery name"></el-input>
          </el-form-item>

          <el-form-item label="Surgery Begin Time">
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="surgeryFilterForm.beginTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime1">
                <el-date-picker
                  v-model="surgeryFilterForm.endTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Surgery End Time" v-if="isHistory">
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="surgeryFilterForm.beginTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime2">
                <el-date-picker
                  v-model="surgeryFilterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId">
            <el-input v-model="surgeryFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>
        </el-form>

        <el-form-item>
          <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
          <el-button :disabled="formButtonDisabled" @click="resetSurgeryFilterForm(surgeryFilterFormRef)">Reset</el-button>
        </el-form-item>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <el-table
        class="table-container"
        :data="displayedTableData"
        v-loading="!tableDataReady"
        @sort-change="handleTableSortChange"
        ref="surgeryTableRef"
      >
        <el-table-column label="Surgery ID" prop="surgeryId" sortable="custom"/>
        <el-table-column label="Surgery Name" prop="surgeryName" sortable="custom"/>
        <el-table-column label="Lead Surgeon Name" prop="doctorName" sortable="custom"/>
        <el-table-column label="Begin Time" prop="beginTime" sortable="custom"/>
        <el-table-column v-if="isHistory" label="End Time" prop="endTime" sortable="custom"/>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable="custom"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleTableShowDetailButton(scope.row)">Show Detail</el-button>
            <el-button type="danger" v-if="!isHistory" size="small" @click="handleTableCancelButton(scope.row)">Cancel</el-button>
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