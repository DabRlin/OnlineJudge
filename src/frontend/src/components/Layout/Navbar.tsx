import { FC } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Menu, Button, Dropdown, Avatar, Space } from 'antd'
import type { MenuProps } from 'antd'
import {
  HomeOutlined,
  CodeOutlined,
  TrophyOutlined,
  TeamOutlined,
  UserOutlined,
  LogoutOutlined,
  FileTextOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'

export const Navbar: FC = () => {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
      danger: true,
    },
  ]

  const menuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: 'problems',
      icon: <CodeOutlined />,
      label: <Link to="/problems">题库</Link>,
    },
    {
      key: 'submissions',
      icon: <FileTextOutlined />,
      label: <Link to="/submissions">提交记录</Link>,
    },
    {
      key: 'contests',
      icon: <TrophyOutlined />,
      label: <Link to="/contests">竞赛</Link>,
    },
    {
      key: 'discuss',
      icon: <TeamOutlined />,
      label: <Link to="/discuss">讨论</Link>,
    },
  ]

  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-blue-600">
              Online Judge
            </Link>
          </div>
          <Menu
            mode="horizontal"
            items={menuItems}
            className="flex-1 justify-center border-0"
          />
          <div className="flex items-center gap-4">
            {isAuthenticated && user ? (
              <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                <Space className="cursor-pointer">
                  <Avatar
                    src={user.avatar}
                    icon={<UserOutlined />}
                    className="bg-blue-500"
                  />
                  <span className="text-gray-700">{user.username}</span>
                </Space>
              </Dropdown>
            ) : (
              <Space>
                <Button type="default" onClick={() => navigate('/login')}>
                  登录
                </Button>
                <Button type="primary" onClick={() => navigate('/register')}>
                  注册
                </Button>
              </Space>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
