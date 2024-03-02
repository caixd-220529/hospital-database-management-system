<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import {sortConsultationId, sortRehabilitationId, sortName, sortTime} from "../../utils/sort.ts"

interface RehabilitationTableData {
  rehabilitationId: string
  rehabilitationName: string
  beginTime: string
  endTime: string
  consultationId: string
}

interface RehabilitationFilterForm {
  rehabilitationId: string
  rehabilitationName: string
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
const rehabilitationTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: RehabilitationTableData[] = []
const orderedTableData = ref<RehabilitationTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelRehabilitationDialogVisible = ref(false)
const rehabilitationIdToCancel = ref('')
const cancelRehabilitationDialogButtonDisabled = ref(false)
const rehabilitationIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Rehabilitation Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const rehabilitationFilterFormRef = ref<FormInstance>()
const rehabilitationFilterForm = ref<RehabilitationFilterForm>({
  rehabilitationId: '',
  rehabilitationName: '',
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

  const submitValue = { ...rehabilitationFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-rehabilitation', { params: submitValue })
      .then((response) => {
        originalTableData = response.data.results.slice()
        orderedTableData.value = response.data.results
        totalDataNumber.value = response.data.results.length
        currentTablePage.value = 1
        rehabilitationTableRef.value?.clearSort()
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
    case 'rehabilitationId':
      orderedTableData.value.sort((a, b)=>sortRehabilitationId(a.rehabilitationId, b.rehabilitationId, order))
      break
    case 'rehabilitationName':
      orderedTableData.value.sort((a, b)=>sortName(a.rehabilitationName, b.rehabilitationName, order))
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
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableCancelButton = (row: RehabilitationTableData)=>{
  cancelRehabilitationDialogButtonDisabled.value = false
  rehabilitationIdToCancel.value = row.rehabilitationId
  cancelRehabilitationDialogVisible.value = true
}

const handleConfirmCancelRehabilitationButton = () => {
  cancelRehabilitationDialogButtonDisabled.value = true
  cancelRehabilitationDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-rehabilitation', {rehabilitationId: rehabilitationIdToCancel.value})
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.rehabilitationId !== rehabilitationIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.rehabilitationId !== rehabilitationIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel rehabilitation successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: RehabilitationTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  rehabilitationIdToShowDetail.value = row.rehabilitationId
  handleChangeDetailDialogTitle('Rehabilitation Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetRehabilitationFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetRehabilitationFilterForm(rehabilitationFilterFormRef.value)
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
        :item-type="DescribableItem.Rehabilitation"
        :item-id="rehabilitationIdToShowDetail"
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
      v-model="cancelRehabilitationDialogVisible"
      title="Cancel Rehabilitation"
  >
    <span>Are you sure to cancel rehabilitation with ID <el-text tag="b">{{ rehabilitationIdToCancel }}</el-text> ?</span>

    <template #footer>
      <el-button
          @click="cancelRehabilitationDialogVisible = false"
          :disabled="cancelRehabilitationDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelRehabilitationButton"
        :disabled="cancelRehabilitationDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="rehabilitationFilterFormRef"
          :model="rehabilitationFilterForm"
          label-position="top"
        >
          <el-form-item label="Rehabilitation ID" prop="rehabilitationId">
            <el-input v-model="rehabilitationFilterForm.rehabilitationId" placeholder="Enter the rehabilitation ID"></el-input>
          </el-form-item>

          <el-form-item label="Rehabilitation Name" prop="rehabilitationName">
            <el-input v-model="rehabilitationFilterForm.rehabilitationName" placeholder="Enter rehabilitation name"></el-input>
          </el-form-item>

          <el-form-item label="Rehabilitation Begin Time">
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="rehabilitationFilterForm.beginTime1"
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
                  v-model="rehabilitationFilterForm.endTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Rehabilitation End Time" v-if="isHistory">
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="rehabilitationFilterForm.beginTime2"
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
                  v-model="rehabilitationFilterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId">
            <el-input v-model="rehabilitationFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>
        </el-form>

        <el-form-item>
          <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
          <el-button :disabled="formButtonDisabled" @click="resetRehabilitationFilterForm(rehabilitationFilterFormRef)">Reset</el-button>
        </el-form-item>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <el-table
        class="table-container"
        :data="displayedTableData"
        v-loading="!tableDataReady"
        @sort-change="handleTableSortChange"
        ref="rehabilitationTableRef"
      >
        <el-table-column label="Rehabilitation ID" prop="rehabilitationId" sortable="custom"/>
        <el-table-column label="Rehabilitation Name" prop="rehabilitationName" sortable="custom"/>
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