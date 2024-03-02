<script setup lang="ts">
import {useRouter} from 'vue-router'
import {computed, onMounted, ref, watch} from 'vue'
import {ElMessage, type FormInstance, type FormRules, type TableInstance} from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import axios from 'axios';
import dayjs from "dayjs"
import utc from 'dayjs/plugin/utc'
import {useConfigStore} from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import {useDescriptionBoxHistoryArrStore} from '../../stores/descriptionBoxHistoryArr'
import {
  sortPrescriptionId,
  sortDoctorId,
  sortName,
  sortPatientId,
  sortTime,
  sortPharmacyPickWindow
} from "../../utils/sort.ts";
import {DescribableItem, PrescriptionMedicineRough} from "../../types/other.ts";
import {
  patientIdRemoteMethod, patientNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod
} from "../../utils/remote.ts";

dayjs.extend(utc)

interface PrescriptionTableData {
  consultationId: string
  prescriptionId: string
  pharmacyPickupTime: string
  pharmacyPickWindow: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  hasStarted: string
}

interface PrescriptionFilterForm {
  consultationId: string
  prescriptionId: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  beginTime: string
  endTime: string
  inquirerId?: string
  hasStarted?: boolean
  isSearchingPatientInfo?: boolean
}

interface medicineInfo extends PrescriptionMedicineRough{
  confirm: boolean
}

interface PrescriptionToRecord {
  prescriptionId: string
  patientId: string
  patientName: string
  pharmacyPickupTime: string
  prescriptionMedicineRoughArr: medicineInfo[]
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()
const isSearchPatientInfo = computed(() => router.currentRoute.value.path.includes('patient-information'))
const isSearchDoctorInfo = computed(() => router.currentRoute.value.path.includes('doctor-information'))
const isRecord = computed(() => router.currentRoute.value.path.includes('record'))

const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const prescriptionTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: PrescriptionTableData[] = []
const orderedTableData = ref<PrescriptionTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelPrescriptionDialogVisible = ref(false)
const prescriptionIdToCancel = ref('')
const cancelPrescriptionDialogButtonDisabled = ref(false)
const prescriptionIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Prescription Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const prescriptionFilterFormRef = ref<FormInstance>()
const prescriptionFilterForm = ref<PrescriptionFilterForm>({
  consultationId: '',
  prescriptionId: '',
  patientId: '',
  patientName: '',
  doctorId: '',
  doctorName: '',
  beginTime: '',
  endTime: '',
})
const doctorIdOptions = ref<string[]>([])
const doctorIdLoading = ref(false)
const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const patientIdOptions = ref<string[]>([])
const patientIdLoading = ref(false)
const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const formButtonDisabled = ref(false)

const recordDialogVisible = ref(false)
const prescriptionIdToRecord = ref('')
const recordDialogButtonDisabled = ref(false)
const recordFormRef = ref<FormInstance>()
const prescriptionToRecord = ref<PrescriptionToRecord>({
  prescriptionId: '',
  pharmacyPickupTime: '',
  patientId: '',
  patientName: '',
  prescriptionMedicineRoughArr: [],
})

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...prescriptionFilterForm.value}
  submitValue.inquirerId = config.userId
  if (isRecord.value) {
    submitValue.hasStarted = false
    submitValue.doctorId = config.userId
  } else {
    submitValue.isSearchingPatientInfo = isSearchPatientInfo.value
  }

  axios.get(rootOfPath + '/get-doctor-prescription', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      prescriptionTableRef.value?.clearSort()
    })
    .catch((err) => {
      console.log(err)
    })
    .finally(() => {
      tableDataReady.value = true
      formButtonDisabled.value = false
    })
}

const handleTableSortChange = (param: any) => {
  const {prop, order} = param
  if (!order) {
    orderedTableData.value = originalTableData.slice()
    return;
  }
  switch (prop) {
    case 'prescriptionId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortPrescriptionId(a.prescriptionId, b.prescriptionId, order))
      break
    case 'pharmacyPickupTime':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortTime(a.pharmacyPickupTime, b.pharmacyPickupTime, order))
      break
    case 'pharmacyPickWindow':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortPharmacyPickWindow(a.pharmacyPickWindow, b.pharmacyPickWindow, order))
      break
    case 'patientId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortPatientId(a.patientId, b.patientId, order))
      break
    case 'patientName':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortName(a.patientName, b.patientName, order))
      break
    case 'doctorId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortDoctorId(a.doctorId, b.doctorId, order))
      break
    case 'doctorName':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortName(a.doctorName, b.doctorName, order))
      break
    default:
      console.error('Unknown prop:', prop)
  }
}

