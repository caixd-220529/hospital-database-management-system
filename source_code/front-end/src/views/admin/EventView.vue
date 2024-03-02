<script setup lang="ts">
import DynamicForm from "../../components/DynamicForm.vue"
import DynamicTable from "../../components/DynamicTable.vue"
import {useRouter} from "vue-router"
import {computed, ref, Ref, onMounted, watch} from "vue"
import {DescribableItem} from "../../types/other.ts";
import {useDescriptionBoxHistoryArrStore} from "../../stores/descriptionBoxHistoryArr.ts";
import InformationDescriptionBox from "../../components/description/InformationDescriptionBox.vue";
import {useConfigStore} from "../../stores/config.ts";
import axios from "axios"
import {ElMessage} from "element-plus";

const router = useRouter()
const itemName = computed(()=>{
  return router.currentRoute.value.path.split('/')[3]
})
const config = useConfigStore()
const rootOfPath = config.rootOfPath

const collapseActiveItem = ref<string[]>(['search'])
// const collapseActiveItem = ref<string[]>([])
const searchCollapseTitle = ref<string>('Hide Filter Form')
const addCollapseTitle = ref<string>('Show Add Form')
const addCollapseVisible = ref<boolean>(false)
const clearCollapseTitle = ref<string>('Show Clear User Button')
const clearCollapseVisible = computed(()=>['patient', 'doctor', 'nurse', 'helping-staff'].includes(router.currentRoute.value.path.split('/')[3]))

const formGetNewDataFlag = ref<string>(String(Date.now()))
const submitEditFormFlag = ref<string>(String(Date.now()))
const resetEditFormFlag = ref<string>(String(Date.now()))

const tableDataReady = ref(false)
const tableData = ref([])
const tableKeyPropName = ref('')
const resetTableDataFlag = ref<string>(String(Date.now()))

const itemTypeToShowDetail = ref<DescribableItem>(DescribableItem.Consultation)
const itemIdToShowDetail = ref<string>('')
const detailDialogVisible = ref(false)
const detailDialogTitle = ref('No initialization')
const historyDescriptionItemArrStore = useDescriptionBoxHistoryArrStore()
const detailedDialogPreviousButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === 0)
const detailedDialogNextButtonDisabled = computed(() => historyDescriptionItemArrStore.descriptionBoxHistoryArrIndex === historyDescriptionItemArrStore.descriptionBoxHistoryArrLength - 1)

const deleteDialogVisible = ref(false)
const itemIdToDelete = ref('')

const editDialogVisible = ref(false)
const itemIdToEdit = ref('')

const clearDeletedUserDialogVisible = ref(false)

const changeFlag = (flag: Ref<string>)=>{
  flag.value = String(Date.now())
}
const isTrue = (value: string)=>{
  return value === 'true'
}
const handleCollapseChange = (activeNames: string[]) => {
  activeNames.includes('search') ? searchCollapseTitle.value = 'Hide Filter Form' : searchCollapseTitle.value = 'Show Filter Form'
  activeNames.includes('add') ? addCollapseTitle.value = 'Hide Add Form' : addCollapseTitle.value = 'Show Add Form'
  activeNames.includes('clear') ? clearCollapseTitle.value = 'Hide Clear User Button' : clearCollapseTitle.value = 'Show Clear User Button'
}
const handleResetTableData = (data: []) => {
  changeFlag(resetTableDataFlag)
  tableData.value = data.slice()
}
const handleSetTableDataNotReady = () => {
  tableDataReady.value = false
}
const handleSetTableDataReady = () => {
  tableDataReady.value = true
}
const handleTableDataChange = () => {
  changeFlag(formGetNewDataFlag)
}
const handleChangeDetailDialogTitle = (title: string) => {
  detailDialogTitle.value = title
}

