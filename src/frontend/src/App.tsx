import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Problems from './pages/Problems'
import ProblemDetail from './pages/ProblemDetail'
import ProblemEdit from './pages/ProblemEdit'
import Submissions from './pages/Submissions'
import SubmissionDetail from './pages/SubmissionDetail'
import Contests from './pages/Contests'
import ContestDetail from './pages/ContestDetail'
import ContestEdit from './pages/ContestEdit'

function App() {
  return (
    <Routes>
      {/* 认证相关路由（无布局） */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* 题目详情页（独立布局，全屏） */}
      <Route path="problems/:id" element={<ProblemDetail />} />
      
      {/* 主要路由（带布局） */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="profile" element={<Profile />} />
        <Route path="problems" element={<Problems />} />
        <Route path="problems/new" element={<ProblemEdit />} />
        <Route path="problems/:id/edit" element={<ProblemEdit />} />
        <Route path="submissions" element={<Submissions />} />
        <Route path="submissions/:id" element={<SubmissionDetail />} />
        <Route path="contests" element={<Contests />} />
        <Route path="contests/new" element={<ContestEdit />} />
        <Route path="contests/:id" element={<ContestDetail />} />
        <Route path="contests/:id/edit" element={<ContestEdit />} />
      </Route>
    </Routes>
  )
}

export default App
