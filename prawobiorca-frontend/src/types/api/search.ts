export type searchResultElement = { text: string; subsection: string | null }

export type searchResult = {
  id: string
  score: number
  text: string
  header: string
  elements: Array<searchResultElement> | null
}

export type searchOrder = 'document' | 'score'

export type searchParams = {
  query: string
  threshold: number
  limit?: number
  order_by: searchOrder
}
