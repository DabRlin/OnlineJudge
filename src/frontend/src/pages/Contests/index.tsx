/**
 * 竞赛列表页面
 */

import { FC, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Table, Tag, Button, Tabs, Space, Input, message } from 'antd'
import { TrophyOutlined, PlusOutlined } from '@ant-design/icons'
import { contestApi } from '@/services/contest'
import type { ContestListItem, ContestStatus } from '@/types'
import { useAuthStore } from '@/stores/authStore'
import { formatDate } from '@/utils'
import './styles.css'

const { TabPane } = Tabs
const { Search } = Input

export const Contests: FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [contests, setContests] = useState<ContestListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [activeTab, setActiveTab] = useState<string>('all')
  const [keyword, setKeyword] = useState('')

  const fetchContests = async () => {
    setLoading(true)
    try {
      const statusFilter = activeTab === 'all' ? undefined : activeTab
      const data = await contestApi.getContests({
        page,
        page_size: pageSize,
        status: statusFilter,
        keyword: keyword || undefined,
      })
      setContests(data.items)
      setTotal(data.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取竞赛列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchContests()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, activeTab, keyword])

  const getStatusColor = (status: ContestStatus): string => {
    const colorMap: Record<ContestStatus, string> = {
      not_started: 'default',
      running: 'success',
      ended: 'error',
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status: ContestStatus): string => {
    const textMap: Record<ContestStatus, string> = {
      not_started: '未开始',
      running: '进行中',
      ended: '已结束',
    }
    return textMap[status] || status
  }

  const getRuleTypeText = (ruleType: string): string => {
    return ruleType === 'acm' ? 'ACM' : 'OI'
  }

  const columns = [
    {
      title: '竞赛名称',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: ContestListItem) => (
        <a onClick={() => navigate(`/contests/${record.id}`)}>
          <TrophyOutlined className="mr-2" />
          {text}
        </a>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: ContestStatus) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '规则',
      dataIndex: 'rule_type',
      key: 'rule_type',
      width: 80,
      render: (ruleType: string) => getRuleTypeText(ruleType),
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
      render: (time: string) => formatDate(time),
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      width: 180,
      render: (time: string) => formatDate(time),
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration: number) => `${duration} 分钟`,
    },
    {
      title: '参与人数',
      dataIndex: 'participant_count',
      key: 'participant_count',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: ContestListItem) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/contests/${record.id}`)}
        >
          查看详情
        </Button>
      ),
    },
  ]

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin')

  return (
    <div className="contests-page">
      <Card>
        <div className="contests-header">
          <h2>竞赛列表</h2>
          <Space>
            <Search
              placeholder="搜索竞赛"
              allowClear
              style={{ width: 250 }}
              onSearch={setKeyword}
            />
            {isAdmin && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/contests/new')}
              >
                创建竞赛
              </Button>
            )}
          </Space>
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key)
            setPage(1)
          }}
        >
          <TabPane tab="全部" key="all" />
          <TabPane tab="未开始" key="not_started" />
          <TabPane tab="进行中" key="running" />
          <TabPane tab="已结束" key="ended" />
        </Tabs>

        <Table
          columns={columns}
          dataSource={contests}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 场竞赛`,
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

export default Contests
