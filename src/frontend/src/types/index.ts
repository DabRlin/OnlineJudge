/**
 * 通用类型定义
 */

/**
 * API 响应基础类型
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

/**
 * 分页响应类型
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 用户角色枚举
 */
export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
}

/**
 * 用户类型
 */
export interface User {
  id: number
  username: string
  email: string
  role: UserRole
  is_active: boolean
  avatar?: string
  created_at: string
  updated_at?: string
}

/**
 * 用户注册数据
 */
export interface UserRegister {
  username: string
  email: string
  password: string
}

/**
 * 用户登录数据
 */
export interface UserLogin {
  username: string
  password: string
}

/**
 * 用户更新数据
 */
export interface UserUpdate {
  username?: string
  email?: string
  avatar?: string
}

/**
 * 密码更新数据
 */
export interface PasswordUpdate {
  old_password: string
  new_password: string
}

/**
 * Token 响应
 */
export interface TokenResponse {
  access_token: string
  token_type: string
}

/**
 * 题目难度
 */
export enum Difficulty {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

/**
 * 测试用例类型
 */
export interface TestCase {
  id: number
  problem_id: number
  input: string
  output: string
  is_sample: boolean
  score: number
  created_at: string
}

/**
 * 题目类型
 */
export interface Problem {
  id: number
  title: string
  description: string
  difficulty: Difficulty
  input_format?: string
  output_format?: string
  constraints?: string
  time_limit: number
  memory_limit: number
  tags: string[]
  source?: string
  is_public: boolean
  submission_count: number
  accepted_count: number
  acceptance_rate: number
  created_at: string
  updated_at?: string
}

/**
 * 题目详情类型（包含测试用例）
 */
export interface ProblemDetail extends Problem {
  test_cases: TestCase[]
}

/**
 * 提交状态
 */
export enum SubmissionStatus {
  PENDING = 'pending',
  JUDGING = 'judging',
  ACCEPTED = 'accepted',
  WRONG_ANSWER = 'wrong_answer',
  TIME_LIMIT_EXCEEDED = 'time_limit_exceeded',
  MEMORY_LIMIT_EXCEEDED = 'memory_limit_exceeded',
  RUNTIME_ERROR = 'runtime_error',
  COMPILE_ERROR = 'compile_error',
  SYSTEM_ERROR = 'system_error',
}

/**
 * 编程语言
 */
export type ProgrammingLanguage = 'python' | 'cpp' | 'java' | 'c' | 'javascript' | 'go'

export interface Submission {
  id: number
  user_id: number
  user_username: string
  problem_id: number
  problem_title: string
  language: ProgrammingLanguage
  code: string
  status: SubmissionStatus
  score: number | null
  time_used: number | null
  memory_used: number | null
  error_message: string | null
  test_cases_result: string | null
  submitted_at: string
  judged_at: string | null
}

// ============ Contest Types ============

export type ContestType = 'public' | 'private'
export type ContestStatus = 'not_started' | 'running' | 'ended'
export type RuleType = 'acm' | 'oi'

export interface Contest {
  id: number
  title: string
  description: string | null
  start_time: string
  end_time: string
  duration: number
  contest_type: ContestType
  rule_type: RuleType
  password: string | null
  is_visible: boolean
  real_time_rank: boolean
  freeze_time: number | null
  created_by: number
  participant_count: number
  submission_count: number
  status: ContestStatus
  is_frozen: boolean
  created_at: string
  updated_at: string
}

export interface ContestListItem {
  id: number
  title: string
  start_time: string
  end_time: string
  duration: number
  contest_type: ContestType
  rule_type: RuleType
  participant_count: number
  status: ContestStatus
  created_at: string
}

export interface ContestProblem {
  id: number
  contest_id: number
  problem_id: number
  display_id: string
  score: number
  submission_count: number
  accepted_count: number
  created_at: string
}

export interface RankItem {
  rank: number
  user_id: number
  username: string
  total_score: number
  solved_count: number
  total_time: number
  submission_count: number
  last_submission_at: string | null
}

/**
 * 提交创建数据
 */
export interface SubmissionCreate {
  problem_id: number
  language: string
  code: string
}
