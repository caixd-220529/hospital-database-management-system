const defaultSort = (a: string, b: string, order: string):number => {
  if (order === 'ascending') {
    return a.localeCompare(b)
  } else if (order === 'descending') {
    return b.localeCompare(a)
  } else {
    console.error('Invalid order')
    return 0
  }
}

export const sortConsultationId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortDepartment = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortName = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortPrescriptionId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortPharmacyWindow = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortExaminationId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortRehabilitationId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortSurgeryId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortHospitalizationId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortChargeId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortDescribableItemId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortCost = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}


export const sortPosition = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortPatientId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortDoctorId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortNurseId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortHelpingStaffId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortPharmacyPickWindow = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortSurgerySite = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortRoomId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortUserId = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortUserType = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortPaymentMethod = (a: string, b: string, order: string):number => {
  return defaultSort(a, b, order)
}

export const sortTime = (a: string, b: string, order: string):number => {
  if (order === 'ascending') {
    return new Date(a).getTime() - new Date(b).getTime()
  } else if (order === 'descending') {
    return new Date(b).getTime() - new Date(a).getTime()
  } else {
    console.error('Invalid order')
    return 0
  }
}