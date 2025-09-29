#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class TyphoonDandelionViz:
    def __init__(self):
        self.fig = None
        self.ax = None
        self.typhoon_data = []
        self.colors = {
            'prediction': '#90C4B8',
            'actual': '#4A9B8E',
            'stem': '#2D5F4F',
            'year_branch': '#5A8F7B',
            'month_branch': '#D4A574',
            'background': '#FBF8F1',
            'text': '#2C3E50',
            'panel_bg': '#FFFFFF'
        }
        self.current_year = 2025
        self.data_cache = {}
        
        # 文字区域配置字典
        self.text_config = {
            'fontsize_multiplier': 9.5,
            'line_spacing': 1,     # 行间距（1.0=标准，2.0=双倍）
            'padding': 1.2,          # 段落边距/内边距
            'background_alpha': 0.0,
            'show_border': False,
            'border_width': 1.5,
            'border_color': None,
            'border_style': 'round',
            'margin_left_px': 5,      # 左边距（像素）
            'margin_right_px': 5,     # 右边距（像素）
            'max_width_chars': 80  
        }

    # 布局配置
        self.layout_config = {
            'header_rows': (0, 2),      # 标题区域行范围
            'text_rows': (3, 5),        # 文字区域行范围（增加了1行间距）
            'main_rows': (5, 17),       # 主可视化区域
            'footer_rows': (17, 22),    # 底部区域
            'hspace': 0.4,              # 垂直间距
            'wspace': 0.3               # 水平间距
        }

        # 动画状态
        self.mouse_x = 0
        self.mouse_y = 0
        self.branch_velocities = {}
        self.time = 0
        
        # 固定宽高比
        self.aspect_ratio = 1.414
    
    def get_optimal_figure_size(self):
        """根据屏幕尺寸计算最佳图像尺寸，保持固定宽高比"""
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # 计算可用空间
            usable_width = screen_width * 0.75
            usable_height = screen_height * 0.85
            
            # 方式1：以宽度为基准
            width_based_width = usable_width / 96
            width_based_height = width_based_width * self.aspect_ratio
            
            # 方式2：以高度为基准
            height_based_height = usable_height / 96
            height_based_width = height_based_height / self.aspect_ratio
            
            # 选择适合屏幕的方案
            if width_based_height <= usable_height / 96:
                fig_width = width_based_width
                fig_height = width_based_height
                fit_mode = "宽度适配"
            else:
                fig_width = height_based_width
                fig_height = height_based_height
                fit_mode = "高度适配"
            
            # 限制最大和最小尺寸
            fig_width = max(8, min(fig_width, 20))
            fig_height = fig_width * self.aspect_ratio
            
            print(f"屏幕尺寸: {screen_width}x{screen_height}px")
            print(f"可用空间: {usable_width:.0f}x{usable_height:.0f}px")
            print(f"图像尺寸: {fig_width:.1f}x{fig_height:.1f}英寸 ({fit_mode})")
            print(f"宽高比: {fig_height/fig_width:.3f}")
            
            # 根据图像大小调整DPI
            if fig_width < 10:
                dpi = 120
            elif fig_width < 14:
                dpi = 100
            else:
                dpi = 80
                
            return fig_width, fig_height, dpi
            
        except Exception as e:
            print(f"无法获取屏幕信息，使用默认尺寸: {e}")
            return 10, 14.14, 100

    def setup_figure_with_layout(self):
        """设置完整的布局结构，自适应屏幕大小"""
        fig_width, fig_height, dpi = self.get_optimal_figure_size()
        
        self.fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        self.fig.patch.set_facecolor(self.colors['background'])
        
        import matplotlib.gridspec as gridspec
        gs = gridspec.GridSpec(22, 20, figure=self.fig, 
                            left=0.05, right=0.95, top=0.97, bottom=0.03,
                            hspace=self.layout_config['hspace'],
                            wspace=self.layout_config['wspace'])
        
        # 使用配置的行范围
        self.ax_header = self.fig.add_subplot(
            gs[self.layout_config['header_rows'][0]:self.layout_config['header_rows'][1], :]
        )
        self.ax_header.axis('off')
        
        self.ax_text = self.fig.add_subplot(
            gs[self.layout_config['text_rows'][0]:self.layout_config['text_rows'][1], :]
        )
        self.ax_text.axis('off')
        
        self.ax = self.fig.add_subplot(
            gs[self.layout_config['main_rows'][0]:self.layout_config['main_rows'][1], :]
        )
        self.ax.set_facecolor(self.colors['background'])
        self.ax.set_xlim(-2, 12)
        self.ax.set_ylim(-2, 12)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        footer_start = self.layout_config['footer_rows'][0]
        footer_end = self.layout_config['footer_rows'][1]
        
        self.ax_scale = self.fig.add_subplot(gs[footer_start:footer_end, 0:10])
        self.ax_scale.axis('off')
        
        self.ax_legend = self.fig.add_subplot(gs[footer_start:footer_end, 10:20])
        self.ax_legend.axis('off')
        
        self.font_scale = min(fig_width / 10, fig_height / 14.14)
        print(f"字体缩放系数: {self.font_scale:.2f}")


    def draw_header_section(self):
        """绘制顶部标题和更新时间"""
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.ax_header.text(0.02, 0.7, f'Updated: {update_time}', 
                           fontsize=9*self.font_scale, color=self.colors['text'],
                           transform=self.ax_header.transAxes)
        
        self.ax_header.text(0.5, 0.4, 'Hong Kong Typhoon Dandelion', 
                           fontsize=22*self.font_scale, fontweight='bold', 
                           color=self.colors['text'], ha='center',
                           transform=self.ax_header.transAxes)
        
        self.ax_header.text(0.5, 0.05, '2014-2024 Tropical Cyclone Data Visualization', 
                           fontsize=12*self.font_scale, color=self.colors['text'], 
                           ha='center', style='italic', 
                           transform=self.ax_header.transAxes)
    
    def draw_text_section(self):
        """绘制文字内容区域 - 完整可配置版本"""
        text_content = """Despite the destruction brought by typhoons, this visualization displays the natural cycle and patterns of tropical cyclone formation in the Western Pacific. Like dandelion seeds drifting in the wind, the distribution of typhoon data across the temporal dimension presents unique regularity. Each 'seed' represents a typhoon, with its size reflecting storm intensity, and colors distinguishing between historical data and forecast data."""
        
        text_fontsize = self.text_config['fontsize_multiplier'] * self.font_scale

        if self.text_config.get('max_width_chars'):
            max_chars = self.text_config['max_width_chars']
        else:
            # 自动计算
            fig_width_pixels = self.fig.get_figwidth() * self.fig.dpi
            margin_total = self.text_config['margin_left_px'] + self.text_config['margin_right_px']
            usable_width = fig_width_pixels * 0.9 - margin_total
            char_width = text_fontsize * 0.55 * self.fig.dpi / 72
            max_chars = int(usable_width / char_width)

        # 自动换行
        import textwrap
        wrapped_text = textwrap.fill(
            text_content,
            width=max_chars,
            break_long_words=False,
            break_on_hyphens=True
        )

        padding = self.text_config['padding']
        line_spacing = self.text_config['line_spacing']
        bg_alpha = self.text_config['background_alpha']
        
        border_style = self.text_config['border_style']
        boxstyle_str = f"{border_style},pad={padding}"
        
        bbox_props = {
            'boxstyle': boxstyle_str,
            'facecolor': self.colors['panel_bg'],
            'alpha': bg_alpha
        }
        
        if self.text_config['show_border']:
            border_color = self.text_config['border_color'] or self.colors['text']
            bbox_props['edgecolor'] = border_color
            bbox_props['linewidth'] = self.text_config['border_width'] * self.font_scale
        else:
            bbox_props['edgecolor'] = 'none'
        
        self.ax_text.text(
            0.5, 0.5,
            wrapped_text,  # 改为 wrapped_text
            fontsize=text_fontsize,
            color=self.colors['text'],
            ha='center',
            va='center',
            bbox=bbox_props,
            linespacing=line_spacing,
            transform=self.ax_text.transAxes,
            family='sans-serif',
            weight='normal'
        )
    
    def set_text_style(self, **kwargs):
        """便捷方法：动态调整文字样式"""
        for key, value in kwargs.items():
            if key in self.text_config:
                self.text_config[key] = value
            else:
                print(f"警告: 未知的配置参数 '{key}'")

    def draw_scale_section(self):
        """绘制左下角比例尺"""
        self.ax_scale.text(0.1, 0.9, 'Intensity Scale', 
                          fontsize=12*self.font_scale, fontweight='bold',
                          color=self.colors['text'],
                          transform=self.ax_scale.transAxes)
        
        categories = [
            ('TD', 30, '<63 km/h'),
            ('TS', 50, '63-87 km/h'),
            ('STS', 80, '88-117 km/h'),
            ('TY', 120, '118-149 km/h'),
            ('STY', 160, '150-184 km/h'),
            ('Super TY', 200, '≥185 km/h')
        ]
        
        y_positions = np.linspace(0.7, 0.1, len(categories))
        
        for (name, size, speed), y_pos in zip(categories, y_positions):
            circle = Circle((0.15, y_pos), size/2000*self.font_scale, 
                          color=self.colors['actual'], alpha=0.7,
                          transform=self.ax_scale.transAxes)
            self.ax_scale.add_patch(circle)
            
            self.ax_scale.text(0.25, y_pos, f'{name}\n{speed}',
                             fontsize=7.5*self.font_scale, va='center',
                             color=self.colors['text'],
                             transform=self.ax_scale.transAxes)
    
    def draw_legend_section(self):
        """绘制右下角图例"""
        self.ax_legend.text(0.5, 0.9, 'Data Legend', 
                           fontsize=12*self.font_scale, fontweight='bold',
                           color=self.colors['text'], ha='center',
                           transform=self.ax_legend.transAxes)
        
        actual_circle = Circle((0.2, 0.7), 0.025*self.font_scale,
                              color=self.colors['actual'], alpha=0.8,
                              transform=self.ax_legend.transAxes)
        pred_circle = Circle((0.2, 0.5), 0.025*self.font_scale,
                            color=self.colors['prediction'], alpha=0.8,
                            transform=self.ax_legend.transAxes)
        
        self.ax_legend.add_patch(actual_circle)
        self.ax_legend.add_patch(pred_circle)
        
        self.ax_legend.text(0.3, 0.7, 'Historical (2014-2024)',
                           fontsize=8.5*self.font_scale, va='center',
                           color=self.colors['text'],
                           transform=self.ax_legend.transAxes)
        self.ax_legend.text(0.3, 0.5, 'Forecast (2025+)',
                           fontsize=8.5*self.font_scale, va='center',
                           color=self.colors['text'],
                           transform=self.ax_legend.transAxes)
        
        total_typhoons = len(self.typhoon_data)
        stats_text = f"""Total: {total_typhoons}
Source: HKO
Model: Dandelion Dispersion"""
        
        self.ax_legend.text(0.5, 0.2, stats_text,
                           fontsize=7.5*self.font_scale, ha='center', va='top',
                           color=self.colors['text'],
                           transform=self.ax_legend.transAxes,
                           linespacing=1.6)
    
    def calculate_dandelion_from_bottom_left(self):
        """从左下角开始计算蒲公英结构"""
        positions = {
            'stem': {'x': [], 'y': []},
            'years': {},
            'typhoons': {}
        }
        
        stem_length = 40
        stem_x = np.linspace(0, 5, stem_length)
        stem_y = np.linspace(0, 5, stem_length)
        
        for i in range(stem_length):
            t = i / stem_length
            curve = 0.3 * np.sin(2 * np.pi * t)
            stem_x[i] += curve * 0.3
            stem_y[i] += curve * 0.2
        
        positions['stem']['x'] = stem_x
        positions['stem']['y'] = stem_y
        
        years_data = {}
        for typhoon in self.typhoon_data:
            year = typhoon['year']
            if year not in years_data:
                years_data[year] = []
            years_data[year].append(typhoon)
        
        years = sorted(years_data.keys())
        num_years = len(years)
        center_x, center_y = 5, 5
        
        for i, year in enumerate(years):
            base_angle = -2 * np.pi * i / num_years
            angle_variation = np.random.uniform(-0.2, 0.2)
            angle = base_angle + angle_variation
            
            spiral_growth = 0.3 * (i / num_years)
            radius = 2.5 + spiral_growth + np.random.uniform(0, 0.5)
            
            year_x = center_x + radius * np.cos(angle)
            year_y = center_y + radius * np.sin(angle)
            
            positions['years'][year] = {
                'x': year_x, 'y': year_y, 
                'angle': angle, 'radius': radius,
                'center_x': center_x, 'center_y': center_y
            }
            
            year_typhoons = years_data[year]
            positions['typhoons'][year] = []
            
            cluster_count = min(3, len(year_typhoons))
            
            for cluster_idx in range(cluster_count):
                cluster_angle = angle + (cluster_idx - cluster_count/2) * 0.4
                cluster_radius = radius + 1.5 + np.random.uniform(0, 1)
                
                cluster_x = center_x + cluster_radius * np.cos(cluster_angle)
                cluster_y = center_y + cluster_radius * np.sin(cluster_angle)
                
                typhoons_in_cluster = year_typhoons[cluster_idx::cluster_count]
                
                for j, typhoon in enumerate(typhoons_in_cluster):
                    offset_angle = np.random.uniform(0, 2*np.pi)
                    offset_radius = np.random.uniform(0.1, 0.4)
                    
                    typhoon_x = cluster_x + offset_radius * np.cos(offset_angle)
                    typhoon_y = cluster_y + offset_radius * np.sin(offset_angle)
                    
                    seed_size = self.calculate_seed_size(typhoon['max_wind_speed'])
                    
                    pos = {
                        'x': typhoon_x,
                        'y': typhoon_y,
                        'size': seed_size,
                        'typhoon': typhoon,
                        'cluster_id': cluster_idx
                    }
                    positions['typhoons'][year].append(pos)
        
        return positions
    
    def calculate_seed_size(self, wind_speed):
        """根据风速计算种子大小"""
        if wind_speed < 63:
            return 30
        elif wind_speed < 88:
            return 50
        elif wind_speed < 118:
            return 80
        elif wind_speed < 150:
            return 120
        elif wind_speed < 185:
            return 160
        else:
            return 200
    
    def draw_tapered_branch(self, x_points, y_points, start_width, end_width, color, alpha=0.8):
        """绘制渐变粗细的枝干"""
        n_segments = len(x_points) - 1
        
        for i in range(n_segments):
            t = i / n_segments
            width = start_width * (1 - t) + end_width * t
            
            self.ax.plot(
                [x_points[i], x_points[i+1]], 
                [y_points[i], y_points[i+1]],
                color=color, linewidth=width, alpha=alpha,
                solid_capstyle='round', zorder=1
            )
    
    def calculate_sway_offset(self, year, base_x, base_y):
        """计算摆动偏移量"""
        if year not in self.branch_velocities:
            return 0, 0
            
        params = self.branch_velocities[year]
        
        wind_sway_x = params['amplitude'] * np.sin(
            self.time * params['frequency'] + params['phase']
        )
        wind_sway_y = params['amplitude'] * 0.3 * np.cos(
            self.time * params['frequency'] * 1.3 + params['phase']
        )
        
        mouse_dist = np.sqrt((base_x - self.mouse_x)**2 + (base_y - self.mouse_y)**2)
        if mouse_dist < 3:
            influence = np.exp(-mouse_dist / 1.5)
            mouse_push_x = (base_x - self.mouse_x) * influence * 0.5
            mouse_push_y = (base_y - self.mouse_y) * influence * 0.5
        else:
            mouse_push_x = 0
            mouse_push_y = 0
        
        return wind_sway_x + mouse_push_x, wind_sway_y + mouse_push_y
    
    def draw_swaying_dandelion(self, positions):
        """绘制摇曳的蒲公英主体"""
        stem_x = positions['stem']['x']
        stem_y = positions['stem']['y']
        
        self.ax.plot(stem_x, stem_y,
                    color=self.colors['stem'], linewidth=14, alpha=0.9,
                    solid_capstyle='round', zorder=1)
        
        center_x, center_y = stem_x[-1], stem_y[-1]
        center_circle = Circle((center_x, center_y), 0.25,
                              color=self.colors['stem'], alpha=0.9, zorder=2)
        self.ax.add_patch(center_circle)
        
        for year, year_pos in positions['years'].items():
            sway_x, sway_y = self.calculate_sway_offset(
                year, year_pos['x'], year_pos['y']
            )
            swayed_x = year_pos['x'] + sway_x
            swayed_y = year_pos['y'] + sway_y
            
            n_points = 25
            branch_x = np.linspace(year_pos['center_x'], swayed_x, n_points)
            branch_y = np.linspace(year_pos['center_y'], swayed_y, n_points)
            
            for i in range(len(branch_x)):
                t = i / (len(branch_x) - 1)
                dx = swayed_x - year_pos['center_x']
                dy = swayed_y - year_pos['center_y']
                perp_x = -dy
                perp_y = dx
                norm = np.sqrt(perp_x**2 + perp_y**2) + 1e-6
                
                curve_amount = 0.4 * np.sin(np.pi * t) * year_pos['radius'] * 0.3
                branch_x[i] += curve_amount * perp_x / norm
                branch_y[i] += curve_amount * perp_y / norm
            
            self.draw_tapered_branch(branch_x, branch_y, 8, 3,
                                    self.colors['year_branch'], 0.8)
            
            if year in positions['typhoons']:
                for typhoon_pos in positions['typhoons'][year]:
                    typhoon_sway_x = sway_x * 1.8
                    typhoon_sway_y = sway_y * 1.8
                    final_x = typhoon_pos['x'] + typhoon_sway_x
                    final_y = typhoon_pos['y'] + typhoon_sway_y
                    
                    n_fine = 15
                    fine_x = np.linspace(swayed_x, final_x, n_fine)
                    fine_y = np.linspace(swayed_y, final_y, n_fine)
                    
                    for i in range(len(fine_x)):
                        t = i / (len(fine_x) - 1)
                        wobble = 0.15 * np.sin(self.time * 2.5 + typhoon_pos['x'] * 7) * t
                        fine_x[i] += wobble * 0.7
                        fine_y[i] += wobble * 0.4
                    
                    self.draw_tapered_branch(fine_x, fine_y, 3, 0.8,
                                            self.colors['month_branch'], 0.75)
                    
                    typhoon = typhoon_pos['typhoon']
                    color = (self.colors['prediction'] if typhoon['is_prediction']
                            else self.colors['actual'])
                    
                    seed_wobble_x = 0.08 * np.sin(self.time * 3 + final_x * 10)
                    seed_wobble_y = 0.05 * np.cos(self.time * 3.5 + final_y * 10)
                    seed_x = final_x + seed_wobble_x
                    seed_y = final_y + seed_wobble_y
                    
                    seed_circle = Circle((seed_x, seed_y), typhoon_pos['size']/1200,
                                        color=color, alpha=0.85, zorder=3,
                                        edgecolor='white', linewidth=0.5)
                    self.ax.add_patch(seed_circle)
                    
                    self.draw_swaying_fluff(seed_x, seed_y,
                                          typhoon_pos['size']/1200, color)
    
    def draw_swaying_fluff(self, x, y, radius, color):
        """绘制摇曳的种子绒毛"""
        fluff_count = 10
        for i in range(fluff_count):
            base_angle = 2 * np.pi * i / fluff_count
            angle_wobble = 0.25 * np.sin(self.time * 2.8 + i * 0.5)
            angle = base_angle + angle_wobble
            fluff_length = radius * 2.5
            
            start_x = x + radius * 0.85 * np.cos(angle)
            start_y = y + radius * 0.85 * np.sin(angle)
            end_x = x + fluff_length * np.cos(angle)
            end_y = y + fluff_length * np.sin(angle)
            
            self.ax.plot([start_x, end_x], [start_y, end_y],
                        color=color, linewidth=0.6, alpha=0.5, zorder=2)
    
    def on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if event.inaxes == self.ax and event.xdata is not None:
            self.mouse_x = event.xdata
            self.mouse_y = event.ydata
    
    def create_interactive_animation(self):
        """创建完整的交互式动画"""
        self.setup_figure_with_layout()
        
        self.draw_header_section()
        self.draw_text_section()
        self.draw_scale_section()
        self.draw_legend_section()
        
        positions = self.calculate_dandelion_from_bottom_left()
        
        for year in positions['years'].keys():
            self.branch_velocities[year] = {
                'phase': np.random.uniform(0, 2*np.pi),
                'amplitude': np.random.uniform(0.12, 0.28),
                'frequency': np.random.uniform(0.7, 1.3)
            }
        
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        def animate(frame):
            self.ax.clear()
            self.ax.set_xlim(-2, 12)
            self.ax.set_ylim(-2, 12)
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            self.ax.set_facecolor(self.colors['background'])
            
            self.time = frame * 0.04
            self.draw_swaying_dandelion(positions)
            return []
        
        anim = animation.FuncAnimation(
            self.fig, animate, frames=np.arange(0, 2000),
            interval=50, blit=False, repeat=True
        )
        return anim
    
    def classify_typhoon(self, wind_speed):
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
    
    def generate_simulated_data(self, year):
        """生成模拟台风数据"""
        historical_names = [
            'Maliksi', 'Prapiroon', 'Yagi', 'Trami', 'Kong-rey', 'Yinxing',
            'Toraji', 'Man-yi', 'Usagi', 'Bebinca', 'Pulasan', 'Wutip'
        ]
        
        month_distribution = {
            1: 0.02, 2: 0.02, 3: 0.03, 4: 0.05, 5: 0.08, 6: 0.12,
            7: 0.18, 8: 0.22, 9: 0.15, 10: 0.08, 11: 0.03, 12: 0.02
        }
        
        typhoons = []
        num_typhoons = np.random.randint(5, 9)
        
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
    
    def collect_all_data(self, start_year=2014, end_year=2024):
        """收集所有年份的数据"""
        all_data = []
        
        for year in range(start_year, end_year + 1):
            year_data = self.generate_simulated_data(year)
            all_data.extend(year_data)
        
        self.typhoon_data = all_data
        return all_data

def main():
    viz = TyphoonDandelionViz()
    viz.collect_all_data(start_year=2014, end_year=2024)
    
    # 使用便捷方法配置文字样式
    viz.set_text_style(
        fontsize_multiplier=10,
        padding=1.0,
        line_spacing=2.0,
        background_alpha=0.0,
        show_border=False,
        margin_left_px=0,
        margin_right_px=0,
        max_width_chars=80  # 或者设为None让它自动计算
    )

        # 调整布局间距
    viz.layout_config['hspace'] = 0.3  # 增大垂直间距
    viz.layout_config['text_rows'] = (3, 4)  # 调整文字区域位置
    
    anim = viz.create_interactive_animation()
    plt.show()

if __name__ == "__main__":
    main()

