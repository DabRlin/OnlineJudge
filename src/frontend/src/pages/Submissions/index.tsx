/**
 * 提交记录页面
 */

import { FC, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Tag, Select, Button, Space, Card, message } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { submissionApi } from '@/services/submission'
import type { Submission, SubmissionStatus, ProgrammingLanguage } from '@/types'
import { formatDate } from '@/utils'
import './styles.css'

const { Option } = Select

export const Submissions: FC = () => {
  const navigate = useNavigate()
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [languageFilter, setLanguageFilter] = useState<string>('')

  const fetchSubmissions = async () => {
    setLoading(true)
    try {
      const data = await submissionApi.getSubmissions({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        language: languageFilter || undefined,
      })
      setSubmissions(data.items)
      setTotal(data.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取提交记录失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSubmissions()
  }, [page, pageSize, statusFilter, languageFilter])

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

  const columns = [
    {
      title: '提交 ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: '题目',
      dataIndex: 'problem_title',
      key: 'problem_title',
      render: (text: string, record: Submission) => (
        <a onClick={() => navigate(`/problems/${record.problem_id}`)}>
          {record.problem_id}. {text}
        </a>
      ),
    },
    {
      title: '用户',
      dataIndex: 'user_username',
      key: 'user_username',
      width: 120,
    },
    {
      title: '语言',
      dataIndex: 'language',
      key: 'language',
      width: 100,
      render: (language: ProgrammingLanguage) => getLanguageText(language),
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
      title: '得分',
      dataIndex: 'score',
      key: 'score',
      width: 80,
      render: (score: number | null) => score !== null ? `${score}分` : '-',
    },
    {
      title: '时间',
      dataIndex: 'time_used',
      key: 'time_used',
      width: 100,
      render: (time: number | null) => time !== null ? `${time}ms` : '-',
    },
    {
      title: '内存',
      dataIndex: 'memory_used',
      key: 'memory_used',
      width: 100,
      render: (memory: number | null) => memory !== null ? `${memory}KB` : '-',
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
          查看详情
        </Button>
      ),
    },
  ]

  return (
    <div className="submissions-page">
      <Card>
        <div className="submissions-header">
          <h2>提交记录</h2>
          <Space>
            <Select
              placeholder="筛选状态"
              style={{ width: 150 }}
              allowClear
              value={statusFilter || undefined}
              onChange={(value) => {
                setStatusFilter(value || '')
                setPage(1)
              }}
            >
              <Option value="accepted">通过</Option>
              <Option value="wrong_answer">答案错误</Option>
              <Option value="time_limit_exceeded">超时</Option>
              <Option value="runtime_error">运行错误</Option>
              <Option value="compile_error">编译错误</Option>
            </Select>

            <Select
              placeholder="筛选语言"
              style={{ width: 120 }}
              allowClear
              value={languageFilter || undefined}
              onChange={(value) => {
                setLanguageFilter(value || '')
                setPage(1)
              }}
            >
              <Option value="python">Python</Option>
              <Option value="cpp">C++</Option>
              <Option value="java">Java</Option>
            </Select>

            <Button
              icon={<ReloadOutlined />}
              onClick={fetchSubmissions}
            >
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={submissions}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Card>
    </div>
  )
}

export default Submissions
