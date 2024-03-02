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
import {sortDoctorId, sortName, sortPatientId, sortHospitalizationId, sortTime,} from "../../utils/sort.ts"
import {
  patientIdRemoteMethod,
  patientNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod,
} from "../../utils/remote.ts"
import {DescribableItem, DoctorRough, HelpingStaffRough, NurseRough, ConsultationRough} from "../../types/other.ts"
import {UserType} from '../../types/user.ts'
import {useAddEmployeeDialog} from "../../composables/addEmployeeDialog.ts";

dayjs.extend(utc)

interface HospitalizationTableData {
  consultationId: string
  hospitalizationId: string
  hospitalizationTime: string
  roomId: string
  bedNumber: string
  dischargeTime: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  hasBegin: string
}

interface HospitalizationFilterForm {
  consultationId: string
  hospitalizationId: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  beginHospitalizationTime: string
  endHospitalizationTime: string
  beginDischargeTime: string
  endDischargeTime: string
  rationButtonString: string
  hasBegin?: boolean
  hasEnd?: boolean
  inquirerId?: string
  isSearchingPatientInfo?: boolean
}

interface HospitalizationToBegin {
  hospitalizationId: string
  hospitalizationReason: string
  roomId: string
  bedNumber: string
  patientId: string
  patientName: string
  beginTime: string
}

