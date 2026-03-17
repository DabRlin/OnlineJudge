/**
 * 题目列表页面
 */

import { FC, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Tag, Input, Select, Card, Space, Button, Modal, Upload, message, Alert } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { SearchOutlined, UploadOutlined, PlusOutlined, InboxOutlined } from '@ant-design/icons'
import { problemApi } from '@/services/problem'
import type { Problem, Difficulty } from '@/types'
import { useAuthStore } from '@/stores/authStore'

const { Search } = Input
const { Option } = Select
const { Dragger } = Upload

export const Problems: FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [problems, setProblems] = useState<Problem[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [difficulty, setDifficulty] = useState<string>()
  const [search, setSearch] = useState<string>()
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)
  const [jsonText, setJsonText] = useState('')

  const fetchProblems = async () => {
    setLoading(true)
    try {
      const data = await problemApi.getProblems({
        page,
        page_size: pageSize,
        difficulty,
        search,
      })
      setProblems(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch problems:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProblems()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, difficulty, search])

  const handleFileSelect = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      setJsonText(e.target?.result as string)
    }
    reader.readAsText(file)
    return false
  }

  const handleImport = async () => {
    if (!jsonText.trim()) {
      message.warning('请先选择或粘贴 JSON 文件内容')
      return
    }
    let parsed: any
    try {
      parsed = JSON.parse(jsonText)
    } catch {
      message.error('JSON 格式错误，请检查内容')
      return
    }
    const problemsList = Array.isArray(parsed) ? parsed : parsed.problems
    if (!Array.isArray(problemsList) || problemsList.length === 0) {
      message.error('未找到题目数据，请确保格式为 {"problems": [...]} 或直接是数组')
      return
    }
    setImportLoading(true)
    setImportResult(null)
    try {
      const result = await problemApi.importProblems(problemsList)
      setImportResult(result)
      if (result.created > 0) {
        fetchProblems()
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '导入失败')
    } finally {
      setImportLoading(false)
    }
  }

  const getDifficultyColor = (diff: Difficulty) => {
    const colors = {
      easy: 'green',
      medium: 'orange',
      hard: 'red',
    }
    return colors[diff] || 'default'
  }

  const getDifficultyText = (diff: Difficulty) => {
    const texts = {
      easy: '简单',
      medium: '中等',
      hard: '困难',
    }
    return texts[diff] || diff
  }

  const columns: ColumnsType<Problem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '题目',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: Problem) => (
        <a
          onClick={() => navigate(`/problems/${record.id}`)}
          className="text-blue-600 hover:text-blue-800 cursor-pointer"
        >
          {title}
        </a>
      ),
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 100,
      render: (difficulty: Difficulty) => (
        <Tag color={getDifficultyColor(difficulty)}>
          {getDifficultyText(difficulty)}
        </Tag>
      ),
    },
    {
      title: '通过率',
      dataIndex: 'acceptance_rate',
      key: 'acceptance_rate',
      width: 120,
      render: (rate: number) => `${rate.toFixed(1)}%`,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <>
          {tags.slice(0, 3).map((tag) => (
            <Tag key={tag} className="mb-1">
              {tag}
            </Tag>
          ))}
        </>
      ),
    },
  ]

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin')

  return (
    <div className="container mx-auto px-4 py-8">
      <Card
        title={<h2 className="text-2xl font-bold">题库</h2>}
        extra={
          <Space>
            <Select
              placeholder="难度"
              style={{ width: 120 }}
              allowClear
              onChange={setDifficulty}
            >
              <Option value="easy">简单</Option>
              <Option value="medium">中等</Option>
              <Option value="hard">困难</Option>
            </Select>
            <Search
              placeholder="搜索题目"
              allowClear
              onSearch={setSearch}
              style={{ width: 250 }}
              prefix={<SearchOutlined />}
            />
            {isAdmin && (
              <>
                <Button
                  icon={<UploadOutlined />}
                  onClick={() => { setImportModalVisible(true); setImportResult(null); setJsonText('') }}
                >
                  导入题目
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => navigate('/problems/new')}
                >
                  新建题目
                </Button>
              </>
            )}
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={problems}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 道题目`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Card>

      <Modal
        title="批量导入题目"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        onOk={handleImport}
        okText="开始导入"
        cancelText="关闭"
        confirmLoading={importLoading}
        width={640}
        okButtonProps={{ disabled: !!importResult }}
      >
        {!importResult ? (
          <div>
            <p className="text-gray-500 mb-4">
              支持 JSON 格式，结构为 <code>{'{"problems": [...]}'}</code> 或直接是数组。
              同名题目默认跳过。
            </p>
            <Dragger
              accept=".json"
              showUploadList={false}
              beforeUpload={handleFileSelect}
              style={{ marginBottom: 16 }}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽 JSON 文件到此区域</p>
              <p className="ant-upload-hint">支持 classic_problems.json 格式</p>
            </Dragger>
            <Input.TextArea
              placeholder="或直接粘贴 JSON 内容..."
              rows={8}
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              style={{ fontFamily: 'monospace', fontSize: 12 }}
            />
            {jsonText && (() => {
              try {
                const parsed = JSON.parse(jsonText)
                const list = Array.isArray(parsed) ? parsed : parsed.problems
                return <p className="text-green-600 mt-2">✅ 检测到 {list?.length ?? 0} 道题目</p>
              } catch {
                return <p className="text-red-500 mt-2">❌ JSON 格式错误</p>
              }
            })()}
          </div>
        ) : (
          <div>
            <Alert
              type={importResult.failed > 0 ? 'warning' : 'success'}
              message={`导入完成：成功 ${importResult.created} 道，跳过 ${importResult.skipped} 道，失败 ${importResult.failed} 道`}
              style={{ marginBottom: 16 }}
            />
            {importResult.created > 0 && (
              <div className="mb-3">
                <p className="font-semibold text-green-600 mb-1">✅ 成功导入：</p>
                <div className="flex flex-wrap gap-1">
                  {importResult.created_titles.map((t: string) => <Tag key={t} color="success">{t}</Tag>)}
                </div>
              </div>
            )}
            {importResult.skipped > 0 && (
              <div className="mb-3">
                <p className="font-semibold text-gray-500 mb-1">⏭ 跳过（已存在）：</p>
                <div className="flex flex-wrap gap-1">
                  {importResult.skipped_titles.map((t: string) => <Tag key={t}>{t}</Tag>)}
                </div>
              </div>
            )}
            {importResult.failed > 0 && (
              <div>
                <p className="font-semibold text-red-500 mb-1">❌ 失败：</p>
                {importResult.failed_details.map((f: any) => (
                  <p key={f.title} className="text-sm text-red-400">{f.title}: {f.error}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Problems
