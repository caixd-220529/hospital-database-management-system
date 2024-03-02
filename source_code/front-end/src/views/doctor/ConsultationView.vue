<script setup lang="ts">
import {useRouter} from 'vue-router'
import {computed, onMounted, ref, watch} from 'vue'
import {ElCollapseTransition, ElMessage, type FormInstance, type FormRules, type TableInstance} from 'element-plus'
import axios from 'axios';
import dayjs from "dayjs"
import utc from 'dayjs/plugin/utc'
import {useConfigStore} from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import {useDescriptionBoxHistoryArrStore} from '../../stores/descriptionBoxHistoryArr'
import {sortConsultationId, sortDepartment, sortDoctorId, sortName, sortPatientId, sortTime} from '../../utils/sort'
import {
  departmentRemoteMethod,
  examinationNameRemoteMethod,
  medicineInfoRemoteMethod,
  patientIdRemoteMethod,
  patientNameRemoteMethod,
  rehabilitationNameRemoteMethod,
  subordinateNameAndInquirerIdRemoteMethod,
  subordinateNameAndInquirerNameRemoteMethod,
  surgeryNameRemoteMethod,
  surgerySiteRemoteMethod,
  roomTypeRemoteMethod,
} from "../../utils/remote.ts"
import {
  DescribableItem,
  ExaminationRough,
  HospitalizationRough,
  PrescriptionRough,
  RehabilitationRough,
  SurgeryRough
} from "../../types/other"

dayjs.extend(utc)

interface ConsultationTableData {
  consultationId: string
  time: string
  patientId: string
  patientName: string
  department: string
  doctorId: string
  doctorName: string
  hasStarted: string
}

interface ConsultationFilterForm {
  consultationId: string
  patientId: string
  patientName: string
  department: string
  doctorId: string
  doctorName: string
  beginTime: string
  endTime: string
  inquirerId?: string
  hasStarted?: boolean
  isSearchingPatientInfo?: boolean
}

interface MedicineInfo {
  medicineId: string
  medicineName: string
}

interface MedicineForm {
  medicineId: string
  medicineName: string  // actually store the ID of medicine, but show the name of medicine
  courseOfMedication: string
  dosage: string
  frequency: string
  quantity: string
}

interface PrescriptionForm {
  prescriptionId: string
  medicineFormArr: MedicineForm[]
}

interface ExaminationForm {
  examinationName: string
  examinationDate: string
  examinationTime: string
}

interface ExaminationTimeInfo {
  examinationTime: string
  isAvailable: string
}

interface RehabilitationForm {
  rehabilitationName: string
  beginDate: string
  beginTime: string
}

interface RehabilitationTimeInfo {
  beginTime: string
  isAvailable: string
}

interface SurgeryForm {
  surgerySite: string
  surgeryName: string
  surgeryType: string
  surgeryDescription: string
  beginDate: string
  beginTime: string
}

interface SurgeryTimeInfo {
  beginTime: string
  isAvailable: string
}

interface HospitalizationForm {
  roomType: string
  hospitalizationDate: string
  hospitalizationTime: string
  hospitalizationReason: string
}

interface HospitalizationTimeInfo {
  hospitalizationTime: string
  isAvailable: string
}

interface ConsultationToRecord {
  consultationId: string
  patientId: string
  patientName: string
  time: string
  selfReport: string
  medicalHistory: string
  medicationHistory: string
  medicalAdvice: string
  prescriptionRoughArr: PrescriptionRough[]
  examinationRoughArr: ExaminationRough[]
  rehabilitationRoughArr: RehabilitationRough[]
  surgeryRoughArr: SurgeryRough[]
  hospitalizationRoughArr: HospitalizationRough[]
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
const consultationTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: ConsultationTableData[] = []
const orderedTableData = ref<ConsultationTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelConsultationDialogVisible = ref(false)
const consultationIdToCancel = ref('')
const cancelConsultationDialogButtonDisabled = ref(false)
const itemIdToShowDetail = ref('')
const itemTypeToShowDetail = ref<DescribableItem>(DescribableItem.Consultation)

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Consultation Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const consultationFilterFormRef = ref<FormInstance>()
const consultationFilterForm = ref<ConsultationFilterForm>({
  consultationId: '',
  patientId: '',
  patientName: '',
  department: '',
  doctorId: '',
  doctorName: '',
  beginTime: '',
  endTime: '',
  inquirerId: ''
})
const doctorIdOptions = ref<string[]>([])
const doctorIdLoading = ref(false)
const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const patientIdOptions = ref<string[]>([])
const patientIdLoading = ref(false)
const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const departmentOptions = ref<string[]>([])
const departmentLoading = ref(false)
const formButtonDisabled = ref(false)

const recordDialogVisible = ref(false)
const consultationIdToRecord = ref('')
const recordDialogButtonDisabled = ref(false)
const recordFormRef = ref<FormInstance>()
const consultationToRecord = ref<ConsultationToRecord>({
  consultationId: '',
  patientId: '',
  patientName: '',
  time: '',
  selfReport: '',
  medicalHistory: '',
  medicationHistory: '',
  medicalAdvice: '',
  prescriptionRoughArr: [],
  examinationRoughArr: [],
  rehabilitationRoughArr: [],
  surgeryRoughArr: [],
  hospitalizationRoughArr: []
})
const recordFormRules = ref<FormRules<ConsultationToRecord>>({
  consultationId: [
    {required: true}
  ],
  patientId: [
    {required: true}
  ],
  patientName: [
    {required: true}
  ],
  time: [
    {required: true}
  ],
  selfReport: [
    {required: true, message: 'Please enter self report', trigger: 'change'}
  ],
  medicalHistory: [
    {required: true, message: 'Please enter medical history', trigger: 'change'}
  ],
  medicationHistory: [
    {required: true, message: 'Please enter medication history', trigger: 'change'}
  ],
  medicalAdvice: [
    {required: true, message: 'Please enter medical advice', trigger: 'change'}
  ],
})

const addPrescriptionDialogVisible = ref(false)
const prescriptionConfirmButtonDisabled = ref(false)
const prescriptionCancelButtonDisabled = ref(false)
const prescriptionFormRef = ref<FormInstance>()
const prescriptionFormRules =ref<FormRules<PrescriptionForm>>({
  prescriptionId: [
    {required: true}
  ],
  medicineFormArr: [
    {required: true, message: 'Please add at least one medicine', trigger: 'change' }
  ]
})
const prescriptionForm = ref<PrescriptionForm>({
  prescriptionId: '',
  medicineFormArr: [],
})

const addMedicineDialogVisible = ref(false)
const medicineConfirmButtonDisabled = ref(false)
const medicineFormRef = ref<FormInstance>()
const medicineForm = ref<MedicineForm>({
  medicineId: '',
  medicineName: '',
  courseOfMedication: '',
  dosage: '',
  frequency: '',
  quantity: '',
})
const medicineFormRules = ref<FormRules<MedicineForm>>({
  medicineId: [
    {required: true, message: 'Please enter medicine name', trigger: 'change'}
  ],
  medicineName: [
    {required: true, message: 'Please enter medicine name', trigger: 'change'}
  ],
  courseOfMedication: [
    {required: true, message: 'Please enter course of medication', trigger: 'change'}
  ],
  dosage: [
    {required: true, message: 'Please enter dosage', trigger: 'change'}
  ],
  frequency: [
    {required: true, message: 'Please enter frequency', trigger: 'change'}
  ],
  quantity: [
    {required: true, message: 'Please enter quantity', trigger: 'change'}
  ],
})
const medicineNameOptions = ref<MedicineInfo[]>([])
const medicineNameLoading = ref(false)

const addExaminationDialogVisible = ref(false)
const examinationConfirmButtonDisabled = ref(false)
const examinationFormRef = ref<FormInstance>()
const examinationForm = ref<ExaminationForm>({
  examinationName: '',
  examinationDate: '',
  examinationTime: '',
})
const examinationFormRules = ref<FormRules<ExaminationForm>>({
  examinationName: [
    {required: true, message: 'Please enter examination name', trigger: 'change'}
  ],
  examinationDate: [
    {required: true, message: 'Please select examination date', trigger: 'change'}
  ],
  examinationTime: [
    {required: true, message: 'Please select examination time', trigger: 'change'}
  ]
})
const examinationNameOptions = ref<string[]>([])
const examinationNameLoading = ref(false)
const examinationTimeOptions = ref<ExaminationTimeInfo[]>([])
const examinationTimeLoading = ref(false)
const examinationTimeVisible = ref(false)

const addRehabilitationDialogVisible = ref(false)
const rehabilitationConfirmButtonDisabled = ref(false)
const rehabilitationFormRef = ref<FormInstance>()
const rehabilitationForm = ref<RehabilitationForm>({
  rehabilitationName: '',
  beginDate: '',
  beginTime: '',
})
const rehabilitationFormRules = ref<FormRules<RehabilitationForm>>({
  rehabilitationName: [
    {required: true, message: 'Please enter rehabilitation name', trigger: 'change'}
  ],
  beginDate: [
    {required: true, message: 'Please select date', trigger: 'change'}
  ],
  beginTime: [
    {required: true, message: 'Please select time', trigger: 'change'}
  ]
})
const rehabilitationNameOptions = ref<string[]>([])
const rehabilitationNameLoading = ref(false)
const rehabilitationTimeOptions = ref<RehabilitationTimeInfo[]>([])
const rehabilitationTimeLoading = ref(false)
const rehabilitationTimeVisible = ref(false)

const addSurgeryDialogVisible = ref(false)
const surgeryConfirmButtonDisabled = ref(false)
const surgeryFormRef = ref<FormInstance>()
const surgeryForm = ref<SurgeryForm>({
  surgerySite: '',
  surgeryName: '',
  surgeryType: '',
  surgeryDescription: '',
  beginDate: '',
  beginTime: '',
})
const surgeryFormRules = ref<FormRules<SurgeryForm>>({
  surgerySite: [
    {required: true, message: 'Please enter surgery site', trigger: 'change'}
  ],
  surgeryName: [
    {required: true, message: 'Please enter surgery name', trigger: 'change'}
  ],
  surgeryType: [
    {required: true, message: 'Please enter surgery type', trigger: 'change'}
  ],
  surgeryDescription: [
    {required: true, message: 'Please enter surgery description', trigger: 'change'}
  ],
  beginTime: [
    {required: true, message: 'Please select time', trigger: 'change'}
  ],
  beginDate: [
    {required: true, message: 'Please select date', trigger: 'change'}
  ],

})
const surgerySiteOptions = ref<string[]>([])
const surgerySiteLoading = ref(false)
const surgeryNameOptions = ref<string[]>([])
const surgeryNameLoading = ref(false)
const surgeryTimeOptions = ref<SurgeryTimeInfo[]>([])
const surgeryTimeLoading = ref(false)
const surgeryTypeOptions = ref<string[]>([])
const surgeryFormSurgeryNameVisible = computed(() => surgeryForm.value.surgerySite !== '')
const surgeryFormSurgeryTypeVisible = computed(() => surgeryForm.value.surgeryName !== '')
const surgeryFormBeginDateVisible = computed(() => surgeryForm.value.surgeryType !== '')
const surgeryFormBeginTimeVisible = ref(false)
const surgeryFormSurgeryDescriptionVisible = computed(() => surgeryForm.value.beginTime !== '')

const addHospitalizationDialogVisible = ref(false)
const hospitalizationConfirmButtonDisabled = ref(false)
const hospitalizationFormRef = ref<FormInstance>()
const hospitalizationForm = ref<HospitalizationForm>({
  roomType: '',
  hospitalizationDate: '',
  hospitalizationTime: '',
  hospitalizationReason: '',
})
const hospitalizationFormRules = ref<FormRules<HospitalizationForm>>({
  roomType: [
    {required: true, message: 'Please enter room type', trigger: 'change'}
  ],
  hospitalizationDate: [
    {required: true, message: 'Please select date', trigger: 'change'}
  ],
  hospitalizationTime: [
    {required: true, message: 'Please select time', trigger: 'change'}
  ],
  hospitalizationReason: [
    {required: true, message: 'Please enter hospitalization reason', trigger: 'change'}
  ],
})
const roomTypeOptions = ref<string[]>([])
const roomTypeLoading = ref(false)
const hospitalizationTimeOptions = ref<HospitalizationTimeInfo[]>([])
const hospitalizationTimeLoading = ref(false)
const hospitalizationDateVisible = computed(() => hospitalizationForm.value.roomType !== '')
const hospitalizationTimeVisible = ref(false)


const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = {...consultationFilterForm.value}
  submitValue.inquirerId = config.userId
  if (isRecord.value) {
    submitValue.hasStarted = false
    submitValue.doctorId = config.userId
  } else {
    submitValue.isSearchingPatientInfo = router.currentRoute.value.path.includes('patient-information')
  }

  axios.get(rootOfPath + '/get-doctor-consultation', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      consultationTableRef.value?.clearSort()
    }).catch((err) => {
    console.log(err)
  }).finally(() => {
    formButtonDisabled.value = false
    tableDataReady.value = true
  })
}

const handleTableSortChange = (param: any) => {
  const {prop, order} = param
  if (!order) {
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch (prop) {
    case 'consultationId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'time':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortTime(a.time, b.time, order))
      break
    case 'patientName':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortName(a.patientName, b.patientName, order))
      break
    case 'patientId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortPatientId(a.patientId, b.patientId, order))
      break
    case 'department':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortDepartment(a.department, b.department, order))
      break
    case 'doctorName':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortName(a.doctorName, b.doctorName, order))
      break
    case 'doctorId':
      orderedTableData.value = orderedTableData.value.sort((a, b) => sortDoctorId(a.doctorId, b.doctorId, order))
      break
    default:
      console.error('Invalid prop: ' + prop)
  }
}

