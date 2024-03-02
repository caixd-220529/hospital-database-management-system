<script setup lang="ts">
import {useRouter} from 'vue-router'
import {computed, onMounted, ref, watch} from 'vue'
import {ElMessage, type FormInstance, type FormRules, type TableInstance} from 'element-plus'
import axios from 'axios';
import dayjs from "dayjs"
import utc from 'dayjs/plugin/utc'
import {useConfigStore} from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import {useDescriptionBoxHistoryArrStore} from '../../stores/descriptionBoxHistoryArr'
import {sortDoctorId, sortName, sortPatientId, sortSurgeryId, sortSurgerySite, sortTime,} from "../../utils/sort.ts"
import {
  patientIdRemoteMethod,
  patientNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod,
  surgeryNameRemoteMethod,
  surgerySiteRemoteMethod,
} from "../../utils/remote.ts"
import {DescribableItem, DoctorRough, HelpingStaffRough, NurseRough, SurgeryRelatedRecordRough} from "../../types/other.ts"
import {UserType} from '../../types/user.ts'
import {useAddEmployeeDialog} from "../../composables/addEmployeeDialog.ts";

dayjs.extend(utc)

interface SurgeryTableData {
  consultationId: string
  surgeryId: string
  surgeryName: string
  surgerySite: string
  surgeryType: string
  beginTime: string
  endTime: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  hasBegin: string
}

interface SurgeryFilterForm {
  consultationId: string
  surgeryId: string
  surgeryName: string
  surgerySite: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  beginTime1: string
  endTime1: string
  beginTime2: string
  endTime2: string
  rationButtonString: string
  hasBegin?: boolean
  hasEnd?: boolean
  inquirerId?: string
  isSearchingPatientInfo?: boolean
}

interface SurgeryToBegin {
  surgeryId: string
  surgeryName: string
  surgerySite: string
  surgeryType: string
  surgeryDescription: string
  patientId: string
  patientName: string
  beginTime: string
}

interface SurgeryRecord {
  recordTime: string
  recordDetail: string
}

