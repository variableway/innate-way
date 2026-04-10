# Capture TUI 输入模块

这个模块主要考虑的是通过TUI Teminal输入的内容。如果主要模块分的话：
1. input 记录
2. process 模块： 如何把记录的内容转化为可执行的计划和任务
3. output 模块： 如何把处理后的计划和任务输出到项目目录中

实现这个文档内容的话都需要使用githu-web-follow和local-workf-flow skill

## Capture CLI 场景 1： Cli直接输入

使用场景: ClI 命令行输入
1. 用户直接使用cli命令直接输入todo，然后这部分内容保存到ideas这个目录中
2. ideas 这个目录需要categorzie，每一个子目录就是一个category，cli命令输入的时候保存到对应的category目录中，如果没有对应的cateory就创建这个目录
3. category 总目录不能超过10个，如果超过10个提示不能添加新的category
4. 可以通过命令行的方式要求给一个category 目录做分析和提炼出要点，这个应该需要skill，ai帮助，这个如何命令行中实现，或者其他cli中实现，或者skill实现
但是需要程序执行
5. 支持直接文字，也支持一份文件地址，todo保存如何保存容易之后可以找到呢？或者可以容易转化为结构化的TODO Dashboard 或者飞书多维表格

## Capture CLI 场景 2： Terminal 对话形式输入

使用场景 2: 启动这个CLI命令，用户可以直接和这个对话进行输入，让她可以记录对话过程

但是这个场景可能有不同方式：
1. 直接使用claude code/kimi cli这样的工具，有个skill可以直接记录这些完整的对话记录
2. 如果自建一个这样TUI conversation 去调用claude code这种似乎也没有太大意义，那么如何用好这些功能呢》
7. 另外如何可以完整的记录AI 是如何进行判断，分析，确认的，使用的什么分析技能和思维方式，为什么使用这个思维方式再这个分析报告上。

请先实现以上任务，把记录内容都计入本地文件中，主要是分析报告，技术架构，任务等，先不需要写代码，先把事情想清楚一些.

## Task 4: Test TUI-GO 

1. 测试TUI-GO 当前功能
2. 使用build出现的binary进行测试
3. 测试场景包括：创建和删除category，添加和删除todo，查看和确认todo，输出和导入todo
4. 如果有failed case 写入文档中