interface HospitalizationToEnd {
  hospitalizationId: string
  patientId: string
  patientName: string
  hospitalizationTime: string
  dischargeTime: string
  dischargeReason: string
  consultationRoughArr: ConsultationRough[]
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
const hospitalizationTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: HospitalizationTableData[] = []
const orderedTableData = ref<HospitalizationTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelHospitalizationDialogVisible = ref(false)
const hospitalizationIdToCancel = ref('')
const cancelHospitalizationDialogButtonDisabled = ref(false)
const itemIdToShowDetail = ref('')
const itemTypeToShowDetail = ref<DescribableItem>(DescribableItem.Consultation)

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Hospitalization Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const hospitalizationFilterFormRef = ref<FormInstance>()
const hospitalizationFilterForm = ref<HospitalizationFilterForm>({
  consultationId: '',
  hospitalizationId: '',
  patientId: '',
  patientName: '',
  doctorId: '',
  doctorName: '',
  beginHospitalizationTime: '',
  endHospitalizationTime: '',
  beginDischargeTime: '',
  endDischargeTime: '',
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
const formButtonDisabled = ref(false)

const beginDialogVisible = ref(false)
const hospitalizationIdToBegin = ref('')
const beginDialogButtonDisabled = ref(false)
const beginFormRef = ref<FormInstance>()
const hospitalizationToBegin = ref<HospitalizationToBegin>({
  hospitalizationId: '',
  hospitalizationReason: '',
  patientId: '',
  roomId: '',
  bedNumber: '',
  patientName: '',
  beginTime: '',
})

const recordDialogVisible = ref(false)
const hospitalizationIdToRecord = ref('')
const recordDialogButtonDisabled = ref(false)
const consultationIdOfRecord = ref('')

const endDialogVisible = ref(false)
const hospitalizationIdToEnd = ref('')
const endDialogButtonDisabled = ref(false)
const endFormRef = ref<FormInstance>()
const hospitalizationToEnd = ref<HospitalizationToEnd>({
  hospitalizationId: '',
  patientId: '',
  patientName: '',
  hospitalizationTime: '',
  dischargeTime: '',
  dischargeReason: '',
  consultationRoughArr: [],
  doctorRoughArr: [{doctorId: config.userId, doctorName: config.userName}],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
})
const endFormRules = ref<FormRules<HospitalizationToEnd>>({
  hospitalizationId: [
    {required: true}
  ],
  patientId: [
    {required: true}
  ],
  patientName: [
    {required: true}
  ],
  hospitalizationTime: [
    {required: true}
  ],
  dischargeTime: [
    {required: true}
  ],
  dischargeReason: [
    {required: true, message: 'Please input discharge reason', trigger: 'blur'}
  ],
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
} = useAddEmployeeDialog(hospitalizationToEnd)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...hospitalizationFilterForm.value}
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

  axios.get(rootOfPath + '/get-doctor-hospitalization', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      hospitalizationTableRef.value?.clearSort()
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
    case 'hospitalizationId':
      orderedTableData.value.sort((a, b) => sortHospitalizationId(a.hospitalizationId, b.hospitalizationId, order))
      break
    case 'hospitalizationTime':
      orderedTableData.value.sort((a, b) => sortTime(a.hospitalizationTime, b.hospitalizationTime, order))
      break
    case 'dischargeTime':
      orderedTableData.value.sort((a, b) => sortTime(a.dischargeTime, b.dischargeTime, order))
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

const handleTableCancelHospitalization = (hospitalizationId: string) => {
  cancelHospitalizationDialogButtonDisabled.value = false
  hospitalizationIdToCancel.value = hospitalizationId
  cancelHospitalizationDialogVisible.value = true
}

const handleConfirmCancelHospitalizationButton = () => {
  cancelHospitalizationDialogButtonDisabled.value = true
  cancelHospitalizationDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-hospitalization',
    {
      hospitalizationId: hospitalizationIdToCancel.value,
      doctorId: config.userId
    })
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

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleShowDetailButton = (itemId: string, itemType: DescribableItem) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  itemIdToShowDetail.value = itemId
  itemTypeToShowDetail.value = itemType
  switch (itemType) {
    case DescribableItem.Hospitalization:
      handleChangeDetailDialogTitle('Hospitalization Detail')
      break
    case DescribableItem.Consultation:
      handleChangeDetailDialogTitle('Consultation Detail')
      break
  }
  detailDialogVisible.value = true
}

const handleTableBeginButton = (row: HospitalizationTableData) => {
  hospitalizationIdToBegin.value = row.hospitalizationId
  hospitalizationToBegin.value.hospitalizationId = row.hospitalizationId
  hospitalizationToBegin.value.patientId = row.patientId
  hospitalizationToBegin.value.patientName = row.patientName
  hospitalizationToBegin.value.roomId = row.roomId
  hospitalizationToBegin.value.bedNumber = row.bedNumber
  hospitalizationToBegin.value.beginTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  axios.get(rootOfPath + '/doctor/get-hospitalization-reason', {params: {hospitalizationId: hospitalizationIdToBegin.value}})
    .then((res) => {
      hospitalizationToBegin.value.hospitalizationReason = res.data.results
    })
    .finally(() => {
      beginDialogButtonDisabled.value = false
      beginDialogVisible.value = true
    })
}

const handleTableRecordButton = (row: HospitalizationTableData) => {
  hospitalizationIdToRecord.value = row.hospitalizationId
  consultationIdOfRecord.value = ''
  recordDialogButtonDisabled.value = false
  recordDialogVisible.value = true
}

const handleTableEndButton = (row: HospitalizationTableData) => {
  resetEndForm()
  hospitalizationIdToEnd.value = row.hospitalizationId
  hospitalizationToEnd.value.hospitalizationId = row.hospitalizationId
  hospitalizationToEnd.value.patientId = row.patientId
  hospitalizationToEnd.value.patientName = row.patientName
  hospitalizationToEnd.value.hospitalizationTime = row.hospitalizationTime
  hospitalizationToEnd.value.dischargeTime = dayjs().format('YYYY-MM-DD HH:mm:ss')
  axios.get(rootOfPath + '/doctor/hospitalization/get-hospitalization-record-rough', {
    params: {
      hospitalizationId: hospitalizationIdToEnd.value,
    }
  })
    .then(res => {
      hospitalizationToEnd.value.consultationRoughArr = res.data.results
      endDialogButtonDisabled.value = false
      endDialogVisible.value = true
    })
}

const resetForm = (form: FormInstance | undefined) => {
  if (form) {
    if (form !== hospitalizationFilterFormRef.value) {
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

const resetEndForm = () => {
  resetForm(endFormRef.value)
  hospitalizationToEnd.value.consultationRoughArr = []
  hospitalizationToEnd.value.doctorRoughArr = [{doctorId: config.userId, doctorName: config.userName}]
  hospitalizationToEnd.value.nurseRoughArr = []
  hospitalizationToEnd.value.helpingStaffRoughArr = []
}

const handleBeginDialogConfirm = () => {
  beginDialogButtonDisabled.value = true
  axios.post(rootOfPath + '/doctor/hospitalization/begin', {
    hospitalizationId: hospitalizationIdToBegin.value,
    hospitalizationTime: dayjs(hospitalizationToBegin.value.beginTime).utc().format()
  })
    .then(() => {
      ElMessage.success('Begin hospitalization successfully')
      resetForm(beginFormRef.value)
      beginDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.hospitalizationId !== hospitalizationIdToBegin.value)
      originalTableData = originalTableData.filter((item) => item.hospitalizationId !== hospitalizationIdToBegin.value)
      totalDataNumber.value -= 1
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleRecordDialogConfirm = async () => {
  if (consultationIdOfRecord.value !== '') {
    await router.push('/doctor/record/consultation')
    return
  }
  recordDialogButtonDisabled.value = true
  recordDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/hospitalization/record', {
    hospitalizationId: hospitalizationIdToRecord.value,
  })
    .then((res) => {
      recordDialogButtonDisabled.value = false
      recordDialogVisible.value = true
      consultationIdOfRecord.value = res.data.results.consultationId
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleEndDialogConfirm = async () => {
  endDialogButtonDisabled.value = true
  let formValid = false
  await endFormRef.value?.validate((valid) => {
    formValid = valid
  })
  if (!formValid) {
    endDialogButtonDisabled.value = false
    return
  }
  axios.post(rootOfPath + '/doctor/hospitalization/end', {
    hospitalizationId: hospitalizationIdToEnd.value,
    dischargeTime: dayjs(hospitalizationToEnd.value.dischargeTime).utc().format(),
    dischargeReason: hospitalizationToEnd.value.dischargeReason,
    doctorRoughArr: hospitalizationToEnd.value.doctorRoughArr,
    nurseRoughArr: hospitalizationToEnd.value.nurseRoughArr,
    helpingStaffRoughArr: hospitalizationToEnd.value.helpingStaffRoughArr
  })
    .then(() => {
      ElMessage.success('End hospitalization successfully')
      resetEndForm()
      endDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.hospitalizationId !== hospitalizationIdToEnd.value)
      originalTableData = originalTableData.filter((item) => item.hospitalizationId !== hospitalizationIdToEnd.value)
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
  resetForm(hospitalizationFilterFormRef.value)
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
    v-model="cancelHospitalizationDialogVisible"
    title="Cancel Hospitalization"
  >
    <span>Are you sure to cancel hospitalization with ID <el-text tag="b">{{
        hospitalizationIdToCancel
      }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelHospitalizationDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelHospitalizationButton"
        :disabled="cancelHospitalizationDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="beginDialogVisible"
    title="Begin Hospitalization"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="beginFormRef"
            :model="hospitalizationToBegin"
            label-position="top"
          >
            <el-form-item label="Hospitalization ID" prop="hospitalizationId">
              <el-input v-model="hospitalizationToBegin.hospitalizationId" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="hospitalizationToBegin.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="hospitalizationToBegin.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Begin Time" prop="hospitalizationTime">
              <el-input v-model="hospitalizationToBegin.beginTime" disabled/>
            </el-form-item>

            <el-form-item label="Room ID" prop="roomId">
              <el-input v-model="hospitalizationToBegin.roomId" disabled/>
            </el-form-item>

            <el-form-item label="Bed Number" prop="bedNumber">
              <el-input v-model="hospitalizationToBegin.bedNumber" disabled/>
            </el-form-item>

            <el-form-item label="Hospitalization Reason" prop="hospitalizationReason">
              <el-input v-model="hospitalizationToBegin.hospitalizationReason" type="textarea" autosize disabled/>
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
    :title="consultationIdOfRecord === ''?'Record Hospitalization':'Success'"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div v-if="consultationIdOfRecord === ''">
      <span>Are you sure to add an consultation related to this hospitalization record?</span>
    </div>
    <div v-else>
      <span>Success. The consultation ID is <el-text tag="b">{{ consultationIdOfRecord }}</el-text>. </span>
      <span>Go the the consultation page to add detail record.</span>
    </div>
    <template #footer>
      <el-button @click="recordDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleRecordDialogConfirm"
        :disabled="recordDialogButtonDisabled"
      >
        <div v-if="consultationIdOfRecord === ''">
          Confirm
        </div>
        <div v-else>
          Go To Consultation
        </div>
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="endDialogVisible"
    title="End Hospitalization"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="endFormRef"
            :model="hospitalizationToEnd"
            :rules="endFormRules"
            label-position="top"
          >
            <el-form-item label="Hospitalization ID" prop="hospitalizationId">
              <el-input v-model="hospitalizationToEnd.hospitalizationId" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="hospitalizationToEnd.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="hospitalizationToEnd.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Hospitalization Time" prop="hospitalizationTime">
              <el-input v-model="hospitalizationToEnd.hospitalizationTime" disabled/>
            </el-form-item>

            <el-form-item label="Discharge Time" prop="dischargeTime">
              <el-input v-model="hospitalizationToEnd.dischargeTime" disabled/>
            </el-form-item>

            <el-form-item label="Discharge Reason" prop="dischargeReason">
              <el-input v-model="hospitalizationToEnd.dischargeReason" type="textarea" autosize/>
            </el-form-item>

            <el-form-item label="Related Consultation Record" prop="hospitalizationRecord">
              <el-table
                :data="hospitalizationToEnd.consultationRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Consultation ID" prop="consultationId" align="center"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button size="small" plain type="primary"
                               @click="handleShowDetailButton(scope.row.consultationId, DescribableItem.Consultation)">
                      Show Detail
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <template v-if="false">
              <el-form-item>
                <template #label>
                  Related Doctor
                  <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.Doctor)" plain>Add
                  </el-button>
                </template>
                <el-table
                  :data="hospitalizationToEnd.doctorRoughArr"
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
                  :data="hospitalizationToEnd.nurseRoughArr"
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
                  :data="hospitalizationToEnd.helpingStaffRoughArr"
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
            </template>
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
          ref="hospitalizationFilterFormRef"
          :model="hospitalizationFilterForm"
          label-position="top"
        >
          <el-form-item
            label="Type"
            prop="rationButtonString"
            v-if="isRecord"
          >
            <el-radio-group v-model="hospitalizationFilterForm.rationButtonString">
              <el-radio label="Not yet begin"/>
              <el-radio label="Already begin"/>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Hospitalization ID" prop="hospitalizationId">
            <el-input v-model="hospitalizationFilterForm.hospitalizationId" placeholder="Enter the hospitalization ID"/>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="hospitalizationFilterForm.patientId"
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
              v-model="hospitalizationFilterForm.patientName"
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

          <el-form-item label="Attending Doctor ID" prop="doctorId" v-if="isSearchDoctorInfo">
            <el-select
              v-model="hospitalizationFilterForm.doctorId"
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

          <el-form-item label="Attending Doctor Name" prop="doctorName" v-if="isSearchDoctorInfo">
            <el-select
              v-model="hospitalizationFilterForm.doctorName"
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

          <el-form-item label="Hospitalization Time">
            <el-col :span="11">
              <el-form-item prop="beginHospitalizationTime">
                <el-date-picker
                  v-model="hospitalizationFilterForm.beginHospitalizationTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endHospitalizationTime">
                <el-date-picker
                  v-model="hospitalizationFilterForm.endHospitalizationTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Discharge Time" v-if="isSearchPatientInfo||isSearchDoctorInfo">
            <el-col :span="11">
              <el-form-item prop="beginDischargeTime">
                <el-date-picker
                  v-model="hospitalizationFilterForm.beginDischargeTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endDischargeTime">
                <el-date-picker
                  v-model="hospitalizationFilterForm.endDischargeTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId" v-if="isSearchPatientInfo">
            <el-input v-model="hospitalizationFilterForm.consultationId" placeholder="Enter the consultation ID"/>
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
              @click="resetForm(hospitalizationFilterFormRef)"
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
        ref="hospitalizationTableRef"
      >
        <el-table-column label="Hospitalization ID" prop="hospitalizationId" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Hospitalization Time" prop="hospitalizationTime" sortable/>
        <el-table-column label="Discharge Time" prop="dischargeTime" sortable
                         v-if="isSearchDoctorInfo || isSearchPatientInfo"/>
        <el-table-column label="Attending Doctor ID" prop="doctorId" sortable v-if="isSearchDoctorInfo"/>
        <el-table-column label="Attending Doctor Name" prop="doctorName" sortable
                         v-if="isSearchDoctorInfo||isSearchPatientInfo"/>
        <el-table-column label="Related Consultation ID" prop="consultationId" sortable v-if="isSearchPatientInfo"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleShowDetailButton(scope.row.hospitalizationId, DescribableItem.Hospitalization)"
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
              @click="handleTableCancelHospitalization(scope.row.hospitalizationId)"
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