const handleShowDetailDialog = (itemType: DescribableItem, itemId: string) => {
  historyDescriptionItemArrStore.setIndexToZero()
  historyDescriptionItemArrStore.setLengthToZero()
  itemTypeToShowDetail.value = itemType
  switch (itemType){
    case DescribableItem.Consultation:
      handleChangeDetailDialogTitle('Consultation Detail')
      break
    case DescribableItem.Prescription:
      handleChangeDetailDialogTitle('Prescription Detail')
      break
    case DescribableItem.Examination:
      handleChangeDetailDialogTitle('Examination Detail')
      break
    case DescribableItem.Rehabilitation:
      handleChangeDetailDialogTitle('Rehabilitation Detail')
      break
    case DescribableItem.Surgery:
      handleChangeDetailDialogTitle('Surgery Detail')
      break
    case DescribableItem.Hospitalization:
      handleChangeDetailDialogTitle('Hospitalization Detail')
      break
    case DescribableItem.Patient:
      handleChangeDetailDialogTitle('Patient Detail')
      break
    case DescribableItem.Doctor:
      handleChangeDetailDialogTitle('Doctor Detail')
      break
    case DescribableItem.Nurse:
      handleChangeDetailDialogTitle('Nurse Detail')
      break
    case DescribableItem.HelpingStaff:
      handleChangeDetailDialogTitle('Helping Staff Detail')
      break
    case DescribableItem.PrescriptionMedicine:
      handleChangeDetailDialogTitle('Medicine Detail')
      break
    case DescribableItem.SurgeryRecord:
      handleChangeDetailDialogTitle('Surgery Record Detail')
      break
    case DescribableItem.Room:
      handleChangeDetailDialogTitle('Room Detail')
      break
    default:
      console.error('Unknown item type')
  }
  itemIdToShowDetail.value = itemId
  detailDialogVisible.value = true
}
const handleShowDeleteDialog = (_tableKeyPropName: string, itemId: string) => {
  itemIdToDelete.value = itemId
  tableKeyPropName.value = _tableKeyPropName
  deleteDialogVisible.value = true
}

const handleShowEditDialog = (_tableKeyPropName: string, itemId: string) => {
  itemIdToEdit.value = itemId
  tableKeyPropName.value = _tableKeyPropName
  editDialogVisible.value = true
}
const handleCloseEditFormSurroundingDialog =()=> {
  editDialogVisible.value = false
}
const handleSubmitEditForm = () => {
  changeFlag(submitEditFormFlag)
}
const handleResetEditForm = () => {
  changeFlag(resetEditFormFlag)
}
const handleConfirmDelete = (type: string='')=>{
  axios.post(rootOfPath+'/admin/delete',
    {
      itemName: itemName.value,
      itemId: itemIdToDelete.value,
      isCascade: type==='cascade'?'true':'false'
    })
    .then((res)=>{
      ElMessage.success('Delete successfully')
      if(isTrue(res.data.results.onlyRemoveOneRecord)){
        tableData.value = tableData.value.filter((item: any)=>{
          return item[tableKeyPropName.value] !== itemIdToDelete.value
        })
      }else{
        formGetNewDataFlag.value = String(Date.now())
      }
    })
    .catch((error)=>{
      ElMessage.error(error.response.data.results)
    })
  deleteDialogVisible.value = false
}

const addFromVisibleDecision = ()=>{
  axios.get(rootOfPath + '/admin/can-add', {params: {itemName: itemName.value}})
    .then((res)=>{
      addCollapseVisible.value = isTrue(res.data.results)
    })
    .catch((err)=>{
      console.error(err)
    })
}

// the button of clear users that are deleted
const handleClearDeletedUsers = ()=>{
  clearDeletedUserDialogVisible.value = false
  axios.post(rootOfPath + '/admin/clear-deleted-users', {itemName: itemName.value})
    .then(()=>{
      ElMessage.success('Clear successfully')
    })
    .catch((err)=>{
      ElMessage.error(err.response.data.results)
    })
}

