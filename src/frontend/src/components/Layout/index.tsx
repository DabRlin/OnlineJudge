import { Outlet } from 'react-router-dom'
import { Layout as AntLayout } from 'antd'
import Navbar from './Navbar'
import Footer from './Footer'

const { Content } = AntLayout

export default function Layout() {
  return (
    <AntLayout className="min-h-screen">
      <Navbar />
      <Content className="mt-16">
        <Outlet />
      </Content>
      <Footer />
    </AntLayout>
  )
}