const handleTableCancelPrescription = (prescriptionId: string) => {
  cancelPrescriptionDialogButtonDisabled.value = false
  prescriptionIdToCancel.value = prescriptionId
  cancelPrescriptionDialogVisible.value = true
}

const handleConfirmCancelPrescriptionButton = () => {
  cancelPrescriptionDialogButtonDisabled.value = true
  cancelPrescriptionDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-prescription',
    {
      prescriptionId: prescriptionIdToCancel.value,
      doctorId: config.userId
    })
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.prescriptionId !== prescriptionIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.prescriptionId !== prescriptionIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel prescription successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: PrescriptionTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  prescriptionIdToShowDetail.value = row.prescriptionId
  handleChangeDetailDialogTitle('Prescription Detail')
  detailDialogVisible.value = true
}

const handleTableRecordButton = (row: PrescriptionTableData) => {
  prescriptionIdToRecord.value = row.prescriptionId
  prescriptionToRecord.value.prescriptionId = row.prescriptionId
  prescriptionToRecord.value.pharmacyPickupTime = dayjs().format('YYYY-MM-DD HH:mm:ss')
  prescriptionToRecord.value.patientId = row.patientId
  prescriptionToRecord.value.patientName = row.patientName

  axios.get(rootOfPath + `/get-prescription-detailed?prescriptionId=${row.prescriptionId}`)
    .then((response) => {
      prescriptionToRecord.value.prescriptionMedicineRoughArr = response.data.results.prescriptionMedicineRoughArr
      prescriptionToRecord.value.prescriptionMedicineRoughArr.forEach((item)=>{
        item.confirm = false
      })
      recordDialogButtonDisabled.value = false
      prescriptionIdToRecord.value = row.prescriptionId
      recordDialogVisible.value = true
    })
    .catch((err) => {
      console.log(err)
    })
}

const resetForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

const doctorIdRemoteMethod = (query: string) => {
  subordinateNameAndInquirerIdRemoteMethod(query, config.userId, config.userType, doctorIdOptions, doctorIdLoading)
}
const doctorNameRemoteMethod = (query: string) => {
  subordinateNameAndInquirerNameRemoteMethod(query, config.userId, config.userType, doctorNameOptions, doctorNameLoading)
}
const _patientIdRemoteMethod = (query: string) => {
  patientIdRemoteMethod(query, config.userId, config.userType, patientIdOptions, patientIdLoading)
}
const _patientNameRemoteMethod = (query: string) => {
  patientNameRemoteMethod(query, config.userName, config.userType, patientNameOptions, patientNameLoading)
}

const resetRecordForm = () => {
  resetForm(recordFormRef.value)
  prescriptionToRecord.value.prescriptionMedicineRoughArr = []
}
const handleRecordDialogBeforeClose = (done: () => void) => {
  resetRecordForm()
  done()
}
const handleRecordDialogClose = () => {
  resetRecordForm()
  recordDialogVisible.value = false
}
const handleRecordDialogConfirm = () => {
  recordDialogButtonDisabled.value=true
  if(!recordFormRef.value){
    return
  }
  let validate = true
  prescriptionToRecord.value.prescriptionMedicineRoughArr.forEach((item)=>{
    if(!item.confirm){
      validate = false
      return
    }
  })
  if(!validate){
    ElMessage.error('You must check all the medicine')
    recordDialogButtonDisabled.value=false
    return
  }
  axios.post(rootOfPath + '/prescription/finish', {
    prescriptionId: prescriptionToRecord.value.prescriptionId,
    pharmacyPickupTime: dayjs(prescriptionToRecord.value.pharmacyPickupTime).utc().format()
  })
    .then(() => {
      ElMessage.success('Record successfully')
      recordDialogVisible.value=false
      resetRecordForm()
      orderedTableData.value = orderedTableData.value.filter((item) => item.prescriptionId !== prescriptionIdToRecordoRecord.value)
      originalTableData = originalTableData.filter((item) => item.prescriptionId !== prescriptionIdToRecordoRecord.value)
      totalDataNumber.value -= 1
    })
    .catch((err)=>{
      ElMessage.error(err.response.data.results)
      recordDialogButtonDisabled.value=false
    })
}


onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetForm(prescriptionFilterFormRef.value)
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
      :item-type="DescribableItem.Prescription"
      :item-id="prescriptionIdToShowDetail"
      :show-employee-id="false"
      :show-medicine-id="true"
      @change-title="handleChangeDetailDialogTitle"
    />
    <template #footer>
      <el-button
        @click="historyDescriptionItemArrStore.decreaseIndexByOne"
        :disabled="detailedDialogPreviousButtonDisabled"
      >Previous
      </el-button>
      <el-button
        @click="historyDescriptionItemArrStore.increaseIndexByOne"
        :disabled="detailedDialogNextButtonDisabled"
      >Next
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="cancelPrescriptionDialogVisible"
    title="Cancel Prescription"
  >
    <span>Are you sure to cancel prescription with ID <el-text tag="b">{{ prescriptionIdToCancel }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelPrescriptionDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelPrescriptionButton"
        :disabled="cancelPrescriptionDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="recordDialogVisible"
    :width="config.recordDialogWidth"
    title="Record"
    destory-on-close
    :before-close="handleRecordDialogBeforeClose"
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="recordFormRef"
            :model="prescriptionToRecord"
            label-position="top"
          >
            <el-form-item label="Prescription ID" prop="prescriptionId">
              <el-input v-model="prescriptionToRecord.prescriptionId" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="prescriptionToRecord.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="prescriptionToRecord.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Pharmacy Pickup Time" prop="pharmacyPickupTime">
              <el-input v-model="prescriptionToRecord.pharmacyPickupTime" disabled/>
            </el-form-item>

            <el-form-item label="Medicine List" prop="prescriptionMedicineRoughArr">
              <el-table
                :data="prescriptionToRecord.prescriptionMedicineRoughArr"
                style="width: 100%"
              >
                <el-table-column label="ID" align="center" prop="medicineId"/>
                <el-table-column label="Name" align="center" prop="medicineName"/>
                <el-table-column label="Check" align="center">
                  <template #default="scope">
                    <el-switch
                      v-model="scope.row.confirm"
                      size="small"
                      inline-prompt
                      :active-icon="Check"
                      :inactive-icon="Close"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleRecordDialogClose">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleRecordDialogConfirm"
        :disabled="recordDialogButtonDisabled">Confirm</el-button>
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
            <el-input v-model="prescriptionFilterForm.prescriptionId" placeholder="Enter the prescription ID"/>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="prescriptionFilterForm.patientId"
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

          <el-form-item label="Patient Name" prop="patientName" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="prescriptionFilterForm.patientName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_patientNameRemoteMethod"
              :loading="patientNameLoading"
              placeholder="Enter the patient name"
              style="width: 100%"
            >
              <el-option
                v-for="item in patientNameOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Doctor ID" prop="doctorId" v-if="isSearchDoctorInfo">
            <el-select
              v-model="prescriptionFilterForm.doctorId"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="doctorIdRemoteMethod"
              :loading="doctorIdLoading"
              placeholder="Enter the doctor ID"
              style="width: 100%"
            >
              <el-option
                v-for="item in doctorIdOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Doctor Name" prop="doctorName" v-if="isSearchDoctorInfo">
            <el-select
              v-model="prescriptionFilterForm.doctorName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="doctorNameRemoteMethod"
              :loading="doctorNameLoading"
              placeholder="Enter the doctor name"
              style="width: 100%"
            >
              <el-option
                v-for="item in doctorNameOptions"
                :key="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Time">
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="prescriptionFilterForm.beginTime"
                  type="datetime"
                  placeholder="Select date and time"
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
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId" v-if="isSearchPatientInfo">
            <el-input v-model="prescriptionFilterForm.consultationId" placeholder="Enter the consultation ID"/>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              @click="getTableData"
              :disabled="formButtonDisabled"
            >Search
            </el-button>
            <el-button
              @click="resetForm(prescriptionFilterFormRef)"
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
        v-loading="!tableDataReady"
        @sort-change="handleTableSortChange"
        ref="prescriptionTableRef"
      >
        <el-table-column label="Prescription ID" prop="prescriptionId" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Pharmaceutical Doctor ID" prop="doctorId" sortable v-if="isSearchDoctorInfo"/>
        <el-table-column label="Pharmaceutical Doctor Name" prop="doctorName" sortable v-if="isSearchDoctorInfo||isSearchPatientInfo"/>
        <el-table-column label="Pickup Time" prop="pharmacyPickupTime" sortable/>
        <el-table-column label="Pickup Window" prop="pharmacyPickWindow" sortable v-if="isRecord"/>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable v-if="isSearchPatientInfo"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleTableShowDetailButton(scope.row)"
              v-if="isSearchPatientInfo||isSearchDoctorInfo"
            >Show Detail
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleTableRecordButton(scope.row)"
              v-if="isRecord"
              >Record
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleTableCancelPrescription(scope.row.prescriptionId)"
              :disabled="scope.row.hasStarted==='true'"
              v-if="isSearchPatientInfo"
            >Cancel
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
    </el-scrollbar>
  </div>
</template>

<style scoped>

</style>