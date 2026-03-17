/**
 * 提交详情页面
 */

import { FC, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Tag, Descriptions, Button, Spin, message, Divider, Table } from 'antd'
import { ArrowLeftOutlined, ReloadOutlined } from '@ant-design/icons'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { submissionApi } from '@/services/submission'
import type { Submission, SubmissionStatus, ProgrammingLanguage } from '@/types'
import { formatDate } from '@/utils'
import { useAuthStore } from '@/stores/authStore'
import './styles.css'

export const SubmissionDetail: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [submission, setSubmission] = useState<Submission | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchSubmission = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const data = await submissionApi.getSubmission(Number(id))
      setSubmission(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取提交详情失败')
      navigate('/submissions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSubmission()
  }, [id])

  const handleRejudge = async () => {
    if (!id) return
    
    try {
      await submissionApi.rejudge(Number(id))
      message.success('重新判题请求已提交')
      setTimeout(fetchSubmission, 1000)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '重新判题失败')
    }
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

  const getLanguageText = (language: ProgrammingLanguage): string => {
    const textMap: Record<ProgrammingLanguage, string> = {
      python: 'Python',
      cpp: 'C++',
      java: 'Java',
      c: 'C',
      javascript: 'JavaScript',
      go: 'Go',
    }
    return textMap[language] || language
  }

  const getLanguageMode = (language: ProgrammingLanguage): string => {
    const modeMap: Record<ProgrammingLanguage, string> = {
      python: 'python',
      cpp: 'cpp',
      java: 'java',
      c: 'c',
      javascript: 'javascript',
      go: 'go',
    }
    return modeMap[language] || 'text'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    )
  }

  if (!submission) {
    return null
  }

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin')
  const testCasesResult = submission.test_cases_result 
    ? JSON.parse(submission.test_cases_result) 
    : []

  const testCaseColumns = [
    {
      title: '测试用例',
      dataIndex: 'case_id',
      key: 'case_id',
      render: (caseId: number) => `测试用例 ${caseId}`,
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={status === 'accepted' ? 'success' : 'error'}>
          {status === 'accepted' ? '通过' : status === 'wrong_answer' ? '答案错误' : status === 'time_limit_exceeded' ? '超时' : status === 'runtime_error' ? '运行错误' : '失败'}
        </Tag>
      ),
    },
    {
      title: '时间',
      dataIndex: 'time_used',
      key: 'time_used',
      width: 100,
      render: (time: number) => time !== undefined ? `${time}ms` : '-',
    },
    {
      title: '内存',
      dataIndex: 'memory_used',
      key: 'memory_used',
      width: 100,
      render: (memory: number) => memory ? `${Math.round(memory / 1024)}MB` : '-',
    },
    {
      title: '实际输出',
      dataIndex: 'output',
      key: 'output',
      render: (output: string) => output ? <code style={{ fontSize: 12 }}>{output.slice(0, 50)}{output.length > 50 ? '...' : ''}</code> : '-',
    },
  ]

  return (
    <div className="submission-detail-page">
      <div className="submission-header">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/submissions')}
        >
          返回列表
        </Button>
        <div className="header-actions">
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchSubmission}
          >
            刷新
          </Button>
          {isAdmin && (
            <Button
              type="primary"
              onClick={handleRejudge}
            >
              重新判题
            </Button>
          )}
        </div>
      </div>

      <Card className="submission-info-card">
        <h2>提交详情 #{submission.id}</h2>
        
        <Descriptions bordered column={2}>
          <Descriptions.Item label="题目">
            <a onClick={() => navigate(`/problems/${submission.problem_id}`)}>
              {submission.problem_id}. {submission.problem_title}
            </a>
          </Descriptions.Item>
          <Descriptions.Item label="用户">
            {submission.user_username}
          </Descriptions.Item>
          <Descriptions.Item label="语言">
            {getLanguageText(submission.language)}
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={getStatusColor(submission.status)}>
              {getStatusText(submission.status)}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="得分">
            {submission.score !== null ? `${submission.score}分` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="时间">
            {submission.time_used !== null ? `${submission.time_used}ms` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="内存">
            {submission.memory_used !== null ? `${submission.memory_used}KB` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="提交时间">
            {formatDate(submission.submitted_at)}
          </Descriptions.Item>
          {submission.judged_at && (
            <Descriptions.Item label="判题时间" span={2}>
              {formatDate(submission.judged_at)}
            </Descriptions.Item>
          )}
        </Descriptions>

        {submission.error_message && (
          <>
            <Divider>错误信息</Divider>
            <div className="error-message">
              <pre>{submission.error_message}</pre>
            </div>
          </>
        )}

        {testCasesResult.length > 0 && (
          <>
            <Divider>测试用例结果</Divider>
            <Table
              columns={testCaseColumns}
              dataSource={testCasesResult}
              rowKey={(record: any) => record.case_id}
              pagination={false}
              size="small"
            />
          </>
        )}

        <Divider>提交代码</Divider>
        <div className="code-display">
          <SyntaxHighlighter
            language={getLanguageMode(submission.language)}
            style={vscDarkPlus}
            showLineNumbers
            customStyle={{
              borderRadius: '8px',
              fontSize: '14px',
            }}
          >
            {submission.code}
          </SyntaxHighlighter>
        </div>
      </Card>
    </div>
  )
}

export default SubmissionDetail
