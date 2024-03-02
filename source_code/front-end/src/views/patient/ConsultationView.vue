<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import { sortConsultationId, sortDepartment, sortName, sortTime } from '../../utils/sort'

const config = useConfigStore()
const rootOfPath = config.rootOfPath
const router = useRouter()

interface ConsultationTableData {
  consultationId: string
  time: string
  department: string
  doctorName: string
}

const isHistory = computed(() => router.currentRoute.value.path.includes('history'))
const orderedTableData = ref<ConsultationTableData[]>([])
let originalTableData = [] as ConsultationTableData[]
const getData = ref(false)
onMounted(() => {
  getTableData()
})
const path = computed(() => router.currentRoute.value.path)
watch(path, () => {
  console.log('path changed')
  resetConsultationFilterForm(consultationFilterFormRef.value)
  getTableData()
  pageSize.value = config.defaultPageSize
})

const currentPage = ref(1)
const pageSize = ref(config.defaultPageSize)
const totalDataNum = ref(0)
const displayedTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = currentPage.value * pageSize.value
  return orderedTableData.value.slice(start, end)
})


const disabledDate = (time: Date) => {
  const currentDate = new Date()
  if (isHistory.value) {
    return time.getTime() > currentDate.getTime()
  } else {
    return time.getTime() < currentDate.getTime() - 3600 * 24 * 1000
  }
}

const buttonDisabled = ref(false)
const consultationTableRef = ref<TableInstance>()
const getTableData = () => {
  buttonDisabled.value = true
  getData.value = false
  const submitValue = { ...consultationFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId
  axios.get(rootOfPath + '/get-patient-consultation', {
    params: submitValue
  }).then((res) => {
    originalTableData = res.data.results.slice()
    orderedTableData.value = res.data.results
    totalDataNum.value = orderedTableData.value.length
    currentPage.value = 1
    consultationTableRef.value?.clearSort()
    })
    .catch((err) => {
      console.log(err)
    }).finally(() => {
      getData.value = true
      buttonDisabled.value = false
    })
}
const resetDateOrder = () => {
  orderedTableData.value = originalTableData.slice()
}

const handleCancelButton = (row: ConsultationTableData) => {
  console.log(row)
  consultationIdToBeCanceled.value = row.consultationId
  cancelMessageDialogVisible.value = true
}
const cancelMessageDialogVisible = ref(false)
const consultationIdToBeCanceled = ref('')
const cancelDialogButtonDisabled = ref(false)
const handleConfirmCancelButton = () => {
  cancelDialogButtonDisabled.value = true
  cancelMessageDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-consultation', {
    consultationId: consultationIdToBeCanceled.value
  }).then(() => {
    // console.log(res)
    // getTableData()
    orderedTableData.value = orderedTableData.value.filter((item) => {
      return item.consultationId !== consultationIdToBeCanceled.value
    })
    originalTableData = originalTableData.filter((item) => item.consultationId !== consultationIdToBeCanceled.value)
    totalDataNum.value -= 1
    ElMessage.success('Cancel consultation successfully')
  }).catch((err) => {
    ElMessage({
      type: 'error',
      message: err.response.data.results
    })
  }).finally(() => {
    cancelDialogButtonDisabled.value = false
  })
}

