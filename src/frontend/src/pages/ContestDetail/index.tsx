/**
 * 竞赛详情页面
 */

import { FC, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Button, Table, Tag, Tabs, Modal, Input, message, Statistic, Row, Col } from 'antd'
import { ArrowLeftOutlined, TrophyOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { contestApi } from '@/services/contest'
import type { Contest, ContestProblem, RankItem, ContestStatus } from '@/types'
import { useAuthStore } from '@/stores/authStore'
import { formatDate } from '@/utils'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import './styles.css'

const { TabPane } = Tabs
const { Countdown } = Statistic

export const ContestDetail: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [contest, setContest] = useState<Contest | null>(null)
  const [problems, setProblems] = useState<ContestProblem[]>([])
  const [rankList, setRankList] = useState<RankItem[]>([])
  const [loading, setLoading] = useState(true)
  const [registerModalVisible, setRegisterModalVisible] = useState(false)
  const [password, setPassword] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  const fetchContest = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const data = await contestApi.getContest(Number(id))
      setContest(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取竞赛详情失败')
      navigate('/contests')
    } finally {
      setLoading(false)
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

  const fetchRank = async () => {
    if (!id) return
    
    try {
      const data = await contestApi.getContestRank(Number(id))
      setRankList(data.items)
    } catch (error: any) {
      console.error('获取排行榜失败:', error)
    }
  }

  useEffect(() => {
    fetchContest()
    fetchProblems()
    fetchRank()
  }, [id])

  const handleRegister = async () => {
    if (!id) return
    
    try {
      await contestApi.registerContest(Number(id), { password: password || undefined })
      message.success('报名成功！')
      setRegisterModalVisible(false)
      setPassword('')
      fetchContest()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '报名失败')
    }
  }

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

  if (loading || !contest) {
    return <div className="flex items-center justify-center min-h-screen">加载中...</div>
  }

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin')
  const problemColumns = [
    {
      title: '题号',
      dataIndex: 'display_id',
      key: 'display_id',
      width: 80,
    },
    {
      title: '题目',
      key: 'title',
      render: (_: any, record: ContestProblem) => (
        <a onClick={() => navigate(`/problems/${record.problem_id}`)}>
          题目 {record.problem_id}
        </a>
      ),
    },
    {
      title: '分数',
      dataIndex: 'score',
      key: 'score',
      width: 80,
      render: (score: number) => contest.rule_type === 'oi' ? `${score}分` : '-',
    },
    {
      title: '通过/提交',
      key: 'stats',
      width: 120,
      render: (_: any, record: ContestProblem) => (
        <span>{record.accepted_count} / {record.submission_count}</span>
      ),
    },
  ]

  const rankColumns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: contest.rule_type === 'acm' ? '通过题数' : '总分',
      key: 'score',
      width: 120,
      render: (_: any, record: RankItem) => (
        contest.rule_type === 'acm' ? record.solved_count : record.total_score
      ),
    },
    {
      title: contest.rule_type === 'acm' ? '罚时' : '用时',
      dataIndex: 'total_time',
      key: 'total_time',
      width: 100,
      render: (time: number) => `${time} 分钟`,
    },
    {
      title: '提交次数',
      dataIndex: 'submission_count',
      key: 'submission_count',
      width: 100,
    },
  ]

  return (
    <div className="contest-detail-page">
      <div className="contest-header">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/contests')}
        >
          返回列表
        </Button>
        {isAdmin && (
          <Button
            type="primary"
            onClick={() => navigate(`/contests/${id}/edit`)}
          >
            编辑竞赛
          </Button>
        )}
      </div>

      <Card className="contest-info-card">
        <div className="contest-title">
          <TrophyOutlined className="title-icon" />
          <h1>{contest.title}</h1>
          <Tag color={getStatusColor(contest.status)}>{getStatusText(contest.status)}</Tag>
        </div>

        <Row gutter={24} className="contest-stats">
          <Col span={6}>
            <Statistic
              title="参赛人数"
              value={contest.participant_count}
              suffix="人"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="提交次数"
              value={contest.submission_count}
              suffix="次"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="竞赛规则"
              value={contest.rule_type === 'acm' ? 'ACM' : 'OI'}
            />
          </Col>
          <Col span={6}>
            {contest.status === 'running' && (
              <Countdown
                title="剩余时间"
                value={new Date(contest.end_time).getTime()}
                format="HH:mm:ss"
              />
            )}
            {contest.status === 'not_started' && (
              <Countdown
                title="距离开始"
                value={new Date(contest.start_time).getTime()}
                format="D 天 HH:mm:ss"
              />
            )}
            {contest.status === 'ended' && (
              <Statistic title="状态" value="已结束" />
            )}
          </Col>
        </Row>

        {user && contest.status !== 'ended' && (
          <div className="contest-actions">
            <Button
              type="primary"
              size="large"
              onClick={() => {
                if (contest.contest_type === 'private') {
                  setRegisterModalVisible(true)
                } else {
                  handleRegister()
                }
              }}
            >
              报名参赛
            </Button>
          </div>
        )}
      </Card>

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="竞赛概览" key="overview">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="开始时间" span={2}>
                {formatDate(contest.start_time)}
              </Descriptions.Item>
              <Descriptions.Item label="结束时间" span={2}>
                {formatDate(contest.end_time)}
              </Descriptions.Item>
              <Descriptions.Item label="时长">
                {contest.duration} 分钟
              </Descriptions.Item>
              <Descriptions.Item label="类型">
                {contest.contest_type === 'public' ? '公开赛' : '私有赛'}
              </Descriptions.Item>
              <Descriptions.Item label="规则">
                {contest.rule_type === 'acm' ? 'ACM 规则' : 'OI 规则'}
              </Descriptions.Item>
              <Descriptions.Item label="实时排名">
                {contest.real_time_rank ? '是' : '否'}
              </Descriptions.Item>
            </Descriptions>

            {contest.description && (
              <div className="contest-description">
                <h3>竞赛说明</h3>
                <MarkdownRenderer content={contest.description} />
              </div>
            )}
          </TabPane>

          <TabPane tab={`题目列表 (${problems.length})`} key="problems">
            <Table
              columns={problemColumns}
              dataSource={problems}
              rowKey="id"
              pagination={false}
            />
          </TabPane>

          <TabPane tab="排行榜" key="rank">
            {contest.is_frozen && (
              <div className="freeze-notice">
                <ClockCircleOutlined /> 排行榜已封榜
              </div>
            )}
            <Table
              columns={rankColumns}
              dataSource={rankList}
              rowKey="user_id"
              pagination={{ pageSize: 50 }}
            />
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        title="报名参赛"
        open={registerModalVisible}
        onOk={handleRegister}
        onCancel={() => {
          setRegisterModalVisible(false)
          setPassword('')
        }}
      >
        <p>此竞赛需要密码才能参加，请输入密码：</p>
        <Input.Password
          placeholder="请输入竞赛密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </Modal>
    </div>
  )
}

export default ContestDetail
