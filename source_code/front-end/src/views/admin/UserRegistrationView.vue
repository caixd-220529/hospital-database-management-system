<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {ElMessage, type FormInstance, type TableInstance} from 'element-plus'
import axios from 'axios';
import {useConfigStore} from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import {useDescriptionBoxHistoryArrStore} from '../../stores/descriptionBoxHistoryArr'
import {DescribableItem} from "../../types/other.ts"
import {sortName, sortTime, sortUserId, sortUserType} from "../../utils/sort.ts"

interface FilterForm {
  userType: string,
  beginTime: string
  endTime: string
}

interface TableData {
  userId: string,
  userName: string,
  userType: string,
  registerTime: string,
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const currentTablePage = ref(1)
const tablePageSize = ref(config.defaultPageSize)
const totalDataNumber = ref(0)
const tableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: TableData[] = []
const orderedTableData = ref<TableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const filterFormRef = ref<FormInstance>()
const filterForm = ref<FilterForm>({
  userType: '',
  beginTime: '',
  endTime: ''
})
const formButtonDisabled = ref(false)

const confirmDialogVisible = ref(false)
const confirmButtonDialogDisabled = ref(false)
// const confirmDialogContent = ref<string>('')
const userTypeToConfirm = ref('')
const userIdToConfirm = ref('')
const actionTypeToConfirm = ref('')

const itemIdToShowDetail = ref('')
const itemTypeToShowDetail = ref<DescribableItem>(DescribableItem.Patient)
const detailDialogVisible = ref(false)
const detailDialogTitle = ref('No initialization :(')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const getTableData = () => {
  formButtonDisabled.value = true
  tableDataReady.value = false

  axios.get(rootOfPath + '/admin/get-registration-waiting-list',
    {params: {
      userType: filterForm.value.userType,
      beginTime: filterForm.value.beginTime,
      endTime: filterForm.value.endTime
      }})
    .then((response)=>{
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      tableRef.value?.clearSort()
      
      orderedTableData.value.forEach((item: TableData) => {
        console.assert(['doctor', 'nurse', 'helping staff'].includes(item['userType']), 'Invalid userType: ' + item['userType'])
      })
    })
    .catch((error)=>{
      ElMessage.error(error.response.data.message)
    })
    .finally(()=>{
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
  switch (prop){
    case 'userId':
      orderedTableData.value.sort((a, b) => sortUserId(a.userId, b.userId, order))
      break
    case 'userName':
      orderedTableData.value.sort((a, b) => sortName(a.userName, b.userName, order))
      break
    case 'userType':
      orderedTableData.value.sort((a, b) => sortUserType(a.userType, b.userType, order))
      break
    case 'registerTime':
      orderedTableData.value.sort((a, b) => sortTime(a.registerTime, b.registerTime, order))
      break
  }
}

const resetFilterForm = () => {
  filterForm.value = {
    userType: '',
    beginTime: '',
    endTime: ''
  }
}

const handleAllowDisAllowButton = (actionType: string, userId:string, userType: string) => {
  console.assert(actionType === 'allow' || actionType === 'disallow', 'type must be accept or reject')
  userTypeToConfirm.value = userType
  actionTypeToConfirm.value = actionType
  userIdToConfirm.value = userId
  confirmButtonDialogDisabled.value = false
  confirmDialogVisible.value = true
}

const handleConfirmDialogConfirm = () => {
  confirmButtonDialogDisabled.value = true
  confirmDialogVisible.value = false
  axios.post(rootOfPath + `/admin/registration/${actionTypeToConfirm.value}`, {
    userId: userIdToConfirm.value,
    userType: userTypeToConfirm.value
  })
    .then(()=>{
      ElMessage.success('Success')
      orderedTableData.value = orderedTableData.value.filter((item) => item.userId !== userIdToConfirm.value||item.userType !== userTypeToConfirm.value)
      originalTableData = originalTableData.filter((item) => item.userId !== userIdToConfirm.value||item.userType !== userTypeToConfirm.value)
      totalDataNumber.value -= 1
    })
    .catch((err) => {
      ElMessage.error(err.response.data.message)
    })
}

const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleShowDetailButton = (itemId: string, itemTypeString: string) => {
  let itemType = DescribableItem.Patient
  switch (itemTypeString) {
    case 'doctor':
      itemType = DescribableItem.Doctor
      break
    case 'nurse':
      itemType = DescribableItem.Nurse
      break
    case 'helping staff':
      itemType = DescribableItem.HelpingStaff
      break
    default:
      console.error('Invalid itemTypeString: ' + itemTypeString)
  }
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  itemIdToShowDetail.value = itemId
  itemTypeToShowDetail.value = itemType
  switch (itemType) {
    case DescribableItem.Doctor:
      handleChangeDetailDialogTitle('Doctor Detail')
      break
    case DescribableItem.Nurse:
      handleChangeDetailDialogTitle('Nurse Detail')
      break
    case DescribableItem.HelpingStaff:
      handleChangeDetailDialogTitle('Helping Staff Detail')
      break
    default:
      console.error('Invalid itemType: ' + itemType)
  }
  detailDialogVisible.value = true
}

const disableDate = (time: Date) => {
  return time.getTime() > Date.now()
}

onMounted(() => {
  getTableData()
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
      :show-employee-id="true"
      :show-medicine-id="true"
      :show-room-detail="true"
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
    title="Confirm"
    v-model="confirmDialogVisible"
  >
    <span>Are you sure to
      <span v-if="actionTypeToConfirm==='allow'">
        allow
      </span>
      <span v-else>
        disallow
      </span>
      the user with ID <el-text tag="b">{{userIdToConfirm}}</el-text> to register?</span>
    <template #footer>
      <el-button type="primary" @click="handleConfirmDialogConfirm" :disabled="confirmButtonDialogDisabled">Confirm</el-button>
      <el-button @click="confirmDialogVisible = false" :disabled="confirmButtonDialogDisabled">Cancel</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="filterFormRef"
          :model="filterForm"
          label-position="top"
        >
          <el-form-item label="User Type">
            <el-select v-model="filterForm.userType" placeholder="Select user type" style="width: 100%">
              <el-option label="Doctor" value="doctor"></el-option>
              <el-option label="Nurse" value="nurse"></el-option>
              <el-option label="Helping Staff" value="helping staff"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Registration Time" >
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="filterForm.beginTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disableDate"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endTime">
                <el-date-picker
                  v-model="filterForm.endTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disableDate"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="getTableData" :disabled="formButtonDisabled">Search</el-button>
            <el-button @click="resetFilterForm" :disabled="formButtonDisabled">Reset</el-button>
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
        ref="tableRef"
      >
        <el-table-column prop="userId" label="User ID" sortable/>
        <el-table-column prop="userName" label="User Name" sortable/>
        <el-table-column prop="userType" label="User Type" sortable/>
        <el-table-column prop="registerTime" label="Register Time" sortable/>
        <el-table-column label="Detail">
          <template #default="{row}">
            <el-button
              type="primary"
              size="small"
              @click="handleShowDetailButton(row.userId, row.userType)"
            >Show Detail</el-button>
          </template>
        </el-table-column>
        <el-table-column label="Action">
          <template #default="{row}">
            <el-button
              type="success"
              size="small"
              @click="handleAllowDisAllowButton('allow', row.userId, row.userType)"
            >Allow</el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleAllowDisAllowButton('disallow', row.userId, row.userType)"
            >Disallow</el-button>
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