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
import {sortDoctorId, sortExaminationId, sortName, sortPatientId, sortTime} from "../../utils/sort.ts"
import {
  examinationNameRemoteMethod,
  patientIdRemoteMethod,
  patientNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod,
} from "../../utils/remote.ts"
import {DescribableItem, DoctorRough, HelpingStaffRough, NurseRough} from "../../types/other.ts"
import {UserType} from '../../types/user.ts'
import {useAddEmployeeDialog} from "../../composables/addEmployeeDialog.ts";

dayjs.extend(utc)

interface ExaminationTableData {
  consultationId: string
  examinationId: string
  examinationName: string
  examinationTime: string
  resultTime: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  hasConducted: string
}

interface ExaminationFilterForm {
  consultationId: string
  examinationId: string
  examinationName: string
  patientId: string
  patientName: string
  doctorId: string
  doctorName: string
  beginExaminationTime: string
  endExaminationTime: string
  beginResultTime: string
  endResultTime: string
  rationButtonString: string
  hasConducted?: boolean
  hasResult?: boolean
  inquirerId?: string
  isSearchingPatientInfo?: boolean
}

interface ExaminationToConduct {
  examinationId: string
  examinationName: string
  patientId: string
  patientName: string
  examinationTime: string
}

interface ExaminationToRecord {
  examinationId: string
  examinationName: string
  patientId: string
  patientName: string
  result: string
  examinationTime: string
  resultTime: string
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
const isTableDataConducted = ref(false)

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
  consultationId: '',
  examinationId: '',
  examinationName: '',
  patientId: '',
  patientName: '',
  doctorId: '',
  doctorName: '',
  beginExaminationTime: '',
  endExaminationTime: '',
  beginResultTime: '',
  endResultTime: '',
  rationButtonString: 'Not yet conducted',  // another is Already conducted
})
const doctorIdOptions = ref<string[]>([])
const doctorIdLoading = ref(false)
const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const patientIdOptions = ref<string[]>([])
const patientIdLoading = ref(false)
const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const examinationNameOptions = ref<string[]>([])
const examinationNameLoading = ref(false)
const formButtonDisabled = ref(false)

const conductDialogVisible = ref(false)
const examinationIdToConduct = ref('')
const conductDialogButtonDisabled = ref(false)
const conductFormRef = ref<FormInstance>()
const examinationToConduct = ref<ExaminationToConduct>({
  examinationId: '',
  examinationName: '',
  patientId: '',
  patientName: '',
  examinationTime: '',
})

const recordDialogVisible = ref(false)
const examinationIdToRecord = ref('')
const recordDialogButtonDisabled = ref(false)
const recordFormRef = ref<FormInstance>()
const examinationToRecord = ref<ExaminationToRecord>({
  examinationId: '',
  examinationName: '',
  patientId: '',
  patientName: '',
  result: '',
  examinationTime: '',
  resultTime: '',
  doctorRoughArr: [{doctorId: config.userId, doctorName: config.userName}],
  nurseRoughArr: [],
  helpingStaffRoughArr: [],
})
const recordFormRules = ref<FormRules<ExaminationToRecord>>({
  examinationId: [
    {required: true}
  ],
  examinationName: [
    {required: true}
  ],
  patientId: [
    {required: true}
  ],
  patientName: [
    {required: true}
  ],
  examinationTime: [
    {required: true}
  ],
  resultTime: [
    {required: true}
  ],
  result: [
    {required: true, message: 'Please input the result', trigger: 'change'}
  ]
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
} = useAddEmployeeDialog(examinationToRecord)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...examinationFilterForm.value}

  submitValue.inquirerId = config.userId
  if (isSearchPatientInfo.value || isSearchDoctorInfo.value) {
    delete submitValue.hasConducted
    delete submitValue.hasResult
    submitValue.isSearchingPatientInfo = router.currentRoute.value.path.includes('patient-information')
  } else {
    console.assert(submitValue.rationButtonString === 'Not yet conducted' || submitValue.rationButtonString === 'Already conducted')
    submitValue.hasResult = false
    isTableDataConducted.value = submitValue.hasConducted = submitValue.rationButtonString !== 'Not yet conducted'
    submitValue.doctorId = config.userId
    submitValue.doctorName = ''
  }

  axios.get(rootOfPath + '/get-doctor-examination', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      examinationTableRef.value?.clearSort()
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
    case 'examinationId':
      orderedTableData.value.sort((a, b) => sortExaminationId(a.examinationId, b.examinationId, order))
      break
    case 'examinationName':
      orderedTableData.value.sort((a, b) => sortName(a.examinationName, b.examinationName, order))
      break
    case 'examinationTime':
      orderedTableData.value.sort((a, b) => sortTime(a.examinationTime, b.examinationTime, order))
      break
    case 'resultTime':
      orderedTableData.value.sort((a, b) => sortTime(a.resultTime, b.resultTime, order))
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

const handleTableCancelExamination = (examinationId: string) => {
  cancelExaminationDialogButtonDisabled.value = false
  examinationIdToCancel.value = examinationId
  cancelExaminationDialogVisible.value = true
}

const handleConfirmCancelExaminationButton = () => {
  cancelExaminationDialogButtonDisabled.value = true
  cancelExaminationDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-examination',
    {
      examinationId: examinationIdToCancel.value,
      doctorId: config.userId
    })
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

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: ExaminationTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  examinationIdToShowDetail.value = row.examinationId
  handleChangeDetailDialogTitle('Examination Detail')
  detailDialogVisible.value = true
}