interface SurgeryToEnd {
  surgeryId: string
  surgeryName: string
  patientId: string
  patientName: string
  beginTime: string
  endTime: string
  recordRoughArr: SurgeryRelatedRecordRough[]
  doctorRoughArr: DoctorRough[]
  nurseRoughArr: NurseRough[]
  helpingStaffRoughArr: HelpingStaffRough[]
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()
const isSearchPatientInfo = computed(() => router.currentRoute.value.path.includes('patient-information'))
const isSearchDoctorInfo = computed(() => router.currentRoute.value.path.includes('doctor-information'))
const isRecord = computed(() => router.currentRoute.value.path.includes('record'))
const isTableDataBegin = ref(false)

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
const itemIdToShowDetail = ref('')
const itemTypeToShowDetail = ref<DescribableItem>(DescribableItem.Consultation)

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Surgery Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const surgeryFilterFormRef = ref<FormInstance>()
const surgeryFilterForm = ref<SurgeryFilterForm>({
  consultationId: '',
  surgeryId: '',
  surgeryName: '',
  surgerySite: '',
  patientId: '',
  patientName: '',
  doctorId: '',
  doctorName: '',
  beginTime1: '',
  endTime1: '',
  beginTime2: '',
  endTime2: '',
  rationButtonString: 'Not yet begin',  // another is Already begin
})
const doctorIdOptions = ref<string[]>([])
const doctorIdLoading = ref(false)
const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const patientIdOptions = ref<string[]>([])
const patientIdLoading = ref(false)
const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const surgeryNameOptions = ref<string[]>([])
const surgeryNameLoading = ref(false)
const surgerySiteOptions = ref<string[]>([])
const surgerySiteLoading = ref(false)
const formButtonDisabled = ref(false)

const beginDialogVisible = ref(false)
const surgeryIdToBegin = ref('')
const beginDialogButtonDisabled = ref(false)
const beginFormRef = ref<FormInstance>()
const surgeryToBegin = ref<SurgeryToBegin>({
  surgeryId: '',
  surgeryName: '',
  surgerySite: '',
  surgeryType: '',
  surgeryDescription: '',
  patientId: '',
  patientName: '',
  beginTime: '',
})

const recordDialogVisible = ref(false)
const surgeryIdToRecord = ref('')
const recordDialogButtonDisabled = ref(false)
const recordFormRef = ref<FormInstance>()
const surgeryToRecord = ref<SurgeryRecord>({
  recordTime: '',
  recordDetail: '',
})
const recordFormRules = ref<FormRules<SurgeryRecord>>({
  recordTime: [
    {required: true}
  ],
  recordDetail: [
    {required: true, trigger: 'change', message: 'Please input record detail'}
  ],
})

const endDialogVisible = ref(false)
const surgeryIdToEnd = ref('')
const endDialogButtonDisabled = ref(false)
const endFormRef = ref<FormInstance>()
const surgeryToEnd = ref<SurgeryToEnd>({
  surgeryId: '',
  surgeryName: '',
  patientId: '',
  patientName: '',
  beginTime: '',
  endTime: '',
  recordRoughArr: [],
  doctorRoughArr: [{doctorId: config.userId, doctorName: config.userName}],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
})

const {
  addEmployeeDialogVisible,
  employeeType,
  addEmployeeDialogTitle,
  addEmployeeDialogButtonDisabled,
  doctorInfoToAdd,
  nurseInfoToAdd,
  helpingStaffInfoToAdd,
  addDoctorFormRef,
  addNurseFormRef,
  addHelpingStaffFormRef,
  doctorInfoOptions,
  doctorInfoLoading,
  nurseInfoOptions,
  nurseInfoLoading,
  helpingStaffInfoOptions,
  helpingStaffInfoLoading,
  addDoctorFormRules,
  addNurseFormRules,
  addHelpingStaffFormRules,
  handleAddEmployeeButton,
  handleDeleteEmployeeButton,
  handleAddEmployeeDialogConfirm,
  handleAddEmployeeDialogCancel,
  doctorInfoRemoteMethod,
  nurseInfoRemoteMethod,
  helpingStaffInfoRemoteMethod
} = useAddEmployeeDialog(surgeryToEnd)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...surgeryFilterForm.value}
  submitValue.inquirerId = config.userId
  if (isSearchPatientInfo.value || isSearchDoctorInfo.value) {
    delete submitValue.hasBegin
    delete submitValue.hasEnd
    submitValue.isSearchingPatientInfo = isSearchPatientInfo.value
  } else {
    console.assert(submitValue.rationButtonString === 'Not yet begin' || submitValue.rationButtonString === 'Already begin')
    submitValue.hasEnd = false
    isTableDataBegin.value = submitValue.hasBegin = submitValue.rationButtonString !== 'Not yet begin'
    submitValue.doctorId = config.userId
    submitValue.doctorName = ''
  }

  axios.get(rootOfPath + '/get-doctor-surgery', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      surgeryTableRef.value?.clearSort()
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
    return
  }
  switch (prop) {
    case 'surgeryId':
      orderedTableData.value.sort((a, b) => sortSurgeryId(a.surgeryId, b.surgeryId, order))
      break
    case 'surgeryName':
      orderedTableData.value.sort((a, b) => sortName(a.surgeryName, b.surgeryName, order))
      break
    case 'surgerySite':
      orderedTableData.value.sort((a, b) => sortSurgerySite(a.surgerySite, b.surgerySite, order))
      break
    case 'beginTime':
      orderedTableData.value.sort((a, b) => sortTime(a.beginTime, b.beginTime, order))
      break
    case 'endTime':
      orderedTableData.value.sort((a, b) => sortTime(a.endTime, b.endTime, order))
      break
    case 'patientId':
      orderedTableData.value.sort((a, b) => sortPatientId(a.patientId, b.patientId, order));
      break
    case 'patientName':
      orderedTableData.value.sort((a, b) => sortName(a.patientName, b.patientName, order))
      break
    case 'doctorId':
      orderedTableData.value.sort((a, b) => sortDoctorId(a.doctorId, b.doctorId, order));
      break
    case 'doctorName':
      orderedTableData.value.sort((a, b) => sortName(a.doctorName, b.doctorName, order))
      break
    default:
      console.error('Invalid prop: ' + prop)
  }
}

const handleTableCancelSurgery = (surgeryId: string) => {
  cancelSurgeryDialogButtonDisabled.value = false
  surgeryIdToCancel.value = surgeryId
  cancelSurgeryDialogVisible.value = true
}

