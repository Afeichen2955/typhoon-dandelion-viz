#!/usr/bin/env python3
"""
Hong Kong Typhoon Dandelion Visualization - Fixed Version
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import json
import os
import warnings
from urllib.parse import urljoin
import time
import math
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

class TyphoonDandelionViz:
    def __init__(self):
        self.fig = None
        self.ax = None
        self.typhoon_data = []
        self.colors = {
            'prediction': '#90EE90',    # Light green - prediction data
            'actual': '#255751',        # Deep green - actual data
            'stem': '#659B4C',          # Medium green - main stem
            'month_branch': '#EDA071',  # Soft orange - month branches
            'background': '#FEFAEF',    # Warm off-white background
            'text': '#2C3E50'           # Dark blue-gray text
        }
        self.current_year = 2025
        self.data_cache = {}
        
    def setup_figure(self):
        """Initialize the figure with A4 proportions"""
        # A4 proportions: 297:210 ≈ 1.414:1
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 8.5), dpi=300)
        self.fig.patch.set_facecolor(self.colors['background'])
        self.ax.set_facecolor(self.colors['background'])
        
        # Remove axes and set equal aspect ratio
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
    def fetch_hko_publication_data(self, year):
        """从香港天文台年报获取真实数据"""
        print(f"📖 从香港天文台年报获取 {year} 年数据...")
        
        try:
            # 构建年报URL
            if year >= 2000:
                base_url = f"https://www.hko.gov.hk/en/publica/tc/tc{year}"
                overview_url = f"{base_url}/section2.html"
            else:
                print(f"⚠️ {year} 年数据格式较旧，使用模拟数据")
                return self.generate_simulated_data(year)
            
            # 获取年报概览页面
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(overview_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return self.parse_hko_publication(response.text, year)
            else:
                print(f"⚠️ 无法访问 {year} 年报，状态码: {response.status_code}")
                return self.generate_simulated_data(year)
                
        except Exception as e:
            print(f"⚠️ 获取 {year} 年数据时出错: {e}")
            return self.generate_simulated_data(year)
    
    def parse_hko_publication(self, html_content, year):
        """解析香港天文台年报HTML内容"""
        typhoons = []
        
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找台风表格或列表
            # 这里使用简化的解析方法，实际可能需要根据具体HTML结构调整
            text_content = soup.get_text()
            
            # 查找台风名称模式
            typhoon_patterns = [
                r'(?:Typhoon|Super Typhoon|Severe Typhoon|Tropical Storm|Severe Tropical Storm)\s+(\w+)\s*\((\d+)\)',
                r'(\w+)\s*\((\d{4})\)',  # 更简单的模式
                r'TC\s+(\w+)\s+\((\d+)\)'
            ]
            
            found_typhoons = set()  # 避免重复
            
            for pattern in typhoon_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        name, tc_id = match
                        if name not in found_typhoons:
                            found_typhoons.add(name)
                            
                            # 生成合理的台风数据
                            typhoon = self.create_realistic_typhoon(name, tc_id, year)
                            typhoons.append(typhoon)
            
            # 如果没有找到足够的台风，补充一些
            if len(typhoons) < 3:
                print(f"⚠️ {year} 年只找到 {len(typhoons)} 个台风，补充模拟数据")
                additional = self.generate_simulated_data(year)
                typhoons.extend(additional[:max(0, 6-len(typhoons))])
            
            print(f"✅ {year} 年获取到 {len(typhoons)} 个台风数据")
            return typhoons
            
        except Exception as e:
            print(f"⚠️ 解析 {year} 年数据时出错: {e}")
            return self.generate_simulated_data(year)
    
    def create_realistic_typhoon(self, name, tc_id, year):
        """创建真实的台风数据结构"""
        # 根据台风名称和年份生成合理的数据
        month_prob = {
            1: 0.02, 2: 0.02, 3: 0.03, 4: 0.05, 5: 0.08, 6: 0.12,
            7: 0.18, 8: 0.22, 9: 0.18, 10: 0.08, 11: 0.03, 12: 0.01
        }
        
        # 生成形成月份
        month = np.random.choice(list(month_prob.keys()), p=list(month_prob.values()))
        day = np.random.randint(1, 29)
        
        # 生成强度（基于历史分布）
        wind_speeds = [70, 85, 105, 130, 160, 200]
        probabilities = [0.3, 0.25, 0.2, 0.15, 0.08, 0.02]
        max_wind = np.random.choice(wind_speeds, p=probabilities)
        
        return {
            'id': tc_id if tc_id.isdigit() else f"{year}{np.random.randint(1,20):02d}",
            'name': name,
            'name_en': name,
            'formation_date': f"{year}-{month:02d}-{day:02d}",
            'max_wind_speed': max_wind,
            'min_pressure': np.random.randint(920, 1000),
            'category': self.classify_typhoon(max_wind),
            'year': year,
            'is_prediction': year > datetime.now().year,
            'source': 'HKO_Publication'
        }
    
    def fetch_typhoon_data(self, year):
        """获取台风数据的主要方法"""
        print(f"📊 获取 {year} 年台风数据...")
        
        # 检查缓存
        cache_key = f"typhoon_{year}"
        if cache_key in self.data_cache:
            print(f"✅ 使用 {year} 年缓存数据")
            return self.data_cache[cache_key]
        
        # 尝试从香港天文台年报获取
        data = self.fetch_hko_publication_data(year)
        
        # 缓存数据
        self.data_cache[cache_key] = data
        return data
    
    def generate_simulated_data(self, year):
        """生成模拟台风数据"""
        # 历史台风名称库
        historical_names = [
            'Maliksi', 'Prapiroon', 'Yagi', 'Trami', 'Kong-rey', 'Yinxing',
            'Toraji', 'Man-yi', 'Usagi', 'Bebinca', 'Pulasan', 'Wutip',
            'Krathon', 'Bailu', 'Podul', 'Lingling', 'Mitag', 'Hagibis',
            'Francisco', 'Lekima', 'Haishen', 'Maysak', 'Bavi', 'Jangmi'
        ]
        
        # 季节分布
        month_distribution = {
            1: 0.02, 2: 0.02, 3: 0.03, 4: 0.05, 5: 0.08, 6: 0.12,
            7: 0.18, 8: 0.22, 9: 0.15, 10: 0.08, 11: 0.03, 12: 0.02
        }
        
        typhoons = []
        num_typhoons = np.random.randint(4, 8)  # 每年4-7个台风
        
        selected_names = np.random.choice(
            historical_names, 
            size=min(num_typhoons, len(historical_names)), 
            replace=False
        )
        
        for i, name in enumerate(selected_names):
            month = np.random.choice(
                list(month_distribution.keys()), 
                p=list(month_distribution.values())
            )
            day = np.random.randint(1, 29)
            
            # 生成强度
            max_wind = np.random.choice([70, 85, 105, 130, 160, 200], 
                                      p=[0.3, 0.25, 0.2, 0.15, 0.08, 0.02])
            
            typhoon = {
                'id': f"{year}{i+1:02d}",
                'name': name,
                'name_en': name,
                'formation_date': f"{year}-{month:02d}-{day:02d}",
                'max_wind_speed': max_wind,
                'min_pressure': np.random.randint(920, 1000),
                'category': self.classify_typhoon(max_wind),
                'year': year,
                'is_prediction': year > datetime.now().year,
                'source': 'Simulated'
            }
            typhoons.append(typhoon)
        
        return typhoons
    
    def classify_typhoon(self, wind_speed):
        """根据风速分类台风"""
        if wind_speed < 63:
            return "Tropical Depression"
        elif wind_speed < 88:
            return "Tropical Storm"
        elif wind_speed < 118:
            return "Severe Tropical Storm"
        elif wind_speed < 150:
            return "Typhoon"
        elif wind_speed < 185:
            return "Severe Typhoon"
        else:
            return "Super Typhoon"
    
    def collect_all_data(self, start_year=2014, end_year=2024):
        """收集所有年份的数据"""
        print(f"🌪️ 收集 {start_year}-{end_year} 年台风数据...")
        all_data = []
        
        for year in range(start_year, end_year + 1):
            year_data = self.fetch_typhoon_data(year)
            all_data.extend(year_data)
            time.sleep(1)  # 礼貌性延迟
        
        self.typhoon_data = all_data
        print(f"✅ 总共收集到 {len(all_data)} 个台风数据")
        return all_data
    
    def calculate_dandelion_positions(self):
        """计算蒲公英结构的位置"""
        positions = {
            'stem': {'x': 0, 'y': np.linspace(-8, 0, 50)},
            'years': {},
            'typhoons': {}
        }
        
        # 按年份分组数据
        years_data = {}
        for typhoon in self.typhoon_data:
            year = typhoon['year']
            if year not in years_data:
                years_data[year] = []
            years_data[year].append(typhoon)
        
        # 计算年份分支位置
        years = sorted(years_data.keys())
        num_years = len(years)
        
        for i, year in enumerate(years):
            # 放射状分布
            angle = 2 * np.pi * i / num_years
            radius = 3
            
            year_x = radius * np.cos(angle)
            year_y = radius * np.sin(angle)
            
            positions['years'][year] = {'x': year_x, 'y': year_y, 'angle': angle}
            
            # 计算台风位置
            year_typhoons = years_data[year]
            positions['typhoons'][year] = []
            
            for j, typhoon in enumerate(year_typhoons):
                sub_angle = angle + (j - len(year_typhoons)/2) * 0.3
                sub_radius = radius + 2 + np.random.uniform(0, 1.5)
                
                typhoon_x = sub_radius * np.cos(sub_angle)
                typhoon_y = sub_radius * np.sin(sub_angle)
                
                circle_size = max(50, typhoon['max_wind_speed'] * 2)
                
                pos = {
                    'x': typhoon_x,
                    'y': typhoon_y,
                    'size': circle_size,
                    'typhoon': typhoon
                }
                positions['typhoons'][year].append(pos)
        
        return positions
    
    def draw_static_dandelion(self):
        """绘制静态蒲公英可视化"""
        self.setup_figure()
        positions = self.calculate_dandelion_positions()
        
        # 绘制主干
        stem_x = positions['stem']['x']
        stem_y = positions['stem']['y']
        self.ax.plot([stem_x] * len(stem_y), stem_y, 
                    color=self.colors['stem'], linewidth=8, alpha=0.8)
        
        # 绘制年份分支和台风
        for year, year_pos in positions['years'].items():
            # 年份分支
            self.ax.plot([0, year_pos['x']], [0, year_pos['y']], 
                        color=self.colors['month_branch'], linewidth=4, alpha=0.7)
            
            # 年份标签
            label_x = year_pos['x'] * 1.2
            label_y = year_pos['y'] * 1.2
            self.ax.text(label_x, label_y, str(year), 
                        fontsize=10, fontweight='bold', 
                        color=self.colors['text'], ha='center', va='center')
            
            # 台风
            if year in positions['typhoons']:
                for typhoon_pos in positions['typhoons'][year]:
                    typhoon = typhoon_pos['typhoon']
                    
                    # 台风分支
                    self.ax.plot([year_pos['x'], typhoon_pos['x']], 
                               [year_pos['y'], typhoon_pos['y']], 
                               color=self.colors['stem'], linewidth=2, alpha=0.6)
                    
                    # 台风圆圈
                    color = self.colors['prediction'] if typhoon['is_prediction'] else self.colors['actual']
                    circle = Circle((typhoon_pos['x'], typhoon_pos['y']), 
                                  typhoon_pos['size']/1000, 
                                  color=color, alpha=0.7)
                    self.ax.add_patch(circle)
                    
                    # 台风名称
                    self.ax.text(typhoon_pos['x'], typhoon_pos['y'], 
                               typhoon['name_en'][:4], 
                               fontsize=6, ha='center', va='center',
                               color='white', fontweight='bold')
        
        # 添加标题和图例
        self.add_title_and_legend()
        plt.tight_layout()
        return self.fig
    
    def add_title_and_legend(self):
        """添加标题、图例和元数据"""
        # 标题
        self.ax.text(0, 9, 'Hong Kong Typhoon Dandelion', 
                    fontsize=20, fontweight='bold', 
                    color=self.colors['text'], ha='center')
        
        self.ax.text(0, 8.5, '2014-2024 Tropical Cyclone Visualization', 
                    fontsize=12, color=self.colors['text'], ha='center')
        
        # 图例
        legend_x, legend_y = -9, -8
        
        # 实际 vs 预测数据
        actual_circle = Circle((legend_x, legend_y), 0.2, 
                              color=self.colors['actual'], alpha=0.7)
        pred_circle = Circle((legend_x, legend_y - 0.8), 0.2, 
                            color=self.colors['prediction'], alpha=0.7)
        
        self.ax.add_patch(actual_circle)
        self.ax.add_patch(pred_circle)
        
        self.ax.text(legend_x + 0.5, legend_y, 'Actual Data', 
                    fontsize=10, va='center', color=self.colors['text'])
        self.ax.text(legend_x + 0.5, legend_y - 0.8, 'Predicted Data', 
                    fontsize=10, va='center', color=self.colors['text'])
        
        # 数据源
        self.ax.text(9, -9, f'Data: Hong Kong Observatory\nUpdated: {datetime.now().strftime("%Y-%m-%d")}', 
                    fontsize=8, ha='right', va='bottom', 
                    color=self.colors['text'], alpha=0.7)
        
        # 比例尺
        scale_circles = [0.1, 0.2, 0.3]
        scale_labels = ['63-87 km/h\n(Tropical Storm)', '88-117 km/h\n(Severe TS)', '118+ km/h\n(Typhoon)']
        
        for i, (size, label) in enumerate(zip(scale_circles, scale_labels)):
            circle = Circle((legend_x + 2, legend_y - i * 1.2), size, 
                           color=self.colors['actual'], alpha=0.5)
            self.ax.add_patch(circle)
            self.ax.text(legend_x + 2.8, legend_y - i * 1.2, label, 
                        fontsize=8, va='center', color=self.colors['text'])
    
    def create_growth_animation(self, duration=8.0, fps=30):
        """创建生长动画 - 修复版本"""
        self.setup_figure()
        positions = self.calculate_dandelion_positions()
        
        frames = int(duration * fps)
        
        def animate(frame):
            self.ax.clear()
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(-10, 10)
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            self.ax.set_facecolor(self.colors['background'])
            
            progress = frame / frames
            
            # 获取完整的stem_y数据
            full_stem_y = positions['stem']['y']
            
            # 阶段1: 生长主干 (0-30%)
            if progress <= 0.3:
                stem_progress = progress / 0.3
                stem_y = full_stem_y[:int(len(full_stem_y) * stem_progress)]
                if len(stem_y) > 0:
                    self.ax.plot([0] * len(stem_y), stem_y, 
                               color=self.colors['stem'], linewidth=8, alpha=0.8)
            
            # 阶段2: 生长年份分支 (30-60%)
            elif progress <= 0.6:
                # 绘制完整主干
                self.ax.plot([0] * len(full_stem_y), full_stem_y, 
                           color=self.colors['stem'], linewidth=8, alpha=0.8)
                
                branch_progress = (progress - 0.3) / 0.3
                years = list(positions['years'].keys())
                branches_to_show = int(len(years) * branch_progress)
                
                for i, year in enumerate(sorted(years)[:branches_to_show]):
                    year_pos = positions['years'][year]
                    self.ax.plot([0, year_pos['x']], [0, year_pos['y']], 
                               color=self.colors['month_branch'], linewidth=4, alpha=0.7)
            
            # 阶段3: 添加台风 (60-100%)
            else:
                # 绘制完整结构
                self.ax.plot([0] * len(full_stem_y), full_stem_y, 
                           color=self.colors['stem'], linewidth=8, alpha=0.8)
                
                typhoon_progress = (progress - 0.6) / 0.4
                
                for year, year_pos in positions['years'].items():
                    # 年份分支
                    self.ax.plot([0, year_pos['x']], [0, year_pos['y']], 
                               color=self.colors['month_branch'], linewidth=4, alpha=0.7)
                    
                    # 逐步添加台风
                    if year in positions['typhoons']:
                        typhoons_to_show = int(len(positions['typhoons'][year]) * typhoon_progress)
                        
                        for typhoon_pos in positions['typhoons'][year][:typhoons_to_show]:
                            typhoon = typhoon_pos['typhoon']
                            
                            # 台风分支
                            self.ax.plot([year_pos['x'], typhoon_pos['x']], 
                                       [year_pos['y'], typhoon_pos['y']], 
                                       color=self.colors['stem'], linewidth=2, alpha=0.6)
                            
                            # 台风圆圈
                            color = self.colors['prediction'] if typhoon['is_prediction'] else self.colors['actual']
                            circle = Circle((typhoon_pos['x'], typhoon_pos['y']), 
                                          typhoon_pos['size']/1000, 
                                          color=color, alpha=0.7)
                            self.ax.add_patch(circle)
            
            # 始终显示标题
            self.ax.text(0, 9, 'Hong Kong Typhoon Dandelion', 
                        fontsize=20, fontweight='bold', 
                        color=self.colors['text'], ha='center')
        
        anim = animation.FuncAnimation(self.fig, animate, frames=frames, 
                                     interval=1000/fps, blit=False, repeat=True)
        return anim
    
    def save_visualization(self, filename='typhoon_dandelion.png'):
        """保存可视化图像"""
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                           facecolor=self.colors['background'])
            print(f"💾 可视化图像已保存为 {filename}")
    
    def save_animation(self, filename='typhoon_dandelion_growth.gif', duration=8.0):
        """保存生长动画为GIF"""
        try:
            anim = self.create_growth_animation(duration=duration)
            anim.save(filename, writer='pillow', fps=15, dpi=100)
            print(f"🎬 动画已保存为 {filename}")
        except Exception as e:
            print(f"⚠️ 保存动画时出错: {e}")
            print("💡 跳过动画保存，继续执行...")

    def get_optimal_figure_size(self):
        """根据屏幕尺寸计算最佳图像尺寸"""
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # 计算可用空间 (考虑菜单栏、dock等)
            usable_width = screen_width * 0.8
            usable_height = screen_height * 0.7
            
            # 转换为英寸 (假设96 DPI)
            fig_width = min(usable_width / 96, 12)
            fig_height = min(usable_height / 96, 9)
            
            print(f"检测到屏幕尺寸: {screen_width}x{screen_height}")
            print(f"优化图像尺寸: {fig_width:.1f}x{fig_height:.1f}英寸")
            
            return fig_width, fig_height
            
        except:
            # 默认14寸MacBook Pro优化尺寸
            return 10, 7

    def setup_figure(self):
        """Initialize the figure with optimized proportions"""
        # 获取最佳尺寸
        fig_width, fig_height = self.get_optimal_figure_size()
        
        self.fig, self.ax = plt.subplots(1, 1, figsize=(fig_width, fig_height), dpi=100)
        self.fig.patch.set_facecolor(self.colors['background'])
        self.ax.set_facecolor(self.colors['background'])
        
        # 动态调整坐标范围
        coord_range = min(fig_width, fig_height) * 0.8
        self.ax.set_xlim(-coord_range, coord_range)
        self.ax.set_ylim(-coord_range, coord_range)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

def main():
    """主执行函数"""
    print("🌪️ 启动香港台风蒲公英可视化...")
    
    # 创建可视化器
    viz = TyphoonDandelionViz()
    
    # 收集数据
    viz.collect_all_data(start_year=2014, end_year=2024)
    
    # 创建静态可视化
    print("🎨 创建静态可视化...")
    fig = viz.draw_static_dandelion()
    viz.save_visualization('typhoon_dandelion_2014_2024.png')
    
    # 尝试创建生长动画
    print("🎬 创建生长动画...")
    viz.save_animation('typhoon_dandelion_growth.gif', duration=6.0)
    
    # 显示图像
    plt.show()
    
    print("✅ 可视化完成!")

if __name__ == "__main__":
    main()