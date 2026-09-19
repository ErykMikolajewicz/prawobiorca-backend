export type searchResultElement = { text: string; subsection: string | null }

export type searchResultHighlight = {
  start_element: number
  start_offset: number
  end_element: number
  end_offset: number
}

export type searchResult = {
  id: string
  score: number
  text: string
  header: string
  elements: Array<searchResultElement> | null
  highlight: searchResultHighlight | null
}

export type searchOrder = 'document' | 'score'

export type searchParams = {
  query: string
  threshold: number
  limit?: number
  order_by: searchOrder
}
