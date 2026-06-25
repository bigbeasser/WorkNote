---
tags:
  - Arthas
  - Java
  - 故障排查
  - 用户案例
created: 2026-06-24
category: 个人学习/Java工具
aliases:
  - Arthas用户案例
  - Arthas user-case
---

# Arthas 用户案例汇总（GitHub user-case）

> **数据来源**: [alibaba/arthas Issues · label:user-case](https://github.com/alibaba/arthas/issues?q=label%3Auser-case)
> **拉取时间**: 2026-06-24 13:51
> **案例总数**: 60 篇（Open 4 / Closed 56）

## 一句话总结

Arthas 社区 `user-case` 标签汇集了 60 篇真实生产/研发排查案例，覆盖 **性能 Trace 优化、OOM/线程/CPU 定位、Spring 运行时诊断、OGNL 动态执行、与 Spring Boot Admin 集成** 等场景；高频命令为 `trace`、`watch`、`thread`、`ognl`、`vmtool`、`redefine`。

## 场景分类速览

| 场景 | 案例数 | 典型能力 |
|------|--------|---------|
| 性能优化 | 58 | `monitor, thread, watch, stack, vmtool, jad` |
| CPU/线程 | 24 | `monitor, thread, watch, stack, jad, trace` |
| 内存/OOM | 21 | `thread, vmtool, options, trace, ognl, mc` |
| 异常排查 | 39 | `monitor, thread, watch, stack, jad, vmtool` |
| Spring/框架 | 41 | `monitor, thread, watch, stack, vmtool, jad` |
| 集成实践 | 24 | `vmtool, watch, options, mc, profiler` |
| 工具技巧 | 32 | `monitor, thread, watch, stack, jad, mc` |

## 全量案例索引

| # | 标题 | 状态 | 作者 | 创建时间 | 涉及命令 |
|---|------|------|------|----------|----------|
| [2938](https://github.com/alibaba/arthas/issues/2938) | Elasticsearch 进程使用watch命令被卡死了大部分线程 | Open | cfangpp | 2024-11-07 | `monitor, thread` |
| [2893](https://github.com/alibaba/arthas/issues/2893) | 【分享】如何通过arthas来定位 StackOverflowError？ | Open | btpka3 | 2024-09-05 | `watch, stack, thread` |
| [2739](https://github.com/alibaba/arthas/issues/2739) | 使用Arthas 获取 Spring 应用运行时配置值 | Open | hengyunabc | 2023-11-27 | `vmtool, watch` |
| [2526](https://github.com/alibaba/arthas/issues/2526) | 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源 | Open | WangJi92 | 2023-05-17 | `thread, jad` |
| [2521](https://github.com/alibaba/arthas/issues/2521) | 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案 | Closed | v24342317 | 2023-05-14 | `thread` |
| [1920](https://github.com/alibaba/arthas/issues/1920) | Arthas vmtool源码分析 | Closed | loongs-zhang | 2021-09-22 | `vmtool, options` |
| [1892](https://github.com/alibaba/arthas/issues/1892) | 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿） | Closed | reliefeai | 2021-08-19 | `trace` |
| [1823](https://github.com/alibaba/arthas/issues/1823) | 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率 | Closed | reliefeai | 2021-06-14 | `-` |
| [1802](https://github.com/alibaba/arthas/issues/1802) | 使用OGNL表达式获取spring bean 时，bean 的字段值显示是null，但调用字段的get方法显示有值 | Closed | baobinghai | 2021-05-26 | `ognl` |
| [1736](https://github.com/alibaba/arthas/issues/1736) | SpringBoot Admin2.0集成Arthas实践 | Closed | password36 | 2021-03-15 | `mc` |
| [1709](https://github.com/alibaba/arthas/issues/1709) | arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题 | Closed | WangJi92 | 2021-02-25 | `thread, sc` |
| [1687](https://github.com/alibaba/arthas/issues/1687) | 对于某些工具的后台进程，可以使用 -XX:+DisableAttachMechanism 参数，避免用户选择到错误的进程 | Closed | hengyunabc | 2021-02-01 | `stack, trace` |
| [1653](https://github.com/alibaba/arthas/issues/1653) | 使用 SkyWalking & Arthas 优化微服务性能 | Closed | Ax1an | 2021-01-05 | `-` |
| [1602](https://github.com/alibaba/arthas/issues/1602) | alpine容器镜像中生成火焰图错误的其它解决方案 | Closed | shalousun | 2020-12-03 | `profiler` |
| [1601](https://github.com/alibaba/arthas/issues/1601) | SpringBoot Admin集成Arthas实践 | Closed | jujunchen | 2020-12-03 | `-` |
| [1598](https://github.com/alibaba/arthas/issues/1598) | watch/trace 执行中，再执行jad可以看到插入的增强字节码，但停止 watch/trace之后，再执行jad看不到插入的增强字节码 | Closed | hengyunabc | 2020-12-02 | `watch, trace, jad` |
| [1566](https://github.com/alibaba/arthas/issues/1566) | 利用Arthas解决启动StandbyNameNode加载EditLog慢的问题 | Closed | yhf20071 | 2020-11-04 | `trace, profiler, options, stack` |
| [1538](https://github.com/alibaba/arthas/issues/1538) | 工商银行打造在线诊断平台的探索与实践 | Closed | lyghzh | 2020-10-12 | `-` |
| [1525](https://github.com/alibaba/arthas/issues/1525) | watch配合stack查看调用链 | Closed | saytime | 2020-09-24 | `watch` |
| [1504](https://github.com/alibaba/arthas/issues/1504) | Arthas实践: 定位修复Redisson连接池问题 | Closed | mikawudi | 2020-09-16 | `-` |
| [1494](https://github.com/alibaba/arthas/issues/1494) | Arthas实践：解决由于druid版本造成的慢sql问题 | Closed | hengyunabc | 2020-09-11 | `-` |
| [1424](https://github.com/alibaba/arthas/issues/1424) | arthas 获取spring被代理的目标对象 | Closed | WangJi92 | 2020-08-13 | `ognl, tt, trace, sc` |
| [1416](https://github.com/alibaba/arthas/issues/1416) | 使用arthas+jprofiler做复杂链路分析 | Closed | oxsean | 2020-08-11 | `profiler` |
| [1311](https://github.com/alibaba/arthas/issues/1311) | Arthas ByteKit 深度解读(2)：本地变量及参数绑定 | Closed | kylixs | 2020-07-16 | `stack, getstatic` |
| [1310](https://github.com/alibaba/arthas/issues/1310) | Arthas ByteKit 深度解读(1)：基本原理介绍 | Closed | kylixs | 2020-07-16 | `stack` |
| [1249](https://github.com/alibaba/arthas/issues/1249) | Web-Console一站式解决方案 | Closed | cookiejoo | 2020-06-08 | `-` |
| [1244](https://github.com/alibaba/arthas/issues/1244) | 获取分布式跟踪的 traceId，比如eagleeye的 | Closed | hengyunabc | 2020-06-05 | `watch, trace` |
| [1202](https://github.com/alibaba/arthas/issues/1202) | 利用Arthas精准定位Java应用CPU负载过高问题 | Closed | cafe-babe | 2020-05-22 | `thread, tt, jad, ognl` |
| [1004](https://github.com/alibaba/arthas/issues/1004) | Arthas IDEA插件 | Closed | hengyunabc | 2020-01-07 | `-` |
| [1003](https://github.com/alibaba/arthas/issues/1003) | 一图掌握Arthas—常用命令汇总 | Closed | w454196785 | 2020-01-07 | `-` |
| [849](https://github.com/alibaba/arthas/issues/849) | Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server | Closed | hengyunabc | 2019-09-10 | `heapdump, thread` |
| [772](https://github.com/alibaba/arthas/issues/772) | 如何在内部类对象中访问外部类对象的成员变量 | Closed | ralf0131 | 2019-07-10 | `watch` |
| [764](https://github.com/alibaba/arthas/issues/764) | Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题 | Closed | aiqing2171 | 2019-07-04 | `sc, trace, watch` |
| [763](https://github.com/alibaba/arthas/issues/763) | Arthas源码分析--jad反编译原理 | Closed | hengyunabc | 2019-07-03 | `jad, watch, trace, stack, tt, mc, redefine` |
| [729](https://github.com/alibaba/arthas/issues/729) | Arthas实践：是哪个Controller处理了请求？ | Closed | hengyunabc | 2019-06-05 | `trace, watch` |
| [597](https://github.com/alibaba/arthas/issues/597) | Arthas里 Trace 命令怎样工作的/ Trace命令的实现原理 | Closed | hengyunabc | 2019-03-22 | `trace, stack, getstatic` |
| [569](https://github.com/alibaba/arthas/issues/569) | 引发线程cpu占用率持续飙升的根因分析 | Closed | excel-bat | 2019-03-14 | `monitor, thread, ognl` |
| [561](https://github.com/alibaba/arthas/issues/561) | Arthas排查Kubernetes中的应用频繁挂掉重启问题 | Closed | klboke | 2019-03-06 | `thread, stack, trace` |
| [559](https://github.com/alibaba/arthas/issues/559) | 2019-03-21 [阿里云峰会-北京]Java诊断利器Arthas排查问题实践  | Closed | hengyunabc | 2019-03-04 | `-` |
| [557](https://github.com/alibaba/arthas/issues/557) | Arthas协助排查线上skywalking不可用问题 | Closed | klboke | 2019-03-01 | `thread, ognl, watch` |
| [549](https://github.com/alibaba/arthas/issues/549) | Mbean support | Closed | dili91 | 2019-02-26 | `ognl` |
| [537](https://github.com/alibaba/arthas/issues/537) | Arthas实践--jad/mc/redefine线上热更新一条龙 | Closed | hengyunabc | 2019-02-20 | `jad, mc, redefine, sc` |
| [508](https://github.com/alibaba/arthas/issues/508) | Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全 | Closed | hengyunabc | 2019-02-13 | `mc, redefine, jad, watch, trace, tt, monitor, stack` |
| [482](https://github.com/alibaba/arthas/issues/482) | Alibaba Arthas实践--获取到Spring Context，然后为所欲为 | Closed | hengyunabc | 2019-01-28 | `trace, watch, monitor, tt, ognl` |
| [477](https://github.com/alibaba/arthas/issues/477) | arthas实践 -- sbt Missing scala-library.jar | Closed | x334085347 | 2019-01-25 | `jad, watch` |
| [442](https://github.com/alibaba/arthas/issues/442) | 记录如何使用arthas进行远程访问 | Closed | haifzhu | 2019-01-12 | `-` |
| [434](https://github.com/alibaba/arthas/issues/434) | watch/monitor/trace 等判断重载函数/同名函数 | Closed | hengyunabc | 2019-01-07 | `watch, monitor, trace, thread` |
| [429](https://github.com/alibaba/arthas/issues/429) | Arthas实践--快速排查Spring Boot应用404/401问题 | Closed | hengyunabc | 2019-01-07 | `trace` |
| [406](https://github.com/alibaba/arthas/issues/406) | [slides] 2018.12.22 Green tea JUG meetup@Shanghai  | Closed | ralf0131 | 2018-12-25 | `-` |
| [327](https://github.com/alibaba/arthas/issues/327) | 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践 | Closed | hengyunabc | 2018-12-01 | `watch, redefine, ognl, sc, tt, trace, thread, jad` |
| [324](https://github.com/alibaba/arthas/issues/324) | Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验 | Closed | hengyunabc | 2018-11-29 | `ognl, watch, jad` |
| [270](https://github.com/alibaba/arthas/issues/270) | lambda代码的trace | Closed | along101 | 2018-10-29 | `thread, trace` |
| [263](https://github.com/alibaba/arthas/issues/263) | Arthas实践--使用redefine排查应用奇怪的日志来源 | Closed | hengyunabc | 2018-10-23 | `redefine, stack` |
| [237](https://github.com/alibaba/arthas/issues/237) | 使用Arthas排查线上应用日志打满问题 | Closed | hengyunabc | 2018-10-16 | `thread, sc, getstatic` |
| [222](https://github.com/alibaba/arthas/issues/222) | Debug Arthas In IDEA | Closed | hengyunabc | 2018-10-11 | `-` |
| [198](https://github.com/alibaba/arthas/issues/198) | No class or method is affected when trying command like trace or watch | Closed | ralf0131 | 2018-10-09 | `trace, watch, options, sc, sm` |
| [160](https://github.com/alibaba/arthas/issues/160) | 利用Arthas排查Spring Boot应用NoSuchMethodError | Closed | hengyunabc | 2018-09-25 | `sc, jad` |
| [71](https://github.com/alibaba/arthas/issues/71) | Arthas的一些特殊用法文档说明 | Closed | hengyunabc | 2018-09-19 | `ognl` |
| [20](https://github.com/alibaba/arthas/issues/20) | 【Arthas问题排查集】谁调用了System.exit/System.gc? | Closed | ralf0131 | 2018-09-14 | `options, stack, thread` |
| [11](https://github.com/alibaba/arthas/issues/11) | 【Arthas问题排查集】活用ognl表达式 | Closed | hengyunabc | 2018-09-12 | `ognl, thread, watch` |

## 分类详情与摘要

### 性能优化（58）

#### [2938] Elasticsearch 进程使用watch命令被卡死了大部分线程

- **链接**: https://github.com/alibaba/arthas/issues/2938
- **状态**: open | **作者**: cfangpp | **创建**: 2024-11-07
- **涉及命令**: `monitor, thread`

> **摘要**：实际运行结果，最好有详细的日志，异常栈。尽量贴文本。

#### [2893] 【分享】如何通过arthas来定位 StackOverflowError？

- **链接**: https://github.com/alibaba/arthas/issues/2893
- **状态**: open | **作者**: btpka3 | **创建**: 2024-09-05
- **涉及命令**: `watch, stack, thread`

> **摘要**：如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调用前）执行 - 通过当前调用堆栈的深度大于某个阈值，在实际发生StackOverflowError前输出完整堆栈。 示例arthas命令 下面的case是判断调用堆栈深度500。 定位到异常点之后，就可以review相关代码，再配合该行进行...

#### [2739] 使用Arthas 获取 Spring 应用运行时配置值

- **链接**: https://github.com/alibaba/arthas/issues/2739
- **状态**: open | **作者**: hengyunabc | **创建**: 2023-11-27
- **涉及命令**: `vmtool, watch`

> **摘要**：众所周之，Spring 应用的配置注入方式非常多。除了我们熟悉的方式，比如 * System Properties/System Env * application.properties/application.yaml * spring profiles * spring cloud config * https://docs.spring.io/spring-boot/docs/2.1.13.RELEASE/reference/html/boot-features-external-config.html 对于开发人员来说，在运行时怎样确定某个配置是否生效？它的具体值是什么？ 比如获取server.port的具体值： 1....

#### [2526] 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源

- **链接**: https://github.com/alibaba/arthas/issues/2526
- **状态**: open | **作者**: WangJi92 | **创建**: 2023-05-17
- **涉及命令**: `thread, jad`

> **摘要**：背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反序列化失败.. 自己写一个mock 服务,eg 返回对象 返回一个string 断点跟踪 JacksonResponseBodyConverter.convert 确实是 抛出了一个异常 com.fasterxml.jackson.core...

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1920] Arthas vmtool源码分析

- **链接**: https://github.com/alibaba/arthas/issues/1920
- **状态**: closed | **作者**: loongs-zhang | **创建**: 2021-09-22
- **涉及命令**: `vmtool, options`

> **摘要**：Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write application with JNI ? step1.定义native方法 step2.生成头文件 我们使用命令生成c语言使用的头文件。 下面是生成头文件Main.h的具体内容： step3.编写native的实现MainImpl.c st...

#### [1892] 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）

- **链接**: https://github.com/alibaba/arthas/issues/1892
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-08-19
- **涉及命令**: `trace`

> **摘要**：Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 [图片] 从链路上看，线上获取一整天的数据时大概 300 多 ms，而查询数据库只有 11ms，说明大部分时间都是程序组装数据时消耗的，于是动起了优化代码的念头。 ...

#### [1823] 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率

- **链接**: https://github.com/alibaba/arthas/issues/1823
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-06-14

> **摘要**：（用户案例） 前提 本方法最适用于 Spring Boot 项目。 谁拖垮了效率？ 本地开发时有两个操作最耗时： 1. 无法热加载：每次代码变更都要重启项目，重启时间长。 2. 代码调用困难：代码深层的方法，需要有类似 HTTP 的触发入口，再经过各种判断条件一层一层调用过来，非常麻烦。 所以我在寻找一种可以不停机的开发方法，所有变更都能随时生效，代码随写随测。 探索 代码热变更方面，我使用了久负盛名的 IDEA 插件 JRebel。该插件可以做到热加载绝大部分的新增/修改代码，安装使用方式可以在网上搜索。 但有了 JRebel 之后，我发现仍然很难调用看到的方法，如果通过 HTTP 接口调用过来很麻烦，过程很长，并且前后的一...

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1709] arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题

- **链接**: https://github.com/alibaba/arthas/issues/1709
- **状态**: closed | **作者**: WangJi92 | **创建**: 2021-02-25
- **涉及命令**: `thread, sc`

> **摘要**：一、背景 大早上 线上k8s 机子 某个机子 cpu 飙高，导致k8s 健康检查失败，线上环境会自动执行jstack，上传到oss 通知到 钉钉告警群，直接分析锁、cpu 高的线程。 二、过程分析 2.1 排查cpu 占用最高的线程 使用jstack 分析: 发现占用CPU最高的线程栈是： org.apache.commons.beanutils.MethodUtils#getMatchingAccessibleMethod 。 当然也可以使用arthas 的 thread -n 10 命令 ，由于自动监控抓取的，省去了这一步了。 一般的常规操作 jstack+top ，参考： * https://blog.csdn.net/...

#### [1687] 对于某些工具的后台进程，可以使用 -XX:+DisableAttachMechanism 参数，避免用户选择到错误的进程

- **链接**: https://github.com/alibaba/arthas/issues/1687
- **状态**: closed | **作者**: hengyunabc | **创建**: 2021-02-01
- **涉及命令**: `stack, trace`

> **摘要**：在一台机器上，应用方通常会认为只有自己的进程。但是某些工具的后台进程也是以 java方式启动的，就会导致用户可能手滑选择了工具的后台进程，导致出错。 所以这些工具的后台进程可以考虑加上 -XX:+DisableAttachMechanism 的jvm参数。这样子用户选错了就会报错：

#### [1653] 使用 SkyWalking & Arthas 优化微服务性能

- **链接**: https://github.com/alibaba/arthas/issues/1653
- **状态**: closed | **作者**: Ax1an | **创建**: 2021-01-05

> **摘要**：使用 SkyWalking & Arthas 优化微服务性能.md

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1598] watch/trace 执行中，再执行jad可以看到插入的增强字节码，但停止 watch/trace之后，再执行jad看不到插入的增强字节码

- **链接**: https://github.com/alibaba/arthas/issues/1598
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-12-02
- **涉及命令**: `watch, trace, jad`

> **摘要**：首先，要了解目前的 watch/trace是怎样工作的： * 目前版本，即3.4.4版本里，所有的 watch/trace 共用一个 ClassFileTransformer 在TransformerManager 里 https://github.com/alibaba/arthas/blob/arthas-all-3.4.4/core/src/main/java/com/taobao/arthas/core/advisor/TransformerManager.java#L38 * 多次 watch/trace 也是共用原来的 ClassFileTransformer * watch/trace 命令 ctrl +c 停止...

#### [1566] 利用Arthas解决启动StandbyNameNode加载EditLog慢的问题

- **链接**: https://github.com/alibaba/arthas/issues/1566
- **状态**: closed | **作者**: yhf20071 | **创建**: 2020-11-04
- **涉及命令**: `trace, profiler, options, stack`

> **摘要**：公司新搭HDFS集群，namenode做ha，但是在启动StandbyNamenode节点的时候出现奇怪的现象：空集群加载Editlog很慢，每次重启几乎耗时都在二三十分钟 * 为了方便大家理解，大致说下StandbyNamenode（以下简称SNN）启动过程： 1. SNN启动时，如果本地没有FSImage会去ANN（ActiveNamenode）拉取FSImage 2. 如果本地有FSImage，则会根据transactionId去JournalNode拉取gap的editlog，在本地做合并 * 问题就出在第2步，在从JournalNode拉取EditLog过程中出现固定15s延迟。一般来说，空集群几乎没有操作，...

#### [1525] watch配合stack查看调用链

- **链接**: https://github.com/alibaba/arthas/issues/1525
- **状态**: closed | **作者**: saytime | **创建**: 2020-09-24
- **涉及命令**: `watch`

> **摘要**：使用watch命令观察到某异常方法后，如果想知道调用链，如何进一步使用stack查看调用链 watch demo.MathGame primeFactors "{params[0],throwExp}" -e -x 2

#### [1504] Arthas实践: 定位修复Redisson连接池问题

- **链接**: https://github.com/alibaba/arthas/issues/1504
- **状态**: closed | **作者**: mikawudi | **创建**: 2020-09-16

> **摘要**：https://mp.weixin.qq.com/s/WcEAmUjtzOLRfGTeKPvrvg

#### [1494] Arthas实践：解决由于druid版本造成的慢sql问题

- **链接**: https://github.com/alibaba/arthas/issues/1494
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-09-11

> **摘要**：https://mp.weixin.qq.com/s/7SQxy0hSm_urJY05QyIwMg

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1416] 使用arthas+jprofiler做复杂链路分析

- **链接**: https://github.com/alibaba/arthas/issues/1416
- **状态**: closed | **作者**: oxsean | **创建**: 2020-08-11
- **涉及命令**: `profiler`

> **摘要**：arthas提供了profiler命令，可以生成热点火焰图。通过采样录制调用链路来做性能分析，极大提升了线上排查性能问题的效率。 但是有一个问题，当async-profiler全量采样导出的svg文件太大时，想要找到关键的调用点，就非常困难。 没有办法做聚合或过滤，这方面本地的profiler工具比如jprofiler、yourkits就方便很多，有没有办法将两者结合起来呢？ 经过分析发现，async-profiler支持jfr (Java Flight Recorder)格式输出，jprofiler也支持打开jfr快照，成了！具体操作步骤如下： 启动arthas之后，执行以下采样命令： %t 表示当前时间，-d 后面是采样秒...

#### [1311] Arthas ByteKit 深度解读(2)：本地变量及参数绑定

- **链接**: https://github.com/alibaba/arthas/issues/1311
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack, getstatic`

> **摘要**：Arthas ByteKit 深度解读(2)：本地变量及参数绑定 前言 本文通过分析ByteKit的本地变量绑定（LocalVarsBinding）处理代码，结合Java Opcode手册、asm代码、javap反汇编字节码等工具，深入讲解每个指令的用法及在本场景的实际作用。结合上下文线索，从字节码的角度去理解ByteKit 本地变量绑定的实现过程。 相关文章： Arthas ByteKit 深度解读(1)：基本原理介绍 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完...

#### [1310] Arthas ByteKit 深度解读(1)：基本原理介绍

- **链接**: https://github.com/alibaba/arthas/issues/1310
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack`

> **摘要**：Arthas ByteKit 深度解读(1)：基本原理介绍 前言 本文由整体到局部的思路展开分析Arthas ByteKit 字节码处理框架，结合类图和数据流图，介绍ByteKit字节码处理流程及核心对象。 相关文章： Arthas ByteKit 深度解读(2)：本地变量及参数绑定 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完成字节码增强。 * ByteKit 基本用法 * ByteKit 字节码处理流程 * 如何解析Interceptor Class * Byt...

#### [1249] Web-Console一站式解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1249
- **状态**: closed | **作者**: cookiejoo | **创建**: 2020-06-08

> **摘要**：今天接上次的写了一篇个人在开发Arthas的web控制台一站式解决方案 https://blog.csdn.net/caodegao/article/details/106622430

#### [1244] 获取分布式跟踪的 traceId，比如eagleeye的

- **链接**: https://github.com/alibaba/arthas/issues/1244
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-06-05
- **涉及命令**: `watch, trace`

> **摘要**：可以直接调用static函数来获取traceId，比如： trace 命令会自动打印 eagleeye的traceId，比如：

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [1004] Arthas IDEA插件

- **链接**: https://github.com/alibaba/arthas/issues/1004
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-01-07

> **摘要**：插件地址： https://plugins.jetbrains.com/plugin/13581-arthas-idea 使用文档： https://www.yuque.com/docs/share/fa77c7b4-c016-4de6-9fa3-58ef25a97948?#

#### [1003] 一图掌握Arthas—常用命令汇总

- **链接**: https://github.com/alibaba/arthas/issues/1003
- **状态**: closed | **作者**: w454196785 | **创建**: 2020-01-07

> **摘要**：总结了Arthas中的常用命令、参数以及用例，在使用时可以方便查到需要的功能。 下载点我：Arthas.xmind.tar.gz !ArtHas

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [772] 如何在内部类对象中访问外部类对象的成员变量

- **链接**: https://github.com/alibaba/arthas/issues/772
- **状态**: closed | **作者**: ralf0131 | **创建**: 2019-07-10
- **涉及命令**: `watch`

> **摘要**：我想在内部类的run方法里面，访问allConnections这个变量的大小，应该如何写ognl表达式？ 使用target.this$0可以访问到外部类对象

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [763] Arthas源码分析--jad反编译原理

- **链接**: https://github.com/alibaba/arthas/issues/763
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-07-03
- **涉及命令**: `jad, watch, trace, stack, tt, mc, redefine`

> **摘要**：Arthas是阿里巴巴开源的Java应用诊断利器，本文介绍Arthas 3.1.1版本里jad命令的实现原理。 * https://github.com/alibaba/arthas * https://alibaba.github.io/arthas/jad.html jad即java decompiler，把JVM已加载类的字节码反编译成Java代码。比如反编译String类： 1. 获取到字节码 2. 反编译为Java代码 最常见的思路是，在classpaths下面查找，比如 ClassLoader.getResource("java/lang/String.class")，但是这样子查找到的字节码不一定对。比如可能有多...

#### [729] Arthas实践：是哪个Controller处理了请求？

- **链接**: https://github.com/alibaba/arthas/issues/729
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-06-05
- **涉及命令**: `trace, watch`

> **摘要**：Arthas是阿里巴巴开源的Java诊断利器，深受开发者喜爱。 * https://github.com/alibaba/arthas * Arthas在线教程 之前分享了Arthas怎样排查 404/401 的问题: http://hengyunabc.github.io/arthas-spring-boot-404-401/ 我们可以快速定位一个请求是被哪些Filter拦截的，或者请求最终是由哪些Servlet处理的。 但有时，我们想知道一个请求是被哪个Spring MVC Controller处理的。如果翻代码的话，会比较难找，并且不一定准确。 通过Arthas可以精确定位是哪个Controller处理请求。 还是以这个...

#### [597] Arthas里 Trace 命令怎样工作的/ Trace命令的实现原理

- **链接**: https://github.com/alibaba/arthas/issues/597
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-03-22
- **涉及命令**: `trace, stack, getstatic`

> **摘要**：3.3.0 版本后，增加动态trace功能，可以动态深入下一层： https://alibaba.github.io/arthas/trace.html Trace只对匹配到的method内的 子method 做统计 常见的一个疑问是 trace命令为什么有时候输出有时候是只有一级的，有时候是多级的？ 首先trace命令的原理是：对匹配到的method内的 子method 做统计。 使用arthas执行 trace Demo hello: 可以看到每一个invokevirtual都对应一个 trace结果里的entry。 所以，trace实际上是在每一个invokevirtual 前后插入代码，然后统计调用的时...

#### [569] 引发线程cpu占用率持续飙升的根因分析

- **链接**: https://github.com/alibaba/arthas/issues/569
- **状态**: closed | **作者**: excel-bat | **创建**: 2019-03-14
- **涉及命令**: `monitor, thread, ognl`

> **摘要**：在最近系统性能调优的过程中，用到了很多工具，由于笔者开发的主要是java应用，从linux 工具到jdk工具，以及全链路追踪工具，都解决了相当多的问题，而完全面向java应用的的工具，笔者墙裂推荐 阿里的arthas,这款工具简单，简单到分析cpu、内存问题分分钟就能找到些蛛丝马迹。 问题抽象 --- 项目最近做了一次大升级，压测后发现项目跑了24小时后，开始出现某个线程cpu占用100%，如下图所示： 重启后，仔细观察该线程，发现线程cpu使用率在逐渐递增，我们通过jvisualvm，快速的找到了问题的堆栈，发现是某个redis操作，这个操作里面调用了lua脚本，并使用了evalsha（）的方式执行。 抽丝剥茧 --- 从现...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [559] 2019-03-21 [阿里云峰会-北京]Java诊断利器Arthas排查问题实践 

- **链接**: https://github.com/alibaba/arthas/issues/559
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-03-04

> **摘要**：https://yunqi.youku.com/2019/beijing/meeting?spm=a2c4e.11165380.1317296.1#322-16

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [549] Mbean support

- **链接**: https://github.com/alibaba/arthas/issues/549
- **状态**: closed | **作者**: dili91 | **创建**: 2019-02-26
- **涉及命令**: `ognl`

> **摘要**：Hi, first of all thank you for this amazing tool. it was a huge help for me in the last weeks, much more than existing and commercial tools. Now my question: Is there a way I can enquiry MBean objects on a running java process ? In a similar way like on VisualVm + MBean plugin installed... If not already feasible wi...

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [508] Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全

- **链接**: https://github.com/alibaba/arthas/issues/508
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-13
- **涉及命令**: `mc, redefine, jad, watch, trace, tt, monitor, stack, sc, sm`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 从Arthas上个版本发布，已经过去两个多月了，Arthas 3.1.0版本不仅带来大家投票出来的新LOGO，还带来强大的新功能和更好的易用性，下面一一介绍。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas 在新版本Arthas里，增加了在线教程，用户可以在线运行Demo，一步步学习Arthas的各种用法，推荐新手尝试： * Arthas基础教程 * Arthas进阶教程 3.1.0版本里新增命令mc，不是方块游戏mc，而是Memory Com...

#### [482] Alibaba Arthas实践--获取到Spring Context，然后为所欲为

- **链接**: https://github.com/alibaba/arthas/issues/482
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-28
- **涉及命令**: `trace, watch, monitor, tt, ognl`

> **摘要**：Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。 * https://github.com/alibaba/arthas Arthas提供了非常丰富的关于调用拦截的命令，比如 trace/watch/monitor/tt 。但是很多时候我们在排查问题时，需要更多的线索，并不只是函数的参数和返回值。 比如在一个spring应用里，想获取到spring context里的其它bean。如果能随意获取到spring bean，那就可以“为所欲为”了。 下面介绍如何利用Arthas获取到spring context。 Demo： https://github.com/hengyunabc/spring-boot-...

#### [477] arthas实践 -- sbt Missing scala-library.jar

- **链接**: https://github.com/alibaba/arthas/issues/477
- **状态**: closed | **作者**: x334085347 | **创建**: 2019-01-25
- **涉及命令**: `jad, watch`

> **摘要**：+ 在使用sbt构建一个spark 的项目的时候 遇到一个很奇怪的问题 Missing scala-library.jar 如下图. 按理来说如果少jar包sbt 会自动去下载的 这个就很奇怪了. [图片] + 于是想到用arthas 看一下.首先在arthas中用jad反编译了下scala.sys.pachage\$ 的代码 . + 这里的error只是抛了个异常 没有其他...

#### [442] 记录如何使用arthas进行远程访问

- **链接**: https://github.com/alibaba/arthas/issues/442
- **状态**: closed | **作者**: haifzhu | **创建**: 2019-01-12

> **摘要**：arthas需要在本地进行attach, 通常情况下，开发没有权限登录服务器，如何让开发使用arthas进行远程诊断呢？ 公司内部一般都有一些web管理平台，供开发者去管理自己的应用，如何把arthas集成到自己的web管理平台？ 在公司内部的web管理平台，基于某个主机上的某个应用有个叫开启arthas调试的按钮，点击该按钮会触发如下操作： 1. 登录到对应服务器上，基于应用名称查找对应的pid 2. 检查默认的http端口是不是有pid在监听 3. 如果该端口没有被监听，直接attach该pid之后返回 attach命令: sudo su - -c "java /opt/arthas/lib/3.0.5/arthas/ar...

#### [434] watch/monitor/trace 等判断重载函数/同名函数

- **链接**: https://github.com/alibaba/arthas/issues/434
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `watch, monitor, trace, thread`

> **摘要**：Test类有两个 hello函数，它们的参数不一样，如果直接watch Test hello params，则会匹配到两个hello函数。 那么怎么准确watch第二个hello函数呢？ 下面给出两种方式，ognl表达式是很灵活的，大家可以多尝试下。 第一种方式，判断params的length： 第二种方式，判断params的类型（注意，这里因为int会被包装为Object，所以params[0]的类型是java.lang.Integer）：

#### [429] Arthas实践--快速排查Spring Boot应用404/401问题

- **链接**: https://github.com/alibaba/arthas/issues/429
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `trace`

> **摘要**：在Java Web/Spring Boot开发时，很常见的问题是： * 网页访问404了，为什么访问不到？ * 登陆失败了，请求返回401，到底是哪个Filter拦截了我的请求？ 碰到这种问题时，通常很头痛，特别是在线上环境时。 本文介绍使用Alibaba开源的Java诊断利器Arthas，来快速定位这类Web请求404/401问题。 * https://github.com/alibaba/arthas 在进入正题之前，先温习下知识。一个普通的Java Web请求处理流程大概是这样子的： 可以看出请求经过Spring MVC的DispatcherServlet处理，最终由ViewResolver分派给FreeMarkerVi...

#### [406] [slides] 2018.12.22 Green tea JUG meetup@Shanghai 

- **链接**: https://github.com/alibaba/arthas/issues/406
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-12-25

> **摘要**：2018.12.22 Green tea JUG meetup分享PDF格式下载: Introduction to Arthas.pdf

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [324] Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验

- **链接**: https://github.com/alibaba/arthas/issues/324
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-11-29
- **涉及命令**: `ognl, watch, jad`

> **摘要**：Arthas从9月份开源以来，受到广大Java开发者的支持，Github Star数三个月超过6000，非常感谢用户支持。同时用户给Arthas提出了很多建议，其中反映最多的是： 1. Windows平台用户体验不好 1. Attach的进程和最终连接的进程不一致 1. 某些环境下没有安装Telnet，不能连接到Arthas Server 1. 本地启动，不需要下载远程（很多公司安全考虑） 1. 下载速度慢（默认从maven central repository下载） 在Arthas 3.0.5版本里，我们在用户体验方面做了很多改进，下面逐一介绍。 * 文档：https://alibaba.github.io/arthas/...

#### [270] lambda代码的trace

- **链接**: https://github.com/alibaba/arthas/issues/270
- **状态**: closed | **作者**: along101 | **创建**: 2018-10-29
- **涉及命令**: `thread, trace`

> **摘要**：如何使用trace，跟踪到lambda代码段的执行？ 调试断点到lambda里面，发现生成到类为accept:-1, 920011586 (com.yzl.test.Test$$Lambda$1) 用 trace com.yzl.test.Test$$Lambda$1 * 发现不行，直接使用 trace com.yzl.test.Test * 发现跟踪到的trace： trace com.yzl.test.Test lambda$main$0 trace com.yzl.test.Test *

#### [263] Arthas实践--使用redefine排查应用奇怪的日志来源

- **链接**: https://github.com/alibaba/arthas/issues/263
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-23
- **涉及命令**: `redefine, stack`

> **摘要**：随着应用越来越复杂，依赖越来越多，日志系统越来越混乱，有时会出现一些奇怪的日志，比如： 那么怎样排查这些奇怪的日志从哪里打印出来的呢？因为搞不清楚是什么logger打印出来的，所以想定位就比较头疼。 下面介绍用arthas的redefine命令快速定位奇怪日志来源。 * Arthas: https://github.com/alibaba/arthas * redefine命令：https://alibaba.github.io/arthas/redefine.html 首先在java代码里，字符串拼接基本都是通过StringBuilder来实现的。比如下面的代码： 实际上生成的字节码也是用StringBuilder来拼接的：...

#### [237] 使用Arthas排查线上应用日志打满问题

- **链接**: https://github.com/alibaba/arthas/issues/237
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-16
- **涉及命令**: `thread, sc, getstatic`

> **摘要**：在应用的 service_stdout.log里一直输出下面的日志，直接把磁盘打满了： service_stdout.log是进程标准输出的重定向，可以初步判定是tair插件把日志输出到了stdout里。 尽管有了初步的判断，但是具体logger为什么会打到stdout里，还需要进一步排查，常见的方法可能是本地debug。 下面介绍利用arthas直接在线上定位问题的过程，主要使用sc和getstatic命令。 * https://alibaba.github.io/arthas/sc.html * https://alibaba.github.io/arthas/getstatic.html 日志是io.netty.chan...

#### [222] Debug Arthas In IDEA

- **链接**: https://github.com/alibaba/arthas/issues/222
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-11

> **摘要**：1. It is better to run as-package.sh before start debugging, it will install the newest version. 2. If you want to debug Arthas core like Commands, please check the second part. The first part, debug Arthas how to attach to target JVM. Debug com.taobao.arthas.core.Arthas Start com.taobao.arthas.core.Arthas Actually...

#### [198] No class or method is affected when trying command like trace or watch

- **链接**: https://github.com/alibaba/arthas/issues/198
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-10-09
- **涉及命令**: `trace, watch, options, sc, sm`

> **摘要**：0. 先确认Arthas已经挂载到正确的Java进程里面了，检查Arthas连上时输出的PID，确认是想要挂载的目标进程ID(和 ps -ef 的结果比对) 1. 先用sc或者sm搜索对应的类和方法，确认已经被JVM加载 2. 在~/logs/arthas/arthas.log中查找有没有Method code too large的异常 3. 存在该异常时，尝试用reset class_name命令对类进行恢复，再进行trace，watch等操作 4. 系统级别的类默认不能进行增强，需要增强是请参考这里的unsafe开关，增强系统类时请谨慎操作 0. Please confirm that Arthas is attached...

#### [160] 利用Arthas排查Spring Boot应用NoSuchMethodError

- **链接**: https://github.com/alibaba/arthas/issues/160
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-25
- **涉及命令**: `sc, jad`

> **摘要**：有时spring boot应用会遇到java.lang.NoSuchMethodError的问题，下面以具体的demo来说明怎样利用arthas来排查。 Demo: https://github.com/hengyunabc/spring-boot-inside/tree/master/demo-NoSuchMethodError 在应用的main函数里catch住异常，保证进程不退出 很多时候当应用抛出异常后，进程退出了，就比较难排查问题。可以先改下main函数，把异常catch住： 显然，异常的意思是AnnotationAwareOrderComparator缺少sort(Ljava/util/List;)V这个函数。 参...

#### [71] Arthas的一些特殊用法文档说明

- **链接**: https://github.com/alibaba/arthas/issues/71
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-19
- **涉及命令**: `ognl`

> **摘要**：ognl表达式官网：https://commons.apache.org/dormant/commons-ognl/language-guide.html

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

### CPU/线程（24）

#### [2938] Elasticsearch 进程使用watch命令被卡死了大部分线程

- **链接**: https://github.com/alibaba/arthas/issues/2938
- **状态**: open | **作者**: cfangpp | **创建**: 2024-11-07
- **涉及命令**: `monitor, thread`

> **摘要**：实际运行结果，最好有详细的日志，异常栈。尽量贴文本。

#### [2893] 【分享】如何通过arthas来定位 StackOverflowError？

- **链接**: https://github.com/alibaba/arthas/issues/2893
- **状态**: open | **作者**: btpka3 | **创建**: 2024-09-05
- **涉及命令**: `watch, stack, thread`

> **摘要**：如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调用前）执行 - 通过当前调用堆栈的深度大于某个阈值，在实际发生StackOverflowError前输出完整堆栈。 示例arthas命令 下面的case是判断调用堆栈深度500。 定位到异常点之后，就可以review相关代码，再配合该行进行...

#### [2526] 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源

- **链接**: https://github.com/alibaba/arthas/issues/2526
- **状态**: open | **作者**: WangJi92 | **创建**: 2023-05-17
- **涉及命令**: `thread, jad`

> **摘要**：背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反序列化失败.. 自己写一个mock 服务,eg 返回对象 返回一个string 断点跟踪 JacksonResponseBodyConverter.convert 确实是 抛出了一个异常 com.fasterxml.jackson.core...

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1892] 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）

- **链接**: https://github.com/alibaba/arthas/issues/1892
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-08-19
- **涉及命令**: `trace`

> **摘要**：Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 [图片] 从链路上看，线上获取一整天的数据时大概 300 多 ms，而查询数据库只有 11ms，说明大部分时间都是程序组装数据时消耗的，于是动起了优化代码的念头。 ...

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1709] arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题

- **链接**: https://github.com/alibaba/arthas/issues/1709
- **状态**: closed | **作者**: WangJi92 | **创建**: 2021-02-25
- **涉及命令**: `thread, sc`

> **摘要**：一、背景 大早上 线上k8s 机子 某个机子 cpu 飙高，导致k8s 健康检查失败，线上环境会自动执行jstack，上传到oss 通知到 钉钉告警群，直接分析锁、cpu 高的线程。 二、过程分析 2.1 排查cpu 占用最高的线程 使用jstack 分析: 发现占用CPU最高的线程栈是： org.apache.commons.beanutils.MethodUtils#getMatchingAccessibleMethod 。 当然也可以使用arthas 的 thread -n 10 命令 ，由于自动监控抓取的，省去了这一步了。 一般的常规操作 jstack+top ，参考： * https://blog.csdn.net/...

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1416] 使用arthas+jprofiler做复杂链路分析

- **链接**: https://github.com/alibaba/arthas/issues/1416
- **状态**: closed | **作者**: oxsean | **创建**: 2020-08-11
- **涉及命令**: `profiler`

> **摘要**：arthas提供了profiler命令，可以生成热点火焰图。通过采样录制调用链路来做性能分析，极大提升了线上排查性能问题的效率。 但是有一个问题，当async-profiler全量采样导出的svg文件太大时，想要找到关键的调用点，就非常困难。 没有办法做聚合或过滤，这方面本地的profiler工具比如jprofiler、yourkits就方便很多，有没有办法将两者结合起来呢？ 经过分析发现，async-profiler支持jfr (Java Flight Recorder)格式输出，jprofiler也支持打开jfr快照，成了！具体操作步骤如下： 启动arthas之后，执行以下采样命令： %t 表示当前时间，-d 后面是采样秒...

#### [1244] 获取分布式跟踪的 traceId，比如eagleeye的

- **链接**: https://github.com/alibaba/arthas/issues/1244
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-06-05
- **涉及命令**: `watch, trace`

> **摘要**：可以直接调用static函数来获取traceId，比如： trace 命令会自动打印 eagleeye的traceId，比如：

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [597] Arthas里 Trace 命令怎样工作的/ Trace命令的实现原理

- **链接**: https://github.com/alibaba/arthas/issues/597
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-03-22
- **涉及命令**: `trace, stack, getstatic`

> **摘要**：3.3.0 版本后，增加动态trace功能，可以动态深入下一层： https://alibaba.github.io/arthas/trace.html Trace只对匹配到的method内的 子method 做统计 常见的一个疑问是 trace命令为什么有时候输出有时候是只有一级的，有时候是多级的？ 首先trace命令的原理是：对匹配到的method内的 子method 做统计。 使用arthas执行 trace Demo hello: 可以看到每一个invokevirtual都对应一个 trace结果里的entry。 所以，trace实际上是在每一个invokevirtual 前后插入代码，然后统计调用的时...

#### [569] 引发线程cpu占用率持续飙升的根因分析

- **链接**: https://github.com/alibaba/arthas/issues/569
- **状态**: closed | **作者**: excel-bat | **创建**: 2019-03-14
- **涉及命令**: `monitor, thread, ognl`

> **摘要**：在最近系统性能调优的过程中，用到了很多工具，由于笔者开发的主要是java应用，从linux 工具到jdk工具，以及全链路追踪工具，都解决了相当多的问题，而完全面向java应用的的工具，笔者墙裂推荐 阿里的arthas,这款工具简单，简单到分析cpu、内存问题分分钟就能找到些蛛丝马迹。 问题抽象 --- 项目最近做了一次大升级，压测后发现项目跑了24小时后，开始出现某个线程cpu占用100%，如下图所示： 重启后，仔细观察该线程，发现线程cpu使用率在逐渐递增，我们通过jvisualvm，快速的找到了问题的堆栈，发现是某个redis操作，这个操作里面调用了lua脚本，并使用了evalsha（）的方式执行。 抽丝剥茧 --- 从现...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [434] watch/monitor/trace 等判断重载函数/同名函数

- **链接**: https://github.com/alibaba/arthas/issues/434
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `watch, monitor, trace, thread`

> **摘要**：Test类有两个 hello函数，它们的参数不一样，如果直接watch Test hello params，则会匹配到两个hello函数。 那么怎么准确watch第二个hello函数呢？ 下面给出两种方式，ognl表达式是很灵活的，大家可以多尝试下。 第一种方式，判断params的length： 第二种方式，判断params的类型（注意，这里因为int会被包装为Object，所以params[0]的类型是java.lang.Integer）：

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [270] lambda代码的trace

- **链接**: https://github.com/alibaba/arthas/issues/270
- **状态**: closed | **作者**: along101 | **创建**: 2018-10-29
- **涉及命令**: `thread, trace`

> **摘要**：如何使用trace，跟踪到lambda代码段的执行？ 调试断点到lambda里面，发现生成到类为accept:-1, 920011586 (com.yzl.test.Test$$Lambda$1) 用 trace com.yzl.test.Test$$Lambda$1 * 发现不行，直接使用 trace com.yzl.test.Test * 发现跟踪到的trace： trace com.yzl.test.Test lambda$main$0 trace com.yzl.test.Test *

#### [263] Arthas实践--使用redefine排查应用奇怪的日志来源

- **链接**: https://github.com/alibaba/arthas/issues/263
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-23
- **涉及命令**: `redefine, stack`

> **摘要**：随着应用越来越复杂，依赖越来越多，日志系统越来越混乱，有时会出现一些奇怪的日志，比如： 那么怎样排查这些奇怪的日志从哪里打印出来的呢？因为搞不清楚是什么logger打印出来的，所以想定位就比较头疼。 下面介绍用arthas的redefine命令快速定位奇怪日志来源。 * Arthas: https://github.com/alibaba/arthas * redefine命令：https://alibaba.github.io/arthas/redefine.html 首先在java代码里，字符串拼接基本都是通过StringBuilder来实现的。比如下面的代码： 实际上生成的字节码也是用StringBuilder来拼接的：...

#### [237] 使用Arthas排查线上应用日志打满问题

- **链接**: https://github.com/alibaba/arthas/issues/237
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-16
- **涉及命令**: `thread, sc, getstatic`

> **摘要**：在应用的 service_stdout.log里一直输出下面的日志，直接把磁盘打满了： service_stdout.log是进程标准输出的重定向，可以初步判定是tair插件把日志输出到了stdout里。 尽管有了初步的判断，但是具体logger为什么会打到stdout里，还需要进一步排查，常见的方法可能是本地debug。 下面介绍利用arthas直接在线上定位问题的过程，主要使用sc和getstatic命令。 * https://alibaba.github.io/arthas/sc.html * https://alibaba.github.io/arthas/getstatic.html 日志是io.netty.chan...

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

### 内存/OOM（21）

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1920] Arthas vmtool源码分析

- **链接**: https://github.com/alibaba/arthas/issues/1920
- **状态**: closed | **作者**: loongs-zhang | **创建**: 2021-09-22
- **涉及命令**: `vmtool, options`

> **摘要**：Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write application with JNI ? step1.定义native方法 step2.生成头文件 我们使用命令生成c语言使用的头文件。 下面是生成头文件Main.h的具体内容： step3.编写native的实现MainImpl.c st...

#### [1892] 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）

- **链接**: https://github.com/alibaba/arthas/issues/1892
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-08-19
- **涉及命令**: `trace`

> **摘要**：Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 [图片] 从链路上看，线上获取一整天的数据时大概 300 多 ms，而查询数据库只有 11ms，说明大部分时间都是程序组装数据时消耗的，于是动起了优化代码的念头。 ...

#### [1802] 使用OGNL表达式获取spring bean 时，bean 的字段值显示是null，但调用字段的get方法显示有值

- **链接**: https://github.com/alibaba/arthas/issues/1802
- **状态**: closed | **作者**: baobinghai | **创建**: 2021-05-26
- **涉及命令**: `ognl`

> **摘要**：主要是由于getBean 获取的是一个代理类，使用的是cglib 的继承方式，字段也是父类的字段，所以是null。有值的字段应该是target对象。因此需要获取target。

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1311] Arthas ByteKit 深度解读(2)：本地变量及参数绑定

- **链接**: https://github.com/alibaba/arthas/issues/1311
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack, getstatic`

> **摘要**：Arthas ByteKit 深度解读(2)：本地变量及参数绑定 前言 本文通过分析ByteKit的本地变量绑定（LocalVarsBinding）处理代码，结合Java Opcode手册、asm代码、javap反汇编字节码等工具，深入讲解每个指令的用法及在本场景的实际作用。结合上下文线索，从字节码的角度去理解ByteKit 本地变量绑定的实现过程。 相关文章： Arthas ByteKit 深度解读(1)：基本原理介绍 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完...

#### [1310] Arthas ByteKit 深度解读(1)：基本原理介绍

- **链接**: https://github.com/alibaba/arthas/issues/1310
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack`

> **摘要**：Arthas ByteKit 深度解读(1)：基本原理介绍 前言 本文由整体到局部的思路展开分析Arthas ByteKit 字节码处理框架，结合类图和数据流图，介绍ByteKit字节码处理流程及核心对象。 相关文章： Arthas ByteKit 深度解读(2)：本地变量及参数绑定 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完成字节码增强。 * ByteKit 基本用法 * ByteKit 字节码处理流程 * 如何解析Interceptor Class * Byt...

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [763] Arthas源码分析--jad反编译原理

- **链接**: https://github.com/alibaba/arthas/issues/763
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-07-03
- **涉及命令**: `jad, watch, trace, stack, tt, mc, redefine`

> **摘要**：Arthas是阿里巴巴开源的Java应用诊断利器，本文介绍Arthas 3.1.1版本里jad命令的实现原理。 * https://github.com/alibaba/arthas * https://alibaba.github.io/arthas/jad.html jad即java decompiler，把JVM已加载类的字节码反编译成Java代码。比如反编译String类： 1. 获取到字节码 2. 反编译为Java代码 最常见的思路是，在classpaths下面查找，比如 ClassLoader.getResource("java/lang/String.class")，但是这样子查找到的字节码不一定对。比如可能有多...

#### [569] 引发线程cpu占用率持续飙升的根因分析

- **链接**: https://github.com/alibaba/arthas/issues/569
- **状态**: closed | **作者**: excel-bat | **创建**: 2019-03-14
- **涉及命令**: `monitor, thread, ognl`

> **摘要**：在最近系统性能调优的过程中，用到了很多工具，由于笔者开发的主要是java应用，从linux 工具到jdk工具，以及全链路追踪工具，都解决了相当多的问题，而完全面向java应用的的工具，笔者墙裂推荐 阿里的arthas,这款工具简单，简单到分析cpu、内存问题分分钟就能找到些蛛丝马迹。 问题抽象 --- 项目最近做了一次大升级，压测后发现项目跑了24小时后，开始出现某个线程cpu占用100%，如下图所示： 重启后，仔细观察该线程，发现线程cpu使用率在逐渐递增，我们通过jvisualvm，快速的找到了问题的堆栈，发现是某个redis操作，这个操作里面调用了lua脚本，并使用了evalsha（）的方式执行。 抽丝剥茧 --- 从现...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [508] Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全

- **链接**: https://github.com/alibaba/arthas/issues/508
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-13
- **涉及命令**: `mc, redefine, jad, watch, trace, tt, monitor, stack, sc, sm`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 从Arthas上个版本发布，已经过去两个多月了，Arthas 3.1.0版本不仅带来大家投票出来的新LOGO，还带来强大的新功能和更好的易用性，下面一一介绍。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas 在新版本Arthas里，增加了在线教程，用户可以在线运行Demo，一步步学习Arthas的各种用法，推荐新手尝试： * Arthas基础教程 * Arthas进阶教程 3.1.0版本里新增命令mc，不是方块游戏mc，而是Memory Com...

#### [477] arthas实践 -- sbt Missing scala-library.jar

- **链接**: https://github.com/alibaba/arthas/issues/477
- **状态**: closed | **作者**: x334085347 | **创建**: 2019-01-25
- **涉及命令**: `jad, watch`

> **摘要**：+ 在使用sbt构建一个spark 的项目的时候 遇到一个很奇怪的问题 Missing scala-library.jar 如下图. 按理来说如果少jar包sbt 会自动去下载的 这个就很奇怪了. [图片] + 于是想到用arthas 看一下.首先在arthas中用jad反编译了下scala.sys.pachage\$ 的代码 . + 这里的error只是抛了个异常 没有其他...

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

### 异常排查（39）

#### [2938] Elasticsearch 进程使用watch命令被卡死了大部分线程

- **链接**: https://github.com/alibaba/arthas/issues/2938
- **状态**: open | **作者**: cfangpp | **创建**: 2024-11-07
- **涉及命令**: `monitor, thread`

> **摘要**：实际运行结果，最好有详细的日志，异常栈。尽量贴文本。

#### [2893] 【分享】如何通过arthas来定位 StackOverflowError？

- **链接**: https://github.com/alibaba/arthas/issues/2893
- **状态**: open | **作者**: btpka3 | **创建**: 2024-09-05
- **涉及命令**: `watch, stack, thread`

> **摘要**：如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调用前）执行 - 通过当前调用堆栈的深度大于某个阈值，在实际发生StackOverflowError前输出完整堆栈。 示例arthas命令 下面的case是判断调用堆栈深度500。 定位到异常点之后，就可以review相关代码，再配合该行进行...

#### [2526] 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源

- **链接**: https://github.com/alibaba/arthas/issues/2526
- **状态**: open | **作者**: WangJi92 | **创建**: 2023-05-17
- **涉及命令**: `thread, jad`

> **摘要**：背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反序列化失败.. 自己写一个mock 服务,eg 返回对象 返回一个string 断点跟踪 JacksonResponseBodyConverter.convert 确实是 抛出了一个异常 com.fasterxml.jackson.core...

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1920] Arthas vmtool源码分析

- **链接**: https://github.com/alibaba/arthas/issues/1920
- **状态**: closed | **作者**: loongs-zhang | **创建**: 2021-09-22
- **涉及命令**: `vmtool, options`

> **摘要**：Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write application with JNI ? step1.定义native方法 step2.生成头文件 我们使用命令生成c语言使用的头文件。 下面是生成头文件Main.h的具体内容： step3.编写native的实现MainImpl.c st...

#### [1892] 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）

- **链接**: https://github.com/alibaba/arthas/issues/1892
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-08-19
- **涉及命令**: `trace`

> **摘要**：Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 [图片] 从链路上看，线上获取一整天的数据时大概 300 多 ms，而查询数据库只有 11ms，说明大部分时间都是程序组装数据时消耗的，于是动起了优化代码的念头。 ...

#### [1802] 使用OGNL表达式获取spring bean 时，bean 的字段值显示是null，但调用字段的get方法显示有值

- **链接**: https://github.com/alibaba/arthas/issues/1802
- **状态**: closed | **作者**: baobinghai | **创建**: 2021-05-26
- **涉及命令**: `ognl`

> **摘要**：主要是由于getBean 获取的是一个代理类，使用的是cglib 的继承方式，字段也是父类的字段，所以是null。有值的字段应该是target对象。因此需要获取target。

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1709] arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题

- **链接**: https://github.com/alibaba/arthas/issues/1709
- **状态**: closed | **作者**: WangJi92 | **创建**: 2021-02-25
- **涉及命令**: `thread, sc`

> **摘要**：一、背景 大早上 线上k8s 机子 某个机子 cpu 飙高，导致k8s 健康检查失败，线上环境会自动执行jstack，上传到oss 通知到 钉钉告警群，直接分析锁、cpu 高的线程。 二、过程分析 2.1 排查cpu 占用最高的线程 使用jstack 分析: 发现占用CPU最高的线程栈是： org.apache.commons.beanutils.MethodUtils#getMatchingAccessibleMethod 。 当然也可以使用arthas 的 thread -n 10 命令 ，由于自动监控抓取的，省去了这一步了。 一般的常规操作 jstack+top ，参考： * https://blog.csdn.net/...

#### [1687] 对于某些工具的后台进程，可以使用 -XX:+DisableAttachMechanism 参数，避免用户选择到错误的进程

- **链接**: https://github.com/alibaba/arthas/issues/1687
- **状态**: closed | **作者**: hengyunabc | **创建**: 2021-02-01
- **涉及命令**: `stack, trace`

> **摘要**：在一台机器上，应用方通常会认为只有自己的进程。但是某些工具的后台进程也是以 java方式启动的，就会导致用户可能手滑选择了工具的后台进程，导致出错。 所以这些工具的后台进程可以考虑加上 -XX:+DisableAttachMechanism 的jvm参数。这样子用户选错了就会报错：

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1525] watch配合stack查看调用链

- **链接**: https://github.com/alibaba/arthas/issues/1525
- **状态**: closed | **作者**: saytime | **创建**: 2020-09-24
- **涉及命令**: `watch`

> **摘要**：使用watch命令观察到某异常方法后，如果想知道调用链，如何进一步使用stack查看调用链 watch demo.MathGame primeFactors "{params[0],throwExp}" -e -x 2

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1311] Arthas ByteKit 深度解读(2)：本地变量及参数绑定

- **链接**: https://github.com/alibaba/arthas/issues/1311
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack, getstatic`

> **摘要**：Arthas ByteKit 深度解读(2)：本地变量及参数绑定 前言 本文通过分析ByteKit的本地变量绑定（LocalVarsBinding）处理代码，结合Java Opcode手册、asm代码、javap反汇编字节码等工具，深入讲解每个指令的用法及在本场景的实际作用。结合上下文线索，从字节码的角度去理解ByteKit 本地变量绑定的实现过程。 相关文章： Arthas ByteKit 深度解读(1)：基本原理介绍 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完...

#### [1310] Arthas ByteKit 深度解读(1)：基本原理介绍

- **链接**: https://github.com/alibaba/arthas/issues/1310
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack`

> **摘要**：Arthas ByteKit 深度解读(1)：基本原理介绍 前言 本文由整体到局部的思路展开分析Arthas ByteKit 字节码处理框架，结合类图和数据流图，介绍ByteKit字节码处理流程及核心对象。 相关文章： Arthas ByteKit 深度解读(2)：本地变量及参数绑定 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完成字节码增强。 * ByteKit 基本用法 * ByteKit 字节码处理流程 * 如何解析Interceptor Class * Byt...

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [763] Arthas源码分析--jad反编译原理

- **链接**: https://github.com/alibaba/arthas/issues/763
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-07-03
- **涉及命令**: `jad, watch, trace, stack, tt, mc, redefine`

> **摘要**：Arthas是阿里巴巴开源的Java应用诊断利器，本文介绍Arthas 3.1.1版本里jad命令的实现原理。 * https://github.com/alibaba/arthas * https://alibaba.github.io/arthas/jad.html jad即java decompiler，把JVM已加载类的字节码反编译成Java代码。比如反编译String类： 1. 获取到字节码 2. 反编译为Java代码 最常见的思路是，在classpaths下面查找，比如 ClassLoader.getResource("java/lang/String.class")，但是这样子查找到的字节码不一定对。比如可能有多...

#### [729] Arthas实践：是哪个Controller处理了请求？

- **链接**: https://github.com/alibaba/arthas/issues/729
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-06-05
- **涉及命令**: `trace, watch`

> **摘要**：Arthas是阿里巴巴开源的Java诊断利器，深受开发者喜爱。 * https://github.com/alibaba/arthas * Arthas在线教程 之前分享了Arthas怎样排查 404/401 的问题: http://hengyunabc.github.io/arthas-spring-boot-404-401/ 我们可以快速定位一个请求是被哪些Filter拦截的，或者请求最终是由哪些Servlet处理的。 但有时，我们想知道一个请求是被哪个Spring MVC Controller处理的。如果翻代码的话，会比较难找，并且不一定准确。 通过Arthas可以精确定位是哪个Controller处理请求。 还是以这个...

#### [597] Arthas里 Trace 命令怎样工作的/ Trace命令的实现原理

- **链接**: https://github.com/alibaba/arthas/issues/597
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-03-22
- **涉及命令**: `trace, stack, getstatic`

> **摘要**：3.3.0 版本后，增加动态trace功能，可以动态深入下一层： https://alibaba.github.io/arthas/trace.html Trace只对匹配到的method内的 子method 做统计 常见的一个疑问是 trace命令为什么有时候输出有时候是只有一级的，有时候是多级的？ 首先trace命令的原理是：对匹配到的method内的 子method 做统计。 使用arthas执行 trace Demo hello: 可以看到每一个invokevirtual都对应一个 trace结果里的entry。 所以，trace实际上是在每一个invokevirtual 前后插入代码，然后统计调用的时...

#### [569] 引发线程cpu占用率持续飙升的根因分析

- **链接**: https://github.com/alibaba/arthas/issues/569
- **状态**: closed | **作者**: excel-bat | **创建**: 2019-03-14
- **涉及命令**: `monitor, thread, ognl`

> **摘要**：在最近系统性能调优的过程中，用到了很多工具，由于笔者开发的主要是java应用，从linux 工具到jdk工具，以及全链路追踪工具，都解决了相当多的问题，而完全面向java应用的的工具，笔者墙裂推荐 阿里的arthas,这款工具简单，简单到分析cpu、内存问题分分钟就能找到些蛛丝马迹。 问题抽象 --- 项目最近做了一次大升级，压测后发现项目跑了24小时后，开始出现某个线程cpu占用100%，如下图所示： 重启后，仔细观察该线程，发现线程cpu使用率在逐渐递增，我们通过jvisualvm，快速的找到了问题的堆栈，发现是某个redis操作，这个操作里面调用了lua脚本，并使用了evalsha（）的方式执行。 抽丝剥茧 --- 从现...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [508] Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全

- **链接**: https://github.com/alibaba/arthas/issues/508
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-13
- **涉及命令**: `mc, redefine, jad, watch, trace, tt, monitor, stack, sc, sm`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 从Arthas上个版本发布，已经过去两个多月了，Arthas 3.1.0版本不仅带来大家投票出来的新LOGO，还带来强大的新功能和更好的易用性，下面一一介绍。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas 在新版本Arthas里，增加了在线教程，用户可以在线运行Demo，一步步学习Arthas的各种用法，推荐新手尝试： * Arthas基础教程 * Arthas进阶教程 3.1.0版本里新增命令mc，不是方块游戏mc，而是Memory Com...

#### [482] Alibaba Arthas实践--获取到Spring Context，然后为所欲为

- **链接**: https://github.com/alibaba/arthas/issues/482
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-28
- **涉及命令**: `trace, watch, monitor, tt, ognl`

> **摘要**：Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。 * https://github.com/alibaba/arthas Arthas提供了非常丰富的关于调用拦截的命令，比如 trace/watch/monitor/tt 。但是很多时候我们在排查问题时，需要更多的线索，并不只是函数的参数和返回值。 比如在一个spring应用里，想获取到spring context里的其它bean。如果能随意获取到spring bean，那就可以“为所欲为”了。 下面介绍如何利用Arthas获取到spring context。 Demo： https://github.com/hengyunabc/spring-boot-...

#### [477] arthas实践 -- sbt Missing scala-library.jar

- **链接**: https://github.com/alibaba/arthas/issues/477
- **状态**: closed | **作者**: x334085347 | **创建**: 2019-01-25
- **涉及命令**: `jad, watch`

> **摘要**：+ 在使用sbt构建一个spark 的项目的时候 遇到一个很奇怪的问题 Missing scala-library.jar 如下图. 按理来说如果少jar包sbt 会自动去下载的 这个就很奇怪了. [图片] + 于是想到用arthas 看一下.首先在arthas中用jad反编译了下scala.sys.pachage\$ 的代码 . + 这里的error只是抛了个异常 没有其他...

#### [434] watch/monitor/trace 等判断重载函数/同名函数

- **链接**: https://github.com/alibaba/arthas/issues/434
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `watch, monitor, trace, thread`

> **摘要**：Test类有两个 hello函数，它们的参数不一样，如果直接watch Test hello params，则会匹配到两个hello函数。 那么怎么准确watch第二个hello函数呢？ 下面给出两种方式，ognl表达式是很灵活的，大家可以多尝试下。 第一种方式，判断params的length： 第二种方式，判断params的类型（注意，这里因为int会被包装为Object，所以params[0]的类型是java.lang.Integer）：

#### [429] Arthas实践--快速排查Spring Boot应用404/401问题

- **链接**: https://github.com/alibaba/arthas/issues/429
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `trace`

> **摘要**：在Java Web/Spring Boot开发时，很常见的问题是： * 网页访问404了，为什么访问不到？ * 登陆失败了，请求返回401，到底是哪个Filter拦截了我的请求？ 碰到这种问题时，通常很头痛，特别是在线上环境时。 本文介绍使用Alibaba开源的Java诊断利器Arthas，来快速定位这类Web请求404/401问题。 * https://github.com/alibaba/arthas 在进入正题之前，先温习下知识。一个普通的Java Web请求处理流程大概是这样子的： 可以看出请求经过Spring MVC的DispatcherServlet处理，最终由ViewResolver分派给FreeMarkerVi...

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [324] Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验

- **链接**: https://github.com/alibaba/arthas/issues/324
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-11-29
- **涉及命令**: `ognl, watch, jad`

> **摘要**：Arthas从9月份开源以来，受到广大Java开发者的支持，Github Star数三个月超过6000，非常感谢用户支持。同时用户给Arthas提出了很多建议，其中反映最多的是： 1. Windows平台用户体验不好 1. Attach的进程和最终连接的进程不一致 1. 某些环境下没有安装Telnet，不能连接到Arthas Server 1. 本地启动，不需要下载远程（很多公司安全考虑） 1. 下载速度慢（默认从maven central repository下载） 在Arthas 3.0.5版本里，我们在用户体验方面做了很多改进，下面逐一介绍。 * 文档：https://alibaba.github.io/arthas/...

#### [270] lambda代码的trace

- **链接**: https://github.com/alibaba/arthas/issues/270
- **状态**: closed | **作者**: along101 | **创建**: 2018-10-29
- **涉及命令**: `thread, trace`

> **摘要**：如何使用trace，跟踪到lambda代码段的执行？ 调试断点到lambda里面，发现生成到类为accept:-1, 920011586 (com.yzl.test.Test$$Lambda$1) 用 trace com.yzl.test.Test$$Lambda$1 * 发现不行，直接使用 trace com.yzl.test.Test * 发现跟踪到的trace： trace com.yzl.test.Test lambda$main$0 trace com.yzl.test.Test *

#### [237] 使用Arthas排查线上应用日志打满问题

- **链接**: https://github.com/alibaba/arthas/issues/237
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-16
- **涉及命令**: `thread, sc, getstatic`

> **摘要**：在应用的 service_stdout.log里一直输出下面的日志，直接把磁盘打满了： service_stdout.log是进程标准输出的重定向，可以初步判定是tair插件把日志输出到了stdout里。 尽管有了初步的判断，但是具体logger为什么会打到stdout里，还需要进一步排查，常见的方法可能是本地debug。 下面介绍利用arthas直接在线上定位问题的过程，主要使用sc和getstatic命令。 * https://alibaba.github.io/arthas/sc.html * https://alibaba.github.io/arthas/getstatic.html 日志是io.netty.chan...

#### [198] No class or method is affected when trying command like trace or watch

- **链接**: https://github.com/alibaba/arthas/issues/198
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-10-09
- **涉及命令**: `trace, watch, options, sc, sm`

> **摘要**：0. 先确认Arthas已经挂载到正确的Java进程里面了，检查Arthas连上时输出的PID，确认是想要挂载的目标进程ID(和 ps -ef 的结果比对) 1. 先用sc或者sm搜索对应的类和方法，确认已经被JVM加载 2. 在~/logs/arthas/arthas.log中查找有没有Method code too large的异常 3. 存在该异常时，尝试用reset class_name命令对类进行恢复，再进行trace，watch等操作 4. 系统级别的类默认不能进行增强，需要增强是请参考这里的unsafe开关，增强系统类时请谨慎操作 0. Please confirm that Arthas is attached...

#### [160] 利用Arthas排查Spring Boot应用NoSuchMethodError

- **链接**: https://github.com/alibaba/arthas/issues/160
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-25
- **涉及命令**: `sc, jad`

> **摘要**：有时spring boot应用会遇到java.lang.NoSuchMethodError的问题，下面以具体的demo来说明怎样利用arthas来排查。 Demo: https://github.com/hengyunabc/spring-boot-inside/tree/master/demo-NoSuchMethodError 在应用的main函数里catch住异常，保证进程不退出 很多时候当应用抛出异常后，进程退出了，就比较难排查问题。可以先改下main函数，把异常catch住： 显然，异常的意思是AnnotationAwareOrderComparator缺少sort(Ljava/util/List;)V这个函数。 参...

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

### Spring/框架（41）

#### [2938] Elasticsearch 进程使用watch命令被卡死了大部分线程

- **链接**: https://github.com/alibaba/arthas/issues/2938
- **状态**: open | **作者**: cfangpp | **创建**: 2024-11-07
- **涉及命令**: `monitor, thread`

> **摘要**：实际运行结果，最好有详细的日志，异常栈。尽量贴文本。

#### [2893] 【分享】如何通过arthas来定位 StackOverflowError？

- **链接**: https://github.com/alibaba/arthas/issues/2893
- **状态**: open | **作者**: btpka3 | **创建**: 2024-09-05
- **涉及命令**: `watch, stack, thread`

> **摘要**：如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调用前）执行 - 通过当前调用堆栈的深度大于某个阈值，在实际发生StackOverflowError前输出完整堆栈。 示例arthas命令 下面的case是判断调用堆栈深度500。 定位到异常点之后，就可以review相关代码，再配合该行进行...

#### [2739] 使用Arthas 获取 Spring 应用运行时配置值

- **链接**: https://github.com/alibaba/arthas/issues/2739
- **状态**: open | **作者**: hengyunabc | **创建**: 2023-11-27
- **涉及命令**: `vmtool, watch`

> **摘要**：众所周之，Spring 应用的配置注入方式非常多。除了我们熟悉的方式，比如 * System Properties/System Env * application.properties/application.yaml * spring profiles * spring cloud config * https://docs.spring.io/spring-boot/docs/2.1.13.RELEASE/reference/html/boot-features-external-config.html 对于开发人员来说，在运行时怎样确定某个配置是否生效？它的具体值是什么？ 比如获取server.port的具体值： 1....

#### [2526] 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源

- **链接**: https://github.com/alibaba/arthas/issues/2526
- **状态**: open | **作者**: WangJi92 | **创建**: 2023-05-17
- **涉及命令**: `thread, jad`

> **摘要**：背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反序列化失败.. 自己写一个mock 服务,eg 返回对象 返回一个string 断点跟踪 JacksonResponseBodyConverter.convert 确实是 抛出了一个异常 com.fasterxml.jackson.core...

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1920] Arthas vmtool源码分析

- **链接**: https://github.com/alibaba/arthas/issues/1920
- **状态**: closed | **作者**: loongs-zhang | **创建**: 2021-09-22
- **涉及命令**: `vmtool, options`

> **摘要**：Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write application with JNI ? step1.定义native方法 step2.生成头文件 我们使用命令生成c语言使用的头文件。 下面是生成头文件Main.h的具体内容： step3.编写native的实现MainImpl.c st...

#### [1892] 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）

- **链接**: https://github.com/alibaba/arthas/issues/1892
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-08-19
- **涉及命令**: `trace`

> **摘要**：Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 [图片] 从链路上看，线上获取一整天的数据时大概 300 多 ms，而查询数据库只有 11ms，说明大部分时间都是程序组装数据时消耗的，于是动起了优化代码的念头。 ...

#### [1823] 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率

- **链接**: https://github.com/alibaba/arthas/issues/1823
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-06-14

> **摘要**：（用户案例） 前提 本方法最适用于 Spring Boot 项目。 谁拖垮了效率？ 本地开发时有两个操作最耗时： 1. 无法热加载：每次代码变更都要重启项目，重启时间长。 2. 代码调用困难：代码深层的方法，需要有类似 HTTP 的触发入口，再经过各种判断条件一层一层调用过来，非常麻烦。 所以我在寻找一种可以不停机的开发方法，所有变更都能随时生效，代码随写随测。 探索 代码热变更方面，我使用了久负盛名的 IDEA 插件 JRebel。该插件可以做到热加载绝大部分的新增/修改代码，安装使用方式可以在网上搜索。 但有了 JRebel 之后，我发现仍然很难调用看到的方法，如果通过 HTTP 接口调用过来很麻烦，过程很长，并且前后的一...

#### [1802] 使用OGNL表达式获取spring bean 时，bean 的字段值显示是null，但调用字段的get方法显示有值

- **链接**: https://github.com/alibaba/arthas/issues/1802
- **状态**: closed | **作者**: baobinghai | **创建**: 2021-05-26
- **涉及命令**: `ognl`

> **摘要**：主要是由于getBean 获取的是一个代理类，使用的是cglib 的继承方式，字段也是父类的字段，所以是null。有值的字段应该是target对象。因此需要获取target。

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1709] arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题

- **链接**: https://github.com/alibaba/arthas/issues/1709
- **状态**: closed | **作者**: WangJi92 | **创建**: 2021-02-25
- **涉及命令**: `thread, sc`

> **摘要**：一、背景 大早上 线上k8s 机子 某个机子 cpu 飙高，导致k8s 健康检查失败，线上环境会自动执行jstack，上传到oss 通知到 钉钉告警群，直接分析锁、cpu 高的线程。 二、过程分析 2.1 排查cpu 占用最高的线程 使用jstack 分析: 发现占用CPU最高的线程栈是： org.apache.commons.beanutils.MethodUtils#getMatchingAccessibleMethod 。 当然也可以使用arthas 的 thread -n 10 命令 ，由于自动监控抓取的，省去了这一步了。 一般的常规操作 jstack+top ，参考： * https://blog.csdn.net/...

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1566] 利用Arthas解决启动StandbyNameNode加载EditLog慢的问题

- **链接**: https://github.com/alibaba/arthas/issues/1566
- **状态**: closed | **作者**: yhf20071 | **创建**: 2020-11-04
- **涉及命令**: `trace, profiler, options, stack`

> **摘要**：公司新搭HDFS集群，namenode做ha，但是在启动StandbyNamenode节点的时候出现奇怪的现象：空集群加载Editlog很慢，每次重启几乎耗时都在二三十分钟 * 为了方便大家理解，大致说下StandbyNamenode（以下简称SNN）启动过程： 1. SNN启动时，如果本地没有FSImage会去ANN（ActiveNamenode）拉取FSImage 2. 如果本地有FSImage，则会根据transactionId去JournalNode拉取gap的editlog，在本地做合并 * 问题就出在第2步，在从JournalNode拉取EditLog过程中出现固定15s延迟。一般来说，空集群几乎没有操作，...

#### [1525] watch配合stack查看调用链

- **链接**: https://github.com/alibaba/arthas/issues/1525
- **状态**: closed | **作者**: saytime | **创建**: 2020-09-24
- **涉及命令**: `watch`

> **摘要**：使用watch命令观察到某异常方法后，如果想知道调用链，如何进一步使用stack查看调用链 watch demo.MathGame primeFactors "{params[0],throwExp}" -e -x 2

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1310] Arthas ByteKit 深度解读(1)：基本原理介绍

- **链接**: https://github.com/alibaba/arthas/issues/1310
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack`

> **摘要**：Arthas ByteKit 深度解读(1)：基本原理介绍 前言 本文由整体到局部的思路展开分析Arthas ByteKit 字节码处理框架，结合类图和数据流图，介绍ByteKit字节码处理流程及核心对象。 相关文章： Arthas ByteKit 深度解读(2)：本地变量及参数绑定 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完成字节码增强。 * ByteKit 基本用法 * ByteKit 字节码处理流程 * 如何解析Interceptor Class * Byt...

#### [1244] 获取分布式跟踪的 traceId，比如eagleeye的

- **链接**: https://github.com/alibaba/arthas/issues/1244
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-06-05
- **涉及命令**: `watch, trace`

> **摘要**：可以直接调用static函数来获取traceId，比如： trace 命令会自动打印 eagleeye的traceId，比如：

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [772] 如何在内部类对象中访问外部类对象的成员变量

- **链接**: https://github.com/alibaba/arthas/issues/772
- **状态**: closed | **作者**: ralf0131 | **创建**: 2019-07-10
- **涉及命令**: `watch`

> **摘要**：我想在内部类的run方法里面，访问allConnections这个变量的大小，应该如何写ognl表达式？ 使用target.this$0可以访问到外部类对象

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [729] Arthas实践：是哪个Controller处理了请求？

- **链接**: https://github.com/alibaba/arthas/issues/729
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-06-05
- **涉及命令**: `trace, watch`

> **摘要**：Arthas是阿里巴巴开源的Java诊断利器，深受开发者喜爱。 * https://github.com/alibaba/arthas * Arthas在线教程 之前分享了Arthas怎样排查 404/401 的问题: http://hengyunabc.github.io/arthas-spring-boot-404-401/ 我们可以快速定位一个请求是被哪些Filter拦截的，或者请求最终是由哪些Servlet处理的。 但有时，我们想知道一个请求是被哪个Spring MVC Controller处理的。如果翻代码的话，会比较难找，并且不一定准确。 通过Arthas可以精确定位是哪个Controller处理请求。 还是以这个...

#### [569] 引发线程cpu占用率持续飙升的根因分析

- **链接**: https://github.com/alibaba/arthas/issues/569
- **状态**: closed | **作者**: excel-bat | **创建**: 2019-03-14
- **涉及命令**: `monitor, thread, ognl`

> **摘要**：在最近系统性能调优的过程中，用到了很多工具，由于笔者开发的主要是java应用，从linux 工具到jdk工具，以及全链路追踪工具，都解决了相当多的问题，而完全面向java应用的的工具，笔者墙裂推荐 阿里的arthas,这款工具简单，简单到分析cpu、内存问题分分钟就能找到些蛛丝马迹。 问题抽象 --- 项目最近做了一次大升级，压测后发现项目跑了24小时后，开始出现某个线程cpu占用100%，如下图所示： 重启后，仔细观察该线程，发现线程cpu使用率在逐渐递增，我们通过jvisualvm，快速的找到了问题的堆栈，发现是某个redis操作，这个操作里面调用了lua脚本，并使用了evalsha（）的方式执行。 抽丝剥茧 --- 从现...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [549] Mbean support

- **链接**: https://github.com/alibaba/arthas/issues/549
- **状态**: closed | **作者**: dili91 | **创建**: 2019-02-26
- **涉及命令**: `ognl`

> **摘要**：Hi, first of all thank you for this amazing tool. it was a huge help for me in the last weeks, much more than existing and commercial tools. Now my question: Is there a way I can enquiry MBean objects on a running java process ? In a similar way like on VisualVm + MBean plugin installed... If not already feasible wi...

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [508] Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全

- **链接**: https://github.com/alibaba/arthas/issues/508
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-13
- **涉及命令**: `mc, redefine, jad, watch, trace, tt, monitor, stack, sc, sm`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 从Arthas上个版本发布，已经过去两个多月了，Arthas 3.1.0版本不仅带来大家投票出来的新LOGO，还带来强大的新功能和更好的易用性，下面一一介绍。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas 在新版本Arthas里，增加了在线教程，用户可以在线运行Demo，一步步学习Arthas的各种用法，推荐新手尝试： * Arthas基础教程 * Arthas进阶教程 3.1.0版本里新增命令mc，不是方块游戏mc，而是Memory Com...

#### [482] Alibaba Arthas实践--获取到Spring Context，然后为所欲为

- **链接**: https://github.com/alibaba/arthas/issues/482
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-28
- **涉及命令**: `trace, watch, monitor, tt, ognl`

> **摘要**：Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。 * https://github.com/alibaba/arthas Arthas提供了非常丰富的关于调用拦截的命令，比如 trace/watch/monitor/tt 。但是很多时候我们在排查问题时，需要更多的线索，并不只是函数的参数和返回值。 比如在一个spring应用里，想获取到spring context里的其它bean。如果能随意获取到spring bean，那就可以“为所欲为”了。 下面介绍如何利用Arthas获取到spring context。 Demo： https://github.com/hengyunabc/spring-boot-...

#### [442] 记录如何使用arthas进行远程访问

- **链接**: https://github.com/alibaba/arthas/issues/442
- **状态**: closed | **作者**: haifzhu | **创建**: 2019-01-12

> **摘要**：arthas需要在本地进行attach, 通常情况下，开发没有权限登录服务器，如何让开发使用arthas进行远程诊断呢？ 公司内部一般都有一些web管理平台，供开发者去管理自己的应用，如何把arthas集成到自己的web管理平台？ 在公司内部的web管理平台，基于某个主机上的某个应用有个叫开启arthas调试的按钮，点击该按钮会触发如下操作： 1. 登录到对应服务器上，基于应用名称查找对应的pid 2. 检查默认的http端口是不是有pid在监听 3. 如果该端口没有被监听，直接attach该pid之后返回 attach命令: sudo su - -c "java /opt/arthas/lib/3.0.5/arthas/ar...

#### [434] watch/monitor/trace 等判断重载函数/同名函数

- **链接**: https://github.com/alibaba/arthas/issues/434
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `watch, monitor, trace, thread`

> **摘要**：Test类有两个 hello函数，它们的参数不一样，如果直接watch Test hello params，则会匹配到两个hello函数。 那么怎么准确watch第二个hello函数呢？ 下面给出两种方式，ognl表达式是很灵活的，大家可以多尝试下。 第一种方式，判断params的length： 第二种方式，判断params的类型（注意，这里因为int会被包装为Object，所以params[0]的类型是java.lang.Integer）：

#### [429] Arthas实践--快速排查Spring Boot应用404/401问题

- **链接**: https://github.com/alibaba/arthas/issues/429
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `trace`

> **摘要**：在Java Web/Spring Boot开发时，很常见的问题是： * 网页访问404了，为什么访问不到？ * 登陆失败了，请求返回401，到底是哪个Filter拦截了我的请求？ 碰到这种问题时，通常很头痛，特别是在线上环境时。 本文介绍使用Alibaba开源的Java诊断利器Arthas，来快速定位这类Web请求404/401问题。 * https://github.com/alibaba/arthas 在进入正题之前，先温习下知识。一个普通的Java Web请求处理流程大概是这样子的： 可以看出请求经过Spring MVC的DispatcherServlet处理，最终由ViewResolver分派给FreeMarkerVi...

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [324] Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验

- **链接**: https://github.com/alibaba/arthas/issues/324
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-11-29
- **涉及命令**: `ognl, watch, jad`

> **摘要**：Arthas从9月份开源以来，受到广大Java开发者的支持，Github Star数三个月超过6000，非常感谢用户支持。同时用户给Arthas提出了很多建议，其中反映最多的是： 1. Windows平台用户体验不好 1. Attach的进程和最终连接的进程不一致 1. 某些环境下没有安装Telnet，不能连接到Arthas Server 1. 本地启动，不需要下载远程（很多公司安全考虑） 1. 下载速度慢（默认从maven central repository下载） 在Arthas 3.0.5版本里，我们在用户体验方面做了很多改进，下面逐一介绍。 * 文档：https://alibaba.github.io/arthas/...

#### [237] 使用Arthas排查线上应用日志打满问题

- **链接**: https://github.com/alibaba/arthas/issues/237
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-16
- **涉及命令**: `thread, sc, getstatic`

> **摘要**：在应用的 service_stdout.log里一直输出下面的日志，直接把磁盘打满了： service_stdout.log是进程标准输出的重定向，可以初步判定是tair插件把日志输出到了stdout里。 尽管有了初步的判断，但是具体logger为什么会打到stdout里，还需要进一步排查，常见的方法可能是本地debug。 下面介绍利用arthas直接在线上定位问题的过程，主要使用sc和getstatic命令。 * https://alibaba.github.io/arthas/sc.html * https://alibaba.github.io/arthas/getstatic.html 日志是io.netty.chan...

#### [222] Debug Arthas In IDEA

- **链接**: https://github.com/alibaba/arthas/issues/222
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-11

> **摘要**：1. It is better to run as-package.sh before start debugging, it will install the newest version. 2. If you want to debug Arthas core like Commands, please check the second part. The first part, debug Arthas how to attach to target JVM. Debug com.taobao.arthas.core.Arthas Start com.taobao.arthas.core.Arthas Actually...

#### [160] 利用Arthas排查Spring Boot应用NoSuchMethodError

- **链接**: https://github.com/alibaba/arthas/issues/160
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-25
- **涉及命令**: `sc, jad`

> **摘要**：有时spring boot应用会遇到java.lang.NoSuchMethodError的问题，下面以具体的demo来说明怎样利用arthas来排查。 Demo: https://github.com/hengyunabc/spring-boot-inside/tree/master/demo-NoSuchMethodError 在应用的main函数里catch住异常，保证进程不退出 很多时候当应用抛出异常后，进程退出了，就比较难排查问题。可以先改下main函数，把异常catch住： 显然，异常的意思是AnnotationAwareOrderComparator缺少sort(Ljava/util/List;)V这个函数。 参...

#### [71] Arthas的一些特殊用法文档说明

- **链接**: https://github.com/alibaba/arthas/issues/71
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-19
- **涉及命令**: `ognl`

> **摘要**：ognl表达式官网：https://commons.apache.org/dormant/commons-ognl/language-guide.html

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

### 集成实践（24）

#### [2739] 使用Arthas 获取 Spring 应用运行时配置值

- **链接**: https://github.com/alibaba/arthas/issues/2739
- **状态**: open | **作者**: hengyunabc | **创建**: 2023-11-27
- **涉及命令**: `vmtool, watch`

> **摘要**：众所周之，Spring 应用的配置注入方式非常多。除了我们熟悉的方式，比如 * System Properties/System Env * application.properties/application.yaml * spring profiles * spring cloud config * https://docs.spring.io/spring-boot/docs/2.1.13.RELEASE/reference/html/boot-features-external-config.html 对于开发人员来说，在运行时怎样确定某个配置是否生效？它的具体值是什么？ 比如获取server.port的具体值： 1....

#### [1920] Arthas vmtool源码分析

- **链接**: https://github.com/alibaba/arthas/issues/1920
- **状态**: closed | **作者**: loongs-zhang | **创建**: 2021-09-22
- **涉及命令**: `vmtool, options`

> **摘要**：Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write application with JNI ? step1.定义native方法 step2.生成头文件 我们使用命令生成c语言使用的头文件。 下面是生成头文件Main.h的具体内容： step3.编写native的实现MainImpl.c st...

#### [1823] 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率

- **链接**: https://github.com/alibaba/arthas/issues/1823
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-06-14

> **摘要**：（用户案例） 前提 本方法最适用于 Spring Boot 项目。 谁拖垮了效率？ 本地开发时有两个操作最耗时： 1. 无法热加载：每次代码变更都要重启项目，重启时间长。 2. 代码调用困难：代码深层的方法，需要有类似 HTTP 的触发入口，再经过各种判断条件一层一层调用过来，非常麻烦。 所以我在寻找一种可以不停机的开发方法，所有变更都能随时生效，代码随写随测。 探索 代码热变更方面，我使用了久负盛名的 IDEA 插件 JRebel。该插件可以做到热加载绝大部分的新增/修改代码，安装使用方式可以在网上搜索。 但有了 JRebel 之后，我发现仍然很难调用看到的方法，如果通过 HTTP 接口调用过来很麻烦，过程很长，并且前后的一...

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1538] 工商银行打造在线诊断平台的探索与实践

- **链接**: https://github.com/alibaba/arthas/issues/1538
- **状态**: closed | **作者**: lyghzh | **创建**: 2020-10-12

> **摘要**：工商银行打造在线诊断平台的探索与实践

#### [1504] Arthas实践: 定位修复Redisson连接池问题

- **链接**: https://github.com/alibaba/arthas/issues/1504
- **状态**: closed | **作者**: mikawudi | **创建**: 2020-09-16

> **摘要**：https://mp.weixin.qq.com/s/WcEAmUjtzOLRfGTeKPvrvg

#### [1494] Arthas实践：解决由于druid版本造成的慢sql问题

- **链接**: https://github.com/alibaba/arthas/issues/1494
- **状态**: closed | **作者**: hengyunabc | **创建**: 2020-09-11

> **摘要**：https://mp.weixin.qq.com/s/7SQxy0hSm_urJY05QyIwMg

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1416] 使用arthas+jprofiler做复杂链路分析

- **链接**: https://github.com/alibaba/arthas/issues/1416
- **状态**: closed | **作者**: oxsean | **创建**: 2020-08-11
- **涉及命令**: `profiler`

> **摘要**：arthas提供了profiler命令，可以生成热点火焰图。通过采样录制调用链路来做性能分析，极大提升了线上排查性能问题的效率。 但是有一个问题，当async-profiler全量采样导出的svg文件太大时，想要找到关键的调用点，就非常困难。 没有办法做聚合或过滤，这方面本地的profiler工具比如jprofiler、yourkits就方便很多，有没有办法将两者结合起来呢？ 经过分析发现，async-profiler支持jfr (Java Flight Recorder)格式输出，jprofiler也支持打开jfr快照，成了！具体操作步骤如下： 启动arthas之后，执行以下采样命令： %t 表示当前时间，-d 后面是采样秒...

#### [764] Arthas实践--使用trace、sc、watch命令排查spring事务管理超时设置是否生效问题

- **链接**: https://github.com/alibaba/arthas/issues/764
- **状态**: closed | **作者**: aiqing2171 | **创建**: 2019-07-04
- **涉及命令**: `sc, trace, watch`

> **摘要**：同学们对spring事务注解@Transactional(timeout=20) 超时时间是否生效有疑惑。 大概网上有文章提到运行时DataSourceUtils.applyTimeout方法实际并未被执行。于是本地作了如下实验。 首先，最简单的trace com.package.class methd 直接对注解事务的方法进行追踪. 结果看到确实执行sql时花了24秒(为什么不是刚好20s而是24s，每次耗时都不同，没有细究)，后台抛出异常“ORA-01013: 用户请求取消当前的操作”，说明生效的。。。 然后，我们仔细研究了下源码确认了下准确不。 * 先查到timeout最终通过java.sql.Statement...

#### [763] Arthas源码分析--jad反编译原理

- **链接**: https://github.com/alibaba/arthas/issues/763
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-07-03
- **涉及命令**: `jad, watch, trace, stack, tt, mc, redefine`

> **摘要**：Arthas是阿里巴巴开源的Java应用诊断利器，本文介绍Arthas 3.1.1版本里jad命令的实现原理。 * https://github.com/alibaba/arthas * https://alibaba.github.io/arthas/jad.html jad即java decompiler，把JVM已加载类的字节码反编译成Java代码。比如反编译String类： 1. 获取到字节码 2. 反编译为Java代码 最常见的思路是，在classpaths下面查找，比如 ClassLoader.getResource("java/lang/String.class")，但是这样子查找到的字节码不一定对。比如可能有多...

#### [729] Arthas实践：是哪个Controller处理了请求？

- **链接**: https://github.com/alibaba/arthas/issues/729
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-06-05
- **涉及命令**: `trace, watch`

> **摘要**：Arthas是阿里巴巴开源的Java诊断利器，深受开发者喜爱。 * https://github.com/alibaba/arthas * Arthas在线教程 之前分享了Arthas怎样排查 404/401 的问题: http://hengyunabc.github.io/arthas-spring-boot-404-401/ 我们可以快速定位一个请求是被哪些Filter拦截的，或者请求最终是由哪些Servlet处理的。 但有时，我们想知道一个请求是被哪个Spring MVC Controller处理的。如果翻代码的话，会比较难找，并且不一定准确。 通过Arthas可以精确定位是哪个Controller处理请求。 还是以这个...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [559] 2019-03-21 [阿里云峰会-北京]Java诊断利器Arthas排查问题实践 

- **链接**: https://github.com/alibaba/arthas/issues/559
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-03-04

> **摘要**：https://yunqi.youku.com/2019/beijing/meeting?spm=a2c4e.11165380.1317296.1#322-16

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [482] Alibaba Arthas实践--获取到Spring Context，然后为所欲为

- **链接**: https://github.com/alibaba/arthas/issues/482
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-28
- **涉及命令**: `trace, watch, monitor, tt, ognl`

> **摘要**：Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。 * https://github.com/alibaba/arthas Arthas提供了非常丰富的关于调用拦截的命令，比如 trace/watch/monitor/tt 。但是很多时候我们在排查问题时，需要更多的线索，并不只是函数的参数和返回值。 比如在一个spring应用里，想获取到spring context里的其它bean。如果能随意获取到spring bean，那就可以“为所欲为”了。 下面介绍如何利用Arthas获取到spring context。 Demo： https://github.com/hengyunabc/spring-boot-...

#### [477] arthas实践 -- sbt Missing scala-library.jar

- **链接**: https://github.com/alibaba/arthas/issues/477
- **状态**: closed | **作者**: x334085347 | **创建**: 2019-01-25
- **涉及命令**: `jad, watch`

> **摘要**：+ 在使用sbt构建一个spark 的项目的时候 遇到一个很奇怪的问题 Missing scala-library.jar 如下图. 按理来说如果少jar包sbt 会自动去下载的 这个就很奇怪了. [图片] + 于是想到用arthas 看一下.首先在arthas中用jad反编译了下scala.sys.pachage\$ 的代码 . + 这里的error只是抛了个异常 没有其他...

#### [442] 记录如何使用arthas进行远程访问

- **链接**: https://github.com/alibaba/arthas/issues/442
- **状态**: closed | **作者**: haifzhu | **创建**: 2019-01-12

> **摘要**：arthas需要在本地进行attach, 通常情况下，开发没有权限登录服务器，如何让开发使用arthas进行远程诊断呢？ 公司内部一般都有一些web管理平台，供开发者去管理自己的应用，如何把arthas集成到自己的web管理平台？ 在公司内部的web管理平台，基于某个主机上的某个应用有个叫开启arthas调试的按钮，点击该按钮会触发如下操作： 1. 登录到对应服务器上，基于应用名称查找对应的pid 2. 检查默认的http端口是不是有pid在监听 3. 如果该端口没有被监听，直接attach该pid之后返回 attach命令: sudo su - -c "java /opt/arthas/lib/3.0.5/arthas/ar...

#### [429] Arthas实践--快速排查Spring Boot应用404/401问题

- **链接**: https://github.com/alibaba/arthas/issues/429
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `trace`

> **摘要**：在Java Web/Spring Boot开发时，很常见的问题是： * 网页访问404了，为什么访问不到？ * 登陆失败了，请求返回401，到底是哪个Filter拦截了我的请求？ 碰到这种问题时，通常很头痛，特别是在线上环境时。 本文介绍使用Alibaba开源的Java诊断利器Arthas，来快速定位这类Web请求404/401问题。 * https://github.com/alibaba/arthas 在进入正题之前，先温习下知识。一个普通的Java Web请求处理流程大概是这样子的： 可以看出请求经过Spring MVC的DispatcherServlet处理，最终由ViewResolver分派给FreeMarkerVi...

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [324] Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验

- **链接**: https://github.com/alibaba/arthas/issues/324
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-11-29
- **涉及命令**: `ognl, watch, jad`

> **摘要**：Arthas从9月份开源以来，受到广大Java开发者的支持，Github Star数三个月超过6000，非常感谢用户支持。同时用户给Arthas提出了很多建议，其中反映最多的是： 1. Windows平台用户体验不好 1. Attach的进程和最终连接的进程不一致 1. 某些环境下没有安装Telnet，不能连接到Arthas Server 1. 本地启动，不需要下载远程（很多公司安全考虑） 1. 下载速度慢（默认从maven central repository下载） 在Arthas 3.0.5版本里，我们在用户体验方面做了很多改进，下面逐一介绍。 * 文档：https://alibaba.github.io/arthas/...

#### [263] Arthas实践--使用redefine排查应用奇怪的日志来源

- **链接**: https://github.com/alibaba/arthas/issues/263
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-23
- **涉及命令**: `redefine, stack`

> **摘要**：随着应用越来越复杂，依赖越来越多，日志系统越来越混乱，有时会出现一些奇怪的日志，比如： 那么怎样排查这些奇怪的日志从哪里打印出来的呢？因为搞不清楚是什么logger打印出来的，所以想定位就比较头疼。 下面介绍用arthas的redefine命令快速定位奇怪日志来源。 * Arthas: https://github.com/alibaba/arthas * redefine命令：https://alibaba.github.io/arthas/redefine.html 首先在java代码里，字符串拼接基本都是通过StringBuilder来实现的。比如下面的代码： 实际上生成的字节码也是用StringBuilder来拼接的：...

### 工具技巧（32）

#### [2938] Elasticsearch 进程使用watch命令被卡死了大部分线程

- **链接**: https://github.com/alibaba/arthas/issues/2938
- **状态**: open | **作者**: cfangpp | **创建**: 2024-11-07
- **涉及命令**: `monitor, thread`

> **摘要**：实际运行结果，最好有详细的日志，异常栈。尽量贴文本。

#### [2893] 【分享】如何通过arthas来定位 StackOverflowError？

- **链接**: https://github.com/alibaba/arthas/issues/2893
- **状态**: open | **作者**: btpka3 | **创建**: 2024-09-05
- **涉及命令**: `watch, stack, thread`

> **摘要**：如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调用前）执行 - 通过当前调用堆栈的深度大于某个阈值，在实际发生StackOverflowError前输出完整堆栈。 示例arthas命令 下面的case是判断调用堆栈深度500。 定位到异常点之后，就可以review相关代码，再配合该行进行...

#### [2526] 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源

- **链接**: https://github.com/alibaba/arthas/issues/2526
- **状态**: open | **作者**: WangJi92 | **创建**: 2023-05-17
- **涉及命令**: `thread, jad`

> **摘要**：背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反序列化失败.. 自己写一个mock 服务,eg 返回对象 返回一个string 断点跟踪 JacksonResponseBodyConverter.convert 确实是 抛出了一个异常 com.fasterxml.jackson.core...

#### [2521] 关于OkHttpClient 在高并发报java.lang.OutOfMemoryError unalbe to create new native thread，使用arthas的优化解决方案

- **链接**: https://github.com/alibaba/arthas/issues/2521
- **状态**: closed | **作者**: v24342317 | **创建**: 2023-05-14
- **涉及命令**: `thread`

> **摘要**：解决使用OkHttpClient 在高并发下java.lang.OutOfMemoryError: unalbe to create new native thread错误 盛事通APP使用私有百度OCR服务，近期百度升级人脸识别服务从原来的CPU更换成GPU服务器。我们写了一个简单的demo来做压测看看实际新提供的人脸识别服务比使用CPU的人脸识别提升有多少。；网络环境：内网压测没有任何防火墙；服务器环境：使用的阿里云k8s,pod限制为4CPU,8G内存；jmeter配置说明：1秒200并发循环100次，相当于1分40秒每秒200并发；java环境：使用的功能内部架构，代码做了混淆各种封装没有使用文档。 -Xms2...

#### [1823] 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率

- **链接**: https://github.com/alibaba/arthas/issues/1823
- **状态**: closed | **作者**: reliefeai | **创建**: 2021-06-14

> **摘要**：（用户案例） 前提 本方法最适用于 Spring Boot 项目。 谁拖垮了效率？ 本地开发时有两个操作最耗时： 1. 无法热加载：每次代码变更都要重启项目，重启时间长。 2. 代码调用困难：代码深层的方法，需要有类似 HTTP 的触发入口，再经过各种判断条件一层一层调用过来，非常麻烦。 所以我在寻找一种可以不停机的开发方法，所有变更都能随时生效，代码随写随测。 探索 代码热变更方面，我使用了久负盛名的 IDEA 插件 JRebel。该插件可以做到热加载绝大部分的新增/修改代码，安装使用方式可以在网上搜索。 但有了 JRebel 之后，我发现仍然很难调用看到的方法，如果通过 HTTP 接口调用过来很麻烦，过程很长，并且前后的一...

#### [1736] SpringBoot Admin2.0集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1736
- **状态**: closed | **作者**: password36 | **创建**: 2021-03-15
- **涉及命令**: `mc`

> **摘要**：前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine功能组合实现生产环境部分节点代码热更新的能力； 因为公司还未能建立起较为统一的生产微服务配置以及状态管理的能力，各自系统的研发运维较为独立。 同时现在项目使用了Spring Cloud以及Eureka的框架结构，和SBA的基础支撑能力较为匹...

#### [1687] 对于某些工具的后台进程，可以使用 -XX:+DisableAttachMechanism 参数，避免用户选择到错误的进程

- **链接**: https://github.com/alibaba/arthas/issues/1687
- **状态**: closed | **作者**: hengyunabc | **创建**: 2021-02-01
- **涉及命令**: `stack, trace`

> **摘要**：在一台机器上，应用方通常会认为只有自己的进程。但是某些工具的后台进程也是以 java方式启动的，就会导致用户可能手滑选择了工具的后台进程，导致出错。 所以这些工具的后台进程可以考虑加上 -XX:+DisableAttachMechanism 的jvm参数。这样子用户选错了就会报错：

#### [1602] alpine容器镜像中生成火焰图错误的其它解决方案

- **链接**: https://github.com/alibaba/arthas/issues/1602
- **状态**: closed | **作者**: shalousun | **创建**: 2020-12-03
- **涉及命令**: `profiler`

> **摘要**：；在alpine镜像中执行profiler start命令后可能还会发现alpine基础镜像中缺乏libstdc++.so.6库，这时在自己的基础镜像中添加下libstdc++下就好了。 这个问题通常是出现在容器环境中。 arthas实际是利用async-profiler去完成的。在async-profiler官方地址的README中有提到该问题。 async-profiler官方对问题描述和解决方法 perf_event_open() syscall has failed. The error message is printed to the error stream of the target JVM. Typical...

#### [1601] SpringBoot Admin集成Arthas实践

- **链接**: https://github.com/alibaba/arthas/issues/1601
- **状态**: closed | **作者**: jujunchen | **创建**: 2020-12-03

> **摘要**：前言 Arthas 是 Alibaba开源的Java诊断工具，具有实时查看系统的运行状况；查看函数调用参数、返回值和异常；在线热更新代码；秒解决类冲突问题；定位类加载路径；生成热点；通过网页诊断线上应用。如今在各大厂都有广泛应用，也延伸出很多产品。 这里将介绍如何将Arthas集成进SpringBoot监控平台中。 SpringBoot Admin 为了方便SpringBoot Admin 简称为SBA 版本：1.5.x 1.5版本的SBA如果要开发插件比较麻烦，需要下载SBA的源码包，再按照spring-boot-admin-server-ui-hystrix的形式copy一份,由于JS使用的是Angular,本人尝试了很久...

#### [1566] 利用Arthas解决启动StandbyNameNode加载EditLog慢的问题

- **链接**: https://github.com/alibaba/arthas/issues/1566
- **状态**: closed | **作者**: yhf20071 | **创建**: 2020-11-04
- **涉及命令**: `trace, profiler, options, stack`

> **摘要**：公司新搭HDFS集群，namenode做ha，但是在启动StandbyNamenode节点的时候出现奇怪的现象：空集群加载Editlog很慢，每次重启几乎耗时都在二三十分钟 * 为了方便大家理解，大致说下StandbyNamenode（以下简称SNN）启动过程： 1. SNN启动时，如果本地没有FSImage会去ANN（ActiveNamenode）拉取FSImage 2. 如果本地有FSImage，则会根据transactionId去JournalNode拉取gap的editlog，在本地做合并 * 问题就出在第2步，在从JournalNode拉取EditLog过程中出现固定15s延迟。一般来说，空集群几乎没有操作，...

#### [1525] watch配合stack查看调用链

- **链接**: https://github.com/alibaba/arthas/issues/1525
- **状态**: closed | **作者**: saytime | **创建**: 2020-09-24
- **涉及命令**: `watch`

> **摘要**：使用watch命令观察到某异常方法后，如果想知道调用链，如何进一步使用stack查看调用链 watch demo.MathGame primeFactors "{params[0],throwExp}" -e -x 2

#### [1424] arthas 获取spring被代理的目标对象

- **链接**: https://github.com/alibaba/arthas/issues/1424
- **状态**: closed | **作者**: WangJi92 | **创建**: 2020-08-13
- **涉及命令**: `ognl, tt, trace, sc`

> **摘要**：背景 记得一次问题排查，通过ognl 获取到 spring aop 代理过的cglib 代理对象的原始对象获取问题，spring的静态static spring context 进行调用获取被代理的目标对象的问题，记得当事是通过内部的一个工具 代理对象中被代理的目标对象 类似这个方法，通过静态的方法进行调用.挺方便的，但是这个方法比较麻烦，不是所有的工程都有这个方法，如何通过工具化让大家都能使用，这里使用 ognl 表达式进行复原整个过程，方便使用。更多使用参考 Idea Plugin,最近会把这个功能集成工具化，方便使用。 参考文章 Ongl Lambda表达式 Ongl 官方文档 定义了一个Ongl Lambda表达式,...

#### [1416] 使用arthas+jprofiler做复杂链路分析

- **链接**: https://github.com/alibaba/arthas/issues/1416
- **状态**: closed | **作者**: oxsean | **创建**: 2020-08-11
- **涉及命令**: `profiler`

> **摘要**：arthas提供了profiler命令，可以生成热点火焰图。通过采样录制调用链路来做性能分析，极大提升了线上排查性能问题的效率。 但是有一个问题，当async-profiler全量采样导出的svg文件太大时，想要找到关键的调用点，就非常困难。 没有办法做聚合或过滤，这方面本地的profiler工具比如jprofiler、yourkits就方便很多，有没有办法将两者结合起来呢？ 经过分析发现，async-profiler支持jfr (Java Flight Recorder)格式输出，jprofiler也支持打开jfr快照，成了！具体操作步骤如下： 启动arthas之后，执行以下采样命令： %t 表示当前时间，-d 后面是采样秒...

#### [1311] Arthas ByteKit 深度解读(2)：本地变量及参数绑定

- **链接**: https://github.com/alibaba/arthas/issues/1311
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack, getstatic`

> **摘要**：Arthas ByteKit 深度解读(2)：本地变量及参数绑定 前言 本文通过分析ByteKit的本地变量绑定（LocalVarsBinding）处理代码，结合Java Opcode手册、asm代码、javap反汇编字节码等工具，深入讲解每个指令的用法及在本场景的实际作用。结合上下文线索，从字节码的角度去理解ByteKit 本地变量绑定的实现过程。 相关文章： Arthas ByteKit 深度解读(1)：基本原理介绍 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完...

#### [1310] Arthas ByteKit 深度解读(1)：基本原理介绍

- **链接**: https://github.com/alibaba/arthas/issues/1310
- **状态**: closed | **作者**: kylixs | **创建**: 2020-07-16
- **涉及命令**: `stack`

> **摘要**：Arthas ByteKit 深度解读(1)：基本原理介绍 前言 本文由整体到局部的思路展开分析Arthas ByteKit 字节码处理框架，结合类图和数据流图，介绍ByteKit字节码处理流程及核心对象。 相关文章： Arthas ByteKit 深度解读(2)：本地变量及参数绑定 简介 Arthas ByteKit 为新开发的字节码工具库，基于ASM提供更高层的字节码处理能力，面向诊断/APM领域，不是通用的字节码库。ByteKit期望能提供一套简洁的API，让开发人员可以比较轻松的完成字节码增强。 * ByteKit 基本用法 * ByteKit 字节码处理流程 * 如何解析Interceptor Class * Byt...

#### [1202] 利用Arthas精准定位Java应用CPU负载过高问题

- **链接**: https://github.com/alibaba/arthas/issues/1202
- **状态**: closed | **作者**: cafe-babe | **创建**: 2020-05-22
- **涉及命令**: `thread, tt, jad, ognl`

> **摘要**：最近我们线上有个应用服务器有点上头，CPU总能跑到99%，我寻思着它流量也不大啊，为啥能把自己整这么累？于是我登上这台服务器，看看它到底在干啥！ 以前碰到类似问题，可能会考虑使用 加 命令去排查，虽然能大致定位到问题范围，但有效信息还是太少了，多数时候还是要靠猜。 今天向大家推荐一款更高效更精准的工具： ！ Arthas 是Alibaba开源的Java诊断工具，能够帮助我们快速定位线上问题。基本的安装使用可以参考官方文档：https://alibaba.github.io/arthas 这次我们利用它来排查CPU负载高的问题。 CPU负载过高一般是某个或某几个线程有问题，所以我们尝试使用第一个命令： ，这个命令会显示所有线程的...

#### [1003] 一图掌握Arthas—常用命令汇总

- **链接**: https://github.com/alibaba/arthas/issues/1003
- **状态**: closed | **作者**: w454196785 | **创建**: 2020-01-07

> **摘要**：总结了Arthas中的常用命令、参数以及用例，在使用时可以方便查到需要的功能。 下载点我：Arthas.xmind.tar.gz !ArtHas

#### [849] Alibaba Arthas 3.1.2版本:增加logger/heapdump/vmoption命令,支持tunnel server

- **链接**: https://github.com/alibaba/arthas/issues/849
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-09-10
- **涉及命令**: `heapdump, thread`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas Arthas 3.1.2版本持续增加新特性，下面重点介绍： * logger/heapdump/vmoption/stop命令 * 通过tunnel server连接不同网络的arthas，方便统一管控 * 易用性持续提升：提示符修改为arthas@pid形式，支持ctrl + k清屏快捷键 logger/heapdump/vmoption/stop命令；查看logger信息，更新logger...

#### [561] Arthas排查Kubernetes中的应用频繁挂掉重启问题

- **链接**: https://github.com/alibaba/arthas/issues/561
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-06
- **涉及命令**: `thread, stack, trace`

> **摘要**：其实最终定位到的问题还是蛮好解决的，但是因为应用在Kubernetes容器中的特殊性,导致在使用Arthas过程中出现了各种问题，所以单独成文和大家分享下。照例先讲下问题发生的背景，一个很老的web系统部署在tomcat容器里。近期打成了镜像丢到了Kubernetes环境中运行，总是各种挂，在Kubernetes层面定位了很久没找到具体问题，但是初步定位到是因为系统中的报表导出接口导致的问题，最后使用Arthas找到问题并解决。 首先说下，我们的Kubernetes容器中运行的应用都是基于自己构建的基础镜像打包的，如JDK，和tomcat基础镜像，为了减小打包后应用的体积，我们对JDK进行了大量的删减，只保留了最小的jre运行...

#### [557] Arthas协助排查线上skywalking不可用问题

- **链接**: https://github.com/alibaba/arthas/issues/557
- **状态**: closed | **作者**: klboke | **创建**: 2019-03-01
- **涉及命令**: `thread, ognl, watch`

> **摘要**：首先描述下问题的背景，博主有个习惯，每天上下班的时候看下skywalking的trace页面的error情况。但是某天突然发现生产环境skywalking页面没有任何数据了，页面也没有显示任何的异常，有点慌，我们线上虽然没有全面铺开对接skywalking，但是也有十多个应用。看了应用agent端日志后，其实也不用太担心，对应用毫无影响。大概情况就是这样，但是问题还是要解决，下面就开始排查skywalking不可用的问题。 Arthas是阿里巴巴开源的一款在线诊断java应用程序的工具，是greys工具的升级版本，深受开发者喜爱。当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决： 1. 这个类从哪个 jar 包加载...

#### [537] Arthas实践--jad/mc/redefine线上热更新一条龙

- **链接**: https://github.com/alibaba/arthas/issues/537
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-20
- **涉及命令**: `jad, mc, redefine, sc`

> **摘要**：尽管在生产环境热更新代码，并不是很好的行为，很可能导致：热更不规范，同事两行泪。 但很多时候我们的确希望能热更新代码，比如：；线上排查问题，找到修复思路了，但应用重启之后，环境现场就变了，难以复现。怎么验证修复方案？；本地开发时，发现某个开源组件有bug，希望修改验证。如果是自己编译开源组件再发布，流程非常的长，还不一定能编译成功。有没有办法快速测试？ Arthas是阿里巴巴开源的Java应用诊断利器，深受开发者喜爱。 下面介绍利用Arthas 3.1.0版本的 jad/mc/redefine 一条龙来热更新代码。 * Arthas: https://github.com/alibaba/arthas * jad命令：...

#### [508] Arthas 3.1.0版本发布：在线教程、内存编译器和强大的自动补全

- **链接**: https://github.com/alibaba/arthas/issues/508
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-02-13
- **涉及命令**: `mc, redefine, jad, watch, trace, tt, monitor, stack, sc, sm`

> **摘要**：Arthas是Alibaba开源的Java诊断工具，深受开发者喜爱。 从Arthas上个版本发布，已经过去两个多月了，Arthas 3.1.0版本不仅带来大家投票出来的新LOGO，还带来强大的新功能和更好的易用性，下面一一介绍。 * Github： https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas 在新版本Arthas里，增加了在线教程，用户可以在线运行Demo，一步步学习Arthas的各种用法，推荐新手尝试： * Arthas基础教程 * Arthas进阶教程 3.1.0版本里新增命令mc，不是方块游戏mc，而是Memory Com...

#### [482] Alibaba Arthas实践--获取到Spring Context，然后为所欲为

- **链接**: https://github.com/alibaba/arthas/issues/482
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-28
- **涉及命令**: `trace, watch, monitor, tt, ognl`

> **摘要**：Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。 * https://github.com/alibaba/arthas Arthas提供了非常丰富的关于调用拦截的命令，比如 trace/watch/monitor/tt 。但是很多时候我们在排查问题时，需要更多的线索，并不只是函数的参数和返回值。 比如在一个spring应用里，想获取到spring context里的其它bean。如果能随意获取到spring bean，那就可以“为所欲为”了。 下面介绍如何利用Arthas获取到spring context。 Demo： https://github.com/hengyunabc/spring-boot-...

#### [477] arthas实践 -- sbt Missing scala-library.jar

- **链接**: https://github.com/alibaba/arthas/issues/477
- **状态**: closed | **作者**: x334085347 | **创建**: 2019-01-25
- **涉及命令**: `jad, watch`

> **摘要**：+ 在使用sbt构建一个spark 的项目的时候 遇到一个很奇怪的问题 Missing scala-library.jar 如下图. 按理来说如果少jar包sbt 会自动去下载的 这个就很奇怪了. [图片] + 于是想到用arthas 看一下.首先在arthas中用jad反编译了下scala.sys.pachage\$ 的代码 . + 这里的error只是抛了个异常 没有其他...

#### [434] watch/monitor/trace 等判断重载函数/同名函数

- **链接**: https://github.com/alibaba/arthas/issues/434
- **状态**: closed | **作者**: hengyunabc | **创建**: 2019-01-07
- **涉及命令**: `watch, monitor, trace, thread`

> **摘要**：Test类有两个 hello函数，它们的参数不一样，如果直接watch Test hello params，则会匹配到两个hello函数。 那么怎么准确watch第二个hello函数呢？ 下面给出两种方式，ognl表达式是很灵活的，大家可以多尝试下。 第一种方式，判断params的length： 第二种方式，判断params的类型（注意，这里因为int会被包装为Object，所以params[0]的类型是java.lang.Integer）：

#### [327] 分享及其资料：当DUBBO遇上Arthas - 排查问题的实践

- **链接**: https://github.com/alibaba/arthas/issues/327
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-12-01
- **涉及命令**: `watch, redefine, ognl, sc, tt, trace, thread, jad`

> **摘要**：Apache Dubbo是Alibaba开源的高性能RPC框架，在国内有非常多的用户。 * Github: https://github.com/apache/incubator-dubbo * 文档：http://dubbo.incubator.apache.org/zh-cn/ Arthas是Alibaba开源的应用诊断利器，9月份开源以来，Github Star数三个月超过6000。 * Github: https://github.com/alibaba/arthas * 文档：https://alibaba.github.io/arthas/ * Arthas开源交流QQ群: 916328269 * Arthas开源...

#### [324] Alibaba应用诊断利器Arthas 3.0.5版本发布：提升全平台用户体验

- **链接**: https://github.com/alibaba/arthas/issues/324
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-11-29
- **涉及命令**: `ognl, watch, jad`

> **摘要**：Arthas从9月份开源以来，受到广大Java开发者的支持，Github Star数三个月超过6000，非常感谢用户支持。同时用户给Arthas提出了很多建议，其中反映最多的是： 1. Windows平台用户体验不好 1. Attach的进程和最终连接的进程不一致 1. 某些环境下没有安装Telnet，不能连接到Arthas Server 1. 本地启动，不需要下载远程（很多公司安全考虑） 1. 下载速度慢（默认从maven central repository下载） 在Arthas 3.0.5版本里，我们在用户体验方面做了很多改进，下面逐一介绍。 * 文档：https://alibaba.github.io/arthas/...

#### [237] 使用Arthas排查线上应用日志打满问题

- **链接**: https://github.com/alibaba/arthas/issues/237
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-10-16
- **涉及命令**: `thread, sc, getstatic`

> **摘要**：在应用的 service_stdout.log里一直输出下面的日志，直接把磁盘打满了： service_stdout.log是进程标准输出的重定向，可以初步判定是tair插件把日志输出到了stdout里。 尽管有了初步的判断，但是具体logger为什么会打到stdout里，还需要进一步排查，常见的方法可能是本地debug。 下面介绍利用arthas直接在线上定位问题的过程，主要使用sc和getstatic命令。 * https://alibaba.github.io/arthas/sc.html * https://alibaba.github.io/arthas/getstatic.html 日志是io.netty.chan...

#### [198] No class or method is affected when trying command like trace or watch

- **链接**: https://github.com/alibaba/arthas/issues/198
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-10-09
- **涉及命令**: `trace, watch, options, sc, sm`

> **摘要**：0. 先确认Arthas已经挂载到正确的Java进程里面了，检查Arthas连上时输出的PID，确认是想要挂载的目标进程ID(和 ps -ef 的结果比对) 1. 先用sc或者sm搜索对应的类和方法，确认已经被JVM加载 2. 在~/logs/arthas/arthas.log中查找有没有Method code too large的异常 3. 存在该异常时，尝试用reset class_name命令对类进行恢复，再进行trace，watch等操作 4. 系统级别的类默认不能进行增强，需要增强是请参考这里的unsafe开关，增强系统类时请谨慎操作 0. Please confirm that Arthas is attached...

#### [160] 利用Arthas排查Spring Boot应用NoSuchMethodError

- **链接**: https://github.com/alibaba/arthas/issues/160
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-25
- **涉及命令**: `sc, jad`

> **摘要**：有时spring boot应用会遇到java.lang.NoSuchMethodError的问题，下面以具体的demo来说明怎样利用arthas来排查。 Demo: https://github.com/hengyunabc/spring-boot-inside/tree/master/demo-NoSuchMethodError 在应用的main函数里catch住异常，保证进程不退出 很多时候当应用抛出异常后，进程退出了，就比较难排查问题。可以先改下main函数，把异常catch住： 显然，异常的意思是AnnotationAwareOrderComparator缺少sort(Ljava/util/List;)V这个函数。 参...

#### [20] 【Arthas问题排查集】谁调用了System.exit/System.gc?

- **链接**: https://github.com/alibaba/arthas/issues/20
- **状态**: closed | **作者**: ralf0131 | **创建**: 2018-09-14
- **涉及命令**: `options, stack, thread`

> **摘要**：我们有时候可能会遇到这样的问题，进程莫名其妙的退出了，或者是发生了GC，通过日志或者是其他办法发现是有人调用了System.gc/System.exit，但是确不知道是谁干的。 如何找出这个罪魁祸首呢？一般来说，可以通过一段Btrace脚本来解决 类似这样的脚本（不保证能正常执行啊。。）经常容易写错，导致各种问题，有没有更好的办法呢？ 今天我们来分享下，如何通过Arthas排查这类问题。 这里我们假设你已经了解下载，安装，启动Arthas的步骤。 第一步，由于java.lang.System是JDK自带的类，Arthas默认关闭了对JDK类的自带类的增强，需要通过options命令打开。 第二步，使用stack命令，观察谁调用...

#### [11] 【Arthas问题排查集】活用ognl表达式

- **链接**: https://github.com/alibaba/arthas/issues/11
- **状态**: closed | **作者**: hengyunabc | **创建**: 2018-09-12
- **涉及命令**: `ognl, thread, watch`

> **摘要**：Arthas 3.0中使用ognl表达式替换了groovy来实现表达式的求值功能，解决了groovy潜在会出现内存泄露的问题。灵活运用ognl表达式，能够极大提升问题排查的效率。 ognl官方文档：https://commons.apache.org/proper/commons-ognl/language-guide.html params是参数列表，是一个数组，可以直接通过下标方式访问 第一个参数是一个List，想要看List中第一个Pojo对象，可以通过下标方式，也可以通过List的get方法访问。 拿到这个Pojo可以，直接访问Pojo的属性，如age 还可以通过下标的方式访问params[0][0]["age"]，这...

## 高频命令与适用场景

| 命令 | 在用户案例中的典型用途 |
|------|------------------------|
| `trace` | 方法调用链路与耗时分布，性能优化（如接口优化十倍） |
| `watch` | 观察方法入参/返回值/异常，定位 StackOverflow、watch 卡死等 |
| `thread` | 线程栈分析，CPU 飙高、死循环、线程泄漏 |
| `ognl` | 动态执行表达式，读 Spring Bean 字段/配置 |
| `vmtool` | 在 JVM 内执行代码、获取对象实例 |
| `monitor` | 方法调用统计（次数/成功率/RT） |
| `stack` | 输出当前线程栈，配合 CPU 问题 |
| `redefine` | 热更新 class，不重启修复/验证 |
| `mc` | 内存编译 Java 代码 |
| `jad` | 反编译线上 class 对照排查 |
| `profiler` | 火焰图/profile CPU 热点 |
| `heapdump` | 堆转储配合 OOM 分析 |
| `tt` | 时间隧道，记录方法调用现场 |
| `sc` | 搜索已加载的 class |
| `sm` | 查看类的方法信息 |

## 推荐阅读（代表性案例）

- **[#1892 通过 Arthas Trace 命令将接口性能优化十倍（User Case 投稿）](https://github.com/alibaba/arthas/issues/1892)** — Helios 系统要处理的数据量比较大，尤其是查询所有服务一天的评分数据时要返回每日 1440 分钟的所有应用的评分，总计有几十万个数据点，接口有时延迟会达到数秒。本文记录如何利用 Arthas ，将接口从几百几千 ms，优化到几十 ms。 ![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7b81932d3e514f8fa3ff21...
- **[#1823 使用Arthas显式执行代码，避免重启应用，10倍提升本地研发效率](https://github.com/alibaba/arthas/issues/1823)** — （用户案例） 前提 本方法最适用于 Spring Boot 项目。 谁拖垮了效率？ 本地开发时有两个操作最耗时： 1. 无法热加载：每次代码变更都要重启项目，重启时间长。 2. 代码调用困难：代码深层的方法，需要有类似 HTTP 的触发入口，再经过各种判断条件一层一层调用过来，非常麻烦。 所以我在寻找一种可以不停机的开发方法，所有变更都能随时生效，代码随写随测。 探索 代码热变更方面，我使用...
- **[#1709 arthas 定位 多线程WeakHashMap引起的死循环cpu跑满问题](https://github.com/alibaba/arthas/issues/1709)** — 一、背景 大早上 线上k8s 机子 某个机子 cpu 飙高，导致k8s 健康检查失败，线上环境会自动执行jstack，上传到oss 通知到 钉钉告警群，直接分析锁、cpu 高的线程。 二、过程分析 2.1 排查cpu 占用最高的线程 使用jstack 分析: 发现占用CPU最高的线程栈是： org.apache.commons.beanutils.MethodUtils#getMatchin...
- **[#2739 使用Arthas 获取 Spring 应用运行时配置值](https://github.com/alibaba/arthas/issues/2739)** — 众所周之，Spring 应用的配置注入方式非常多。除了我们熟悉的方式，比如 * System Properties/System Env * application.properties/application.yaml * spring profiles * spring cloud config * https://docs.spring.io/spring-boot/docs/2.1....
- **[#2526 巧用arthas 分析 java.lang.reflect.UndeclaredThrowableException 异常来源](https://github.com/alibaba/arthas/issues/2526)** — 背景 使用了https://square.github.io/retrofit/ 包装接口，响应值不正常的时候抛出一个异常堆栈 异常堆栈从哪里来的？不应该是 com.fasterxml.jackson.core.JsonParseException 异常？ 怎么会被包装成了 java.lang.reflect.UndeclaredThrowableException 模拟不正常的响应值导致反...
- **[#2893 【分享】如何通过arthas来定位 StackOverflowError？](https://github.com/alibaba/arthas/issues/2893)** — 如何定位 StackOverflowError 发生 StackOverflowError 时，堆栈里往往看不到是哪里触发了该异常，比如上面的case中，从 DispatcherServlet.doDispatch 到 Caused by: java.lang.StackOverflowError 之间发生了什么？看不出来。 思路 - 通过arthas watch 命令 使用 -b（在方法调...
- **[#1736 SpringBoot Admin2.0集成Arthas实践](https://github.com/alibaba/arthas/issues/1736)** — 前言 - [参考原文-SpringBoot Admin集成Arthas实践 #1601] (https://github.com/alibaba/arthas/issues/1601#issue-755947978) 项目最初使用Arthas主要有两个目的： 1. 通过arthas解决实现测试环境、性能测试环境以及生产环境性能问题分析工具的问题； 2. 通过使用jad、mc、redefine...
- **[#1920 Arthas vmtool源码分析](https://github.com/alibaba/arthas/issues/1920)** — Arthas vmtool源码分析 Hello JNI Why use JNI ? - 提高程序性能； - 实现某些纯Java代码不可能实现的功能； - 使用其他语言的类库； - 与硬件、操作系统进行交互。 What is JNI ? JNI是Java Native Interface的缩写，通过使用native关键字书写程序，允许Java与其他语言进行交互。 How to write ap...

## 使用说明

1. 「全量案例索引」可点击 Issue 编号直达 GitHub 原文（含完整命令与截图）。
2. 「分类详情」摘要为精简版，完整内容请查看原文链接。
3. 同一 Issue 可能归入多个场景分类。
4. 定期更新：[user-case 标签页](https://github.com/alibaba/arthas/issues?q=label%3Auser-case)。
5. 官方征集帖：[Wanted: who's using Arthas #111](https://github.com/alibaba/arthas/issues/111)。
