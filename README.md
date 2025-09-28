# 🌪️ Hong Kong Typhoon Data Dandelion Visualization Project

## 📖 Project Overview

This project visualizes Hong Kong Observatory's tropical cyclone data from 2014-2024 in the form of dandelions, creatively combining natural forms with data visualization. The project draws inspiration from how dandelion seeds spread with the wind, symbolizing the formation and movement of typhoons across the ocean.

### ✨ Key Features
- 🌱 **Dandelion Design**: Main stem represents years, branches represent months, end circles indicate typhoon intensity
- 📊 **Multi-year Data**: Supports comparative analysis of 2014-2024 data
- 📊 **Dynamic Updates**: Supports real-time data crawling and visualization updates
- 🎬 **Multiple Modes**: Static charts, growth animations, interactive exploration
- 🎭 **Dynamic Interaction**: Includes growth animations and interactive swaying effects, supports hover for details, click for more information

## 🚀 Quick Start

### Core Dependencies
- **Python 3.8+** - Main programming language
- **matplotlib 3.5+** - Core data visualization library
- **pandas 1.3+** - Data processing and analysis
- **numpy 1.21+** - Numerical computation support
- **requests 2.25+** - HTTP requests and data crawling

## 📦 Installation Guide

### 1. Clone the Project
```bash
git clone https://github.com/yourusername/typhoon-dandelion-viz.git
cd typhoon-dandelion-viz
```

### 2. Create Virtual Environment
```bash
python -m venv typhoon_env
source typhoon_env/bin/activate  # Linux/Mac
# or
typhoon_env\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Program
```bash
python typhoon_dandelion.py
```

## 🌐 Data Sources

### Hong Kong Observatory Official Website

URL: https://www.hko.gov.hk/tc/publica/pubtc.htm
Data Type: PDF annual typhoon reports
Coverage Years: 2014-2024
Data Content: Typhoon names, numbers, formation dates, intensity, categories, etc.

### Data Acquisition Process
1. Automatically access Hong Kong Observatory annual report list page
2. Identify and download PDF reports for corresponding years
3. Use pdfplumber to parse PDF content
4. Extract basic typhoon information and statistical data
5. Data cleaning, deduplication, and formatting
6. Local caching to improve subsequent access speed

## 🎨 Visualization Design

### Design Philosophy
- **Main Stem**: 2025 timeline, growing from bottom to top
- **Major Branches**: 12 months, arranged radially
- **Minor Branches**: Specific typhoon events, including dates, numbers, names
- **Circle Size**: Reflects typhoon wind scale intensity
- **Color Coding**: Distinguishes between actual data and predicted data

### Visual Elements
The system uses a soft, natural color scheme:
```python
colors = {
    'prediction': '#90EE90',  # Light green - predicted data
    'actual': '#255751',      # Dark green - actual data
    'stem': '#659B4C',       # Medium green, year branch accent color
    'stem': '#EDA071',        # Soft orange, typhoon grade auxiliary color
    'stem': '#85C8BC',        # Teal green, tropical storm
    'background': '#FEFAEF'   # Warm off-white background main color
}
```

### Layout Rules
- A4 ratio (297:210)
- Central radial layout
- Legend and scale in bottom left corner
- Data update time in bottom right corner

## 🎬 Animation Features

### 1. Growth Animation
```python
def create_growth_animation():
    """Simulate dandelion growth process"""
    # Gradually draw main stem
    # Sequentially expand monthly branches
    # Finally display typhoon data points
```

### 2. Swaying Effect
```python
def add_swaying_effect():
    """Add wind swaying effect"""
    # Use trigonometric functions to simulate natural swaying
    # Adjust swaying amplitude based on wind scale
```

### 3. Interactive Features
- Mouse hover displays detailed information
- Click typhoon circles to view specific data
- Drag interaction to change viewing angle

## 📁 Project Structure

```
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
```

## ⚙️ Configuration Options

### Edit config.yaml Example
```yaml
visualization:
  figure:
    width: 12      # Figure width
    height: 8.5    # Figure height
    dpi: 300       # Resolution

animation:
  fps: 30                    # Animation frame rate
  growth_duration: 8.0       # Growth animation duration

data:
  cache:
    enabled: true            # Enable caching
    expiry: 3600            # Cache expiry time (seconds)
```

## 📊 Data Format

### Typhoon Data Structure
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

## 🔧 Customization Features

### Adding New Data Sources
```python
class CustomCrawler:
    def __init__(self, source_url):
        self.url = source_url
    
    def fetch_data(self):
        # Implement data crawling logic
        pass
    
    def parse_data(self, raw_data):
        # Implement data parsing logic
        pass
```

### Modifying Visual Styles
```python
# Modify in typhoon_dandelion.py
colors = {
    'prediction': '#YOUR_COLOR',  # Custom color
    'actual': '#YOUR_COLOR',
    'stem': '#YOUR_COLOR',
    'background': '#YOUR_COLOR'
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🤝 Contributing Guidelines

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact Information

- Project Maintainer: [Chen Yifei]
- Email: 25112646g@connect.polyu.hk
- Project Link: https://github.com/yourusername/typhoon-dandelion-viz

## 🙏 Acknowledgments

- Hong Kong Observatory for providing excellent data services
- matplotlib community for outstanding visualization tools
- All developers who contribute to open source projects

---

**Note**: This project is for data visualization and educational purposes only and should not be used for actual typhoon warnings or decision-making. For official typhoon information, please visit relevant meteorological department websites.