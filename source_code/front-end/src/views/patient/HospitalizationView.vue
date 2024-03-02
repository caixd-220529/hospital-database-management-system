<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import {sortConsultationId, sortHospitalizationId, sortName, sortTime} from "../../utils/sort.ts"

interface HospitalizationTableData {
  hospitalizationId: string
  doctorName: string
  beginTime: string
  endTime: string
  consultationId: string
}

interface HospitalizationFilterForm {
  hospitalizationId: string
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
const hospitalizationTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: HospitalizationTableData[] = []
const orderedTableData = ref<HospitalizationTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelHospitalizationDialogVisible = ref(false)
const hospitalizationIdToCancel = ref('')
const cancelHospitalizationDialogButtonDisabled = ref(false)
const hospitalizationIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Hospitalization Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const hospitalizationFilterFormRef = ref<FormInstance>()
const hospitalizationFilterForm = ref<HospitalizationFilterForm>({
  hospitalizationId: '',
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

  const submitValue = { ...hospitalizationFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-hospitalization', { params: submitValue })
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      hospitalizationTableRef.value?.clearSort()
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
    case 'hospitalizationId':
      orderedTableData.value.sort((a, b)=>sortHospitalizationId(a.hospitalizationId, b.hospitalizationId, order))
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

const handleTableCancelButton = (row: HospitalizationTableData)=>{
  cancelHospitalizationDialogButtonDisabled.value = false
  hospitalizationIdToCancel.value = row.hospitalizationId
  cancelHospitalizationDialogVisible.value = true
}

const handleConfirmCancelHospitalizationButton = () => {
  cancelHospitalizationDialogButtonDisabled.value = true
  cancelHospitalizationDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-hospitalization', {hospitalizationId: hospitalizationIdToCancel.value})
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.hospitalizationId !== hospitalizationIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.hospitalizationId !== hospitalizationIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel hospitalization successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: HospitalizationTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  hospitalizationIdToShowDetail.value = row.hospitalizationId
  handleChangeDetailDialogTitle('Hospitalization Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetHospitalizationFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetHospitalizationFilterForm(hospitalizationFilterFormRef.value)
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
      :item-type="DescribableItem.Hospitalization"
      :item-id="hospitalizationIdToShowDetail"
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
    v-model="cancelHospitalizationDialogVisible"
    title="Cancel Hospitalization"
  >
    <span>Are you sure to cancel hospitalization with ID <el-text tag="b">{{ hospitalizationIdToCancel }}</el-text> ?</span>

    <template #footer>
      <el-button
        @click="cancelHospitalizationDialogVisible = false"
        :disabled="cancelHospitalizationDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelHospitalizationButton"
        :disabled="cancelHospitalizationDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="hospitalizationFilterFormRef"
          :model="hospitalizationFilterForm"
          label-position="top"
        >
          <el-form-item label="Hospitalization ID" prop="hospitalizationId">
            <el-input v-model="hospitalizationFilterForm.hospitalizationId" placeholder="Enter the hospitalization ID"></el-input>
          </el-form-item>

          <el-form-item label="Attending Doctor Name" prop="doctorName">
            <el-input v-model="hospitalizationFilterForm.doctorName" placeholder="Enter attending doctor name"></el-input>
          </el-form-item>

          <el-form-item label="Hospitalization Begin Time">
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="hospitalizationFilterForm.beginTime1"
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
                  v-model="hospitalizationFilterForm.endTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Hospitalization End Time" v-if="isHistory">
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="hospitalizationFilterForm.beginTime2"
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
                  v-model="hospitalizationFilterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId">
            <el-input v-model="hospitalizationFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>
        </el-form>

        <el-form-item>
          <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
          <el-button :disabled="formButtonDisabled" @click="resetHospitalizationFilterForm(hospitalizationFilterFormRef)">Reset</el-button>
        </el-form-item>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <el-table
        class="table-container"
        :data="displayedTableData"
        v-loading="!tableDataReady"
        @sort-change="handleTableSortChange"
        ref="hospitalizationTableRef"
      >
        <el-table-column label="Hospitalization ID" prop="hospitalizationId" sortable="custom"/>
        <el-table-column label="Attending Doctor Name" prop="doctorName" sortable="custom"/>
        <el-table-column label="Hospitalization Time" prop="beginTime" sortable="custom"/>
        <el-table-column v-if="isHistory" label="Discharge Time" prop="endTime" sortable="custom"/>
        <el-table-column label="Consultation ID" prop="consultationId" sortable="custom"/>
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