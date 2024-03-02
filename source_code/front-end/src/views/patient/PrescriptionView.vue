<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import { sortPrescriptionId, sortConsultationId, sortPharmacyWindow, sortTime } from "../../utils/sort.ts"

interface PrescriptionTableData {
  prescriptionId: string
  consultationId: string
  pharmacyWindow: string
  pharmacyPickupTime: string
}
interface PrescriptionFilterForm {
  prescriptionId: string
  consultationId: string
  beginTime: string
  endTime: string
  pharmacyWindow: string
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
const prescriptionTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData = [] as PrescriptionTableData[]
const orderedTableData = ref<PrescriptionTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const refusePrescriptionDialogVisible = ref(false)
const prescriptionIdToRefuse = ref('')
const refusePrescriptionDialogButtonDisabled = ref(false)
const prescriptionIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Prescription Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const prescriptionFilterFormRef = ref<FormInstance>()
const prescriptionFilterForm = ref<PrescriptionFilterForm>({
  prescriptionId: '',
  consultationId: '',
  beginTime: '',
  pharmacyWindow: '',
  endTime: ''
})
const formButtonDisabled = ref(false)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = { ...prescriptionFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-prescription', { params: submitValue })
      .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      prescriptionTableRef.value?.clearSort()
    })
    .catch((error) => {
      console.log(error)
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
  switch(prop) {
    case 'prescriptionId':
      orderedTableData.value.sort((a, b)=>sortPrescriptionId(a.prescriptionId, b.prescriptionId, order))
      break
    case 'consultationId':
      orderedTableData.value.sort((a, b)=>sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'pharmacyWindow':
      orderedTableData.value.sort((a, b)=>sortPharmacyWindow(a.pharmacyWindow, b.pharmacyWindow, order))
      break
    case 'pharmacyPickupTime':
      orderedTableData.value.sort((a, b)=>sortTime(a.pharmacyPickupTime, b.pharmacyPickupTime, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableRefuseButton = (row: PrescriptionTableData) => {
  refusePrescriptionDialogButtonDisabled.value = false
  prescriptionIdToRefuse.value = row.prescriptionId
  refusePrescriptionDialogVisible.value = true
}

const handleConfirmRefusePrescriptionButton = () =>{
  refusePrescriptionDialogButtonDisabled.value = true
  refusePrescriptionDialogVisible.value = false
  axios.post(rootOfPath + '/patient/refuse-prescription', { prescriptionId: prescriptionIdToRefuse.value })
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.prescriptionId !== prescriptionIdToRefuse.value)
      ElMessage.success('Refuse prescription successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) =>{
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: PrescriptionTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()  // originally in the description box
  historyDescriptionItemArrStore.setLengthToZero()
  prescriptionIdToShowDetail.value = row.prescriptionId
  handleChangeDetailDialogTitle('Prescription Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetPrescriptionFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}


onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetPrescriptionFilterForm(prescriptionFilterFormRef.value)
  getTableData()
  tablePageSize.value = config.defaultPageSize
})
</script>

<template>
  <el-dialog
    v-model="detailDialogVisible"
    :title="detailDialogTitle"
    :width="config.showDetailDialogWidth"
    destory-on-close
  >
    <InformationDescriptionBox
      :item-type="DescribableItem.Prescription"
      :item-id="prescriptionIdToShowDetail"
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
    v-model="refusePrescriptionDialogVisible"
    title="Refuse Prescription"
  >
    <span>Are you sure to refuse prescription with ID <el-text tag="b">{{ prescriptionIdToRefuse }}</el-text> ?</span>

    <template #footer>
      <el-button
        @click="refusePrescriptionDialogVisible = false"
        :disabled="refusePrescriptionDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmRefusePrescriptionButton"
        :disabled="refusePrescriptionDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="prescriptionFilterFormRef"
          :model="prescriptionFilterForm"
          label-position="top"
        >
          <el-form-item label="Prescription ID" prop="prescriptionId">
            <el-input v-model="prescriptionFilterForm.prescriptionId" placeholder="Enter the prescription ID"></el-input>
          </el-form-item>


          <el-form-item label="Pickup Window" prop="pharmacyWindow">
            <el-input v-model="prescriptionFilterForm.pharmacyWindow" placeholder="Enter the pharmacy window"></el-input>
          </el-form-item>

          <el-form-item label="Pickup Time" v-if="isHistory">
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="prescriptionFilterForm.beginTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime">
                <el-date-picker
                  v-model="prescriptionFilterForm.endTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId">
            <el-input v-model="prescriptionFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
            <el-button :disabled="formButtonDisabled" @click="resetPrescriptionFilterForm(prescriptionFilterFormRef)">Reset</el-button>
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
        ref="prescriptionTableRef"
      >
        <el-table-column label="Prescription ID" prop="prescriptionId" sortable="custom"></el-table-column>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable="custom"></el-table-column>
        <el-table-column label="Pharmacy Window" prop="pharmacyWindow" sortable="custom"></el-table-column>
        <el-table-column v-if="isHistory" label="Pharmacy Pickup Time" prop="pharmacyPickupTime" sortable="custom"></el-table-column>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleTableShowDetailButton(scope.row)">Show Detail</el-button>
            <el-button type="danger" v-if="!isHistory" size="small" @click="handleTableRefuseButton(scope.row)">Refuse</el-button>
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