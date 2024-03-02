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
import {
  sortDoctorId,
  sortRehabilitationId,
  sortName,
  sortPatientId,
  sortTime,
} from "../../utils/sort.ts"
import {
  rehabilitationNameRemoteMethod,
  patientIdRemoteMethod,
  patientNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod,
} from "../../utils/remote.ts"
import {DescribableItem, DoctorRough, HelpingStaffRough, NurseRough} from "../../types/other.ts"
import {UserType} from '../../types/user.ts'
import {useAddEmployeeDialog} from "../../composables/addEmployeeDialog.ts";

dayjs.extend(utc)

interface RehabilitationTableData {
  consultationId: string
  rehabilitationId: string
  rehabilitationName: string
  beginTime: string
  endTime: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  hasBegin: string
}

interface RehabilitationFilterForm {
  consultationId: string
  rehabilitationId: string
  rehabilitationName: string
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

interface RehabilitationToBegin {
  rehabilitationId: string
  rehabilitationName: string
  patientId: string
  patientName: string
  beginTime: string
}

interface RehabilitationToEnd {
  rehabilitationId: string
  rehabilitationName: string
  patientId: string
  patientName: string
  beginTime: string
  endTime: string
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
  consultationId: '',
  rehabilitationId: '',
  rehabilitationName: '',
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
const rehabilitationNameOptions = ref<string[]>([])
const rehabilitationNameLoading = ref(false)
const formButtonDisabled = ref(false)

const beginDialogVisible = ref(false)
const rehabilitationIdToBegin = ref('')
const beginDialogButtonDisabled = ref(false)
const beginFormRef = ref<FormInstance>()
const rehabilitationToBegin = ref<RehabilitationToBegin>({
  rehabilitationId: '',
  rehabilitationName: '',
  patientId: '',
  patientName: '',
  beginTime: '',
})

const endDialogVisible = ref(false)
const rehabilitationIdToEnd = ref('')
const endDialogButtonDisabled = ref(false)
const endFormRef = ref<FormInstance>()
const rehabilitationToEnd = ref<RehabilitationToEnd>({
  rehabilitationId: '',
  rehabilitationName: '',
  patientId: '',
  patientName: '',
  beginTime: '',
  endTime: '',
  doctorRoughArr: [{doctorId: config.userId, doctorName: config.userName}],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
})
const endFormRules = ref<FormRules<RehabilitationToEnd>>({
  rehabilitationId: [
    {required: true}
  ],
  rehabilitationName: [
    {required: true}
  ],
  patientId: [
    {required: true}
  ],
  patientName: [
    {required: true}
  ],
  beginTime: [
    {required: true}
  ],
  endTime: [
    {required: true}
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
} = useAddEmployeeDialog(rehabilitationToEnd)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...rehabilitationFilterForm.value}
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

  axios.get(rootOfPath + '/get-doctor-rehabilitation', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      rehabilitationTableRef.value?.clearSort()
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
    case 'rehabilitationId':
      orderedTableData.value.sort((a, b) => sortRehabilitationId(a.rehabilitationId, b.rehabilitationId, order))
      break
    case 'rehabilitationName':
      orderedTableData.value.sort((a, b) => sortName(a.rehabilitationName, b.rehabilitationName, order))
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

const handleTableCancelRehabilitation = (rehabilitationId: string) => {
  cancelRehabilitationDialogButtonDisabled.value = false
  rehabilitationIdToCancel.value = rehabilitationId
  cancelRehabilitationDialogVisible.value = true
}

const handleConfirmCancelRehabilitationButton = () => {
  cancelRehabilitationDialogButtonDisabled.value = true
  cancelRehabilitationDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-rehabilitation',
    {
      rehabilitationId: rehabilitationIdToCancel.value,
      doctorId: config.userId
    })
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

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: RehabilitationTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  rehabilitationIdToShowDetail.value = row.rehabilitationId
  handleChangeDetailDialogTitle('Rehabilitation Detail')
  detailDialogVisible.value = true
}

const handleTableBeginButton = (row: RehabilitationTableData) => {
  rehabilitationIdToBegin.value = row.rehabilitationId
  rehabilitationToBegin.value.rehabilitationId = row.rehabilitationId
  rehabilitationToBegin.value.rehabilitationName = row.rehabilitationName
  rehabilitationToBegin.value.patientId = row.patientId
  rehabilitationToBegin.value.patientName = row.patientName
  rehabilitationToBegin.value.beginTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  beginDialogButtonDisabled.value = false
  beginDialogVisible.value = true
}

const handleTableEndButton = (row: RehabilitationTableData) => {
  resetEndForm()
  rehabilitationIdToEnd.value = row.rehabilitationId
  rehabilitationToEnd.value.rehabilitationId = row.rehabilitationId
  rehabilitationToEnd.value.rehabilitationName = row.rehabilitationName
  rehabilitationToEnd.value.patientId = row.patientId
  rehabilitationToEnd.value.patientName = row.patientName
  rehabilitationToEnd.value.beginTime = row.beginTime
  rehabilitationToEnd.value.endTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  endDialogButtonDisabled.value = false
  endDialogVisible.value = true
}

const resetForm = (form: FormInstance | undefined) => {
  if (form) {
    if (form !== rehabilitationFilterFormRef.value) {
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
const _rehabilitationNameRemoteMethod = (query: string) => {
  rehabilitationNameRemoteMethod(query, rehabilitationNameOptions, rehabilitationNameLoading)
}

const resetEndForm = () => {
  resetForm(endFormRef.value)
  rehabilitationToEnd.value.doctorRoughArr = [{doctorId: config.userId, doctorName: config.userName}]
  rehabilitationToEnd.value.nurseRoughArr = []
  rehabilitationToEnd.value.helpingStaffRoughArr = []
}

const handleBeginDialogConfirm = () => {
  beginDialogButtonDisabled.value = true
  axios.post(rootOfPath + '/doctor/rehabilitation/begin', {
    rehabilitationId: rehabilitationIdToBegin.value,
    rehabilitationTime: dayjs(rehabilitationToBegin.value.beginTime).utc().format()
  })
    .then(() => {
      ElMessage.success('Begin rehabilitation successfully')
      resetForm(beginFormRef.value)
      beginDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.rehabilitationId !== rehabilitationIdToBegin.value)
      originalTableData = originalTableData.filter((item) => item.rehabilitationId !== rehabilitationIdToBegin.value)
      totalDataNumber.value -= 1
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
  axios.post(rootOfPath + '/doctor/rehabilitation/end', {
    rehabilitationId: rehabilitationIdToEnd.value,
    endTime: dayjs(rehabilitationToEnd.value.endTime).utc().format(),
    doctorRoughArr: rehabilitationToEnd.value.doctorRoughArr,
    nurseRoughArr: rehabilitationToEnd.value.nurseRoughArr,
    helpingStaffRoughArr: rehabilitationToEnd.value.helpingStaffRoughArr
  })
    .then(() => {
      ElMessage.success('End rehabilitation successfully')
      resetEndForm()
      endDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.rehabilitationId !== rehabilitationIdToEnd.value)
      originalTableData = originalTableData.filter((item) => item.rehabilitationId !== rehabilitationIdToEnd.value)
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
  resetForm(rehabilitationFilterFormRef.value)
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
    v-model="cancelRehabilitationDialogVisible"
    title="Cancel Rehabilitation"
  >
    <span>Are you sure to cancel rehabilitation with ID <el-text tag="b">{{ rehabilitationIdToCancel }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelRehabilitationDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelRehabilitationButton"
        :disabled="cancelRehabilitationDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="beginDialogVisible"
    title="Begin Rehabilitation"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="beginFormRef"
            :model="rehabilitationToBegin"
            label-position="top"
          >
            <el-form-item label="Rehabilitation ID" prop="rehabilitationId">
              <el-input v-model="rehabilitationToBegin.rehabilitationId" disabled/>
            </el-form-item>

            <el-form-item label="Rehabilitation Name" prop="rehabilitationName">
              <el-input v-model="rehabilitationToBegin.rehabilitationName" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="rehabilitationToBegin.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="rehabilitationToBegin.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Begin Time" prop="rehabilitationTime">
              <el-input v-model="rehabilitationToBegin.beginTime" disabled/>
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
    v-model="endDialogVisible"
    title="End Rehabilitation"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="endFormRef"
            :model="rehabilitationToEnd"
            :rules="endFormRules"
            label-position="top"
          >
            <el-form-item label="Rehabilitation ID" prop="rehabilitationId">
              <el-input v-model="rehabilitationToEnd.rehabilitationId" disabled/>
            </el-form-item>

            <el-form-item label="Rehabilitation Name" prop="rehabilitationName">
              <el-input v-model="rehabilitationToEnd.rehabilitationName" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="rehabilitationToEnd.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="rehabilitationToEnd.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Begin Time" prop="beginTime">
              <el-input v-model="rehabilitationToEnd.beginTime" disabled/>
            </el-form-item>

            <el-form-item label="End Time" prop="endTime">
              <el-input v-model="rehabilitationToEnd.endTime" disabled/>
            </el-form-item>
            
            <el-form-item>
              <template #label>
                Related Doctor
                <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.Doctor)" plain>Add
                </el-button>
              </template>
              <el-table
                :data="rehabilitationToEnd.doctorRoughArr"
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
                :data="rehabilitationToEnd.nurseRoughArr"
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
                :data="rehabilitationToEnd.helpingStaffRoughArr"
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
          ref="rehabilitationFilterFormRef"
          :model="rehabilitationFilterForm"
          label-position="top"
        >
          <el-form-item
            label="Type"
            prop="rationButtonString"
            v-if="isRecord"
          >
            <el-radio-group v-model="rehabilitationFilterForm.rationButtonString">
              <el-radio label="Not yet begin"/>
              <el-radio label="Already begin"/>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Rehabilitation ID" prop="rehabilitationId">
            <el-input v-model="rehabilitationFilterForm.rehabilitationId" placeholder="Enter the rehabilitation ID"/>
          </el-form-item>

          <el-form-item label="Rehabilitation Name" prop="rehabilitationName">
            <el-select
              v-model="rehabilitationFilterForm.rehabilitationName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_rehabilitationNameRemoteMethod"
              :loading="rehabilitationNameLoading"
              placeholder="Enter the rehabilitation name"
              style="width: 100%"
            >
              <el-option
                v-for="item in rehabilitationNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="rehabilitationFilterForm.patientId"
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
              v-model="rehabilitationFilterForm.patientName"
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
              v-model="rehabilitationFilterForm.doctorId"
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
              v-model="rehabilitationFilterForm.doctorName"
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
                  v-model="rehabilitationFilterForm.beginTime1"
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
                  v-model="rehabilitationFilterForm.endTime1"
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
                  v-model="rehabilitationFilterForm.beginTime2"
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
                  v-model="rehabilitationFilterForm.endTime2"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId" v-if="isSearchPatientInfo">
            <el-input v-model="rehabilitationFilterForm.consultationId" placeholder="Enter the consultation ID"/>
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
              @click="resetForm(rehabilitationFilterFormRef)"
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
        ref="rehabilitationTableRef"
      >
        <el-table-column label="Rehabilitation ID" prop="rehabilitationId" sortable/>
        <el-table-column label="Rehabilitation Name" prop="rehabilitationName" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Begin Time" prop="beginTime" sortable/>
        <el-table-column label="End Time" prop="endTime" sortable v-if="isSearchDoctorInfo || isSearchPatientInfo"/>
        <el-table-column label="Doctor ID" prop="doctorId" sortable v-if="isSearchDoctorInfo"/>
        <el-table-column label="Doctor Name" prop="doctorName" sortable v-if="isSearchDoctorInfo||isSearchPatientInfo"/>
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
              v-if="isRecord&&!isTableDataBegin"
              @click="handleTableBeginButton(scope.row)"
            >Begin
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
              @click="handleTableCancelRehabilitation(scope.row.rehabilitationId)"
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