const handleConfirmCancelSurgeryButton = () => {
  cancelSurgeryDialogButtonDisabled.value = true
  cancelSurgeryDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-surgery',
    {
      surgeryId: surgeryIdToCancel.value,
      doctorId: config.userId
    })
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

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleShowDetailButton = (itemId: string, itemType: DescribableItem) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  itemIdToShowDetail.value = itemId
  itemTypeToShowDetail.value = itemType
  switch (itemType){
    case DescribableItem.Surgery:
      handleChangeDetailDialogTitle('Surgery Detail')
      break
    case DescribableItem.SurgeryRecord:
      handleChangeDetailDialogTitle('Surgery Record Detail')
      break
  }
  detailDialogVisible.value = true
}

const handleTableBeginButton = (row: SurgeryTableData) => {
  surgeryIdToBegin.value = row.surgeryId
  surgeryToBegin.value.surgeryId = row.surgeryId
  surgeryToBegin.value.surgeryName = row.surgeryName
  surgeryToBegin.value.surgerySite = row.surgerySite
  surgeryToBegin.value.surgeryType = row.surgeryType
  surgeryToBegin.value.patientId = row.patientId
  surgeryToBegin.value.patientName = row.patientName
  surgeryToBegin.value.beginTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  axios.get(rootOfPath + '/doctor/get-surgery-description', {params: {surgeryId: surgeryIdToBegin.value}})
    .then((res) => {
      surgeryToBegin.value.surgeryDescription = res.data.results
    })
    .finally(() => {
      beginDialogButtonDisabled.value = false
      beginDialogVisible.value = true
    })
}

const handleTableRecordButton = (row: SurgeryTableData) => {
  surgeryIdToRecord.value = row.surgeryId
  surgeryToRecord.value.recordTime = dayjs().format('YYYY-MM-DD HH:mm:ss')
  surgeryToRecord.value.recordDetail = ''
  recordDialogButtonDisabled.value = false
  recordDialogVisible.value = true

}

const handleTableEndButton = (row: SurgeryTableData) => {
  resetEndForm()
  surgeryIdToEnd.value = row.surgeryId
  surgeryToEnd.value.surgeryId = row.surgeryId
  surgeryToEnd.value.surgeryName = row.surgeryName
  surgeryToEnd.value.patientId = row.patientId
  surgeryToEnd.value.patientName = row.patientName
  surgeryToEnd.value.beginTime = row.beginTime
  surgeryToEnd.value.endTime = dayjs().format('YYYY-MM-DD HH:mm:ss')
  axios.get(rootOfPath + '/doctor/surgery/get-surgery-record-rough', {
    params: {
      surgeryId: surgeryIdToEnd.value
    }})
    .then(res=>{
      surgeryToEnd.value.recordRoughArr = res.data.results
      endDialogButtonDisabled.value = false
      endDialogVisible.value = true
    })
}

