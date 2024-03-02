<script setup lang="ts">
import { useRouter } from 'vue-router'
import {computed, ref, onMounted, watch} from 'vue'
import  {type FormInstance, type TableInstance, ElMessage } from 'element-plus'
import axios from 'axios';
import { useConfigStore } from '../../stores/config'
import InformationDescriptionBox from '../../components/description/InformationDescriptionBox.vue'
import { DescribableItem } from '../../types/other'
import { useDescriptionBoxHistoryArrStore } from '../../stores/descriptionBoxHistoryArr'
import {
  sortChargeId,
  sortName,
  sortTime,
  sortCost,
  sortDescribableItemId,
  sortPaymentMethod,
} from "../../utils/sort.ts"

interface ChargeTableData {
  chargeId: string
  itemType: string
  itemId: string
  time: string
  cost: string
  paymentMethod: string
}

interface ChargeItemFilterForm {
  chargeId: string
  itemTypeList: string[]
  itemId: string
  beginTime: string
  endTime: string
  beginCost: string
  endCost: string
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
const chargeTableRef = ref<TableInstance>()
const tableDataReady = ref(false)
let originalTableData: ChargeTableData[] = []
const orderedTableData = ref<ChargeTableData[]>([])
const displayedTableData = computed(() => orderedTableData.value?.slice((currentTablePage.value - 1) * tablePageSize.value, currentTablePage.value * tablePageSize.value))

const cancelChargeDialogVisible = ref(false)
const chargeIdToCancel = ref('')
const cancelChargeDialogButtonDisabled = ref(false)
const chargeIdToShowDetail = ref('')

const detailDialogVisible = ref(false)
const detailDialogTitle = ref('Payment Detail')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const chargeFilterFormRef = ref<FormInstance>()
const chargeFilterForm = ref<ChargeItemFilterForm>({
  chargeId: '',
  itemTypeList: [],
  itemId: '',
  beginTime: '',
  endTime: '',
  beginCost: '',
  endCost: '',
})
const formButtonDisabled = ref(false)

const getTableData = () =>{
  formButtonDisabled.value = true
  tableDataReady.value = false

  const submitValue = { ...chargeFilterForm.value }
  submitValue.isHistory = isHistory.value
  submitValue.patientId = config.userId

  axios.get(rootOfPath + '/get-patient-charge', { params: submitValue })
    .then((response) => {
      originalTableData = response.data.results.slice()
      orderedTableData.value = response.data.results
      totalDataNumber.value = response.data.results.length
      currentTablePage.value = 1
      chargeTableRef.value?.clearSort()
    })
    .catch((error) => {
      console.log(error)
    }).finally(() => {
    formButtonDisabled.value = false
    tableDataReady.value = true
  })
}

const handleTableSortChange = (param:any)=>{
  const { prop, order } = param
  if (!order){
    orderedTableData.value = originalTableData.slice()
    return
  }
  switch (prop) {
    case 'chargeId':
      orderedTableData.value.sort((a, b)=>sortChargeId(a.chargeId, b.chargeId, order))
      break
    case 'itemType':
      orderedTableData.value.sort((a, b)=>sortName(a.itemType, b.itemType, order))
      break
    case 'itemId':
      orderedTableData.value.sort((a, b)=>sortDescribableItemId(a.itemId, b.itemId, order))
      break
    case 'time':
      orderedTableData.value.sort((a, b)=>sortTime(a.time, b.time, order))
      break
    case 'cost':
      orderedTableData.value.sort((a, b)=>sortCost(String(a.cost), String(b.cost), order))
      break
    case 'paymentMethod':
      orderedTableData.value.sort((a, b)=>sortPaymentMethod(a.paymentMethod, b.paymentMethod, order))
      break
    default:
      console.error('Invalid prop: ' + prop )
  }
}

const handleTableCancelButton = (row: ChargeTableData)=>{
  cancelChargeDialogButtonDisabled.value = false
  chargeIdToCancel.value = row.chargeId
  cancelChargeDialogVisible.value = true
}

const handleConfirmCancelChargeButton = () => {
  cancelChargeDialogButtonDisabled.value = true
  cancelChargeDialogVisible.value = false
  axios.post(rootOfPath + '/patient/cancel-charge', {hospitalizationId: chargeIdToCancel.value})
    .then(() => {
      orderedTableData.value = orderedTableData.value.filter((item) => item.chargeId !== chargeIdToCancel.value)
      ElMessage.success('Refund successfully')
    })
    .catch((error) => {
      ElMessage.error(error.response.data.results)
    })
}

const handleChangeDetailDialogTitle = (title:string) => {
  detailDialogTitle.value = title
}

const handleTableShowDetailButton = (row: ChargeTableData) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  chargeIdToShowDetail.value = row.chargeId
  handleChangeDetailDialogTitle('Payment Detail')
  detailDialogVisible.value = true
}