const handleTableConductButton = (row: ExaminationTableData) => {
  examinationIdToConduct.value = row.examinationId
  examinationToConduct.value.examinationId = row.examinationId
  examinationToConduct.value.examinationName = row.examinationName
  examinationToConduct.value.patientId = row.patientId
  examinationToConduct.value.patientName = row.patientName
  examinationToConduct.value.examinationTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  conductDialogButtonDisabled.value = false
  conductDialogVisible.value = true
}

const handleTableRecordButton = (row: ExaminationTableData) => {
  resetRecordForm()
  examinationIdToRecord.value = row.examinationId
  examinationToRecord.value.examinationId = row.examinationId
  examinationToRecord.value.examinationName = row.examinationName
  examinationToRecord.value.patientId = row.patientId
  examinationToRecord.value.patientName = row.patientName
  examinationToRecord.value.examinationTime = row.examinationTime
  examinationToRecord.value.resultTime = dayjs().format('YYYY-MM-DD HH:mm:ss')

  recordDialogButtonDisabled.value = false
  recordDialogVisible.value = true
}

const resetForm = (form: FormInstance | undefined) => {
  if (form) {
    if (form !== examinationFilterFormRef.value) {
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
const _examinationNameRemoteMethod = (query: string) => {
  examinationNameRemoteMethod(query, examinationNameOptions, examinationNameLoading)
}


const resetRecordForm = () => {
  resetForm(recordFormRef.value)
  examinationToRecord.value.result = ''
  examinationToRecord.value.doctorRoughArr = [{doctorId: config.userId, doctorName: config.userName}]
  examinationToRecord.value.nurseRoughArr = []
  examinationToRecord.value.helpingStaffRoughArr = []
}

const handleConductDialogConfirm = () => {
  conductDialogButtonDisabled.value = true
  axios.post(rootOfPath + '/doctor/examination/conduct', {
    examinationId: examinationIdToConduct.value,
    examinationTime: dayjs(examinationToConduct.value.examinationTime).utc().format()
  })
    .then(() => {
      ElMessage.success('Conduct examination successfully')
      resetForm(conductFormRef.value)
      conductDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.examinationId !== examinationIdToConduct.value)
      originalTableData = originalTableData.filter((item) => item.examinationId !== examinationIdToConduct.value)
      totalDataNumber.value -= 1
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleRecordDialogConfirm = async () => {
  recordDialogButtonDisabled.value = true
  let formValid = false
  await recordFormRef.value?.validate((valid) => {
    formValid = valid
  })
  if (!formValid) {
    recordDialogButtonDisabled.value = false
    return
  }
  axios.post(rootOfPath + '/doctor/examination/record', {
    examinationId: examinationIdToRecord.value,
    result: examinationToRecord.value.result,
    resultTime: dayjs(examinationToRecord.value.resultTime).utc().format(),
    doctorRoughArr: examinationToRecord.value.doctorRoughArr,
    nurseRoughArr: examinationToRecord.value.nurseRoughArr,
    helpingStaffRoughArr: examinationToRecord.value.helpingStaffRoughArr
  })
    .then(() => {
      ElMessage.success('Record examination successfully')
      resetRecordForm()
      recordDialogVisible.value = false
      orderedTableData.value = orderedTableData.value.filter((item) => item.examinationId !== examinationIdToRecord.value)
      originalTableData = originalTableData.filter((item) => item.examinationId !== examinationIdToRecord.value)
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
  resetForm(examinationFilterFormRef.value)
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
    v-model="cancelExaminationDialogVisible"
    title="Cancel Examination"
  >
    <span>Are you sure to cancel examination with ID <el-text tag="b">{{ examinationIdToCancel }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelExaminationDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelExaminationButton"
        :disabled="cancelExaminationDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="conductDialogVisible"
    title="Conduct Examination"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="conductFormRef"
            :model="examinationToConduct"
            label-position="top"
          >
            <el-form-item label="Examination ID" prop="examinationId">
              <el-input v-model="examinationToConduct.examinationId" disabled/>
            </el-form-item>

            <el-form-item label="Examination Name" prop="examinationName">
              <el-input v-model="examinationToConduct.examinationName" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="examinationToConduct.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="examinationToConduct.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Conduct Time" prop="examinationTime">
              <el-input v-model="examinationToConduct.examinationTime" disabled/>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="conductDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConductDialogConfirm"
        :disabled="conductDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="recordDialogVisible"
    title="Record Examination"
    :width="config.recordDialogWidth"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="recordFormRef"
            :model="examinationToRecord"
            :rules="recordFormRules"
            label-position="top"
          >
            <el-form-item label="Examination ID" prop="examinationId">
              <el-input v-model="examinationToRecord.examinationId" disabled/>
            </el-form-item>

            <el-form-item label="Examination Name" prop="examinationName">
              <el-input v-model="examinationToRecord.examinationName" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="examinationToRecord.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="examinationToRecord.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Examination Time" prop="examinationTime">
              <el-input v-model="examinationToRecord.examinationTime" disabled/>
            </el-form-item>

            <el-form-item label="Result Time" prop="resultTime">
              <el-input v-model="examinationToRecord.resultTime" disabled/>
            </el-form-item>

            <el-form-item label="Result" prop="result">
              <el-input
                type="textarea"
                v-model="examinationToRecord.result"
                placeholder="Enter result"
                autosize
              />
            </el-form-item>

            <el-form-item>
              <template #label>
                Related Doctor
                <el-button type="primary" size="small" @click="handleAddEmployeeButton(UserType.Doctor)" plain>Add
                </el-button>
              </template>
              <el-table
                :data="examinationToRecord.doctorRoughArr"
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
                :data="examinationToRecord.nurseRoughArr"
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
                :data="examinationToRecord.helpingStaffRoughArr"
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
      <el-button @click="recordDialogVisible=false">Cancel</el-button>
      <el-button
        type="primary"
        :disabled="recordDialogButtonDisabled"
        @click="handleRecordDialogConfirm"
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
          ref="examinationFilterFormRef"
          :model="examinationFilterForm"
          label-position="top"
        >
          <el-form-item
            label="Type"
            prop="rationButtonString"
            v-if="isRecord"
          >
            <el-radio-group v-model="examinationFilterForm.rationButtonString">
              <el-radio label="Not yet conducted">Not yet conducted</el-radio>
              <el-radio label="Already conducted">Already conducted</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Examination ID" prop="examinationId">
            <el-input v-model="examinationFilterForm.examinationId" placeholder="Enter the examination ID"/>
          </el-form-item>

          <el-form-item label="Examination Name" prop="examinationName">
            <el-select
              v-model="examinationFilterForm.examinationName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_examinationNameRemoteMethod"
              :loading="examinationNameLoading"
              placeholder="Enter the examination name"
              style="width: 100%"
            >
              <el-option
                v-for="item in examinationNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="examinationFilterForm.patientId"
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
              v-model="examinationFilterForm.patientName"
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
              v-model="examinationFilterForm.doctorId"
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
              v-model="examinationFilterForm.doctorName"
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

          <el-form-item label="Examination Time">
            <el-col :span="11">
              <el-form-item prop="beginExaminationTime">
                <el-date-picker
                  v-model="examinationFilterForm.beginExaminationTime"
                  type="datetime"
                  placeholder="Select date and time"
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
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Result Time" v-if="isSearchPatientInfo||isSearchDoctorInfo">
            <el-col :span="11">
              <el-form-item prop="beginResultTime">
                <el-date-picker
                  v-model="examinationFilterForm.beginResultTime"
                  type="datetime"
                  placeholder="Select date and time"
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
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Related Consultation ID" prop="consultationId" v-if="isSearchPatientInfo">
            <el-input v-model="examinationFilterForm.consultationId" placeholder="Enter the consultation ID"/>
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
              @click="resetForm(examinationFilterFormRef)"
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
        ref="examinationTableRef"
      >
        <el-table-column label="Examination ID" prop="examinationId" sortable/>
        <el-table-column label="Examination Name" prop="examinationName" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Examination Time" prop="examinationTime" sortable/>
        <el-table-column label="Result Time" prop="resultTime" sortable v-if="isSearchDoctorInfo || isSearchPatientInfo"/>
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
              v-if="isRecord&&!isTableDataConducted"
              @click="handleTableConductButton(scope.row)"
            >Conduct
            </el-button>
            <el-button
              type="primary"
              size="small"
              v-if="isRecord&&isTableDataConducted"
              @click="handleTableRecordButton(scope.row)"
            >Record
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleTableCancelExamination(scope.row.examinationId)"
              :disabled="scope.row.hasConducted==='true'"
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