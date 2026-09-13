export type regulationType = 'ACT' | 'DECREE' | 'STATUTE'

export type regulationPreparationStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'PREPARED' | 'FAILED'

export type regulationRepresentation = {
  id: string
  presentationName: string
  regulationType?: regulationType | null
  preparationStatus: regulationPreparationStatus
}

export type regulationData = {
  name: string
  regulation_type?: regulationType | null
}

export type regulationUploadTarget = {
  id: string
  url: string
  fields: Record<string, string>
}

export type regulationUploadResult = {
  id: string
  preparationStatus: regulationPreparationStatus
}
