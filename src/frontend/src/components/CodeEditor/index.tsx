/**
 * 代码编辑器组件
 * 基于 Monaco Editor
 */

import { FC, useState } from 'react'
import Editor from '@monaco-editor/react'
import { Select, Button, Space, message } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import './styles.css'

interface CodeEditorProps {
  onSubmit?: (code: string, language: string) => void
  defaultLanguage?: string
  defaultCode?: string
  height?: string
  readOnly?: boolean
}

const LANGUAGE_OPTIONS = [
  { label: 'Python', value: 'python' },
  { label: 'C++', value: 'cpp' },
  { label: 'Java', value: 'java' },
  { label: 'Go', value: 'go' },
  { label: 'JavaScript', value: 'javascript' },
]

const DEFAULT_CODE_TEMPLATES: Record<string, string> = {
  python: `# Python 3
def solve():
    # 在这里编写你的代码
    pass

if __name__ == "__main__":
    solve()
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    // 在这里编写你的代码
    
    return 0;
}
`,
  java: `import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // 在这里编写你的代码
        
    }
}
`,
  go: `package main

import "fmt"

func main() {
    // 在这里编写你的代码
    _ = fmt.Scan
}
`,
  javascript: `const lines = require('fs').readFileSync('/dev/stdin', 'utf8').trim().split('\\n');
// 在这里编写你的代码
`,
}

export const CodeEditor: FC<CodeEditorProps> = ({
  onSubmit,
  defaultLanguage = 'python',
  defaultCode,
  height = '500px',
  readOnly = false,
}) => {
  const [language, setLanguage] = useState(defaultLanguage)
  const [code, setCode] = useState(defaultCode || DEFAULT_CODE_TEMPLATES[defaultLanguage])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage)
    // 如果当前代码是默认模板，则切换到新语言的默认模板
    if (!defaultCode && Object.values(DEFAULT_CODE_TEMPLATES).includes(code)) {
      setCode(DEFAULT_CODE_TEMPLATES[newLanguage])
    }
  }

  const handleSubmit = async () => {
    if (!code.trim()) {
      message.warning('请输入代码')
      return
    }

    if (onSubmit) {
      setIsSubmitting(true)
      try {
        await onSubmit(code, language)
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const getMonacoLanguage = (lang: string) => {
    const languageMap: Record<string, string> = {
      python: 'python',
      cpp: 'cpp',
      java: 'java',
      go: 'go',
      javascript: 'javascript',
    }
    return languageMap[lang] || 'plaintext'
  }

  return (
    <div className="code-editor-container">
      <div className="code-editor-toolbar">
        <Space>
          <span className="toolbar-label">语言：</span>
          <Select
            value={language}
            onChange={handleLanguageChange}
            options={LANGUAGE_OPTIONS}
            style={{ width: 120 }}
            disabled={readOnly}
          />
          {!readOnly && onSubmit && (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleSubmit}
              loading={isSubmitting}
            >
              提交代码
            </Button>
          )}
        </Space>
      </div>

      <div className="code-editor-wrapper">
        <Editor
          height={height}
          language={getMonacoLanguage(language)}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme="light"
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on',
          }}
        />
      </div>
    </div>
  )
}

export default CodeEditor
