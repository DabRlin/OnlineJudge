/**
 * 题目编辑页面（管理员）
 */

import { FC, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Space,
  message,
  Spin,
  Tabs,
  Table,
  Modal,
  Tag,
} from 'antd'
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import MDEditor from '@uiw/react-md-editor'
import { problemApi } from '@/services/problem'
import { useAuthStore } from '@/stores/authStore'
import type { ProblemDetail, TestCase } from '@/types'
import './styles.css'

const { TabPane } = Tabs
const { TextArea } = Input

interface TestCaseFormData {
  input: string
  output: string
  is_sample: boolean
  score: number
}

export const ProblemEdit: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [problem, setProblem] = useState<ProblemDetail | null>(null)
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [testCaseModalVisible, setTestCaseModalVisible] = useState(false)
  const [editingTestCase, setEditingTestCase] = useState<TestCase | null>(null)
  const [testCaseForm] = Form.useForm()

  // Markdown 编辑器状态
  const [description, setDescription] = useState('')
  const [inputFormat, setInputFormat] = useState('')
  const [outputFormat, setOutputFormat] = useState('')
  const [constraints, setConstraints] = useState('')

  useEffect(() => {
    // 检查权限
    if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
      message.error('没有权限访问此页面')
      navigate('/problems')
      return
    }

    if (id) {
      fetchProblem()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, user, navigate])

  const fetchProblem = async () => {
    if (!id) return

    setLoading(true)
    try {
      const data = await problemApi.getProblem(Number(id))
      setProblem(data)
      setTestCases(data.test_cases || [])

      // 设置表单值
      form.setFieldsValue({
        title: data.title,
        difficulty: data.difficulty,
        time_limit: data.time_limit,
        memory_limit: data.memory_limit,
        tags: data.tags,
        source: data.source,
        is_public: data.is_public,
      })

      // 设置 Markdown 内容
      setDescription(data.description || '')
      setInputFormat(data.input_format || '')
      setOutputFormat(data.output_format || '')
      setConstraints(data.constraints || '')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载题目失败')
      navigate('/problems')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (values: any) => {
    setLoading(true)
    try {
      const problemData = {
        ...values,
        description,
        input_format: inputFormat,
        output_format: outputFormat,
        constraints,
      }

      if (id) {
        // 更新题目
        await problemApi.updateProblem(Number(id), problemData)
        message.success('题目更新成功')
      } else {
        // 创建题目
        const newProblem = await problemApi.createProblem(problemData)
        message.success('题目创建成功')
        navigate(`/problems/${newProblem.id}/edit`)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAddTestCase = () => {
    setEditingTestCase(null)
    testCaseForm.resetFields()
    setTestCaseModalVisible(true)
  }

  const handleEditTestCase = (testCase: TestCase) => {
    setEditingTestCase(testCase)
    testCaseForm.setFieldsValue(testCase)
    setTestCaseModalVisible(true)
  }

  const handleDeleteTestCase = async (testCaseId: number) => {
    if (!id) return

    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个测试用例吗？',
      onOk: async () => {
        try {
          await problemApi.deleteTestCase(Number(id), testCaseId)
          message.success('删除成功')
          fetchProblem()
        } catch (error: any) {
          message.error(error.response?.data?.detail || '删除失败')
        }
      },
    })
  }

  const handleTestCaseSubmit = async (values: TestCaseFormData) => {
    if (!id) {
      message.warning('请先保存题目')
      return
    }

    try {
      if (editingTestCase) {
        // 更新测试用例
        await problemApi.updateTestCase(Number(id), editingTestCase.id, values)
        message.success('测试用例更新成功')
      } else {
        // 添加测试用例
        await problemApi.addTestCase(Number(id), values)
        message.success('测试用例添加成功')
      }
      setTestCaseModalVisible(false)
      fetchProblem()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const testCaseColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '类型',
      dataIndex: 'is_sample',
      key: 'is_sample',
      width: 100,
      render: (is_sample: boolean) => (
        <Tag color={is_sample ? 'blue' : 'default'}>{is_sample ? '样例' : '测试'}</Tag>
      ),
    },
    {
      title: '输入',
      dataIndex: 'input',
      key: 'input',
      ellipsis: true,
      render: (text: string) => <pre className="test-case-preview">{text}</pre>,
    },
    {
      title: '输出',
      dataIndex: 'output',
      key: 'output',
      ellipsis: true,
      render: (text: string) => <pre className="test-case-preview">{text}</pre>,
    },
    {
      title: '分数',
      dataIndex: 'score',
      key: 'score',
      width: 80,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: TestCase) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditTestCase(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteTestCase(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  if (loading && !problem) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div className="problem-edit-page">
      <div className="mb-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/problems')}>
          返回题库
        </Button>
      </div>

      <Card title={id ? '编辑题目' : '创建题目'}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Tabs defaultActiveKey="basic">
            <TabPane tab="基本信息" key="basic">
              <Form.Item
                label="题目标题"
                name="title"
                rules={[{ required: true, message: '请输入题目标题' }]}
              >
                <Input placeholder="请输入题目标题" />
              </Form.Item>

              <Form.Item
                label="难度"
                name="difficulty"
                rules={[{ required: true, message: '请选择难度' }]}
              >
                <Select>
                  <Select.Option value="easy">简单</Select.Option>
                  <Select.Option value="medium">中等</Select.Option>
                  <Select.Option value="hard">困难</Select.Option>
                </Select>
              </Form.Item>

              <div className="grid grid-cols-2 gap-4">
                <Form.Item
                  label="时间限制 (ms)"
                  name="time_limit"
                  rules={[{ required: true, message: '请输入时间限制' }]}
                >
                  <InputNumber min={100} max={10000} step={100} className="w-full" />
                </Form.Item>

                <Form.Item
                  label="内存限制 (MB)"
                  name="memory_limit"
                  rules={[{ required: true, message: '请输入内存限制' }]}
                >
                  <InputNumber min={32} max={1024} step={32} className="w-full" />
                </Form.Item>
              </div>

              <Form.Item label="标签" name="tags">
                <Select mode="tags" placeholder="请输入标签，按回车添加">
                  <Select.Option value="数组">数组</Select.Option>
                  <Select.Option value="字符串">字符串</Select.Option>
                  <Select.Option value="哈希表">哈希表</Select.Option>
                  <Select.Option value="动态规划">动态规划</Select.Option>
                  <Select.Option value="贪心">贪心</Select.Option>
                  <Select.Option value="数学">数学</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="来源" name="source">
                <Input placeholder="如：LeetCode, Codeforces" />
              </Form.Item>

              <Form.Item label="是否公开" name="is_public" valuePropName="checked">
                <Select>
                  <Select.Option value={true}>公开</Select.Option>
                  <Select.Option value={false}>私有</Select.Option>
                </Select>
              </Form.Item>
            </TabPane>

            <TabPane tab="题目描述" key="description">
              <div className="mb-4">
                <label className="block mb-2 font-medium">题目描述</label>
                <MDEditor value={description} onChange={(val) => setDescription(val || '')} height={400} />
              </div>

              <div className="mb-4">
                <label className="block mb-2 font-medium">输入格式</label>
                <MDEditor value={inputFormat} onChange={(val) => setInputFormat(val || '')} height={200} />
              </div>

              <div className="mb-4">
                <label className="block mb-2 font-medium">输出格式</label>
                <MDEditor value={outputFormat} onChange={(val) => setOutputFormat(val || '')} height={200} />
              </div>

              <div className="mb-4">
                <label className="block mb-2 font-medium">数据范围</label>
                <MDEditor value={constraints} onChange={(val) => setConstraints(val || '')} height={200} />
              </div>
            </TabPane>

            <TabPane tab="测试用例" key="testcases" disabled={!id}>
              <div className="mb-4">
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAddTestCase}>
                  添加测试用例
                </Button>
              </div>

              <Table
                columns={testCaseColumns}
                dataSource={testCases}
                rowKey="id"
                pagination={false}
              />
            </TabPane>
          </Tabs>

          <div className="mt-6 flex justify-end gap-4">
            <Button onClick={() => navigate('/problems')}>取消</Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {id ? '保存修改' : '创建题目'}
            </Button>
          </div>
        </Form>
      </Card>

      <Modal
        title={editingTestCase ? '编辑测试用例' : '添加测试用例'}
        open={testCaseModalVisible}
        onCancel={() => setTestCaseModalVisible(false)}
        footer={null}
      >
        <Form form={testCaseForm} layout="vertical" onFinish={handleTestCaseSubmit}>
          <Form.Item
            label="输入"
            name="input"
            rules={[{ required: true, message: '请输入测试输入' }]}
          >
            <TextArea rows={6} placeholder="请输入测试输入" />
          </Form.Item>

          <Form.Item
            label="输出"
            name="output"
            rules={[{ required: true, message: '请输入测试输出' }]}
          >
            <TextArea rows={6} placeholder="请输入测试输出" />
          </Form.Item>

          <Form.Item label="是否为样例" name="is_sample" valuePropName="checked">
            <Select>
              <Select.Option value={true}>是</Select.Option>
              <Select.Option value={false}>否</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="分数"
            name="score"
            initialValue={10}
            rules={[{ required: true, message: '请输入分数' }]}
          >
            <InputNumber min={0} max={100} className="w-full" />
          </Form.Item>

          <div className="flex justify-end gap-4">
            <Button onClick={() => setTestCaseModalVisible(false)}>取消</Button>
            <Button type="primary" htmlType="submit">
              {editingTestCase ? '保存' : '添加'}
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default ProblemEdit
