<script setup lang="ts">
import {ref, onMounted, watch} from "vue"
import {type FormInstance} from "element-plus"
import axios from "axios"
import {useConfigStore} from "../stores/config.ts"
import {
  departmentRemoteMethod,
  patientNameRemoteMethod,
  doctorNameRemoteMethod,
  examinationNameRemoteMethod,
  rehabilitationNameRemoteMethod,
  medicineNameRemoteMethod,
  surgerySiteRemoteMethod,
  surgeryNameRemoteMethod,
  nurseNameRemoteMethod,
  helpingStaffNameRemoteMethod
} from "../utils/remote.ts"
import {ElMessage} from "element-plus"

const props = defineProps({
  itemName: {
    type: String,
    require: true,
  },
  formType: {
    // can only be 'search', 'edit', 'add'
    type: String,
    require: true,
  },
  getNewDataFlag: {
    // when the flag changes, get new data from server anyway
    type: String,
    require: false,
    default: ''
  },
  editItemId: {
    // only valid when formType is 'edit'
    type: String,
    require: false,
  },
  submitFormFlag: {
    // when the flag changes, submit the form anyway
    type: String,
    require: false,
    default: ''
  },
  resetFormFlag: {
    // when the flag changes, reset the form anyway
    type: String,
    require: false,
    default: ''
  },
  showFormButton: {
    // can only be 'true' or 'false'
    type: String,
    require: false,
    default: 'true'
  },
})
const emit = defineEmits<{
  resetTableData: [data: []]
  setTableDataNotReady: []
  setTableDataReady: []
  tableDataChange: []
  closeSurroundingDialog: []
}>()

interface DomainItem {
  // if isMultiple is 'true', minNum and maxNum must be set
  // if needRemoteMethod is 'true', 'isInterval' must be 'false'
  // if type is 'enumerate', enumerateValue must be set, and 'isInterval' and 'needRemoteMethod' must be 'false'
  prop: string  // must be unique, must in camel case. e.g. 'patientName'
  label: string  // the label of the item. e.g. 'Patient Name'
  disabled: string | boolean  // can only be 'true' or 'false'
  type: string  // can only be 'string', 'date', 'enumerate'
  isInterval: string  // can only be 'true' or 'false'
  enumerateValue: string[]  // only valid when type is 'enumerate'
  isMultiple: string  // only valid when type is 'enumerate', can only be 'true' or 'false'
  minNum: string | number//only valid when the type is 'enumerate' and isMultiple is 'true'
  maxNum: string | number //only valid when the type is 'enumerate' and isMultiple is 'true'

  needRemoteMethod: string // can only be 'true' or 'false', take the OR operation of the following items
  isPatientName: string // can only be 'true' or 'false'
  isDoctorName: string // can only be 'true' or 'false'
  isNurseName: string // can only be 'true' or 'false'
  isHelpingStaffName: string // can only be 'true' or 'false'
  isExaminationName: string // can only be 'true' or 'false'
  isRehabilitationName: string // can only be 'true' or 'false'
  isMedicineName: string // can only be 'true' or 'false'
  isSurgerySite: string // can only be 'true' or 'false'
  isSurgeryName: string // can only be 'true' or 'false'
  isDepartment: string // can only be 'true' or 'false'

  value: string  //  used to store the value when isInterval is 'false'
  beginValue: string  // used to store the lower bound when isInterval is 'true'
  endValue: string  // used to store the upper bound when isInterval is 'true'
  multipleValue: string[] // only valid when isMultiple is 'true'

  rules: {
    required: string | boolean  // can only be 'true' or 'false'
    message: string  // the message to show when the item is required but not filled
    trigger: string  // can only be 'blur' or 'change'
  },
  beginRules: {
    required: string | boolean  // can only be 'true' or 'false'
    message: string  // the message to show when the item is required but not filled
    trigger: string  // can only be 'blur' or 'change'
  },
  endRules: {
    required: string | boolean  // can only be 'true' or 'false'
    message: string  // the message to show when the item is required but not filled
    trigger: string  // can only be 'blur' or 'change'
  }
}

const config = useConfigStore()
const rootOfPath = config.rootOfPath

const formRef = ref<FormInstance>()
const dynamicForm = ref<DomainItem[]>([])
let editFormInitialValue: DomainItem[] = []
const formButtonDisabled = ref(false)