const disabledDateInForm = (time: Date) => isHistory.value ? time.getTime() > Date.now() : time.getTime() < Date.now() - 3600 * 24 * 1000

const resetChargeFilterForm = (form: FormInstance | undefined) => {
  if (form) {
    form.resetFields()
  }
}

onMounted(() => {
  getTableData()
})

watch(() => router.currentRoute.value.path, () => {
  resetChargeFilterForm(chargeFilterFormRef.value)
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
      :item-type="DescribableItem.Charge"
      :item-id="chargeIdToShowDetail"
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
    v-model="cancelChargeDialogVisible"
    title="Refund Charge"
  >
    <span>Are you sure to submit a refund request with ID <el-text tag="b">{{ chargeIdToCancel }}</el-text> ?</span>

    <template #footer>
      <el-button
        @click="cancelChargeDialogVisible = false"
        :disabled="cancelChargeDialogButtonDisabled"
      >Refuse</el-button>
      <el-button
        type="danger"
        @click="handleConfirmCancelChargeButton"
        :disabled="cancelChargeDialogButtonDisabled"
      >Confirm</el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto">
    <el-scrollbar>
      <div class="form-container">
        <el-form
          ref="chargeFilterFormRef"
          :model="chargeFilterForm"
          label-position="top"
        >
          <el-form-item label="Charge ID" prop="chargeId">
            <el-input v-model="chargeFilterForm.chargeId" placeholder="Enter the charge ID"/>
          </el-form-item>

          <el-form-item label="Item Type" prop="itemTypeList">
            <el-select
              v-model="chargeFilterForm.itemTypeList"
              multiple
              placeholder="Select Item Type"
              style="width: 100%"
            >
              <el-option :value="DescribableItem.Consultation"/>
              <el-option :value="DescribableItem.Prescription"/>
              <el-option :value="DescribableItem.Examination"/>
              <el-option :value="DescribableItem.Rehabilitation"/>
              <el-option :value="DescribableItem.Surgery"/>
              <el-option :value="DescribableItem.Hospitalization"/>
            </el-select>

          </el-form-item>

          <el-form-item label="Item ID" prop="itemId">
            <el-input v-model="chargeFilterForm.itemId" placeholder="Enter the item ID"/>
          </el-form-item>

          <el-form-item label="Time">
            <el-col :span="11">
              <el-form-item prop="beginTime">
                <el-date-picker
                  v-model="chargeFilterForm.beginTime"
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
                  v-model="chargeFilterForm.endTime"
                  type="datetime"
                  placeholder="Select date and time"
                  :disabledDate="disabledDateInForm"
                  style="width: 100%"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="Cost">
            <el-col :span="11">
              <el-form-item prop="beginCost">
                <el-input v-model="chargeFilterForm.beginCost" placeholder="Enter cost"/>
              </el-form-item>
            </el-col>
            <el-col :span="2" style="text-align: center;">-</el-col>
            <el-col :span="11">
              <el-form-item prop="endCost">
                <el-input v-model="chargeFilterForm.endCost" placeholder="Enter cost"/>
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :disabled="formButtonDisabled" @click="getTableData">Search</el-button>
            <el-button :disabled="formButtonDisabled" @click="resetChargeFilterForm(chargeFilterFormRef)">Reset</el-button>
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
        ref="chargeTableRef"
      >
        <el-table-column label="Charge ID" prop="chargeId" sortable="custom"/>
        <el-table-column label="Item Type" prop="itemType" sortable="custom"/>
        <el-table-column label="Item ID" prop="itemId" sortable="custom"/>
        <el-table-column v-if="isHistory" label="Time" prop="time" sortable="custom"/>
        <el-table-column v-if="isHistory" label="Payment Method" prop="paymentMethod" sortable="custom"/>
        <el-table-column label="Cost" prop="cost" sortable="custom"/>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleTableShowDetailButton(scope.row)">Show Detail</el-button>
            <el-button type="danger" v-if="isHistory" size="small" @click="handleTableCancelButton(scope.row)">Refund</el-button>
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