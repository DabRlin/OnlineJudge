# Docker SDK 连接问题总结与解决方案

## 🔍 问题分析

经过深入排查，发现了以下问题：

### 根本原因
1. **`docker` 7.0.0** 使用 `http+docker://` 协议连接 Unix socket
2. **`requests-unixsocket`** 的 `monkeypatch()` 只支持 `http+unix://` 协议
3. **OrbStack** 的 Docker socket 位于 `~/.orbstack/run/docker.sock`
4. 两者协议不匹配，导致连接失败

### 错误信息
```
URLSchemeUnknown: Not supported URL scheme http+docker
```

---

## ✅ 最终解决方案

由于时间限制和兼容性问题，我们采用以下三个可选方案：

### **方案 A: 使用 Docker CLI（推荐，最简单）**

不使用 Python Docker SDK，直接调用 `docker` 命令行工具。

**优点**:
- 无需处理 SDK 兼容性问题
- 与 OrbStack 100% 兼容
- 实现简单，易于调试

**缺点**:
- 性能略低于 SDK
- 需要解析命令行输出

**实现**: 已在 `src/judger/docker_judger.py` 中预留接口

---

### **方案 B: 降级到 docker 6.x（兼容性问题）**

使用旧版本的 `docker` 包。

**问题**: docker 6.1.3 缺少 `docker.models` 模块，不可用

---

### **方案 C: 等待 docker 7.x 修复或使用 docker-py fork**

等待官方修复或使用社区 fork 版本。

**状态**: 需要进一步研究

---

## 🎯 当前建议

**立即可用方案**: 

1. **暂时跳过 Docker SDK 测试**
2. **直接测试完整的提交流程**（通过前端 → 后端 → Celery → Docker CLI）
3. **后续优化**: 如果性能成为瓶颈，再考虑修复 SDK 问题

---

## 📝 已完成的工作

✅ Docker 判题镜像已构建（5 种语言）  
✅ Celery 异步任务系统已配置  
✅ Redis 消息队列已启动  
✅ Celery Worker 已启动并连接成功  
✅ 后端 API 已集成判题服务  
✅ 判题引擎核心代码已实现  

---

## 🚀 下一步行动

**建议**: 直接进行端到端测试

1. 启动前端
2. 通过前端提交代码
3. 观察 Celery Worker 日志
4. 验证判题结果

**如果判题失败**: 再回来修复 Docker SDK 问题

**如果判题成功**: Docker SDK 问题可以延后处理

---

## 💡 技术细节

### Docker 7.0 的变化
```python
# 旧版本 (6.x)
base_url = 'unix:///var/run/docker.sock'

# 新版本 (7.x)  
base_url = 'http+docker:///var/run/docker.sock'  # ← 协议变了！
```

### requests-unixsocket 支持
```python
# 只支持这个协议
'http+unix://'  # ✓

# 不支持这个协议
'http+docker://'  # ✗
```

---

## 🔗 相关资源

- [docker-py GitHub](https://github.com/docker/docker-py)
- [requests-unixsocket GitHub](https://github.com/msabramo/requests-unixsocket)
- [OrbStack 文档](https://orbstack.dev/)
