# Guidebot

Guidebot 是一个以自适应 agent 为总枢纽的桌面宠物机器人项目。目标能力包括环境温度与房间
状态感知、空调调节、自然对话、触摸互动，以及未来的视觉和移动能力。

当前版本是一个可运行的 Phase 0 骨架：

- 事件总线与统一传感器/动作模型
- 可替换的硬件适配器和内存模拟器
- 可替换的 Agent 接口与基础温控、触摸、空气质量行为
- 位于 agent 和物理设备之间的确定性安全门
- 轨迹记录，以及受限修改、留出验证、人工发布的技能进化模型

## 快速开始

要求 Python 3.10+。

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
guidebot demo
pytest
```

不安装项目也可直接演示：

```bash
PYTHONPATH=src python -m guidebot.cli demo
```

详细设计见 [docs/architecture.md](docs/architecture.md)。

## 近期路线

1. 接入 ESP32-S3（温湿度、触摸）和 MQTT 消息协议。
2. 接入 Home Assistant，以实体白名单控制空调。
3. 加入流式 ASR/TTS 与可插拔 LLM planner。
4. 建立仿真场景、用户反馈评分和技能候选审批界面。
5. 加入摄像头房间检测；若采用移动底盘，再接 ROS 2/Nav2。

## 调研基线

- [Microsoft SkillOpt](https://github.com/microsoft/SkillOpt)：轨迹驱动、受限编辑、验证门控的技能优化。
- [Reachy Mini](https://www.reachymini.dev/)：桌面机器人硬件抽象、SDK 和应用分层参考。
- [Home Assistant](https://developers.home-assistant.io/)：家庭设备集成边界。

本项目不直接复制上述项目代码；第一阶段只借鉴其公开架构思想。
