import { Layout } from 'antd'
import { Github, Mail } from 'lucide-react'

const { Footer: AntFooter } = Layout

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <AntFooter className="bg-gray-50 mt-auto">
      <div className="container-custom">
        <div className="flex flex-col md:flex-row justify-between items-center py-6">
          <div className="text-gray-600 mb-4 md:mb-0">
            © {currentYear} Online Judge. All rights reserved.
          </div>
          
          <div className="flex space-x-6">
            <a
              href="https://github.com/yourusername/OnlineJudge"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-primary-600 transition-colors"
            >
              <Github size={20} />
            </a>
            <a
              href="mailto:contact@example.com"
              className="text-gray-600 hover:text-primary-600 transition-colors"
            >
              <Mail size={20} />
            </a>
          </div>
        </div>
      </div>
    </AntFooter>
  )
}
