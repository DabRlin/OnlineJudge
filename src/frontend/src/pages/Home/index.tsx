import { Link } from 'react-router-dom'
import { Button, Card, Statistic, Row, Col } from 'antd'
import { Code2, Users, Trophy, CheckCircle } from 'lucide-react'

export default function Home() {
  return (
    <div className="container-custom py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          欢迎来到 Online Judge
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          提升编程技能，挑战算法难题，参与编程竞赛
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/problems">
            <Button type="primary" size="large" icon={<Code2 size={20} />}>
              开始刷题
            </Button>
          </Link>
          <Link to="/contests">
            <Button size="large" icon={<Trophy size={20} />}>
              查看竞赛
            </Button>
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <Row gutter={[16, 16]} className="mb-16">
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="题目总数"
              value={1234}
              prefix={<Code2 className="text-primary-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="用户数量"
              value={5678}
              prefix={<Users className="text-green-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="提交总数"
              value={98765}
              prefix={<CheckCircle className="text-blue-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进行中的竞赛"
              value={12}
              prefix={<Trophy className="text-yellow-600" />}
            />
          </Card>
        </Col>
      </Row>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-8">
        <Card title="丰富的题库" bordered={false}>
          <p className="text-gray-600">
            涵盖数据结构、算法、数学等多个领域，难度从入门到竞赛级别
          </p>
        </Card>
        <Card title="实时判题" bordered={false}>
          <p className="text-gray-600">
            支持多种编程语言，毫秒级判题反馈，详细的错误信息
          </p>
        </Card>
        <Card title="在线竞赛" bordered={false}>
          <p className="text-gray-600">
            定期举办编程竞赛，实时排行榜，与全球程序员同台竞技
          </p>
        </Card>
      </div>
    </div>
  )
}