const handleTableSortChange = (param:any)=>{
  const { prop, order } = param
  if (!order) {
    resetDateOrder()
    return
  }
  console.log(prop, order)
  switch (prop) {
    case 'consultationId':
    orderedTableData.value.sort((a, b) => sortConsultationId(a.consultationId, b.consultationId, order))
      break
    case 'time':
      orderedTableData.value.sort((a, b)=>sortTime(a.time, b.time, order))
      break
    case 'department': 
    orderedTableData.value.sort((a, b) => sortDepartment(a.department, b.department, order))
      break
    case 'doctorName':
    orderedTableData.value.sort((a, b) => sortName(a.doctorName, b.doctorName, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

interface ConsultationFilterForm {
  consultationId: string
  startTime: string
  endTime: string
  department: []
  doctorName: []
  isHistory?: boolean
  patientId?: string
}
const consultationFilterForm = ref<ConsultationFilterForm>({
  consultationId: '', 
  startTime: '',
  endTime: '',
  department: [],
  doctorName: [],
})
const consultationFilterFormRef = ref<FormInstance>()

const departmentOptions = ref<string[]>([])
const departmentLoading = ref(false)
const departmentRemoteMethod = (query: string) => {
  if (query) {
    departmentLoading.value = true
    axios.get(rootOfPath + '/get-patient-consultation/department', {
      params: {
        'patientId': config.userId,
        'department': query,
        'isHistory': isHistory.value
      }
    }).then((res) => {
      departmentOptions.value = res.data.results
    }).catch((err) => {
      console.log(err)
    }).finally(() => {
      departmentLoading.value = false
    })
  } else {
    departmentOptions.value = []
  }
}


const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const doctorNameRemoteMethod = (query: string) => {
  if (query) {
    doctorNameLoading.value = true
    axios.get(rootOfPath + '/get-patient-consultation/doctorName', {
      params: {
        'patientId': config.userId,
        'doctorName': query,
        'isHistory': isHistory.value
      }
    }).then((res) => {
      doctorNameOptions.value = res.data.results
    }).catch((err) => {
      console.log(err)
    }).finally(() => {
      doctorNameLoading.value = false
    })
  } else {
    doctorNameOptions.value = []
  }
}


const resetConsultationFilterForm = (form: FormInstance | undefined) => {
  if (!form) return
  form.resetFields()
}


const detailedConsultationId = ref('')
const handleShowDetailButton = (row: ConsultationTableData) => {
  detailedConsultationId.value = row.consultationId
  showDetailMessageDialogVisible.value = true
}
const showDetailMessageDialogVisible = ref(false)
const dialogTitle = ref('Consultation Detail')
const handleChangeTitle = (title: string) => {
  dialogTitle.value = title
}

const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
historyDescriptionItemArrStore.setIndexToZero()
historyDescriptionItemArrStore.setLengthToZero()
const handleDetailDescriptionDialogClose = () => {
  handleChangeTitle('Consultation Detail')  // not necessary
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  detailedDialogPreviousButtonDisabled.value = true
  detailedDialogNextButtonDisabled.value = true
}
const detailedDialogPreviousButtonDisabled = ref(true)
const detailedDialogNextButtonDisabled = ref(true)

historyDescriptionItemArrStore.$subscribe((mutation, state) => {
  console.assert(mutation.type === 'direct')
  
  detailedDialogPreviousButtonDisabled.value = state.descriptionBoxHistoryArrIndex === 0;

  detailedDialogNextButtonDisabled.value = state.descriptionBoxHistoryArrIndex === state.descriptionBoxHistoryArrLength - 1;
})

</script>

<template>
  <el-dialog
    v-model="showDetailMessageDialogVisible"
    :title="dialogTitle"
    :width="config.showDetailDialogWidth"
    destroy-on-close
    @close="handleDetailDescriptionDialogClose"
  >
    <InformationDescriptionBox
      :item-type="DescribableItem.Consultation" 
      :item-id="detailedConsultationId" 
      :show-employee-id="false"
      :show-medicine-id="false"
      @change-title="handleChangeTitle"
    />

    <template #footer>
      <el-button 
        @click="historyDescriptionItemArrStore.decreaseIndexByOne"
        :disabled = "detailedDialogPreviousButtonDisabled"
      >Previous</el-button>
      <el-button 
        @click="historyDescriptionItemArrStore.increaseIndexByOne"
        :disabled = "detailedDialogNextButtonDisabled"
      >Next</el-button>
      <el-button type="primary" @click="showDetailMessageDialogVisible=false">Close</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="cancelMessageDialogVisible"
    title="Cancel Confirmation"
  >

    <span>Are you sure to cancel consultation with ID <el-text tag="b">{{ consultationIdToBeCanceled }}?</el-text> ?</span>

    <template #footer>
      <el-button @click="cancelMessageDialogVisible=false" :disabled="cancelDialogButtonDisabled">Cancel</el-button>
      <el-button type="danger" @click="handleConfirmCancelButton" :disabled="cancelDialogButtonDisabled">Confirm</el-button>
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
            <el-input v-model="consultationFilterForm.consultationId" placeholder="Enter the consultation ID"></el-input>
          </el-form-item>

          <el-form-item label="Time">
            <el-col :span="11">
              <el-form-item prop="startTime">
                <el-date-picker
                    v-model="consultationFilterForm.startTime"
                    type="datetime"
                    placeholder="Select date and time"
                    :disabled-date="disabledDate"
                    style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime">
                <el-date-picker
                    v-model="consultationFilterForm.endTime"
                    type="datetime"
                    placeholder="Select date and time"
                    :disabled-date="disabledDate"
                    style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Department" prop="department">
            <el-select
              v-model="consultationFilterForm.department"
              multiple
              filterable
              remote
              placeholder="Enter the department"
              :remote-method="departmentRemoteMethod"
              :loading = "departmentLoading"
              style="width: 100%"
            >
              <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Doctor Name" prop="doctorName">
            <el-select
              v-model="consultationFilterForm.doctorName"
              multiple
              filterable
              remote
              placeholder="Enter the doctor name"
              :remote-method="doctorNameRemoteMethod"
              :loading = "doctorNameLoading"
              style="width: 100%"
            >
              <el-option v-for="item in doctorNameOptions" :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :disabled="buttonDisabled" @click="getTableData()">Search</el-button>
            <el-button :disabled="buttonDisabled" @click="resetConsultationFilterForm(consultationFilterFormRef)">Reset</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-scrollbar>


    <el-scrollbar>
      <el-table 
        class="table-container" 
        :data="displayedTableData" 
        v-loading="!getData"
        @sort-change="handleTableSortChange"
        ref="consultationTableRef"
      > 
        <el-table-column label="Consultation ID" prop="consultationId" sortable="custom"></el-table-column>
        <el-table-column label="Time" prop="time" sortable="custom"></el-table-column>
        <el-table-column label="Department" prop="department" sortable="custom"></el-table-column>
        <el-table-column label="Doctor Name" prop="doctorName" sortable="custom"></el-table-column>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleShowDetailButton(scope.row)">Show Detail</el-button>
            <el-button type="danger" v-if="!isHistory" size="small" @click="handleCancelButton(scope.row)">Cancel</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="config.tablePageSizeArr"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalDataNum"
        class="pagination-container"
      />
    </el-scrollbar>


  </div>
</template>

<style scoped>

</style>