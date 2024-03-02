<script setup lang="ts">
import {computed, ref, onMounted} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import {departmentRemoteMethod} from "../../utils/remote.ts"
import {sortCost, sortDepartment, sortName, sortPosition, sortTime} from "../../utils/sort.ts"

interface AppointmentTableData {
  department: string
  position: string
  doctorName: string
  doctorId: string
  time: string
  cost: string
  patientId?: string
}

interface AppointmentFilterForm {
  department: string
  doctorName: string
  beginTime: string
  endTime: string
  patientId?: string
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const appointmentTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: AppointmentTableData[] = []
const orderedTableData = ref<AppointmentTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const scheduleDialogVisible = ref(false)
const scheduleDialogButtonDisabled = ref(false)
const appointToSchedule = ref<AppointmentTableData>()
const consultationIdAfterConfirm = ref('')
const showConsultationIdDialogVisible = ref(false)

const appointmentFilterFormRef = ref<FormInstance>()
const appointmentFilterForm = ref<AppointmentFilterForm>({
  department: '',
  doctorName: '',
  beginTime: '',
  endTime: ''
})
const departmentOptions = ref<string[]>([])
const departmentLoading = ref(false)
const formButtonDisabled = ref(false)

const getTableData = ()=>{
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = { ...appointmentFilterForm.value }
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-appointment', {params: submitValue})
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      appointmentTableRef.value?.clearSort()
    })
    .catch((error)=>{
      console.log(error)
    })
    .finally(()=>{
      formButtonDisabled.value = false
      tableDataReady.value = true
    })
}

const handleTableSortChange = (param:any)=>{
  const {prop, order} = param
  if(!order){
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch(prop){
    case 'department':
      orderedTableData.value.sort((a, b) => sortDepartment(a.department, b.department, order))
      break
    case 'doctorName':
      orderedTableData.value.sort((a, b) => sortName(a.doctorName, b.doctorName, order))
      break
    case 'time':
      orderedTableData.value.sort((a, b) => sortTime(a.time, b.time, order))
      break
    case 'cost':
      orderedTableData.value.sort((a, b) => sortCost(String(a.cost), String(b.cost), order))
      break
    case 'position':
      orderedTableData.value.sort((a, b) => sortPosition(a.position, b.position, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableScheduleButton = (row: AppointmentTableData)=>{
  scheduleDialogButtonDisabled.value = false
  appointToSchedule.value = row
  scheduleDialogVisible.value = true
}

const handleConfirmScheduleButton = () => {
  scheduleDialogButtonDisabled.value = false
  scheduleDialogVisible.value = false

  const submitValue = { ...appointToSchedule.value }
  submitValue.patientId = config.userId
  axios.post(rootOfPath + '/patient/schedule-appointment', submitValue)
    .then((response)=>{
      consultationIdAfterConfirm.value = response.data.results.consultationId
      showConsultationIdDialogVisible.value = true
      getTableData()
    })
    .catch((error)=>{
      ElMessage.error(error.response.data.results)
    })
}

const disabledDateInForm = (time: Date) => time.getTime() < Date.now() - 3600 * 24 * 1000

const resetAppointmentFilterForm = ()  =>{
  appointmentFilterFormRef.value?.resetFields()
}

const appointmentRemoteMethod = (query:string) =>{
  departmentRemoteMethod(query, departmentOptions, departmentLoading)
}

onMounted(()=>{
  getTableData()
})
</script>

<template>
  <el-dialog
    v-model="showConsultationIdDialogVisible"
    title="Success"
  >
    <span>You have already scheduled a consultation. You consultation ID is {{consultationIdAfterConfirm}}</span>
    <template #footer>
      <el-button
        type="primary"
        @click="showConsultationIdDialogVisible = false"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="scheduleDialogVisible"
    title="Schedule Appointment"
  >
    <span>Are you sure to schedule this appointment?</span>
    <template #footer>
      <el-button
        @click="scheduleDialogVisible = false"
        :disabled="scheduleDialogButtonDisabled"
      >Cancel</el-button>
      <el-button
        type="primary"
        @click="handleConfirmScheduleButton"
        :disabled="scheduleDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="appointmentFilterFormRef"
          :model="appointmentFilterForm"
          label-position="top"
        >
          <el-form-item label="Department" prop="department">
           <el-select
             v-model="appointmentFilterForm.department"
             filterable
             remote
             reserve-keyword
             clearable
             :remote-method="appointmentRemoteMethod"
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

          <el-form-item label="Doctor Name" prop="doctorName">
            <el-input v-model="appointmentFilterForm.doctorName" placeholder="Enter doctor name"></el-input>
          </el-form-item>

          <el-form-item label="Time">
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="appointmentFilterForm.beginTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime">
                <el-date-picker
                  v-model="appointmentFilterForm.endTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              @click="getTableData"
              :disabled="formButtonDisabled"
            >Search</el-button>
            <el-button
              @click="resetAppointmentFilterForm"
              :disabled="formButtonDisabled"
            >Reset</el-button>
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
        ref="appointmentTableRef"
      >
        <el-table-column label="Department" prop="department" sortable="custom"/>
        <el-table-column label="Doctor Name" prop="doctorName" sortable="custom"/>
        <el-table-column label="Position" prop="position" sortable="custom"/>
        <el-table-column label="Time" prop="time" sortable="custom"/>
        <el-table-column label="Cost" prop="cost" sortable="custom"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleTableScheduleButton(scope.row)"
            >Schedule</el-button>
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