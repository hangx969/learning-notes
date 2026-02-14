这是一个简单但极其好用的工具，用于手动标准化。

斜杠命令 (Slash Commands) 是手动触发的工作流快捷方式,存在.claude/commands/目录。

本质:
纯Markdown定义的多步骤流程,输入/命令名手动触发。

API注入:
作为用户消息扩展,而非系统提示工具(这是与Skills的核心区别)。

命令内部可以:
调用Skills自动化检查、编排SubAgents并行工作、执行MCP工具链、串联Git操作。

# 典型场景
1. /release - 完整发版流程(测试→构建→打tag→发布→通知)
2. /security-check - 安全扫描(依赖漏洞+代码审计+配置检查)
3. /perf-audit - 性能审计(包体积+加载时间+运行时分析)
4. /refactor-plan - 重构规划(架构分析+影响评估+迁移方案)
5. /onboard - 新人入职(克隆仓库+环境配置+文档导覽)
6. /rollback - 紧急回滚

# 使用
## 示例1
第一步: 定义命令
建文件:.claude/commands/release.md

```
# 版本发布流程

1、拉最新代码确认版本号
2、触发Skills检查:代码审查、完整测试、资源检查
3、生成changelog
、预发布测试
5、人工确认
6、正式发布
7、发通知

```

第二步: 使用
直接输入:/release

第三步: 效果
整个团队按统一流程走,不会漏步骤。版本发布出错率从15%降到0。

## 示例2
在.claude/commands/目录下创建release.md:

```markdown
# 版本发布流程  
你是发布助手,帮助用户安全发布版本。  
  
## 执行步骤  
1、确认当前Git分支是main  
2、拉取最新代码(git pull)  
3、触发Skills:  
- pre-commit-check(代码质量)  
- test-coverage-check(测试覆盖率>80%)  
4、询问版本号(major.minor.patch)  
5、生成changelog(基于Git commit)  
...  
## 每步都需要用户确认  
不要自动执行,每步输出命令,等用户确认。
```

验证: 输入/release,看是否触发完整流程。

