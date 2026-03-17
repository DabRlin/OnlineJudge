/**
 * 用户中心页面
 */

import { FC, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Descriptions, Avatar, Button, Space, Tag, Spin } from 'antd'
import { UserOutlined, EditOutlined, LogoutOutlined } from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'
import { formatDate } from '@/utils'

export const Profile: FC = () => {
  const navigate = useNavigate()
  const { user, isAuthenticated, loading, logout, fetchCurrentUser } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    if (!user) {
      fetchCurrentUser()
    }
  }, [isAuthenticated, user, navigate, fetchCurrentUser])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    )
  }

  const getRoleTag = (role: string) => {
    const roleMap: Record<string, { color: string; text: string }> = {
      user: { color: 'blue', text: '普通用户' },
      admin: { color: 'orange', text: '管理员' },
      super_admin: { color: 'red', text: '超级管理员' },
    }
    const roleInfo = roleMap[role] || roleMap.user
    return <Tag color={roleInfo.color}>{roleInfo.text}</Tag>
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Card
        title={
          <div className="flex items-center gap-4">
            <Avatar
              size={64}
              src={user.avatar}
              icon={<UserOutlined />}
              className="bg-blue-500"
            />
            <div>
              <h2 className="text-2xl font-bold mb-1">{user.username}</h2>
              <div>{getRoleTag(user.role)}</div>
            </div>
          </div>
        }
        extra={
          <Space>
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate('/profile/edit')}
            >
              编辑资料
            </Button>
            <Button
              icon={<LogoutOutlined />}
              onClick={handleLogout}
              danger
            >
              退出登录
            </Button>
          </Space>
        }
      >
        <Descriptions column={1} bordered>
          <Descriptions.Item label="用户 ID">{user.id}</Descriptions.Item>
          <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{user.email}</Descriptions.Item>
          <Descriptions.Item label="角色">
            {getRoleTag(user.role)}
          </Descriptions.Item>
          <Descriptions.Item label="账号状态">
            <Tag color={user.is_active ? 'green' : 'red'}>
              {user.is_active ? '正常' : '已禁用'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {formatDate(user.created_at)}
          </Descriptions.Item>
          {user.updated_at && (
            <Descriptions.Item label="最后更新">
              {formatDate(user.updated_at)}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      <Card title="统计信息" className="mt-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">0</div>
            <div className="text-gray-600 mt-2">已解决题目</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">0</div>
            <div className="text-gray-600 mt-2">提交次数</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">0%</div>
            <div className="text-gray-600 mt-2">通过率</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default Profile
