/**
 * 登录页面
 */

import { FC } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'
import type { UserLogin } from '@/types'

const { Title, Text } = Typography

export const Login: FC = () => {
  const navigate = useNavigate()
  const { login, loading } = useAuthStore()
  const [form] = Form.useForm()

  const handleSubmit = async (values: UserLogin) => {
    try {
      await login(values)
      navigate('/')
    } catch (error) {
      // Error handled in store
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md shadow-xl">
        <div className="text-center mb-8">
          <Title level={2} className="mb-2">
            欢迎回来
          </Title>
          <Text type="secondary">登录到 Online Judge 系统</Text>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名或邮箱' },
              { min: 3, message: '用户名至少 3 个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名或邮箱"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少 8 个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              className="mt-4"
            >
              登录
            </Button>
          </Form.Item>

          <div className="text-center">
            <Space split="|">
              <Link to="/register">
                <Text type="secondary">还没有账号？立即注册</Text>
              </Link>
              <Link to="/forgot-password">
                <Text type="secondary">忘记密码？</Text>
              </Link>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default Login
