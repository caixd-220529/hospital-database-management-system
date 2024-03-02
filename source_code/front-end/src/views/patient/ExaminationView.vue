<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import {sortConsultationId, sortExaminationId, sortName, sortTime} from "../../utils/sort.ts"

interface ExaminationTableData {
  examinationId: string
  examinationName: string
  examinationTime: string
  consultationId: string
  resultTime: string
}
interface ExaminationFilterForm {
  examinationId: string
  examinationName: string
  beginExaminationTime: string
  endExaminationTime: string
  consultationId: string
  beginResultTime: string
  endResultTime: string
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
const examinationTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: ExaminationTableData[] = []
const orderedTableData = ref<ExaminationTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelExaminationDialogVisible = ref(false)
const examinationIdToCancel = ref('')
const cancelExaminationDialogButtonDisabled = ref(false)
const examinationIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Examination Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const examinationFilterFormRef = ref<FormInstance>()
const examinationFilterForm = ref<ExaminationFilterForm>({
  examinationId: '',
  examinationName: '',
  beginExaminationTime: '',
  endExaminationTime: '',
  consultationId: '',
  beginResultTime: '',
  endResultTime: '',
})
const formButtonDisabled = ref(false)

const getTableData = ()=>{
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...examinationFilterForm.value}
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-examination', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      examinationTableRef.value?.clearSort()
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    formButtonDisabled.value = false
    tableDataReady.value = true
  })
}

const handleTableSortChange = (param: any)=>{
  const { prop, order } = param
  if (!order){
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch(prop){
    case 'examinationId':
      orderedTableData.value.sort((a, b) => sortExaminationId(a.examinationId, b.examinationId, order))
      break
    case 'examinationName':
      orderedTableData.value.sort((a, b) => sortName(a.examinationName, b.examinationName, order))
      break
    case 'examinationTime':
      orderedTableData.value.sort((a, b) => sortTime(a.examinationTime, b.examinationTime, order))
      break
    case 'consultationId':
      orderedTableData.value.sort((a, b) => sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'resultTime':
      orderedTableData.value.sort((a, b) => sortTime(a.resultTime, b.resultTime, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableCancelButton = (row: ExaminationTableData)=>{
  cancelExaminationDialogButtonDisabled.value = false
  examinationIdToCancel.value = row.examinationId
  cancelExaminationDialogVisible.value = true
}

const handleConfirmCancelExaminationButton = () => {
  cancelExaminationDialogButtonDisabled.value = true
  cancelExaminationDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-examination', {examinationId: examinationIdToCancel.value})
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.examinationId !== examinationIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.examinationId !== examinationIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel examination successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: ExaminationTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  examinationIdToShowDetail.value = row.examinationId
  handleChangeDetailDialogTitle('Examination Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetExaminationFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetExaminationFilterForm(examinationFilterFormRef.value)
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
      :item-type="DescribableItem.Examination"
      :item-id="examinationIdToShowDetail"
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
    v-model="cancelExaminationDialogVisible"
    title="Cancel Examination"
  >
    <span>Are you sure to cancel examination with ID <el-text tag="b">{{ examinationIdToCancel }}</el-text> ?</span>

    <template #footer>
      <el-button
        @click="cancelExaminationDialogVisible = false"
        :disabled="cancelExaminationDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelExaminationButton"
        :disabled="cancelExaminationDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="examinationFilterFormRef"
          :model="examinationFilterForm"
          label-position="top"
        >
          <el-form-item label="Examination ID" prop="examinationId">
            <el-input v-model="examinationFilterForm.examinationId" placeholder="Enter the examination ID"></el-input>
          </el-form-item>

          <el-form-item label="Examination Name" prop="examinationName">
            <el-input v-model="examinationFilterForm.examinationName" placeholder="Enter the examination name"></el-input>
          </el-form-item>

          <el-form-item label="Examination Time">
            <el-col :span="11">
              <el-form-item prop="beginExaminationTime">
                <el-date-picker
                  v-model="examinationFilterForm.beginExaminationTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endExaminationTime">
                <el-date-picker
                  v-model="examinationFilterForm.endExaminationTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Result Time" v-if="isHistory">
            <el-col :span="11">
              <el-form-item prop="beginResultTime">
                <el-date-picker
                  v-model="examinationFilterForm.beginResultTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endResultTime">
                <el-date-picker
                  v-model="examinationFilterForm.endResultTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId">
            <el-input v-model="examinationFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
            <el-button :disabled="formButtonDisabled" @click="resetExaminationFilterForm(examinationFilterFormRef)">Reset</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <el-table
        class="table-container"
        :data="displayedTableData"
        v-loading="!tableDataReady"
        @sort-change="handleTableSortChange"
        ref="examinationTableRef"
      >
        <el-table-column label="Examination ID" prop="examinationId" sortable="custom"/>
        <el-table-column label="Examination Name" prop="examinationName" sortable="custom"/>
        <el-table-column label="Examination Time" prop="examinationTime" sortable="custom"/>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable="custom"/>
        <el-table-column v-if="isHistory" label="Result Time" prop="resultTime" sortable="custom"/>
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