onMounted(()=>{
  addFromVisibleDecision()
})
watch(itemName, ()=>{
  addFromVisibleDecision()
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
      :item-type= "itemTypeToShowDetail"
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
    v-model="deleteDialogVisible"
    title="Delete Record"
    destroy-on-close
  >
    Are you sure to delete the record whose primary key is <el-text tag="b">{{itemIdToDelete}}</el-text>
    <template #footer>
      <el-button
        @click="deleteDialogVisible = false"
      >Cancel
      </el-button>
      <el-button
        type="danger"
        @click="handleConfirmDelete"
      >Delete
      </el-button>
      <!--   disable the button below since the lack of time   -->
      <el-button
        type="danger"
        @click="handleConfirmDelete('cascade')"
        v-if="false"
      >Delete cascade
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="editDialogVisible"
    title="Edit Record"
    destroy-on-close
  >
    <div style="height: 60vh; margin: 0 auto;">
      <el-scrollbar>
        <div class="form-container">
          <DynamicForm
            :itemName="itemName"
            :edit-item-id="itemIdToEdit"
            :submit-form-flag="submitEditFormFlag"
            :reset-form-flag="resetEditFormFlag"
            show-form-button="false"
            form-type="edit"
            @setTableDataNotReady="handleSetTableDataNotReady"
            @tableDataChange="handleTableDataChange"
            @closeSurroundingDialog="handleCloseEditFormSurroundingDialog"
          />
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button
        @click="editDialogVisible = false"
      >Cancel
      </el-button>
      <el-button
        @click="handleResetEditForm"
      >Reset
      </el-button>
      <el-button
        type="primary"
        @click="handleSubmitEditForm"
      >Submit
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="clearDeletedUserDialogVisible"
    title="Clear Deleted User"
  >
    <el-text>Are you sure to clear all the deleted users?</el-text>
    <template #footer>
      <el-button
        @click="clearDeletedUserDialogVisible = false"
      >Cancel
      </el-button>
      <el-button
        type="danger"
        @click="handleClearDeletedUsers"
      >Clear
      </el-button>
    </template>
  </el-dialog>

  <div style="margin: 0 auto;">
    <el-scrollbar>
      <div class="form-container">
        <el-collapse v-model="collapseActiveItem" @change="handleCollapseChange">
          <el-collapse-item name="search">
            <template #title>
              <el-text type="info">{{searchCollapseTitle}}</el-text>
            </template>
            <DynamicForm
              :itemName="itemName"
              form-type="search"
              :get-new-data-flag="formGetNewDataFlag"
              @resetTableData="handleResetTableData"
              @setTableDataNotReady="handleSetTableDataNotReady"
              @setTableDataReady="handleSetTableDataReady"
            />
          </el-collapse-item>
          <el-collapse-item name="add" v-if="addCollapseVisible">
            <template #title>
              <el-text type="info">{{addCollapseTitle}}</el-text>
            </template>
            <DynamicForm
              :itemName="itemName"
              form-type="add"
              @setTableDataNotReady="handleSetTableDataNotReady"
              @setTableDataReady="handleSetTableDataReady"
              @tableDataChange="handleTableDataChange"
            />
          </el-collapse-item>
          <el-collapse-item name="clear" v-if="clearCollapseVisible">
            <template #title>
              <el-text type="info">{{clearCollapseTitle}}</el-text>
            </template>
            <div><el-text>Click the button bellow to clear all deleted users</el-text></div>
            <el-button
              type="danger"
              @click="clearDeletedUserDialogVisible = true"
            >
              Clear User
            </el-button>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-scrollbar>

    <el-scrollbar>
      <div class="table-container">
        <DynamicTable
          :item-name="itemName"
          :table-data="tableData"
          :table-data-ready="tableDataReady"
          :rest-table-data="resetTableDataFlag"
          @show-detail-dialog="handleShowDetailDialog"
          @show-delete-dialog="handleShowDeleteDialog"
          @show-edit-dialog="handleShowEditDialog"
        />
      </div>
    </el-scrollbar>
  </div>


</template>

<style scoped>

</style>