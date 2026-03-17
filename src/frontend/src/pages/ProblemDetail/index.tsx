/**
 * 题目详情页面
 */

import { FC, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Tag, Descriptions, Tabs, Button, Spin, message, Table } from 'antd'
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons'
import { problemApi } from '@/services/problem'
import { submissionApi } from '@/services/submission'
import type { ProblemDetail as ProblemDetailType, Difficulty, Submission, SubmissionStatus } from '@/types'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import CodeEditor from '@/components/CodeEditor'
import { useAuthStore } from '@/stores/authStore'
import { formatDate } from '@/utils'
import './styles.css'

const { TabPane } = Tabs

export const ProblemDetail: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [problem, setProblem] = useState<ProblemDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [submissionsLoading, setSubmissionsLoading] = useState(false)

  const fetchSubmissions = async () => {
    if (!id || !user) return
    
    setSubmissionsLoading(true)
    try {
      const data = await submissionApi.getSubmissions({
        problem_id: Number(id),
        page: 1,
        page_size: 10,
      })
      setSubmissions(data.items)
    } catch (error: any) {
      console.error('获取提交记录失败:', error)
    } finally {
      setSubmissionsLoading(false)
    }
  }

  useEffect(() => {
    const fetchProblem = async () => {
      if (!id) return
      
      setLoading(true)
      try {
        const data = await problemApi.getProblem(Number(id))
        setProblem(data)
      } catch (error: any) {
        message.error(error.response?.data?.detail || '获取题目详情失败')
      } finally {
        setLoading(false)
      }
    }

    fetchProblem()
    fetchSubmissions()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, user])

  const getDifficultyColor = (diff: Difficulty) => {
    const colors = {
      easy: 'green',
      medium: 'orange',
      hard: 'red',
    }
    return colors[diff] || 'default'
  }

  const getDifficultyText = (difficulty: Difficulty): string => {
    const textMap: Record<Difficulty, string> = {
      easy: '简单',
      medium: '中等',
      hard: '困难',
    }
    return textMap[difficulty] || difficulty
  }

  const getStatusColor = (status: SubmissionStatus): string => {
    const colorMap: Record<SubmissionStatus, string> = {
      pending: 'default',
      judging: 'processing',
      accepted: 'success',
      wrong_answer: 'error',
      time_limit_exceeded: 'warning',
      memory_limit_exceeded: 'warning',
      runtime_error: 'error',
      compile_error: 'error',
      system_error: 'error',
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status: SubmissionStatus): string => {
    const textMap: Record<SubmissionStatus, string> = {
      pending: '等待判题',
      judging: '判题中',
      accepted: '通过',
      wrong_answer: '答案错误',
      time_limit_exceeded: '超时',
      memory_limit_exceeded: '内存超限',
      runtime_error: '运行错误',
      compile_error: '编译错误',
      system_error: '系统错误',
    }
    return textMap[status] || status
  }

  if (loading || !problem) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    )
  }

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin')

  return (
    <div className="h-screen flex flex-col overflow-hidden problem-detail-container">
      {/* 顶部操作栏 */}
      <div className="flex justify-between items-center px-6 py-3 border-b bg-white flex-shrink-0 shadow-sm">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/problems')}
        >
          返回题库
        </Button>
        {isAdmin && (
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/problems/${id}/edit`)}
          >
            编辑题目
          </Button>
        )}
      </div>

      {/* 双列布局 */}
      <div className="flex-1 flex overflow-hidden gap-4 p-4">
        {/* 左侧：题目描述（可滚动） */}
        <div className="w-1/2 overflow-y-auto problem-description-scroll problem-left-panel rounded-lg shadow-sm">
          <div className="p-6">
            <div className="mb-6">
              <h1 className="text-2xl font-bold mb-4 problem-title">
                {problem.id}. {problem.title}
              </h1>
              <div className="flex items-center gap-4 mb-4">
                <Tag color={getDifficultyColor(problem.difficulty)}>
                  {getDifficultyText(problem.difficulty)}
                </Tag>
                <span className="text-gray-600 text-sm">
                  通过率: {problem.acceptance_rate.toFixed(1)}%
                </span>
                <span className="text-gray-600 text-sm">
                  提交: {problem.submission_count} | 通过: {problem.accepted_count}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {problem.tags.map((tag) => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </div>
            </div>

            <Tabs 
              defaultActiveKey="description" 
              className="problem-tabs"
              onChange={(key) => {
                if (key === 'submissions' && user) {
                  fetchSubmissions()
                }
              }}
            >
            <TabPane tab="题目描述" key="description">
              <div className="prose max-w-none">
                <h3>题目描述</h3>
                <MarkdownRenderer content={problem.description} />

                {problem.input_format && (
                  <>
                    <h3>输入格式</h3>
                    <MarkdownRenderer content={problem.input_format} />
                  </>
                )}

                {problem.output_format && (
                  <>
                    <h3>输出格式</h3>
                    <MarkdownRenderer content={problem.output_format} />
                  </>
                )}

                {problem.constraints && (
                  <>
                    <h3>数据范围</h3>
                    <MarkdownRenderer content={problem.constraints} />
                  </>
                )}

                <h3>样例</h3>
                {problem.test_cases.map((testCase, index) => (
                  <div key={testCase.id} className="mb-4">
                    <h4>样例 {index + 1}</h4>
                    <div className="bg-gray-50 p-4 mb-2 sample-box">
                      <div className="font-semibold mb-1">输入：</div>
                      <pre className="whitespace-pre-wrap">{testCase.input}</pre>
                    </div>
                    <div className="bg-gray-50 p-4 sample-box">
                      <div className="font-semibold mb-1">输出：</div>
                      <pre className="whitespace-pre-wrap">{testCase.output}</pre>
                    </div>
                  </div>
                ))}
              </div>
            </TabPane>

            <TabPane tab="提交记录" key="submissions">
              {user ? (
                <Table
                  columns={[
                    {
                      title: '提交 ID',
                      dataIndex: 'id',
                      key: 'id',
                      width: 100,
                    },
                    {
                      title: '状态',
                      dataIndex: 'status',
                      key: 'status',
                      width: 120,
                      render: (status: SubmissionStatus) => (
                        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
                      ),
                    },
                    {
                      title: '语言',
                      dataIndex: 'language',
                      key: 'language',
                      width: 100,
                    },
                    {
                      title: '时间',
                      dataIndex: 'time_used',
                      key: 'time_used',
                      width: 100,
                      render: (time: number | null) => time !== null ? `${time}ms` : '-',
                    },
                    {
                      title: '提交时间',
                      dataIndex: 'submitted_at',
                      key: 'submitted_at',
                      width: 180,
                      render: (time: string) => formatDate(time),
                    },
                    {
                      title: '操作',
                      key: 'action',
                      width: 100,
                      render: (_: any, record: Submission) => (
                        <Button
                          type="link"
                          size="small"
                          onClick={() => navigate(`/submissions/${record.id}`)}
                        >
                          查看
                        </Button>
                      ),
                    },
                  ]}
                  dataSource={submissions}
                  rowKey="id"
                  loading={submissionsLoading}
                  pagination={false}
                  size="small"
                  onRow={() => ({
                    style: { cursor: 'pointer' }
                  })}
                />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  请先登录查看提交记录
                </div>
              )}
            </TabPane>

              <TabPane tab="题解" key="solutions">
                <div className="text-center text-gray-500 py-8">
                  题解功能即将上线...
                </div>
              </TabPane>
            </Tabs>

            <div className="mt-6">
              <Descriptions bordered column={1} size="small" className="problem-descriptions">
                <Descriptions.Item label="时间限制">{problem.time_limit} ms</Descriptions.Item>
                <Descriptions.Item label="内存限制">{problem.memory_limit} MB</Descriptions.Item>
                {problem.source && (
                  <Descriptions.Item label="来源">{problem.source}</Descriptions.Item>
                )}
              </Descriptions>
            </div>
          </div>
        </div>

        {/* 右侧：代码编辑器（固定高度） */}
        <div className="w-1/2 flex flex-col bg-white">
          <div className="flex-1 overflow-hidden">
            <CodeEditor
              onSubmit={async (code, language) => {
                if (!user) {
                  message.warning('请先登录')
                  navigate('/login')
                  return
                }

                try {
                  const submission = await submissionApi.submitCode({
                    problem_id: Number(id),
                    language,
                    code,
                  })
                  message.loading({ content: '代码已提交，判题中...', key: 'judge', duration: 0 })

                  // 轮询判题状态
                  const POLL_INTERVAL = 1500
                  const MAX_POLLS = 20
                  let polls = 0
                  const poll = setInterval(async () => {
                    polls++
                    try {
                      const result = await submissionApi.getSubmission(submission.id)
                      if (result.status !== 'pending' && result.status !== 'judging') {
                        clearInterval(poll)
                        message.destroy('judge')
                        const statusText: Record<string, string> = {
                          accepted: '🎉 通过！',
                          wrong_answer: '❌ 答案错误',
                          time_limit_exceeded: '⏰ 超时',
                          memory_limit_exceeded: '💾 内存超限',
                          runtime_error: '💥 运行错误',
                          compile_error: '🔧 编译错误',
                          system_error: '⚠️ 系统错误',
                        }
                        const isAC = result.status === 'accepted'
                        const text = statusText[result.status] || result.status
                        if (isAC) {
                          message.success(text)
                        } else {
                          message.error(text)
                        }
                        fetchSubmissions()
                      }
                    } catch (_e) { /* polling tick failed, continue */ }
                    if (polls >= MAX_POLLS) {
                      clearInterval(poll)
                      message.destroy('judge')
                      message.warning('判题超时，请稍后查看结果')
                      fetchSubmissions()
                    }
                  }, POLL_INTERVAL)
                } catch (error: any) {
                  message.error(error.response?.data?.detail || '提交失败')
                }
              }}
              height="100%"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProblemDetail
