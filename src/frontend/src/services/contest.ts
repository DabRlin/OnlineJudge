/**
 * 竞赛相关 API 服务
 */

import request from '@/utils/request'
import type { Contest, ContestListItem, ContestProblem, RankItem } from '@/types'

interface GetContestsParams {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}

interface GetContestsResponse {
  items: ContestListItem[]
  total: number
  page: number
  page_size: number
}

interface CreateContestData {
  title: string
  description?: string
  start_time: string
  end_time: string
  duration: number
  contest_type?: 'public' | 'private'
  rule_type?: 'acm' | 'oi'
  password?: string
  is_visible?: boolean
  real_time_rank?: boolean
  freeze_time?: number
}

interface UpdateContestData {
  title?: string
  description?: string
  start_time?: string
  end_time?: string
  duration?: number
  contest_type?: 'public' | 'private'
  rule_type?: 'acm' | 'oi'
  password?: string
  is_visible?: boolean
  real_time_rank?: boolean
  freeze_time?: number
}

interface AddContestProblemData {
  problem_id: number
  display_id: string
  score?: number
}

interface RegisterContestData {
  password?: string
}

interface GetRankResponse {
  items: RankItem[]
  total: number
  is_frozen: boolean
}

export const contestApi = {
  /**
   * 获取竞赛列表
   */
  getContests: async (params: GetContestsParams = {}): Promise<GetContestsResponse> => {
    return request.get('/contests', { params })
  },

  /**
   * 创建竞赛
   */
  createContest: async (data: CreateContestData): Promise<Contest> => {
    return request.post('/contests', data)
  },

  /**
   * 获取竞赛详情
   */
  getContest: async (id: number): Promise<Contest> => {
    return request.get(`/contests/${id}`)
  },

  /**
   * 更新竞赛
   */
  updateContest: async (id: number, data: UpdateContestData): Promise<Contest> => {
    return request.put(`/contests/${id}`, data)
  },

  /**
   * 删除竞赛
   */
  deleteContest: async (id: number): Promise<void> => {
    return request.delete(`/contests/${id}`)
  },

  /**
   * 获取竞赛题目列表
   */
  getContestProblems: async (contestId: number): Promise<ContestProblem[]> => {
    return request.get(`/contests/${contestId}/problems`)
  },

  /**
   * 添加竞赛题目
   */
  addContestProblem: async (contestId: number, data: AddContestProblemData): Promise<ContestProblem> => {
    return request.post(`/contests/${contestId}/problems`, data)
  },

  /**
   * 移除竞赛题目
   */
  removeContestProblem: async (contestId: number, problemId: number): Promise<void> => {
    return request.delete(`/contests/${contestId}/problems/${problemId}`)
  },

  /**
   * 报名参赛
   */
  registerContest: async (contestId: number, data: RegisterContestData = {}): Promise<{ message: string }> => {
    return request.post(`/contests/${contestId}/register`, data)
  },

  /**
   * 获取竞赛排行榜
   */
  getContestRank: async (contestId: number, page: number = 1, pageSize: number = 50): Promise<GetRankResponse> => {
    return request.get(`/contests/${contestId}/rank`, {
      params: { page, page_size: pageSize }
    })
  },
}

export default contestApi
