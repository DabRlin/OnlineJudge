// API endpoints
export const API_ENDPOINTS = {
  HEALTH: '/health',
  USERS: '/users',
  PROBLEMS: '/problems',
  SUBMISSIONS: '/submissions',
  CONTESTS: '/contests',
} as const

// Difficulty colors
export const DIFFICULTY_COLORS = {
  easy: 'green',
  medium: 'orange',
  hard: 'red',
} as const

// Submission status colors
export const STATUS_COLORS = {
  pending: 'default',
  judging: 'processing',
  accepted: 'success',
  wrong_answer: 'error',
  time_limit_exceeded: 'warning',
  memory_limit_exceeded: 'warning',
  runtime_error: 'error',
  compile_error: 'error',
} as const

// Programming languages
export const LANGUAGES = [
  { value: 'cpp', label: 'C++' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'javascript', label: 'JavaScript' },
] as const
