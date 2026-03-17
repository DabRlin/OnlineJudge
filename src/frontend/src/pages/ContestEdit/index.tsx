/**
 * 竞赛创建/编辑页面（管理员）
 */

import { FC, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  DatePicker,
  Select,
  InputNumber,
  Switch,
  Button,
  Space,
  Table,
  Modal,
  message,
} from 'antd'
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { contestApi } from '@/services/contest'
import type { Contest, ContestProblem } from '@/types'
import './styles.css'

const { TextArea } = Input
const { RangePicker } = DatePicker

export const ContestEdit: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [contest, setContest] = useState<Contest | null>(null)
  const [problems, setProblems] = useState<ContestProblem[]>([])
  const [addProblemModalVisible, setAddProblemModalVisible] = useState(false)
  const [problemId, setProblemId] = useState<number | null>(null)
  const [displayId, setDisplayId] = useState('')
  const [score, setScore] = useState(100)

  const isEdit = !!id

  useEffect(() => {
    if (isEdit) {
      fetchContest()
      fetchProblems()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const fetchContest = async () => {
    if (!id) return

    try {
      const data = await contestApi.getContest(Number(id))
      setContest(data)
      
      // 填充表单
      form.setFieldsValue({
        title: data.title,
        description: data.description,
        time_range: [dayjs(data.start_time), dayjs(data.end_time)],
        duration: data.duration,
        contest_type: data.contest_type,
        rule_type: data.rule_type,
        password: data.password,
        is_visible: data.is_visible,
        real_time_rank: data.real_time_rank,
        freeze_time: data.freeze_time,
      })
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取竞赛详情失败')
      navigate('/contests')
    }
  }

  const fetchProblems = async () => {
    if (!id) return

    try {
      const data = await contestApi.getContestProblems(Number(id))
      setProblems(data)
    } catch (error: any) {
      console.error('获取题目列表失败:', error)
    }
  }

  const handleSubmit = async (values: any) => {
    setLoading(true)
    try {
      const [startTime, endTime] = values.time_range
      const contestData = {
        title: values.title,
        description: values.description,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        duration: values.duration,
        contest_type: values.contest_type,
        rule_type: values.rule_type,
        password: values.password,
        is_visible: values.is_visible,
        real_time_rank: values.real_time_rank,
        freeze_time: values.freeze_time,
      }

      if (isEdit) {
        await contestApi.updateContest(Number(id), contestData)
        message.success('竞赛更新成功！')
      } else {
        const newContest = await contestApi.createContest(contestData)
        message.success('竞赛创建成功！')
        navigate(`/contests/${newContest.id}`)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAddProblem = async () => {
    if (!id || !problemId || !displayId) {
      message.error('请填写完整信息')
      return
    }

    try {
      await contestApi.addContestProblem(Number(id), {
        problem_id: problemId,
        display_id: displayId,
        score,
      })
      message.success('题目添加成功！')
      setAddProblemModalVisible(false)
      setProblemId(null)
      setDisplayId('')
      setScore(100)
      fetchProblems()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加题目失败')
    }
  }

  const handleRemoveProblem = async (problemId: number) => {
    if (!id) return

    try {
      await contestApi.removeContestProblem(Number(id), problemId)
      message.success('题目移除成功！')
      fetchProblems()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '移除题目失败')
    }
  }

  const problemColumns = [
    {
      title: '题号',
      dataIndex: 'display_id',
      key: 'display_id',
      width: 80,
    },
    {
      title: '题目 ID',
      dataIndex: 'problem_id',
      key: 'problem_id',
      width: 100,
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
      width: 100,
      render: (_: any, record: ContestProblem) => (
        <Button
          type="link"
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => handleRemoveProblem(record.problem_id)}
        >
          移除
        </Button>
      ),
    },
  ]

  return (
    <div className="contest-edit-page">
      <div className="page-header">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(isEdit ? `/contests/${id}` : '/contests')}
        >
          返回
        </Button>
        <h2>{isEdit ? '编辑竞赛' : '创建竞赛'}</h2>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            contest_type: 'public',
            rule_type: 'acm',
            is_visible: true,
            real_time_rank: true,
            duration: 180,
            freeze_time: 60,
          }}
        >
          <Form.Item
            label="竞赛名称"
            name="title"
            rules={[{ required: true, message: '请输入竞赛名称' }]}
          >
            <Input placeholder="请输入竞赛名称" />
          </Form.Item>

          <Form.Item
            label="竞赛说明"
            name="description"
          >
            <TextArea
              rows={6}
              placeholder="请输入竞赛说明（支持 Markdown）"
            />
          </Form.Item>

          <Form.Item
            label="竞赛时间"
            name="time_range"
            rules={[{ required: true, message: '请选择竞赛时间' }]}
          >
            <RangePicker
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label="竞赛时长（分钟）"
            name="duration"
            rules={[{ required: true, message: '请输入竞赛时长' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="竞赛类型"
            name="contest_type"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="public">公开赛</Select.Option>
              <Select.Option value="private">私有赛</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.contest_type !== currentValues.contest_type
            }
          >
            {({ getFieldValue }) =>
              getFieldValue('contest_type') === 'private' ? (
                <Form.Item
                  label="竞赛密码"
                  name="password"
                  rules={[{ required: true, message: '请输入竞赛密码' }]}
                >
                  <Input.Password placeholder="请输入竞赛密码" />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item
            label="计分规则"
            name="rule_type"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="acm">ACM 规则</Select.Option>
              <Select.Option value="oi">OI 规则</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="是否可见"
            name="is_visible"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="实时排名"
            name="real_time_rank"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="封榜时间（分钟，从结束倒数）"
            name="freeze_time"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                {isEdit ? '保存' : '创建'}
              </Button>
              <Button onClick={() => navigate('/contests')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {isEdit && (
        <Card title="题目管理" className="mt-4">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setAddProblemModalVisible(true)}
            style={{ marginBottom: 16 }}
          >
            添加题目
          </Button>

          <Table
            columns={problemColumns}
            dataSource={problems}
            rowKey="id"
            pagination={false}
          />
        </Card>
      )}

      <Modal
        title="添加题目"
        open={addProblemModalVisible}
        onOk={handleAddProblem}
        onCancel={() => {
          setAddProblemModalVisible(false)
          setProblemId(null)
          setDisplayId('')
          setScore(100)
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <label>题目 ID：</label>
            <InputNumber
              placeholder="请输入题目 ID"
              value={problemId || undefined}
              onChange={(value) => setProblemId(value)}
              style={{ width: '100%' }}
            />
          </div>
          <div>
            <label>题号（A, B, C...）：</label>
            <Input
              placeholder="请输入题号"
              value={displayId}
              onChange={(e) => setDisplayId(e.target.value)}
            />
          </div>
          <div>
            <label>分数（OI 规则）：</label>
            <InputNumber
              placeholder="请输入分数"
              value={score}
              onChange={(value) => setScore(value || 100)}
              style={{ width: '100%' }}
            />
          </div>
        </Space>
      </Modal>
    </div>
  )
}

export default ContestEdit
