import { defineStore } from 'pinia'
import {UserType} from '../types/user.ts'

export const useConfigStore = defineStore('config', {
    state: () => ({
        rootOfPath: 'http://localhost:5000', 
        // rootOfPath: 'http://175.178.87.250:5000',
        userId: 'defaultIdInConfigStore',
        userType: UserType.Patient,
        userName: 'defaultNameInConfigStore',

        sidebarMenuItemActiveColor: 'var(--el-color-primary)',
        sidebarMenuItemInactiveColor: 'var(--el-text-color-primary)',

        defaultPageSize: 10,
        tablePageSizeArr: [10, 20, 50, 100, 200],
        showDetailDialogWidth: '80%',
        recordDialogWidth: '50%',
    }),
})