const resetForm = (form: FormInstance | undefined) => {
  if (form) {
    if (form !== surgeryFilterFormRef.value) {
      form.resetFields()
    } else {
      form.resetFields()
    }
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
const _surgeryNameRemoteMethod = (query: string) => {
  surgeryNameRemoteMethod(query, '',surgeryNameOptions, surgeryNameLoading)
}
const _surgerySiteRemoteMethod = (query: string) => {
  surgerySiteRemoteMethod(query, surgerySiteOptions, surgerySiteLoading)
}
const resetEndForm = () => {
  resetForm(endFormRef.value)
  surgeryToEnd.value.recordRoughArr = []
  surgeryToEnd.value.doctorRoughArr = [{doctorId: config.userId, doctorName: config.userName}]
  surgeryToEnd.value.nurseRoughArr = []
  surgeryToEnd.value.helpingStaffRoughArr = []
}

const handleBeginDialogConfirm = () => {
  beginDialogButtonDisabled.value = true
  axios.post(rootOfPath + '/doctor/surgery/begin', {
    surgeryId: surgeryIdToBegin.value,
    surgeryTime: dayjs(surgeryToBegin.value.beginTime).utc().format()
  })
    .then(() => {
      ElMessage.success('Begin surgery successfully')
      resetForm(beginFormRef.value)
      beginDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.surgeryId !== surgeryIdToBegin.value)
      originalTableData = originalTableData.filter((item) => item.surgeryId !== surgeryIdToBegin.value)
      totalDataNumber.value -= 1
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleRecordDialogConfirm = async () => {
  recordDialogButtonDisabled.value = true
  let formValid = false
  await recordFormRef.value?.validate((valid)=>{
    formValid = valid
  })
  if(!formValid){
    recordDialogButtonDisabled.value = false
    return
  }
  axios.post(rootOfPath + '/doctor/surgery/record', {
    surgeryId: surgeryIdToRecord.value,
    recordTime: dayjs(surgeryToRecord.value.recordTime).utc().format(),
    recordDetail: surgeryToRecord.value.recordDetail
  })
    .then((res) => {
      ElMessage.success(`Surgery record ${res.data.results.recordId} is added successfully`)
      resetForm(recordFormRef.value)
      recordDialogVisible.value = false
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleEndDialogConfirm = async () => {
  endDialogButtonDisabled.value = true
  let formValid = false
  await endFormRef.value?.validate((valid)=>{
    formValid = valid
  })
  if(!formValid){
    endDialogButtonDisabled.value = false
    return
  }
  axios.post(rootOfPath + '/doctor/surgery/end', {
    surgeryId: surgeryIdToEnd.value,
    endTime: dayjs(surgeryToEnd.value.endTime).utc().format(),
    doctorRoughArr: surgeryToEnd.value.doctorRoughArr,
    nurseRoughArr: surgeryToEnd.value.nurseRoughArr,
    helpingStaffRoughArr: surgeryToEnd.value.helpingStaffRoughArr
  })
    .then(() => {
      ElMessage.success('End surgery successfully')
      resetEndForm()
      endDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.surgeryId !== surgeryIdToEnd.value)
      originalTableData = originalTableData.filter((item) => item.surgeryId !== surgeryIdToEnd.value)
      totalDataNumber.value -= 1
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

onMounted(() => {
  getTableData()
})
watch(() => router.currentRoute.value.path, () => {
  resetForm(surgeryFilterFormRef.value)
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
      :item-type="itemTypeToShowDetail"
      :item-id="itemIdToShowDetail"
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
    v-model="cancelSurgeryDialogVisible"
    title="Cancel Surgery"
  >
    <span>Are you sure to cancel surgery with ID <el-text tag="b">{{ surgeryIdToCancel }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelSurgeryDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelSurgeryButton"
        :disabled="cancelSurgeryDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="beginDialogVisible"
    title="Begin Surgery"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="beginFormRef"
            :model="surgeryToBegin"
            label-position="top"
          >
            <el-form-item label="Surgery ID" prop="surgeryId">
              <el-input v-model="surgeryToBegin.surgeryId" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Name" prop="surgeryName">
              <el-input v-model="surgeryToBegin.surgeryName" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Site" prop="surgerySite">
              <el-input v-model="surgeryToBegin.surgerySite" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Type" prop="surgeryType">
              <el-input v-model="surgeryToBegin.surgeryType" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="surgeryToBegin.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="surgeryToBegin.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Begin Time" prop="surgeryTime">
              <el-input v-model="surgeryToBegin.beginTime" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Description" prop="surgeryDescription">
              <el-input v-model="surgeryToBegin.surgeryDescription" type="textarea" autosize disabled/>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="beginDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleBeginDialogConfirm"
        :disabled="beginDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="recordDialogVisible"
    title="Record Surgery"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="recordFormRef"
            :model="surgeryToRecord"
            :rules="recordFormRules"
            label-position="top"
          >
            <el-form-item label="Surgery ID" prop="surgeryId">
              <el-input v-model="surgeryIdToRecord" disabled/>
            </el-form-item>

            <el-form-item label="Record Time" prop="recordTime">
              <el-input v-model="surgeryToRecord.recordTime" disabled/>
            </el-form-item>

            <el-form-item label="Record Detail" prop="recordDetail">
              <el-input v-model="surgeryToRecord.recordDetail" type="textarea" autosize/>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="recordDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleRecordDialogConfirm"
        :disabled="recordDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="endDialogVisible"
    title="End Surgery"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="endFormRef"
            :model="surgeryToEnd"
            label-position="top"
          >
            <el-form-item label="Surgery ID" prop="surgeryId">
              <el-input v-model="surgeryToEnd.surgeryId" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Name" prop="surgeryName">
              <el-input v-model="surgeryToEnd.surgeryName" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="surgeryToEnd.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="surgeryToEnd.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Begin Time" prop="beginTime">
              <el-input v-model="surgeryToEnd.beginTime" disabled/>
            </el-form-item>

            <el-form-item label="End Time" prop="endTime">
              <el-input v-model="surgeryToEnd.endTime" disabled/>
            </el-form-item>

            <el-form-item label="Surgery Record" prop="surgeryRecord">
              <el-table
                :data="surgeryToEnd.recordRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Record ID" prop="recordId" align="center"/>
                <el-table-column label="Record Time" prop="recordTime" align="center"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button size="small" plain type="primary"
                               @click="handleShowDetailButton(surgeryIdToEnd+'#'+scope.row.recordId, DescribableItem.SurgeryRecord)">
                      Show Detail
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Related Doctor
                <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.Doctor)" plain>Add
                </el-button>
              </template>
              <el-table
                :data="surgeryToEnd.doctorRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Doctor ID" prop="doctorId" align="center"/>
                <el-table-column label="Doctor Name" prop="doctorName" align="center"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" plain :disabled="scope.row.doctorId === config.userId"
                               @click="handleDeleteEmployeeButton(UserType.Doctor, scope.row.doctorId)">Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Related Nurse
                <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.Nurse)" plain>Add
                </el-button>
              </template>
              <el-table
                :data="surgeryToEnd.nurseRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Nurse ID" prop="nurseId" align="center"/>
                <el-table-column label="Nurse Name" prop="nurseName" align="center"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" plain
                               @click="handleDeleteEmployeeButton(UserType.Nurse, scope.row.nurseId)">Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Related Helping Staff
                <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.HelpingStaff)" plain>
                  Add
                </el-button>
              </template>
              <el-table
                :data="surgeryToEnd.helpingStaffRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Helping Staff ID" prop="helpingStaffId" align="center"/>
                <el-table-column label="Helping Staff Name" prop="helpingStaffName" align="center"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" plain
                               @click="handleDeleteEmployeeButton(UserType.HelpingStaff, scope.row.helpingStaffId)">
                      Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="endDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        :disabled="endDialogButtonDisabled"
        @click="handleEndDialogConfirm"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addEmployeeDialogVisible"
    :title="addEmployeeDialogTitle"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="addDoctorFormRef"
            :model="doctorInfoToAdd"
            label-position="top"
            :rules="addDoctorFormRules"
            v-if="employeeType === UserType.Doctor"
          >
            <el-form-item label="Doctor ID" prop="doctorId">
              <el-input v-model="doctorInfoToAdd.doctorId" disabled placeholder="Enter the doctor name"/>
            </el-form-item>

            <el-form-item label="Doctor Name" prop="doctorName">
              <el-select
                v-model="doctorInfoToAdd.doctorName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="doctorInfoRemoteMethod"
                :loading="doctorInfoLoading"
                placeholder="Enter the doctor name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in doctorInfoOptions"
                  :key="item.doctorId"
                  :label="item.doctorName"
                  :value="item.doctorId"
                >
                  <span style="float: left">{{ item.doctorName }}</span>
                  <span
                    style="float: right; color: var(--el-text-color-secondary); font-size: 13px">{{
                      item.doctorId
                    }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <el-form
            ref="addNurseFormRef"
            :model="nurseInfoToAdd"
            label-position="top"
            :rules="addNurseFormRules"
            v-if="employeeType === UserType.Nurse"
          >
            <el-form-item label="Nurse ID" prop="nurseId">
              <el-input v-model="nurseInfoToAdd.nurseId" disabled placeholder="Enter the nurse name"/>
            </el-form-item>

            <el-form-item label="Nurse Name" prop="nurseName">
              <el-select
                v-model="nurseInfoToAdd.nurseName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="nurseInfoRemoteMethod"
                :loading="nurseInfoLoading"
                placeholder="Enter the nurse name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in nurseInfoOptions"
                  :key="item.nurseId"
                  :label="item.nurseName"
                  :value="item.nurseId"
                >
                  <span style="float: left">{{ item.nurseName }}</span>
                  <span
                    style="float: right; color: var(--el-text-color-secondary); font-size: 13px">{{
                      item.nurseId
                    }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <el-form
            ref="addHelpingStaffFormRef"
            :model="helpingStaffInfoToAdd"
            label-position="top"
            :rules="addHelpingStaffFormRules"
            v-if="employeeType === UserType.HelpingStaff"
          >
            <el-form-item label="Helping Staff ID" prop="helpingStaffId">
              <el-input v-model="helpingStaffInfoToAdd.helpingStaffId" disabled
                        placeholder="Enter the helping staff name"/>
            </el-form-item>

            <el-form-item label="Helping Staff Name" prop="helpingStaffName">
              <el-select
                v-model="helpingStaffInfoToAdd.helpingStaffName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="helpingStaffInfoRemoteMethod"
                :loading="helpingStaffInfoLoading"
                placeholder="Enter the helping staff name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in helpingStaffInfoOptions"
                  :key="item.helpingStaffId"
                  :label="item.helpingStaffName"
                  :value="item.helpingStaffId"
                >
                  <span style="float: left">{{ item.helpingStaffName }}</span>
                  <span
                    style="float: right; color: var(--el-text-color-secondary); font-size: 13px">{{
                      item.helpingStaffId
                    }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleAddEmployeeDialogCancel">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleAddEmployeeDialogConfirm"
        :disabled="addEmployeeDialogButtonDisabled"
      >Confirm
      </el-button>
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
          <el-form-item
            label="Type"
            prop="rationButtonString"
            v-if="isRecord"
          >
            <el-radio-group v-model="surgeryFilterForm.rationButtonString">
              <el-radio label="Not yet begin"/>
              <el-radio label="Already begin"/>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Surgery ID" prop="surgeryId">
            <el-input v-model="surgeryFilterForm.surgeryId" placeholder="Enter the surgery ID"/>
          </el-form-item>

          <el-form-item label="Surgery Site" prop="surgerySite">
            <el-select
              v-model="surgeryFilterForm.surgerySite"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_surgerySiteRemoteMethod"
              :loading="surgerySiteLoading"
              placeholder="Enter the surgery site"
              style="width: 100%"
            >
              <el-option
                v-for="item in surgerySiteOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Surgery Name" prop="surgeryName">
            <el-select
              v-model="surgeryFilterForm.surgeryName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_surgeryNameRemoteMethod"
              :loading="surgeryNameLoading"
              placeholder="Enter the surgery name"
              style="width: 100%"
            >
              <el-option
                v-for="item in surgeryNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="surgeryFilterForm.patientId"
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
              v-model="surgeryFilterForm.patientName"
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

          <el-form-item label="Lead Surgeon ID" prop="doctorId" v-if="isSearchDoctorInfo">
            <el-select
              v-model="surgeryFilterForm.doctorId"
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

          <el-form-item label="Lead Surgeon Name" prop="doctorName" v-if="isSearchDoctorInfo">
            <el-select
              v-model="surgeryFilterForm.doctorName"
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

          <el-form-item label="Begin Time">
            <el-col :span="11">
              <el-form-item prop="beginTime1">
                <el-date-picker
                  v-model="surgeryFilterForm.beginTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime1">
                <el-date-picker
                  v-model="surgeryFilterForm.endTime1"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="End Time" v-if="isSearchPatientInfo||isSearchDoctorInfo">
            <el-col :span="11">
              <el-form-item prop="beginTime2">
                <el-date-picker
                  v-model="surgeryFilterForm.beginTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime2">
                <el-date-picker
                  v-model="surgeryFilterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId" v-if="isSearchPatientInfo">
            <el-input v-model="surgeryFilterForm.consultationId" placeholder="Enter the consultation ID"/>
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
              @click="resetForm(surgeryFilterFormRef)"
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
        ref="surgeryTableRef"
      >
        <el-table-column label="Surgery ID" prop="surgeryId" sortable/>
        <el-table-column label="Surgery Name" prop="surgeryName" sortable/>
        <el-table-column label="Surgery Site" prop="surgerySite" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Begin Time" prop="beginTime" sortable/>
        <el-table-column label="End Time" prop="endTime" sortable v-if="isSearchDoctorInfo || isSearchPatientInfo"/>
        <el-table-column label="Lead Surgeon ID" prop="doctorId" sortable v-if="isSearchDoctorInfo"/>
        <el-table-column label="Lead Surgeon Name" prop="doctorName" sortable v-if="isSearchDoctorInfo||isSearchPatientInfo"/>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable v-if="isSearchPatientInfo"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleShowDetailButton(scope.row.surgeryId, DescribableItem.Surgery)"
              v-if="isSearchPatientInfo||isSearchDoctorInfo"
            >Show Detail
            </el-button>
            <el-button
              type="primary"
              size="small"
              v-if="isRecord&&!isTableDataBegin"
              @click="handleTableBeginButton(scope.row)"
            >Begin
            </el-button>
            <el-button
              size="small"
              v-if="isRecord&&isTableDataBegin"
              @click="handleTableRecordButton(scope.row)"
            >Record
            </el-button>
            <el-button
              type="primary"
              size="small"
              v-if="isRecord&&isTableDataBegin"
              @click="handleTableEndButton(scope.row)"
            >End
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleTableCancelSurgery(scope.row.surgeryId)"
              :disabled="scope.row.hasBegin==='true'"
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