const patientNameOptions = ref<string[]>([])
const patientNameLoading = ref(false)
const doctorNameOptions = ref<string[]>([])
const doctorNameLoading = ref(false)
const examinationNameOptions = ref<string[]>([])
const examinationNameLoading = ref(false)
const rehabilitationNameOptions = ref<string[]>([])
const rehabilitationNameLoading = ref(false)
const medicineNameOptions = ref<string[]>([])
const medicineNameLoading = ref(false)
const surgerySiteOptions = ref<string[]>([])
const surgerySiteLoading = ref(false)
const surgeryNameOptions = ref<string[]>([])
const surgeryNameLoading = ref(false)
const departmentOptions = ref<string[]>([])
const departmentLoading = ref(false)
const nurseNameOptions = ref<string[]>([])
const nurseNameLoading = ref(false)
const helpingStaffNameOptions = ref<string[]>([])
const helpingStaffNameLoading = ref(false)

const _patientNameRemoteMethod = (query: string) => {
  patientNameRemoteMethod(query, config.userName, config.userType, patientNameOptions, patientNameLoading)
}
const _doctorNameRemoteMethod = (query: string) => {
  doctorNameRemoteMethod(query, config.userName, config.userType, doctorNameOptions, doctorNameLoading)
}
const _nurseNameRemoteMethod = (query: string) => {
  nurseNameRemoteMethod(query, config.userName, config.userType, nurseNameOptions, nurseNameLoading)
}
const _helpingStaffNameRemoteMethod = (query: string) => {
  helpingStaffNameRemoteMethod(query, config.userName, config.userType, helpingStaffNameOptions, helpingStaffNameLoading)
}
const _examinationNameRemoteMethod = (query: string) => {
  examinationNameRemoteMethod(query, examinationNameOptions, examinationNameLoading)
}
const _rehabilitationNameRemoteMethod = (query: string) => {
  rehabilitationNameRemoteMethod(query, rehabilitationNameOptions, rehabilitationNameLoading)
}
const _medicineNameRemoteMethod = (query: string) => {
  medicineNameRemoteMethod(query, medicineNameOptions, medicineNameLoading)
}
const _surgerySiteRemoteMethod = (query: string) => {
  surgerySiteRemoteMethod(query, surgerySiteOptions, surgerySiteLoading)
}
const _surgeryNameRemoteMethod = (query: string) => {
  surgeryNameRemoteMethod(query, '', surgeryNameOptions, surgeryNameLoading)
}
const _departmentRemoteMethod = (query: string) => {
  departmentRemoteMethod(query, departmentOptions, departmentLoading)
}

const isTrue = (value: string): boolean => {
  return value === 'true'
}

const getFormInfo = async () => {
  let params = {
    itemName: props.itemName,
    formType: props.formType,
    editItemId: props.editItemId,
  }
  if (props.formType === 'add') {
    delete params.editItemId
  }
  await axios.get(rootOfPath + '/admin/get-form-info',
    {
      params: params
    }
  )
    .then((response) => {
      dynamicForm.value = response.data.results
      dynamicForm.value.forEach((item) => {
        console.assert(item.type === 'string' || item.type === 'date' || item.type === 'enumerate')

        console.assert(item.rules.required === 'true' || item.rules.required === 'false')
        console.assert(item.rules.trigger === 'blur' || item.rules.trigger === 'change')
        console.assert(item.beginRules.required === 'true' || item.beginRules.required === 'false')
        console.assert(item.beginRules.trigger === 'blur' || item.beginRules.trigger === 'change')
        console.assert(item.endRules.required === 'true' || item.endRules.required === 'false')
        console.assert(item.endRules.trigger === 'blur' || item.endRules.trigger === 'change')
        item.rules.required = isTrue(String(item.rules.required))
        item.beginRules.required = isTrue(String(item.beginRules.required))
        item.endRules.required = isTrue(String(item.endRules.required))
        item.disabled = isTrue(String(item.disabled))
        item.minNum = Number(item.minNum)
        item.maxNum = Number(item.maxNum)
      })
      if (props.formType === 'edit') {
        editFormInitialValue = JSON.parse(JSON.stringify(dynamicForm.value))
      }
      resetForm()
    })
    .catch(() => {
      console.error('error in getTableInfo, current item is ' + props.itemName)
    })
  if (props.formType === 'search') {
    await submitForm()
  }
}
const submitForm = async () => {
  emit('setTableDataNotReady')
  let formValid = false
  await formRef.value?.validate((valid: boolean) => {
    formValid = valid
  })
  if (!formValid) {
    emit('setTableDataReady')
    return
  }
  formButtonDisabled.value = true
  const submitForm: any[] = []
  dynamicForm.value.forEach((item) => {
    submitForm.push({
      prop: item.prop,
      value: item.value,
      beginValue: item.beginValue,
      endValue: item.endValue,
      multipleValue: item.multipleValue,
    })
  })
  switch (props.formType) {
    case 'search':
      await axios.get(rootOfPath + '/admin/get-table-data', {
          params: {
            itemName: props.itemName,
            form: submitForm,
          },
        }
      )
        .then((response) => {
          emit('resetTableData', response.data.results)
          emit('setTableDataReady')
          formButtonDisabled.value = false
        })
        .catch(() => {
          console.error('error in submitForm, current item is ' + props.itemName)
        })
      break
    case 'add':
    case 'edit':
      const submitValue = {
        type: props.formType,
        itemName: props.itemName,
        form: submitForm,
        itemId: props.editItemId,
      }
      if (props.formType === 'add') {
        delete submitValue.itemId
      }
      await axios.post(rootOfPath + '/admin/add-or-edit', submitValue)
        .then(() => {
          if (props.formType === 'add') {
            ElMessage.success('Add successfully')
          } else {
            ElMessage.success('Edit successfully')
            emit('closeSurroundingDialog')
          }
          emit('tableDataChange')
          formButtonDisabled.value = false
        })
        .catch((error) => {
          ElMessage.error(error.response.data.results)
        })
      break
  }
}

