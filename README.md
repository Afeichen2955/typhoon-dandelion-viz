# 🌪️ 香港台风数据蒲公英可视化项目

## 📖 项目简介

这个项目以蒲公英的形态来可视化2014-2024年香港天文台的热带气旋数据，创造性地将自然形态与数据可视化相结合。项目灵感来源于蒲公英种子随风传播的特性，象征着台风在海洋上的形成与移动。

### ✨ 主要特色
- 🌱 **蒲公英形态设计**: 主干代表年份，分支代表月份，末端圆圈表示台风强度
- 📊 **多年数据**: 支持2014-2024年数据对比分析
- 📊 **动态更新**: 支持实时数据爬取和可视化更新
- 🎬 **多种模式**: 静态图、生长动画、交互式探索
- 🎭 **动态交互**: 包含生长动画和交互式摆动效果, 支持悬停查看详情，点击获取更多信息


## 🚀 快速开始

### 核心依赖
- **Python 3.8+** - 主要编程语言
- **matplotlib 3.5+** - 数据可视化核心库
- **pandas 1.3+** - 数据处理和分析
- **numpy 1.21+** - 数值计算支持
- **requests 2.25+** - HTTP请求和数据爬取



## 📦 安装指南

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/typhoon-dandelion-viz.git
cd typhoon-dandelion-viz
```

### 2. 创建虚拟环境
```bash
python -m venv typhoon_env
source typhoon_env/bin/activate  # Linux/Mac
# 或
typhoon_env\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行程序
```bash
python typhoon_dandelion.py
```

## 🌐 数据来源

### 香港天文台官方网站

URL: https://www.hko.gov.hk/tc/publica/pubtc.htm
数据类型: PDF年度台风报告
覆盖年份: 2014-2024年
数据内容: 台风名称、编号、形成日期、强度、等级等

### 数据获取流程
1. 自动访问香港天文台年报列表页面
2. 识别并下载对应年份的PDF报告
3. 使用pdfplumber解析PDF内容
4. 提取台风基本信息和统计数据
5. 数据清洗、去重和格式化
6. 本地缓存以提升后续访问速度

## 🎨 可视化设计

### 设计理念
- **主干**: 2025年时间轴，从下往上生长
- **粗分支**: 12个月份，呈放射状分布
- **细分支**: 具体台风事件，包含日期、编号、名称
- **圆圈大小**: 反映台风风级强度
- **颜色编码**: 区分实际数据与预测数据

### 视觉元素
系统采用柔和自然的色彩方案：
```python
colors = {
    'prediction': '#90EE90',  # 浅绿色 - 预测数据
    'actual': '#255751',      # 深绿色 - 实际数据
    'stem': '#659B4C',       # 中绿色，年份分支强调色
    'stem': '#EDA071',        # 柔和橙色，台风等级辅助色
    'stem': '#85C8BC',        # 青绿色，热带风暴
    'background': '#FEFAEF'   # 温暖的米白色背景主色调
}
```


### 布局规则
- A4比例 (297:210)
- 中心辐射布局
- 左下角图例和比例尺
- 右下角数据更新时间

## 🎬 动画功能

### 1. 生长动画
```python
def create_growth_animation():
    """模拟蒲公英生长过程"""
    # 逐步绘制主干
    # 依次展开月份分支
    # 最后显示台风数据点
```

### 2. 摆动效果
```python
def add_swaying_effect():
    """添加随风摆动效果"""
    # 使用三角函数模拟自然摆动
    # 根据风级调整摆动幅度
```

### 3. 交互功能
- 鼠标悬停显示详细信息
- 点击台风圆圈查看具体数据
- 拖拽交互改变视角

## 📁 项目结构

typhoon-dandelion/
├── typhoon_dandelion.py # Main visualization engine
├── data_crawler.py      # HKO data acquisition
├── config.yaml          # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md            # This documentation
├── data/                # Cached typhoon data
├── output/              # Generated visualizations
│   ├── images/          # Static PNG exports
│   ├── animations/      # GIF animations
│   └── data/            # Processed datasets
└── logs/                # Application logs

## ⚙️ 配置选项

### 编辑config.yaml 示例
```yaml
visualization:
  figure:
    width: 12      # 图形宽度
    height: 8.5    # 图形高度
    dpi: 300       # 分辨率

animation:
  fps: 30                    # 动画帧率
  growth_duration: 8.0       # 生长动画时长

data:
  cache:
    enabled: true            # 启用缓存
    expiry: 3600            # 缓存过期时间(秒)
```

## 📊 数据格式

### 台风数据结构
```json
{
  "typhoons": [
    {
      "id": "202501",
      "name": "贝碧佳",
      "name_en": "Bebinca",
      "formation_date": "2025-01-15",
      "landfall_date": "2025-01-18",
      "max_wind_speed": 8,
      "min_pressure": 995,
      "category": "热带风暴",
      "is_prediction": false,
      "source": "HKO"
    }
  ]
}
```

## 🔧 自定义功能

### 添加新数据源
```python
class CustomCrawler:
    def __init__(self, source_url):
        self.url = source_url
    
    def fetch_data(self):
        # 实现数据抓取逻辑
        pass
    
    def parse_data(self, raw_data):
        # 实现数据解析逻辑
        pass
```

### 修改视觉样式
```python
# 在 typhoon_dandelion.py 中修改
colors = {
    'prediction': '#YOUR_COLOR',  # 自定义颜色
    'actual': '#YOUR_COLOR',
    'stem': '#YOUR_COLOR',
    'background': '#YOUR_COLOR'
}
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

- 项目维护者: [Chen Yifei]
- 邮箱: 25112646g@connect.polyu.hk
- 项目链接: https://github.com/yourusername/typhoon-dandelion-viz

## 🙏 致谢

- 香港天文台提供的优质数据服务
- matplotlib 社区的优秀可视化工具
- 所有为开源项目做出贡献的开typhoon-dandelion-viz发者

---

**注意**: 本项目仅用于数据可视化和教育目的，不应用于实际的台风预警或决策。如需官方台风信息，请访问相关气象部门官网。