const handleTableCancelButton = (row: ConsultationTableData) => {
  cancelConsultationDialogButtonDisabled.value = false
  consultationIdToCancel.value = row.consultationId
  cancelConsultationDialogVisible.value = true
}

const handleConfirmCancelConsultationButton = () => {
  cancelConsultationDialogButtonDisabled.value = true
  cancelConsultationDialogVisible.value = false
  axios.post(rootOfPath + '/doctor/cancel-consultation',
    {
      consultationId: consultationIdToCancel.value,
      doctorId: config.userId
    })
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.consultationId !== consultationIdToCancel.value)
      originalTableData = originalTableData.filter((item) => item.consultationId !== consultationIdToCancel.value)
      totalDataNumber.value -= 1
      ElMessage.success('Cancel consultation successfully')
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
    case DescribableItem.Consultation:
      handleChangeDetailDialogTitle('Consultation Detail')
      break
    case DescribableItem.Examination:
      handleChangeDetailDialogTitle('Examination Detail')
      break
    case DescribableItem.Rehabilitation:
      handleChangeDetailDialogTitle('Rehabilitation Detail')
      break
    case DescribableItem.PrescriptionMedicine:
      handleChangeDetailDialogTitle('Medicine Detail')
      break
    case DescribableItem.Prescription:
      handleChangeDetailDialogTitle('Prescription Detail')
      break
    case DescribableItem.Surgery:
      handleChangeDetailDialogTitle('Surgery Detail')
      break
    case DescribableItem.Hospitalization:
      handleChangeDetailDialogTitle('Hospitalization Detail')
      break
    default:
      console.error('Invalid itemType: ' + itemType)
  }
  detailDialogVisible.value = true
}