const resetForm = () => {
  switch (props.formType) {
    case 'search':
    case 'add':
      dynamicForm.value.forEach((item) => {
        item.value = ''
        item.beginValue = ''
        item.endValue = ''
      })
      break
    case 'edit':
      dynamicForm.value.forEach((item, index) => {
        item.value = editFormInitialValue[index].value
        item.beginValue = editFormInitialValue[index].beginValue
        item.endValue = editFormInitialValue[index].endValue
      })
      break
  }

}

onMounted(() => {
  getFormInfo()
})
watch(() => props.itemName, () => {
  getFormInfo()
})
watch(() => props.getNewDataFlag, () => {
  submitForm()
})
watch(() => props.submitFormFlag, () => {
  submitForm()
})
watch(() => props.resetFormFlag, () => {
  resetForm()
})
</script>

<template>
  <el-form
    ref="formRef"
    :model="dynamicForm"
    label-position="top"
  >
    <template
      v-for="(item, index) in dynamicForm"
      :key="item.prop"
    >
      <template v-if="isTrue(item.needRemoteMethod)">
        <template v-if="isTrue(item.isMultiple)">
          <el-form-item
            :prop="index + '.multipleValue'"
            :label="item.label"
            :rules="item.rules"
          >
            <template v-if="isTrue(item.isPatientName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_patientNameRemoteMethod"
                :loading="patientNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in patientNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isDoctorName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_doctorNameRemoteMethod"
                :loading="doctorNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in doctorNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isNurseName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_nurseNameRemoteMethod"
                :loading="nurseNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in nurseNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isHelpingStaffName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_helpingStaffNameRemoteMethod"
                :loading="helpingStaffNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in helpingStaffNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isExaminationName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_examinationNameRemoteMethod"
                :loading="examinationNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in examinationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isRehabilitationName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_rehabilitationNameRemoteMethod"
                :loading="rehabilitationNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in rehabilitationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isMedicineName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_medicineNameRemoteMethod"
                :loading="medicineNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in medicineNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isSurgerySite)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_surgerySiteRemoteMethod"
                :loading="surgerySiteLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in surgerySiteOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isSurgeryName)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_surgeryNameRemoteMethod"
                :loading="surgeryNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in surgeryNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isDepartment)">
              <el-select
                v-model="item.multipleValue"
                filterable
                remote
                reserve-keyword
                clearable
                multiple
                :remote-method="_departmentRemoteMethod"
                :loading="departmentLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in departmentOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item
            :prop="index + '.value'"
            :label="item.label"
            :rules="item.rules"
          >
            <template v-if="isTrue(item.isPatientName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_patientNameRemoteMethod"
                :loading="patientNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in patientNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isDoctorName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_doctorNameRemoteMethod"
                :loading="doctorNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in doctorNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isNurseName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_nurseNameRemoteMethod"
                :loading="nurseNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in nurseNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isHelpingStaffName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_helpingStaffNameRemoteMethod"
                :loading="helpingStaffNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in helpingStaffNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isExaminationName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_examinationNameRemoteMethod"
                :loading="examinationNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in examinationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isRehabilitationName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_rehabilitationNameRemoteMethod"
                :loading="rehabilitationNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in rehabilitationNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isMedicineName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_medicineNameRemoteMethod"
                :loading="medicineNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in medicineNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isSurgerySite)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_surgerySiteRemoteMethod"
                :loading="surgerySiteLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in surgerySiteOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isSurgeryName)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_surgeryNameRemoteMethod"
                :loading="surgeryNameLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in surgeryNameOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>

            <template v-if="isTrue(item.isDepartment)">
              <el-select
                v-model="item.value"
                filterable
                remote
                reserve-keyword
                clearable
                :remote-method="_departmentRemoteMethod"
                :loading="departmentLoading"
                style="width: 100%"
                placeholder="Enter here"
                :disabled="item.disabled"
              >
                <el-option
                  v-for="item in departmentOptions"
                  :key="item"
                  :value="item"
                />
              </el-select>
            </template>
          </el-form-item>
        </template>

      </template>

      <template v-else>
        <template v-if="isTrue(item.isInterval)">
          <el-form-item :label="item.label">
            <template v-if="item.type==='date'">
              <el-col :span="11">
                <el-form-item
                  :prop="index + '.beginValue'"
                  :rules="item.beginRules"
                >
                  <el-date-picker
                    v-model="item.beginValue"
                    type="datetime"
                    placeholder="Select date and time"
                    style="width: 100%"
                    :disabled="item.disabled"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="2" style="text-align: center;">-</el-col>
              <el-col :span="11">
                <el-form-item
                  :prop="index + '.endValue'"
                  :rules="item.endRules"
                >
                  <el-date-picker
                    v-model="item.endValue"
                    type="datetime"
                    placeholder="Select date and time"
                    style="width: 100%"
                    :disabled="item.disabled"
                  />
                </el-form-item>
              </el-col>
            </template>

            <template v-if="item.type==='string'">
              <el-col :span="11">
                <el-form-item
                  :prop="index + '.beginValue'"
                  :rules="item.beginRules"
                >
                  <el-input v-model="item.beginValue" :disabled="item.disabled"/>
                </el-form-item>
              </el-col>
              <el-col :span="2" style="text-align: center;">-</el-col>
              <el-col :span="11">
                <el-form-item
                  :prop="index + '.endValue'"
                  :rules="item.endRules"
                >
                  <el-input v-model="item.endValue" :disabled="item.disabled"/>
                </el-form-item>
              </el-col>
            </template>

          </el-form-item>
        </template>

        <template v-else>

          <template v-if="item.type === 'string'||item.type==='date'">
            <el-form-item
              :prop="index + '.value'"
              :label="item.label"
              :rules="item.rules"
            >
              <template v-if="item.type === 'string'">
                <el-input v-model="item.value" :disabled="item.disabled"/>
              </template>

              <template v-if="item.type === 'date'">
                <el-date-picker
                  v-model="item.value"
                  type="datetime"
                  placeholder="Select date and time"
                  style="width: 100%"
                  :disabled="item.disabled"
                />
              </template>
            </el-form-item>
          </template>

          <template v-else>
            <template v-if="isTrue(item.isMultiple)">
              <el-form-item
                :prop="index + '.multipleValue'"
                :label="item.label"
                :rules="item.rules"
              >
                <el-checkbox-group
                  v-model="item.multipleValue"
                  :disabled="item.disabled"
                  :min="item.minNum"
                  :max="item.maxNum"
                >
                  <el-checkbox
                    v-for="option in item.enumerateValue"
                    :key="option"
                    :label="option"
                  >{{ option }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </template>
            <template v-else>
              <el-form-item
                :prop="index + '.value'"
                :label="item.label"
                :rules="item.rules"
              >
                <el-radio-group v-model="item.value" :disabled="item.disabled">
                  <el-radio
                    v-for="option in item.enumerateValue"
                    :key="option"
                    :label="option"
                  >{{ option }}
                  </el-radio>
                </el-radio-group>
              </el-form-item>
            </template>

          </template>



        </template>
      </template>
    </template>

    <el-form-item v-if="isTrue(props.showFormButton)">
      <el-button :disabled="formButtonDisabled" type="primary" @click="submitForm">Submit</el-button>
      <el-button :disabled="formButtonDisabled" @click="resetForm">Reset</el-button>
    </el-form-item>
  </el-form>
</template>

<style scoped>

</style>