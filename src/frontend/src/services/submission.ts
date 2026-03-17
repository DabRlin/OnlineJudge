/**
 * 提交相关 API 服务
 */

import api from './api'
import type { Submission, SubmissionCreate } from '@/types'

interface SubmissionsResponse {
  items: Submission[]
  total: number
  page: number
  page_size: number
  pages: number
}

interface SubmissionParams {
  page?: number
  page_size?: number
  user_id?: number
  problem_id?: number
  language?: string
  status?: string
}

export const submissionApi = {
  /**
   * 提交代码
   */
  async submitCode(data: SubmissionCreate): Promise<Submission> {
    const response = await api.post('/submissions', data)
    return response.data.data
  },

  /**
   * 获取提交列表
   */
  async getSubmissions(params: SubmissionParams = {}): Promise<SubmissionsResponse> {
    const response = await api.get('/submissions', { params })
    return response.data.data
  },

  /**
   * 获取提交详情
   */
  async getSubmission(id: number): Promise<Submission> {
    const response = await api.get(`/submissions/${id}`)
    return response.data.data
  },

  /**
   * 重新判题（管理员）
   */
  async rejudge(id: number): Promise<Submission> {
    const response = await api.post(`/submissions/${id}/rejudge`)
    return response.data.data
  },

  /**
   * 获取用户提交记录
   */
  async getUserSubmissions(
    userId: number,
    problemId?: number,
    limit: number = 10
  ): Promise<Submission[]> {
    const response = await api.get(`/submissions/user/${userId}`, {
      params: { problem_id: problemId, limit },
    })
    return response.data.data
  },
}