const handleTableRecordButton = (row: ConsultationTableData) => {
  consultationToRecord.value.consultationId = row.consultationId
  consultationToRecord.value.patientId = row.patientId
  consultationToRecord.value.patientName = row.patientName
  console.assert(config.userId === row.doctorId, 'doctorId is not equal to config.userId')
  console.assert(config.userName === row.doctorName, 'doctorName is not equal to config.userName')
  consultationToRecord.value.time = dayjs().format('YYYY-MM-DD HH:mm:ss')

  recordDialogButtonDisabled.value = false
  consultationIdToRecord.value = row.consultationId
  recordDialogVisible.value = true
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
const _departmentRemoteMethod = (query: string) => {
  departmentRemoteMethod(query, departmentOptions, departmentLoading)
}
const _roomTypeRemoteMethod = (query: string) => {
  roomTypeRemoteMethod(query, roomTypeOptions, roomTypeLoading)
}

const resetRecordForm = () => {
  resetForm(recordFormRef.value)
  consultationToRecord.value.prescriptionRoughArr = []
  consultationToRecord.value.examinationRoughArr = []
  consultationToRecord.value.rehabilitationRoughArr = []
  consultationToRecord.value.surgeryRoughArr = []
  consultationToRecord.value.hospitalizationRoughArr = []
}
const deleteConsultation = () => {
  axios.post(rootOfPath + '/appointment/consultation/delete', {
    consultationId: consultationIdToRecord.value
  })
    .catch((err) => {
      console.error(err)
    })
}
const handleRecordDialogBeforeClose = (done: () => void) => {
  deleteConsultation()
  resetRecordForm()
  done()
}
const handleRecordDialogClose = () => {
  deleteConsultation()
  resetRecordForm()
  recordDialogVisible.value = false
}
const handleRecordDialogConfirm = () => {
  recordDialogButtonDisabled.value = true
  if (!recordFormRef.value) {
    return
  }
  recordFormRef.value.validate((valid) => {
    if (!valid) {
      recordDialogButtonDisabled.value = false
      return
    }
    consultationToRecord.value.time = dayjs(consultationToRecord.value.time).utc().format()
    axios.post(rootOfPath + '/appointment/consultation/submit', consultationToRecord.value)
      .then(() => {
        ElMessage.success('Record successfully')
        resetRecordForm()
        recordDialogVisible.value = false
        orderedTableData.value = orderedTableData.value.filter((item) => item.consultationId !== consultationIdToRecord.value)
        originalTableData = originalTableData.filter((item) => item.consultationId !== consultationIdToRecord.value)
        totalDataNumber.value -= 1
      })
  })

}

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

const handleAddPrescription = () => {
  prescriptionConfirmButtonDisabled.value = false
  prescriptionCancelButtonDisabled.value = false
  axios.post(rootOfPath + '/appointment/prescription/pre-schedule/ask-for-prescription-id', {
    consultationId: consultationToRecord.value.consultationId,
  })
    .then((res) => {
      prescriptionForm.value.prescriptionId = res.data.results.prescriptionId
      prescriptionForm.value.medicineFormArr = []
      addPrescriptionDialogVisible.value = true
    })
    .catch((err) => {
      ElMessage.error(err.response.data.results)
    })
}
const handleAddPrescriptionBeforeClose = (done: () => void) => {
  handleCancelAddPrescriptionDialog()
  done()
}
const handleConfirmAddPrescriptionDialog = () => {
  prescriptionConfirmButtonDisabled.value = true
  prescriptionCancelButtonDisabled.value = true
  if(!prescriptionFormRef.value){
    return
  }
  prescriptionFormRef.value.validate((valid)=>{
    if(!valid){
      prescriptionConfirmButtonDisabled.value = false
      prescriptionCancelButtonDisabled.value = false
      return
    }
    axios.post(rootOfPath + '/appointment/prescription/pre-schedule/confirm', {
      prescriptionId: prescriptionForm.value.prescriptionId,
    })
      .then(() => {
        resetForm(prescriptionFormRef.value)
        addPrescriptionDialogVisible.value = false
        consultationToRecord.value.prescriptionRoughArr.push({
          prescriptionId: prescriptionForm.value.prescriptionId,
        })
      })
      .catch((err) => {
        ElMessage.error(err.response.data.results)
      })
  })
}
const handleCancelAddPrescriptionDialog = () => {
  prescriptionConfirmButtonDisabled.value = true
  prescriptionCancelButtonDisabled.value = true
  addPrescriptionDialogVisible.value = false
  axios.post(rootOfPath + '/appointment/prescription/pre-schedule/cancel', {
    prescriptionId: prescriptionForm.value.prescriptionId,
  })
    .catch((err) => {
      ElMessage.error(err.response.data.results)
    }).finally(() => {
    resetForm(prescriptionFormRef.value)
  })
}
const handleDeletePrescription = (row: PrescriptionRough) => {
  consultationToRecord.value.prescriptionRoughArr =
    consultationToRecord.value.prescriptionRoughArr.filter((item) => item.prescriptionId !== row.prescriptionId)
  axios.post(rootOfPath + '/appointment/prescription/delete-pre-schedule', {
    prescriptionId: row.prescriptionId
  })
    .catch((err) => {
      ElMessage.error(err.response.data.results)
    }).finally(() => {
    resetForm(prescriptionFormRef.value)
  })
}

const handleAddMedicine = () => {
  medicineConfirmButtonDisabled.value = false
  addMedicineDialogVisible.value = true
}
const handleAddMedicineDialogBeforeClose = (done: () => void) => {
  resetForm(medicineFormRef.value)
  done()
}
const _medicineInfoRemoteMethod = (query: string) => {
  medicineInfoRemoteMethod(query, medicineNameOptions, medicineNameLoading)
}
const handleConfirmAddMedicineDialog = () => {
  medicineConfirmButtonDisabled.value = true
  if (!medicineFormRef.value) {
    return
  }
  medicineFormRef.value.validate((valid) => {
    if (!valid) {
      medicineConfirmButtonDisabled.value = false
      return
    }
    // cannot add the same medicine twice
    prescriptionForm.value.medicineFormArr.forEach((item) => {
      if (item.medicineId === medicineForm.value.medicineId) {
        ElMessage.error('Cannot add the same medicine twice')
        medicineConfirmButtonDisabled.value = false
        return
      }
    })
    axios.post(rootOfPath + '/appointment/prescription/pre-schedule/add-medicine', {
      prescriptionId: prescriptionForm.value.prescriptionId,
      medicineId: medicineForm.value.medicineId,
      courseOfMedication: medicineForm.value.courseOfMedication,
      dosage: medicineForm.value.dosage,
      frequency: medicineForm.value.frequency,
      quantity: medicineForm.value.quantity,
    })
      .then(() => {
        axios.get(rootOfPath + '/get-medicine-name-by-id', {
          params: {
            medicineId: medicineForm.value.medicineId,
          }
        })
          .then((res) => {
            medicineForm.value.medicineName = res.data.results
            prescriptionForm.value.medicineFormArr.push({
              medicineId: medicineForm.value.medicineId,
              medicineName: medicineForm.value.medicineName,
              courseOfMedication: medicineForm.value.courseOfMedication,
              dosage: medicineForm.value.dosage,
              frequency: medicineForm.value.frequency,
              quantity: medicineForm.value.quantity,
            })
            resetForm(medicineFormRef.value)
            addMedicineDialogVisible.value = false
          })
          .catch((err) => {
            console.error(err)
          })
      })
      .catch((err) => {
        console.error(err)
        ElMessage.error(err.response.data.results)
        medicineConfirmButtonDisabled.value = false
      })
  })
}
const handleCancelAddMedicineDialog = () => {
  resetForm(medicineFormRef.value)
  addMedicineDialogVisible.value = false
}
const handleDeleteMedicine = (row: MedicineForm) => {
  prescriptionForm.value.medicineFormArr =
    prescriptionForm.value.medicineFormArr.filter((item) => item.medicineId !== row.medicineId)
  axios.post(rootOfPath + '/appointment/prescription/pre-schedule/delete-medicine', {
    prescriptionId: prescriptionForm.value.prescriptionId,
    medicineId: row.medicineId,
  })
    .then(() => {
      ElMessage.success("Delete successfully")
    })
    .catch((err) => {
      console.error('Delete failed')
      ElMessage.error(err.response.data.results)
    })
}

const handleAddExamination = () => {
  examinationConfirmButtonDisabled.value = false
  addExaminationDialogVisible.value = true
}
const handleAddExaminationDialogBeforeClose = (done: () => void) => {
  resetForm(examinationFormRef.value)
  done()
}
const _examinationNameRemoteMethod = (query: string) => {
  examinationNameRemoteMethod(query, examinationNameOptions, examinationNameLoading)
}
const handleConfirmAddExaminationDialog = () => {
  examinationConfirmButtonDisabled.value = true
  if (!examinationFormRef.value) {
    return
  }
  examinationFormRef.value.validate((valid) => {
    if (!valid) {
      examinationConfirmButtonDisabled.value = false
      return
    }
    axios.post(rootOfPath + '/appointment/examination/pre-schedule', {
      consultationId: consultationToRecord.value.consultationId,
      examinationName: examinationForm.value.examinationName,
      examinationTime: dayjs(dayjs(examinationForm.value.examinationDate).format('YYYY-MM-DD') + ' ' + examinationForm.value.examinationTime).utc().format(),
    })
      .then((res) => {
        consultationToRecord.value.examinationRoughArr.push({
          examinationId: res.data.results.examinationId,
          examinationName: res.data.results.examinationName,
        })
        resetForm(examinationFormRef.value)
        addExaminationDialogVisible.value = false
      })
      .catch((err) => {
        ElMessage.error(err.response.data.results)
        examinationConfirmButtonDisabled.value = false
      })
  })
}
const handleCancelAddExaminationDialog = () => {
  resetForm(examinationFormRef.value)
  addExaminationDialogVisible.value = false
}
const handleDeleteExamination = (row: ExaminationRough) => {
  consultationToRecord.value.examinationRoughArr =
    consultationToRecord.value.examinationRoughArr.filter((item) => item.examinationId !== row.examinationId)
  axios.post(rootOfPath + '/appointment/examination/delete-pre-schedule', {
    examinationId: row.examinationId,
  })
    .then(() => {
      ElMessage.success("Delete successfully")
    })
    .catch((err) => {
      console.error('Delete failed')
      ElMessage.error(err.response.data.results)
    })
}

const handleAddRehabilitation = () => {
  rehabilitationConfirmButtonDisabled.value = false
  addRehabilitationDialogVisible.value = true
}
const handleAddRehabilitationDialogBeforeClose = (done: () => void) => {
  resetForm(rehabilitationFormRef.value)
  done()
}
const _rehabilitationNameRemoteMethod = (query: string) => {
  rehabilitationNameRemoteMethod(query, rehabilitationNameOptions, rehabilitationNameLoading)
}
const handleConfirmAddRehabilitationDialog = () => {
  rehabilitationConfirmButtonDisabled.value = true
  if (!rehabilitationFormRef.value) {
    return
  }
  rehabilitationFormRef.value.validate((valid) => {
    if (!valid) {
      rehabilitationConfirmButtonDisabled.value = false
      return
    }
    axios.post(rootOfPath + '/appointment/rehabilitation/pre-schedule', {
      consultationId: consultationToRecord.value.consultationId,
      rehabilitationName: rehabilitationForm.value.rehabilitationName,
      beginTime: dayjs(dayjs(rehabilitationForm.value.beginDate).format('YYYY-MM-DD') + ' ' + rehabilitationForm.value.beginTime).utc().format(),
    })
      .then((res) => {
        consultationToRecord.value.rehabilitationRoughArr.push({
          rehabilitationId: res.data.results.rehabilitationId,
          rehabilitationName: res.data.results.rehabilitationName,
        })
        resetForm(rehabilitationFormRef.value)
        addRehabilitationDialogVisible.value = false
      })
      .catch((err) => {
        ElMessage.error(err.response.data.results)
        rehabilitationConfirmButtonDisabled.value = false
      })
  })
}
const handleCancelAddRehabilitationDialog = () => {
  resetForm(rehabilitationFormRef.value)
  addRehabilitationDialogVisible.value = false
}
const handleDeleteRehabilitation = (row: RehabilitationRough) => {
  consultationToRecord.value.rehabilitationRoughArr =
    consultationToRecord.value.rehabilitationRoughArr.filter((item) => item.rehabilitationId !== row.rehabilitationId)
  axios.post(rootOfPath + '/appointment/rehabilitation/delete-pre-schedule', {
    rehabilitationId: row.rehabilitationId,
  })
    .then(() => {
      ElMessage.success("Delete successfully")
    })
    .catch((err) => {
      console.error('Delete failed')
      ElMessage.error(err.response.data.results)
    })
}

const handleAddSurgery = () => {
  surgeryConfirmButtonDisabled.value = false
  addSurgeryDialogVisible.value = true
}
const handleAddSurgeryDialogBeforeClose = (done: () => void) => {
  resetForm(surgeryFormRef.value)
  done()
}
const _surgerySiteRemoteMethod = (query: string) => {
  surgerySiteRemoteMethod(query, surgerySiteOptions, surgerySiteLoading)
}
const _surgeryNameRemoteMethod = (query: string) => {
  surgeryNameRemoteMethod(query, surgeryForm.value.surgerySite, surgeryNameOptions, surgeryNameLoading)
}
const handleConfirmAddSurgeryDialog = () => {
  surgeryConfirmButtonDisabled.value = true
  if (!surgeryFormRef.value) {
    return
  }
  surgeryFormRef.value.validate((valid) => {
    if (!valid) {
      surgeryConfirmButtonDisabled.value = false
      return
    }
    axios.post(rootOfPath + '/appointment/surgery/pre-schedule', {
      consultationId: consultationToRecord.value.consultationId,
      surgerySite: surgeryForm.value.surgerySite,
      surgeryName: surgeryForm.value.surgeryName,
      surgeryType: surgeryForm.value.surgeryType,
      surgeryDescription: surgeryForm.value.surgeryDescription,
      beginTime: dayjs(dayjs(surgeryForm.value.beginDate).format('YYYY-MM-DD') + ' ' + surgeryForm.value.beginTime).utc().format(),
    })
      .then((res) => {
        consultationToRecord.value.surgeryRoughArr.push({
          surgeryId: res.data.results.surgeryId,
          surgeryName: res.data.results.surgeryName,
        })
        resetForm(surgeryFormRef.value)
        addSurgeryDialogVisible.value = false
      })
      .catch((err) => {
        ElMessage.error(err.response.data.results)
        surgeryConfirmButtonDisabled.value = false
      })
  })
}
const handleCancelAddSurgeryDialog = () => {
  resetForm(surgeryFormRef.value)
  addSurgeryDialogVisible.value = false
}
const handleDeleteSurgery = (row: SurgeryRough) => {
  consultationToRecord.value.surgeryRoughArr =
    consultationToRecord.value.surgeryRoughArr.filter((item) => item.surgeryId !== row.surgeryId)
  axios.post(rootOfPath + '/appointment/surgery/delete-pre-schedule', {
    surgeryId: row.surgeryId,
  })
    .then(() => {
      ElMessage.success("Delete successfully")
    })
    .catch((err) => {
      console.error('Delete failed')
      ElMessage.error(err.response.data.results)
    })
}

const handleAddHospitalization = () => {
  hospitalizationConfirmButtonDisabled.value = false
  addHospitalizationDialogVisible.value = true
}
const handleAddHospitalizationDialogBeforeClose = (done: () => void) => {
  resetForm(hospitalizationFormRef.value)
  done()
}
const handleConfirmAddHospitalizationDialog = () => {
  hospitalizationConfirmButtonDisabled.value = true
  if (!hospitalizationFormRef.value) {
    return
  }
  hospitalizationFormRef.value.validate((valid) => {
    if (!valid) {
      hospitalizationConfirmButtonDisabled.value = false
      return
    }
    axios.post(rootOfPath + '/appointment/hospitalization/pre-schedule', {
      consultationId: consultationToRecord.value.consultationId,
      hospitalizationTime: dayjs(dayjs(hospitalizationForm.value.hospitalizationDate).format('YYYY-MM-DD') + ' ' + hospitalizationForm.value.hospitalizationTime).utc().format(),
      hospitalizationReason: hospitalizationForm.value.hospitalizationReason,
      roomType: hospitalizationForm.value.roomType
    })
      .then((res) => {
        consultationToRecord.value.hospitalizationRoughArr.push({
          hospitalizationId: res.data.results.hospitalizationId,
          doctorName: res.data.results.doctorName,
        })
        resetForm(hospitalizationFormRef.value)
        addHospitalizationDialogVisible.value = false
      })
      .catch((err) => {
        ElMessage.error(err.response.data.results)
        hospitalizationConfirmButtonDisabled.value = false
      })
  })
}
const handleCancelAddHospitalizationDialog = () => {
  resetForm(hospitalizationFormRef.value)
  addHospitalizationDialogVisible.value = false
}
const handleDeleteHospitalization = (row: HospitalizationRough) => {
  consultationToRecord.value.hospitalizationRoughArr =
    consultationToRecord.value.hospitalizationRoughArr.filter((item) => item.hospitalizationId !== row.hospitalizationId)
  axios.post(rootOfPath + '/appointment/hospitalization/delete-pre-schedule', {
    hospitalizationId: row.hospitalizationId,
  })
    .then(() => {
      ElMessage.success("Delete successfully")
    })
    .catch((err) => {
      console.error('Delete failed')
      ElMessage.error(err.response.data.results)
    })
}

onMounted(() => {
  getTableData()
  axios.get(rootOfPath + '/get-surgery-type-arr')
    .then((response) => {
      surgeryTypeOptions.value = response.data.results
    }).catch((err) => {
    console.log(err)
  })
})
watch(() => router.currentRoute.value.path, () => {
  resetForm(consultationFilterFormRef.value)
  getTableData()
  tablePageSize.value = config.defaultPageSize
})

watch(() => medicineForm.value.medicineName, () => {
  medicineForm.value.medicineId = medicineForm.value.medicineName
})

watch(() => examinationForm.value.examinationDate, () => {
  if (examinationForm.value.examinationDate === '' || !examinationForm.value.examinationDate) {
    examinationTimeVisible.value = false
    return
  }
  examinationTimeVisible.value = true
  examinationTimeLoading.value = true
  examinationForm.value.examinationTime = ''
  axios.get(rootOfPath + '/appointment/examination/is-time-available', {
    params: {
      examinationDate: examinationForm.value.examinationDate,
      examinationName: examinationForm.value.examinationName
    }
  }).then((response) => {
    examinationTimeOptions.value = response.data.results
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    examinationTimeLoading.value = false
  })
})
watch(() => examinationForm.value.examinationName, () => {
  examinationForm.value.examinationDate = ''
})

watch(() => rehabilitationForm.value.beginDate, () => {
  if (rehabilitationForm.value.beginDate === '' || !rehabilitationForm.value.beginDate) {
    rehabilitationTimeVisible.value = false
    return
  }
  rehabilitationTimeVisible.value = true
  rehabilitationTimeLoading.value = true
  rehabilitationForm.value.beginTime = ''
  axios.get(rootOfPath + '/appointment/rehabilitation/is-time-available', {
    params: {
      beginDate: rehabilitationForm.value.beginDate,
      rehabilitationName: rehabilitationForm.value.rehabilitationName
    }
  }).then((response) => {
    rehabilitationTimeOptions.value = response.data.results
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    rehabilitationTimeLoading.value = false
  })
})
watch(() => rehabilitationForm.value.rehabilitationName, () => {
  rehabilitationForm.value.beginDate = ''
})

watch(() => surgeryForm.value.surgerySite, () => {
  surgeryForm.value.surgeryName = ''
  surgeryForm.value.surgeryType = ''
  surgeryForm.value.beginDate = ''
  surgeryForm.value.beginTime = ''
  surgeryForm.value.surgeryDescription = ''
})
watch(() => surgeryForm.value.surgeryName, () => {
  surgeryForm.value.surgeryType = ''
  surgeryForm.value.beginDate = ''
  surgeryForm.value.beginTime = ''
  surgeryForm.value.surgeryDescription = ''
})
watch(() => surgeryForm.value.surgeryType, () => {
  surgeryForm.value.beginDate = ''
  surgeryForm.value.beginTime = ''
  surgeryForm.value.surgeryDescription = ''
})
watch(() => surgeryForm.value.beginDate, () => {
  if (surgeryForm.value.beginDate === '' || !surgeryForm.value.beginDate) {
    surgeryFormBeginTimeVisible.value = false
    surgeryForm.value.beginTime = ''
    surgeryForm.value.surgeryDescription = ''
    return
  }
  surgeryFormBeginTimeVisible.value = true
  surgeryTimeLoading.value = true
  surgeryForm.value.beginTime = ''
  axios.get(rootOfPath + '/appointment/surgery/is-time-available', {
    params: {
      beginDate: surgeryForm.value.beginDate,
      surgerySite: surgeryForm.value.surgerySite,
      surgeryName: surgeryForm.value.surgeryName,
      surgeryType: surgeryForm.value.surgeryType,
    }
  }).then((response) => {
    surgeryTimeOptions.value = response.data.results
  }).catch((err) => {
    console.log(err)
  })
})
watch(() => surgeryForm.value.beginTime, () => {
  surgeryForm.value.surgeryDescription = ''
})


watch(() => hospitalizationForm.value.roomType, () => {
  hospitalizationForm.value.hospitalizationDate = ''
  hospitalizationForm.value.hospitalizationTime = ''
  hospitalizationForm.value.hospitalizationReason = ''
})
watch(() => hospitalizationForm.value.hospitalizationDate, () => {
  if (hospitalizationForm.value.hospitalizationDate === '' || !hospitalizationForm.value.hospitalizationDate) {
    hospitalizationTimeVisible.value = false
    return
  }
  hospitalizationTimeVisible.value = true
  hospitalizationTimeLoading.value = true
  hospitalizationForm.value.hospitalizationTime = ''
  axios.get(rootOfPath + '/appointment/hospitalization/is-time-available', {
    params: {
      hospitalizationDate: hospitalizationForm.value.hospitalizationDate,
      roomType: hospitalizationForm.value.roomType
    }
  }).then((response) => {
    hospitalizationTimeOptions.value = response.data.results
  }).catch((err) => {
    console.log(err)
  }).finally(() => {
    hospitalizationTimeLoading.value = false
  })
})
watch(() => hospitalizationForm.value.hospitalizationTime, () => {
  hospitalizationForm.value.hospitalizationReason = ''
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
    v-model="cancelConsultationDialogVisible"
    title="Cancel Consultation"
  >
    <span>Are you sure to cancel consultation with ID <el-text tag="b">{{ consultationIdToCancel }}</el-text> ?</span>
    <template #footer>
      <el-button @click="cancelConsultationDialogVisible=false">Cancel</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelConsultationButton"
        :disabled="cancelConsultationDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="recordDialogVisible"
    title="Record"
    :width="config.recordDialogWidth"
    destroy-on-close
    :before-close="handleRecordDialogBeforeClose"
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="recordFormRef"
            :model="consultationToRecord"
            label-position="top"
            :rules="recordFormRules"
          >
            <el-form-item label="Consultation ID" prop="consultationId">
              <el-input v-model="consultationToRecord.consultationId" disabled/>
            </el-form-item>

            <el-form-item label="Patient ID" prop="patientId">
              <el-input v-model="consultationToRecord.patientId" disabled/>
            </el-form-item>

            <el-form-item label="Patient Name" prop="patientName">
              <el-input v-model="consultationToRecord.patientName" disabled/>
            </el-form-item>

            <el-form-item label="Time" prop="time">
              <el-input v-model="consultationToRecord.time" disabled/>
            </el-form-item>

            <el-form-item label="Self Report" prop="selfReport">
              <el-input
                type="textarea"
                v-model="consultationToRecord.selfReport"
                placeholder="Enter self report"
                autosize
              />
            </el-form-item>

            <el-form-item label="Medical History" prop="medicalHistory">
              <el-input
                type="textarea"
                v-model="consultationToRecord.medicalHistory"
                placeholder="Enter medical history"
                autosize
              />
            </el-form-item>

            <el-form-item label="Medication History" prop="medicationHistory">
              <el-input
                type="textarea"
                v-model="consultationToRecord.medicationHistory"
                placeholder="Enter medication history"
                autosize
              />
            </el-form-item>

            <el-form-item label="Medical Advice" prop="medicalAdvice">
              <el-input
                type="textarea"
                v-model="consultationToRecord.medicalAdvice"
                placeholder="Enter medical advice"
                autosize
              />
            </el-form-item>

            <el-form-item>
              <template #label>
                Prescription
                <el-button type="primary" size="small" @click="handleAddPrescription" plain>Add</el-button>
              </template>
              <el-table
                :data="consultationToRecord.prescriptionRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Prescription ID" align="center" prop="prescriptionId"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(scope.row.prescriptionId, DescribableItem.Prescription)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDeletePrescription(scope.row)" plain>Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Examination
                <el-button type="primary" size="small" @click="handleAddExamination" plain>Add</el-button>
              </template>
              <el-table
                :data="consultationToRecord.examinationRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Name" align="center" prop="examinationName"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(scope.row.examinationId, DescribableItem.Examination)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDeleteExamination(scope.row)" plain>Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Rehabilitation
                <el-button type="primary" size="small" @click="handleAddRehabilitation" plain>Add</el-button>
              </template>
              <el-table
                :data="consultationToRecord.rehabilitationRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Name" align="center" prop="rehabilitationName"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(scope.row.rehabilitationId, DescribableItem.Rehabilitation)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDeleteRehabilitation(scope.row)" plain>Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Surgery
                <el-button type="primary" size="small" @click="handleAddSurgery" plain>Add</el-button>
              </template>
              <el-table
                :data="consultationToRecord.surgeryRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Name" align="center" prop="surgeryName"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(scope.row.surgeryId, DescribableItem.Surgery)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDeleteSurgery(scope.row)" plain>Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <el-form-item>
              <template #label>
                Hospitalization
                <el-button type="primary" size="small" @click="handleAddHospitalization" plain>Add</el-button>
              </template>
              <el-table
                :data="consultationToRecord.hospitalizationRoughArr"
                style="width: 100%"
              >
                <el-table-column label="Hospitalization ID" align="center" prop="hospitalizationId"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(scope.row.hospitalizationId, DescribableItem.Hospitalization)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDeleteHospitalization(scope.row)" plain>Delete
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
      <el-button @click="handleRecordDialogClose">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleRecordDialogConfirm"
        :disabled="recordDialogButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addPrescriptionDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Prescription"
    destroy-on-close
    :before-close="handleAddPrescriptionBeforeClose"
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="prescriptionFormRef"
            :model="prescriptionForm"
            label-position="top"
            :rules="prescriptionFormRules"
          >
            <el-form-item label="Prescription ID" prop="prescriptionId">
              <el-input v-model="prescriptionForm.prescriptionId" disabled/>
            </el-form-item>
            <el-form-item prop="medicineFormArr">
              <template #label>
                Medicine
                <el-button type="primary" size="small" plain @click="handleAddMedicine">Add</el-button>
              </template>
              <el-table
                :data="prescriptionForm.medicineFormArr"
                style="width: 100%"
              >
                <el-table-column label="Medicine Name" align="center" prop="medicineName"/>
                <el-table-column label="Action" align="center">
                  <template #default="scope">
                    <el-button type="primary" size="small" plain
                               @click="handleShowDetailButton(prescriptionForm.prescriptionId+'#'+scope.row.medicineId, DescribableItem.PrescriptionMedicine)">
                      Show Detail
                    </el-button>
                    <el-button type="danger" size="small" plain @click="handleDeleteMedicine(scope.row)">Delete
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
      <el-button
        @click="handleCancelAddPrescriptionDialog"
        :disabled="prescriptionCancelButtonDisabled"
      >Cancel
      </el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddPrescriptionDialog"
        :disabled="prescriptionConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addMedicineDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Medicine"
    :before-close="handleAddMedicineDialogBeforeClose"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="medicineFormRef"
            :model="medicineForm"
            label-position="top"
            :rules="medicineFormRules"
          >
            <el-form-item label="Medicine ID" prop="medicineId">
              <el-input v-model="medicineForm.medicineId" disabled
                        placeholder="Enter medicine name to see medicine ID"/>
            </el-form-item>

            <el-form-item label="Medicine Name" prop="medicineName">
              <el-select
                v-model="medicineForm.medicineName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_medicineInfoRemoteMethod"
                :loading="medicineNameLoading"
                placeholder="Enter medicine name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in medicineNameOptions"
                  :key="item.medicineId"
                  :label="item.medicineName"
                  :value="item.medicineId"
                >
                  <span style="float: left">{{ item.medicineName }}</span>
                  <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">{{
                      item.medicineId
                    }}</span>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Course Of Medication" prop="courseOfMedication">
              <el-input
                v-model="medicineForm.courseOfMedication"
                placeholder="Enter course of medication"
              />
            </el-form-item>

            <el-form-item label="Dosage" prop="dosage">
              <el-input
                v-model="medicineForm.dosage"
                placeholder="Enter dosage"
              />
            </el-form-item>

            <el-form-item label="Frequency" prop="frequency">
              <el-input
                v-model="medicineForm.frequency"
                placeholder="Enter frequency"
              />
            </el-form-item>

            <el-form-item label="Quantity" prop="quantity">
              <el-input
                v-model="medicineForm.quantity"
                placeholder="Enter quantity"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleCancelAddMedicineDialog">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddMedicineDialog"
        :disabled="medicineConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addExaminationDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Examination"
    :before-close="handleAddExaminationDialogBeforeClose"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="examinationFormRef"
            :model="examinationForm"
            label-position="top"
            :rules="examinationFormRules"
          >
            <el-form-item label="Examination Name" prop="examinationName">
              <el-select
                v-model="examinationForm.examinationName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_examinationNameRemoteMethod"
                :loading="examinationNameLoading"
                placeholder="Enter examination name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in examinationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <el-collapse-transition>
              <el-form-item label="Examination Date" prop="examinationDate" v-if="examinationForm.examinationName!==''">
                <el-date-picker
                  v-model="examinationForm.examinationDate"
                  placeholder="Select date"
                  style="width: 100%"
                  :disabled-date="disabledDate"
                  :loading="true"
                ></el-date-picker>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Examination Time" prop="examinationTime" v-if="examinationTimeVisible">
                <el-select
                  v-model="examinationForm.examinationTime"
                  placeholder="Select time"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in examinationTimeOptions"
                    :key="item.examinationTime"
                    :value="item.examinationTime"
                    :disabled="item.isAvailable === 'false'"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleCancelAddExaminationDialog">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddExaminationDialog"
        :disabled="examinationConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addRehabilitationDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Rehabilitation"
    :before-close="handleAddRehabilitationDialogBeforeClose"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="rehabilitationFormRef"
            :model="rehabilitationForm"
            label-position="top"
            :rules="rehabilitationFormRules"
          >
            <el-form-item label="Rehabilitation Name" prop="rehabilitationName">
              <el-select
                v-model="rehabilitationForm.rehabilitationName"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_rehabilitationNameRemoteMethod"
                :loading="rehabilitationNameLoading"
                placeholder="Enter rehabilitation name"
                style="width: 100%"
              >
                <el-option
                  v-for="item in rehabilitationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <el-collapse-transition>
              <el-form-item label="Begin Date" prop="beginDate" v-if="rehabilitationForm.rehabilitationName!==''">
                <el-date-picker
                  v-model="rehabilitationForm.beginDate"
                  placeholder="Select date"
                  style="width: 100%"
                  :disabled-date="disabledDate"
                  :loading="true"
                ></el-date-picker>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Begin Time" prop="beginTime"
                            v-if="rehabilitationTimeVisible">
                <el-select
                  v-model="rehabilitationForm.beginTime"
                  placeholder="Select time"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in rehabilitationTimeOptions"
                    :key="item.beginTime"
                    :value="item.beginTime"
                    :disabled="item.isAvailable === 'false'"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>

          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleCancelAddRehabilitationDialog">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddRehabilitationDialog"
        :disabled="rehabilitationConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addSurgeryDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Surgery"
    :before-close="handleAddSurgeryDialogBeforeClose"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="surgeryFormRef"
            :model="surgeryForm"
            label-position="top"
            :rules="surgeryFormRules"
          >
            <el-form-item label="Surgery Site" prop="surgerySite">
              <el-select
                v-model="surgeryForm.surgerySite"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_surgerySiteRemoteMethod"
                :loading="surgerySiteLoading"
                placeholder="Enter surgery site"
                style="width: 100%"
              >
                <el-option
                  v-for="item in surgerySiteOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <el-collapse-transition>
              <el-form-item label="Surgery Name" prop="surgeryName" v-if="surgeryFormSurgeryNameVisible">
                <el-select
                  v-model="surgeryForm.surgeryName"
                  filterable
                  remote
                  reserve-keyword
                  clearable
                  :remote-method="_surgeryNameRemoteMethod"
                  :loading="surgeryNameLoading"
                  placeholder="Enter surgery name"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in surgeryNameOptions"
                    :key="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Surgery Type" prop="surgeryType" v-if="surgeryFormSurgeryTypeVisible">
                <el-select
                  v-model="surgeryForm.surgeryType"
                  placeholder="Select surgery type"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in surgeryTypeOptions"
                    :key="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Begin Date" prop="beginDate" v-if="surgeryFormBeginDateVisible">
                <el-date-picker
                  v-model="surgeryForm.beginDate"
                  placeholder="Select date"
                  style="width: 100%"
                  :disabled-date="disabledDate"
                  :loading="true"
                ></el-date-picker>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Begin Time" prop="beginTime" v-if="surgeryFormBeginTimeVisible">
                <el-select
                  v-model="surgeryForm.beginTime"
                  placeholder="Select time"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in surgeryTimeOptions"
                    :key="item.beginTime"
                    :value="item.beginTime"
                    :disabled="item.isAvailable === 'false'"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Surgery Description" prop="surgeryDescription"
                            v-if="surgeryFormSurgeryDescriptionVisible">
                <el-input
                  type="textarea"
                  v-model="surgeryForm.surgeryDescription"
                  placeholder="Enter surgery description"
                  autosize
                />
              </el-form-item>
            </el-collapse-transition>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleCancelAddSurgeryDialog">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddSurgeryDialog"
        :disabled="surgeryConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="addHospitalizationDialogVisible"
    :width="config.recordDialogWidth"
    title="Add Hospitalization"
    :before-close="handleAddHospitalizationDialogBeforeClose"
    destroy-on-close
  >
    <div class="record-dialog-first-div">
      <el-scrollbar>
        <div class="form-container">
          <el-form
            ref="hospitalizationFormRef"
            :model="hospitalizationForm"
            label-position="top"
            :rules="hospitalizationFormRules"
          >
            <el-form-item label="Room Type" prop="roomType">
              <el-select
                v-model="hospitalizationForm.roomType"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_roomTypeRemoteMethod"
                :loading="roomTypeLoading"
                placeholder="Enter room Type"
                style="width: 100%"
              >
                <el-option
                  v-for="item in roomTypeOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <el-collapse-transition>
              <el-form-item label="Hospitalization Date" prop="hospitalizationDate" v-if="hospitalizationDateVisible">
                <el-date-picker
                  v-model="hospitalizationForm.hospitalizationDate"
                  type="date"
                  placeholder="Select date"
                  style="width: 100%"
                  :disabled-date="disabledDate"
                  :loading="true"
                ></el-date-picker>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Hospitalization Time" prop="hospitalizationTime" v-if="hospitalizationTimeVisible">
                <el-select
                  v-model="hospitalizationForm.hospitalizationTime"
                  placeholder="Select time"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in hospitalizationTimeOptions"
                    :key="item.hospitalizationTime"
                    :value="item.hospitalizationTime"
                    :disabled="item.isAvailable === 'false'"
                  />
                </el-select>
              </el-form-item>
            </el-collapse-transition>

            <el-collapse-transition>
              <el-form-item label="Hospitalization Reason" prop="hospitalizationReason"
                            v-if="hospitalizationForm.hospitalizationTime!==''">
                <el-input
                  type="textarea"
                  v-model="hospitalizationForm.hospitalizationReason"
                  placeholder="Enter hospitalization description"
                  autosize
                />
              </el-form-item>
            </el-collapse-transition>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="handleCancelAddHospitalizationDialog">Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmAddHospitalizationDialog"
        :disabled="hospitalizationConfirmButtonDisabled"
      >Confirm
      </el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="consultationFilterFormRef"
          :model="consultationFilterForm"
          label-position="top"
        >
          <el-form-item label="Consultation ID" prop="consultationId">
            <el-input v-model="consultationFilterForm.consultationId" placeholder="Enter the consultation ID"/>
          </el-form-item>

          <el-form-item label="Department" prop="department" v-if="isSearchPatientInfo||isSearchDoctorInfo">
            <el-select
              v-model="consultationFilterForm.department"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_departmentRemoteMethod"
              :loading="departmentLoading"
              placeholder="Enter department"
              style="width: 100%"
            >
              <el-option
                v-for="item in departmentOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Patient ID" prop="patientId" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="consultationFilterForm.patientId"
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
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Patient Name" prop="patientName" v-if="isSearchPatientInfo||isRecord">
            <el-select
              v-model="consultationFilterForm.patientName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="_patientNameRemoteMethod"
              :loading="patientNameLoading"
              placeholder="Enter patient name"
              style="width: 100%"
            >
              <el-option
                v-for="item in patientNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Doctor ID" prop="doctorId" v-if="isSearchDoctorInfo">
            <el-select
              v-model="consultationFilterForm.doctorId"
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
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Doctor Name" prop="doctorName" v-if="isSearchDoctorInfo">
            <el-select
              v-model="consultationFilterForm.doctorName"
              filterable
              remote
              reserve-keyword
              clearable
              :remote-method="doctorNameRemoteMethod"
              :loading="doctorNameLoading"
              placeholder="Enter doctor name"
              style="width: 100%"
            >
              <el-option
                v-for="item in doctorNameOptions"
                :key="item"
                :value="item"
              ></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Time">
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="consultationFilterForm.beginTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime">
                <el-date-picker
                  v-model="consultationFilterForm.endTime"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
            <el-button :disabled="formButtonDisabled" @click="resetForm(consultationFilterFormRef)">Reset</el-button>
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
        ref="consultationTableRef"
      >
        <el-table-column label="Consultation ID" prop="consultationId" sortable/>
        <el-table-column label="Department" prop="department" sortable v-if="isSearchPatientInfo||isSearchDoctorInfo"/>
        <el-table-column label="Time" prop="time" sortable/>
        <el-table-column label="Patient ID" prop="patientId" sortable/>
        <el-table-column label="Patient Name" prop="patientName" sortable/>
        <el-table-column label="Doctor ID" prop="doctorId" sortable v-if="isSearchDoctorInfo"/>
        <el-table-column label="Doctor Name" prop="doctorName" sortable v-if="isSearchDoctorInfo||isSearchPatientInfo"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleShowDetailButton(scope.row.consultationId, DescribableItem.Consultation)"
              v-if="isSearchPatientInfo||isSearchDoctorInfo"
            >Show detail
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
              @click="handleTableCancelButton(scope.row)"
              :disabled="scope.row.hasStarted==='true'"
              v-if="isRecord||isSearchPatientInfo"
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
