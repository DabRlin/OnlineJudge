/**
 * 题目相关 API 服务
 */

import api from './api'
import type { Problem, ProblemDetail, TestCase, PaginatedResponse } from '@/types'

interface ProblemListParams {
  page?: number
  page_size?: number
  difficulty?: string
  tags?: string[]
  search?: string
  sort_by?: string
  order?: string
}

interface GetProblemsParams {
  page?: number
  page_size?: number
  difficulty?: string
  tags?: string[]
  search?: string
}

interface ProblemsResponse {
  items: Problem[]
  total: number
  page: number
  page_size: number
  pages: number
}

interface ProblemCreateData {
  title: string
  description: string
  difficulty: string
  input_format?: string
  output_format?: string
  constraints?: string
  time_limit: number
  memory_limit: number
  tags?: string[]
  source?: string
  is_public?: boolean
}

interface TestCaseData {
  input: string
  output: string
  is_sample: boolean
  score: number
}

/**
 * 题目 API
 */
export const problemApi = {
  /**
   * 获取题目列表
   */
  getProblems: async (params: ProblemListParams = {}) => {
    const response = await api.get<{ data: PaginatedResponse<Problem> }>('/problems', {
      params,
    })
    return response.data.data
  },

  /**
   * 获取题目详情
   */
  getProblem: async (id: number): Promise<ProblemDetail> => {
    const response = await api.get<ProblemDetail>(`/problems/${id}`)
    return response.data
  },

  /**
   * 创建题目
   */
  createProblem: async (problemData: ProblemCreateData): Promise<Problem> => {
    const { data } = await api.post('/problems', problemData)
    return data.data
  },

  /**
   * 更新题目
   */
  updateProblem: async (id: number, problemData: Partial<ProblemCreateData>): Promise<Problem> => {
    const { data } = await api.put(`/problems/${id}`, problemData)
    return data.data
  },

  /**
   * 删除题目
   */
  deleteProblem: async (id: number): Promise<void> => {
    await api.delete(`/problems/${id}`)
  },

  /**
   * 添加测试用例
   */
  addTestCase: async (problemId: number, testCaseData: TestCaseData): Promise<TestCase> => {
    const { data } = await api.post(`/problems/${problemId}/test-cases`, testCaseData)
    return data.data
  },

  /**
   * 更新测试用例
   */
  updateTestCase: async (
    problemId: number,
    testCaseId: number,
    testCaseData: TestCaseData
  ): Promise<TestCase> => {
    const { data } = await api.put(
      `/problems/${problemId}/test-cases/${testCaseId}`,
      testCaseData
    )
    return data.data
  },

  /**
   * 删除测试用例
   */
  deleteTestCase: async (problemId: number, testCaseId: number): Promise<void> => {
    await api.delete(`/problems/${problemId}/test-cases/${testCaseId}`)
  },

  /**
   * 批量导入题目（管理员）
   */
  importProblems: async (problems: any[], skipExisting = true): Promise<{
    total: number
    created: number
    skipped: number
    failed: number
    created_titles: string[]
    skipped_titles: string[]
    failed_details: { title: string; error: string }[]
  }> => {
    const { data } = await api.post('/problems/import', { problems, skip_existing: skipExisting })
    return data
  },
}
