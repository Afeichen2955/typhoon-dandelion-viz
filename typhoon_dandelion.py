#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyBboxPatch
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
            'line_spacing': 1,
            'padding': 1.2,
            'background_alpha': 0.0,
            'show_border': False,
            'border_width': 1.5,
            'border_color': None,
            'border_style': 'round',
            'margin_left_px': 5,
            'margin_right_px': 5,
            'max_width_chars': 80  
        }

        # 布局配置
        self.layout_config = {
            'header_rows': (0, 2),
            'text_rows': (3, 5),
            'main_rows': (5, 17),
            'footer_rows': (17, 22),
            'hspace': 0.4,
            'wspace': 0.3
        }

        # 动画状态
        self.mouse_x = 0
        self.mouse_y = 0
        self.branch_velocities = {}
        self.time = 0
        
        # 生命周期状态
        self.lifecycle_state = 'growing'
        self.lifecycle_time = 0
        self.growth_progress = 0
        self.fade_progress = 0
        self.blowing_elapsed = 0
        
        # 时间配置
        self.regrow_duration = 4.0
        self.stable_duration = 3.0
        self.wind_duration = 3.0
        self.fade_delay = 2.0  # 【修改1】从1.0改为2.0，种子被吹走2秒后枝干才开始渐隐
        self.fade_duration = 2.0
        
        # 风吹效果状态
        self.wind_active = False
        self.wind_start_time = 0
        
        # 种子和细枝状态
        self.seed_positions = {}
        self.fine_branch_positions = {}
        
        # 点击信息框状态
        self.selected_typhoon = None
        self.info_box_visible = False
        self.info_box_x = 0
        self.info_box_y = 0
        
        # 固定宽高比
        self.aspect_ratio = 1.414
    
    def get_optimal_figure_size(self):
        """根据屏幕尺寸计算最佳图像尺寸，以高度为基准保持固定宽高比"""
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            usable_width = screen_width * 0.75
            usable_height = screen_height * 0.85
            
            height_based_height = usable_height / 96
            height_based_width = height_based_height / self.aspect_ratio
            
            if height_based_width <= usable_width / 96:
                fig_width = height_based_height
                fig_height = height_based_height
                fit_mode = "高度适配"
            else:
                width_based_width = usable_width / 96
                width_based_height = width_based_width * self.aspect_ratio
                fig_width = width_based_width
                fig_height = width_based_height
                fit_mode = "宽度适配"
            
            # 限制最大和最小尺寸
            fig_height = max(8, min(fig_height, 22))
            fig_width = fig_height / self.aspect_ratio
            
            # 【新增】缩小10%高度，并按比例调整宽度
            fig_height = fig_height * 0.9
            fig_width = fig_height / self.aspect_ratio
            
            print(f"屏幕尺寸: {screen_width}x{screen_height}px")
            print(f"可用空间: {usable_width:.0f}x{usable_height:.0f}px")
            print(f"图像尺寸: {fig_width:.1f}x{fig_height:.1f}英寸 ({fit_mode}, 缩小10%)")
            print(f"宽高比: {fig_height/fig_width:.3f}")
            
            if fig_height < 10:
                dpi = 120
            elif fig_height < 16:
                dpi = 100
            else:
                dpi = 80
                
            return fig_width, fig_height, dpi
            
        except Exception as e:
            print(f"无法获取屏幕信息，使用默认尺寸: {e}")
            # 默认尺寸也缩小10%
            return 10 * 0.9, 14.14 * 0.9, 100
    
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
        """绘制文字内容区域"""
        text_content = """Despite the destruction brought by typhoons, this visualization displays the natural cycle and patterns of tropical cyclone formation in the Western Pacific. Like dandelion seeds drifting in the wind, the distribution of typhoon data across the temporal dimension presents unique regularity. Each 'seed' represents a typhoon, with its size reflecting storm intensity, and colors distinguishing between historical data and forecast data."""
        
        text_fontsize = self.text_config['fontsize_multiplier'] * self.font_scale

        if self.text_config.get('max_width_chars'):
            max_chars = self.text_config['max_width_chars']
        else:
            fig_width_pixels = self.fig.get_figwidth() * self.fig.dpi
            margin_total = self.text_config['margin_left_px'] + self.text_config['margin_right_px']
            usable_width = fig_width_pixels * 0.9 - margin_total
            char_width = text_fontsize * 0.55 * self.fig.dpi / 72
            max_chars = int(usable_width / char_width)

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
            wrapped_text,
            fontsize=text_fontsize,
            color=self.colors['text'],
            ha='center',
            va='center',
            bbox=bbox_props,
            linespacing=line_spacing,
            transform=self.ax_text.transAxes,
            family='sans-serif',
            weight='normal',
            multialignment='center'
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
            ('TD', 40, '<63 km/h'),
            ('TS', 70, '63-87 km/h'),
            ('STS', 110, '88-117 km/h'),
            ('TY', 160, '118-149 km/h'),
            ('STY', 220, '150-184 km/h'),
            ('Super TY', 290, '≥185 km/h')
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

        stem_length = 50
        stem_x = np.linspace(0, 6, stem_length)
        stem_y = np.linspace(0, 6, stem_length)
        
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
        center_x, center_y = 6, 6
        
        typhoon_counts = [len(years_data[year]) for year in years]
        min_count = min(typhoon_counts)
        max_count = max(typhoon_counts)
        count_range = max_count - min_count if max_count > min_count else 1
        
        for i, year in enumerate(years):
            base_angle = -2 * np.pi * i / num_years
            angle_variation = np.random.uniform(-0.2, 0.2)
            angle = base_angle + angle_variation
            
            year_typhoon_count = len(years_data[year])
            normalized_count = 0.5 + 0.5 * (year_typhoon_count - min_count) / count_range
            
            spiral_growth = 0.3 * (i / num_years)
            radius = (2.5 + spiral_growth) * normalized_count + np.random.uniform(0, 0.4)
            
            year_x = center_x + radius * np.cos(angle)
            year_y = center_y + radius * np.sin(angle)
            
            positions['years'][year] = {
                'x': year_x, 'y': year_y, 
                'angle': angle, 'radius': radius,
                'center_x': center_x, 'center_y': center_y,
                'typhoon_count': year_typhoon_count
            }
            
            year_typhoons = years_data[year]
            positions['typhoons'][year] = []
            
            cluster_count = min(3, len(year_typhoons))
            
            for cluster_idx in range(cluster_count):
                cluster_angle = angle + (cluster_idx - cluster_count/2) * 0.4
                cluster_radius = radius + 1.0 + np.random.uniform(0, 0.6)
                
                cluster_x = center_x + cluster_radius * np.cos(cluster_angle)
                cluster_y = center_y + cluster_radius * np.sin(cluster_angle)
                
                typhoons_in_cluster = year_typhoons[cluster_idx::cluster_count]
                
                for j, typhoon in enumerate(typhoons_in_cluster):
                    offset_angle = np.random.uniform(0, 2*np.pi)
                    offset_radius = np.random.uniform(0.1, 0.4)
                    
                    typhoon_x = cluster_x + offset_radius * np.cos(offset_angle)
                    typhoon_y = cluster_y + offset_radius * np.sin(offset_angle)
                    
                    seed_size = self.calculate_seed_size(typhoon['max_wind_speed'])
                    
                    seed_id = f"{year}_{cluster_idx}_{j}"
                    
                    pos = {
                        'x': typhoon_x,
                        'y': typhoon_y,
                        'original_x': typhoon_x,
                        'original_y': typhoon_y,
                        'size': seed_size,
                        'typhoon': typhoon,
                        'cluster_id': cluster_idx,
                        'seed_id': seed_id,
                        'year': year
                    }
                    positions['typhoons'][year].append(pos)
                    
                    self.seed_positions[seed_id] = {
                        'original_x': typhoon_x,
                        'original_y': typhoon_y,
                        'current_x': typhoon_x,
                        'current_y': typhoon_y,
                        'velocity_x': 0,
                        'velocity_y': 0,
                        'alpha': 0.85,
                        'year': year,
                        'typhoon': typhoon,  # 存储台风信息供点击使用
                        'size': seed_size
                    }
                    
                    branch_id = f"branch_{seed_id}"
                    self.fine_branch_positions[branch_id] = {
                        'offset_x': typhoon_x - year_x,
                        'offset_y': typhoon_y - year_y,
                        'alpha': 0.75,
                        'year': year
                    }
        
        return positions
    
    def calculate_seed_size(self, wind_speed):
        """根据风速计算种子大小"""
        if wind_speed < 63:
            return 40
        elif wind_speed < 88:
            return 70
        elif wind_speed < 118:
            return 110
        elif wind_speed < 150:
            return 160
        elif wind_speed < 185:
            return 220
        else:
            return 290

    def draw_tapered_branch_natural(self, x_points, y_points, start_width, end_width, color, alpha=0.8):
        """绘制具有自然粗细变化的枝干"""
        n_segments = len(x_points) - 1
        
        for i in range(n_segments):
            t = i / n_segments
            
            linear_factor = (1 - t)
            sine_variation = 1.0 + 0.15 * np.sin(t * np.pi * 8)
            exp_factor = np.exp(-t * 1.5)
            random_noise = 1.0 + np.random.uniform(-0.05, 0.05)
            
            width = (start_width * linear_factor * exp_factor * sine_variation * random_noise + 
                    end_width * t)
            
            width = max(width, end_width * 0.5)
            
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
    
    def update_lifecycle(self):
        """更新生命周期状态"""
        if self.lifecycle_state == 'growing':
            self.growth_progress = min(1.0, self.lifecycle_time / self.regrow_duration)
            if self.growth_progress >= 1.0:
                self.lifecycle_state = 'stable'
                self.lifecycle_time = 0
                
        elif self.lifecycle_state == 'stable':
            if self.lifecycle_time >= self.stable_duration:
                self.lifecycle_state = 'blowing'
                self.wind_active = True
                self.wind_start_time = self.time
                self.lifecycle_time = 0
                self.blowing_elapsed = 0
                
        elif self.lifecycle_state == 'blowing':
            self.blowing_elapsed = self.lifecycle_time
            
            if self.blowing_elapsed >= self.fade_delay:
                fade_time = self.blowing_elapsed - self.fade_delay
                self.fade_progress = min(1.0, fade_time / self.fade_duration)
            else:
                self.fade_progress = 0
            
            if self.lifecycle_time >= self.wind_duration:
                self.lifecycle_state = 'growing'
                self.wind_active = False
                self.lifecycle_time = 0
                self.growth_progress = 0
                self.fade_progress = 0
                self.reset_positions()
    
    def reset_positions(self):
        """重置所有位置到初始状态"""
        for seed_id, seed_state in self.seed_positions.items():
            seed_state['current_x'] = seed_state['original_x']
            seed_state['current_y'] = seed_state['original_y']
            seed_state['velocity_x'] = 0
            seed_state['velocity_y'] = 0
            seed_state['alpha'] = 0.85
            
        for branch_id, branch_state in self.fine_branch_positions.items():
            branch_state['alpha'] = 0.75
    
    def update_wind_blowing(self):
        """更新风吹效果 - 橙色枝干和种子一起飞散"""
        if not self.wind_active:
            return
            
        wind_progress = self.blowing_elapsed / self.wind_duration
        wind_strength = np.sin(wind_progress * np.pi * 0.5) ** 0.5
        
        for seed_id, seed_state in self.seed_positions.items():
            base_accel_x = -12 * wind_strength
            base_accel_y = 3 * wind_strength
            
            random_x = np.random.uniform(-2, 1)
            random_y = np.random.uniform(-1, 2)
            
            seed_state['velocity_x'] += (base_accel_x + random_x) * 0.05
            seed_state['velocity_y'] += (base_accel_y + random_y) * 0.05
            
            seed_state['velocity_x'] *= 0.98
            seed_state['velocity_y'] *= 0.98
            
            seed_state['current_x'] += seed_state['velocity_x'] * 0.05
            seed_state['current_y'] += seed_state['velocity_y'] * 0.05
            
            if seed_state['current_x'] < -5 or seed_state['current_x'] > 20:
                seed_state['alpha'] = max(0, seed_state['alpha'] - 0.05)
            else:
                seed_state['alpha'] = 0.85 * (1 - wind_progress * 0.8)
        
        for branch_id, branch_state in self.fine_branch_positions.items():
            seed_id = branch_id.replace('branch_', '')
            if seed_id in self.seed_positions:
                seed_state = self.seed_positions[seed_id]
                branch_state['alpha'] = seed_state['alpha']
    
    def on_click(self, event):
        """【修改2】点击事件处理"""
        if event.inaxes != self.ax:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        click_x, click_y = event.xdata, event.ydata
        
        # 检查是否点击了某个种子
        for seed_id, seed_state in self.seed_positions.items():
            seed_x = seed_state['current_x']
            seed_y = seed_state['current_y']
            seed_radius = seed_state['size'] / 1200
            
            # 计算点击位置与种子中心的距离
            distance = np.sqrt((click_x - seed_x)**2 + (click_y - seed_y)**2)
            
            # 如果点击在种子范围内
            if distance <= seed_radius * 1.5:  # 稍微放大点击区域
                # 显示信息框
                self.selected_typhoon = seed_state['typhoon']
                self.info_box_visible = True
                self.info_box_x = seed_x
                self.info_box_y = seed_y
                return
        
        # 如果没有点击任何种子，隐藏信息框
        self.info_box_visible = False
        self.selected_typhoon = None
    
    def draw_info_box(self):
        """绘制台风信息框"""
        if not self.info_box_visible or self.selected_typhoon is None:
            return
        
        typhoon = self.selected_typhoon
        
        # 构建信息文本
        info_lines = [
            f"Name: {typhoon['name_en']}",
            f"ID: {typhoon['id']}",
            f"Date: {typhoon['formation_date']}",
            f"Wind: {typhoon['max_wind_speed']} km/h",
            f"Pressure: {typhoon['min_pressure']} hPa",
            f"Category: {typhoon['category']}"
        ]
        info_text = '\n'.join(info_lines)
        
        # 计算信息框位置
        box_x = self.info_box_x + 0.5
        box_y = self.info_box_y + 0.5
        
        # 增大信息框尺寸
        box_width = 3.5
        box_height = 2.0
        
        # 确保信息框不超出边界
        if box_x > 7:
            box_x = self.info_box_x - 3.8
        if box_y > 8.5:
            box_y = self.info_box_y - 2.3
        
        # 绘制背景框
        fancy_box = FancyBboxPatch(
            (box_x - 0.15, box_y - 0.15),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=self.colors['text'],
            linewidth=0.8,
            alpha=0.6,
            zorder=10
        )
        self.ax.add_patch(fancy_box)
        
        # 绘制信息文字（左对齐，文本块居中）
        # 文本块的x坐标设置为框中心偏左一点，使左对齐的文本块整体居中
        text_x = box_x + box_width/2 - 1.8  # 向左偏移0.8，让文本块居中
        text_y = box_y + box_height/2 - 0.15  # 微调y位置
        
        self.ax.text(
            text_x, text_y,
            info_text,
            fontsize=5,
            color=self.colors['text'],
            ha='left',      # 改为左对齐
            va='center',
            zorder=11,
            family='monospace',
            linespacing=1.5
        )
 
    def draw_swaying_dandelion(self, positions):
        """绘制摇曳的蒲公英主体"""
        stem_x = positions['stem']['x']
        stem_y = positions['stem']['y']
        
        if self.lifecycle_state == 'growing':
            base_alpha = 1.0
        elif self.lifecycle_state == 'blowing':
            base_alpha = 1.0 - self.fade_progress
        else:
            base_alpha = 1.0
        
        if base_alpha > 0.01:
            if self.lifecycle_state == 'growing':
                stem_progress = min(1.0, self.growth_progress / 0.3)
                visible_length = int(len(stem_x) * stem_progress)
                if visible_length > 1:
                    self.draw_tapered_branch_natural(
                        stem_x[:visible_length], 
                        stem_y[:visible_length], 
                        14, 6,
                        self.colors['stem'], 
                        0.9 * base_alpha
                    )
            else:
                self.draw_tapered_branch_natural(
                    stem_x, stem_y, 14, 6,
                    self.colors['stem'], 
                    0.9 * base_alpha
                )
            
            center_x, center_y = stem_x[-1], stem_y[-1]
            if self.lifecycle_state != 'growing' or self.growth_progress > 0.25:
                center_circle = Circle((center_x, center_y), 0.25,
                                      color=self.colors['stem'], 
                                      alpha=0.9 * base_alpha, 
                                      zorder=2)
                self.ax.add_patch(center_circle)
        
        for year, year_pos in positions['years'].items():
            if base_alpha <= 0.01:
                continue
            
            if self.lifecycle_state == 'growing':
                if self.growth_progress < 0.3:
                    continue
                year_branch_progress = min(1.0, (self.growth_progress - 0.3) / 0.3)
            else:
                year_branch_progress = 1.0
            
            sway_x, sway_y = self.calculate_sway_offset(
                year, year_pos['x'], year_pos['y']
            )
            swayed_x = year_pos['x'] + sway_x
            swayed_y = year_pos['y'] + sway_y
            
            n_points = 25
            branch_x = np.linspace(year_pos['center_x'], swayed_x, n_points)
            branch_y = np.linspace(year_pos['center_y'], swayed_y, n_points)
            
            if self.lifecycle_state == 'growing':
                visible_points = int(n_points * year_branch_progress)
                if visible_points < 2:
                    continue
                branch_x = branch_x[:visible_points]
                branch_y = branch_y[:visible_points]
                swayed_x = branch_x[-1]
                swayed_y = branch_y[-1]
            
            for i in range(len(branch_x)):
                t = i / max(1, len(branch_x) - 1)
                dx = swayed_x - year_pos['center_x']
                dy = swayed_y - year_pos['center_y']
                perp_x = -dy
                perp_y = dx
                norm = np.sqrt(perp_x**2 + perp_y**2) + 1e-6
                
                curve_amount = 0.4 * np.sin(np.pi * t) * year_pos['radius'] * 0.3
                branch_x[i] += curve_amount * perp_x / norm
                branch_y[i] += curve_amount * perp_y / norm
            
            self.draw_tapered_branch_natural(
                branch_x, branch_y, 8, 2,
                self.colors['year_branch'], 
                0.8 * base_alpha
            )
            
            if base_alpha > 0.5 and (self.lifecycle_state != 'growing' or year_branch_progress > 0.8):
                label_offset = 0.4
                label_x = swayed_x + label_offset * np.cos(year_pos['angle'])
                label_y = swayed_y + label_offset * np.sin(year_pos['angle'])
                
                typhoon_count = year_pos['typhoon_count']
                label_text = f"{year}\n({typhoon_count})"
                self.ax.text(
                    label_x, label_y,
                    label_text,
                    fontsize=5,
                    color=self.colors['text'],
                    ha='center',
                    va='center',
                    alpha=base_alpha * 0.8,
                    weight='normal',
                    zorder=4
                )
            
            if year in positions['typhoons']:
                for typhoon_pos in positions['typhoons'][year]:
                    seed_id = typhoon_pos['seed_id']
                    branch_id = f"branch_{seed_id}"
                    
                    if self.lifecycle_state == 'growing':
                        if self.growth_progress < 0.6:
                            continue
                        fine_branch_progress = min(1.0, (self.growth_progress - 0.6) / 0.25)
                    else:
                        fine_branch_progress = 1.0
                    
                    if branch_id in self.fine_branch_positions and seed_id in self.seed_positions:
                        branch_state = self.fine_branch_positions[branch_id]
                        seed_state = self.seed_positions[seed_id]
                        
                        if self.lifecycle_state == 'blowing':
                            final_x = seed_state['current_x']
                            final_y = seed_state['current_y']
                            branch_alpha = branch_state['alpha']
                            seed_alpha = seed_state['alpha']
                        else:
                            final_x = swayed_x + branch_state['offset_x']
                            final_y = swayed_y + branch_state['offset_y']
                            
                            if self.lifecycle_state == 'growing':
                                branch_alpha = branch_state['alpha'] * fine_branch_progress
                                seed_alpha = seed_state['alpha'] * fine_branch_progress
                            else:
                                branch_alpha = branch_state['alpha']
                                seed_alpha = seed_state['alpha']
                        
                        if branch_alpha > 0.01:
                            n_fine = 15
                            fine_x = np.linspace(swayed_x, final_x, n_fine)
                            fine_y = np.linspace(swayed_y, final_y, n_fine)
                            
                            if self.lifecycle_state == 'growing':
                                visible_fine = int(n_fine * fine_branch_progress)
                                if visible_fine < 2:
                                    continue
                                fine_x = fine_x[:visible_fine]
                                fine_y = fine_y[:visible_fine]
                            
                            for i in range(len(fine_x)):
                                t = i / max(1, len(fine_x) - 1)
                                wobble = 0.15 * np.sin(self.time * 2.5 + final_x * 7) * t
                                fine_x[i] += wobble * 0.7
                                fine_y[i] += wobble * 0.4
                            
                            self.draw_tapered_branch_natural(
                                fine_x, fine_y, 3, 0.5,
                                self.colors['month_branch'], 
                                branch_alpha
                            )
                        
                        if self.lifecycle_state == 'growing':
                            if self.growth_progress < 0.85:
                                continue
                            seed_display_alpha = seed_alpha * min(1.0, (self.growth_progress - 0.85) / 0.15)
                        else:
                            seed_display_alpha = seed_alpha
                        
                        if seed_display_alpha > 0.01:
                            typhoon = typhoon_pos['typhoon']
                            color = (self.colors['prediction'] if typhoon['is_prediction']
                                    else self.colors['actual'])
                            
                            seed_wobble_x = 0.08 * np.sin(self.time * 3 + final_x * 10)
                            seed_wobble_y = 0.05 * np.cos(self.time * 3.5 + final_y * 10)
                            
                            seed_x = final_x + seed_wobble_x
                            seed_y = final_y + seed_wobble_y
                            
                            # 更新种子的当前位置（用于点击检测）
                            seed_state['current_x'] = seed_x if self.lifecycle_state != 'blowing' else seed_state['current_x']
                            seed_state['current_y'] = seed_y if self.lifecycle_state != 'blowing' else seed_state['current_y']
                            
                            seed_circle = Circle(
                                (seed_x, seed_y), 
                                typhoon_pos['size']/1200,
                                color=color, 
                                alpha=seed_display_alpha, 
                                zorder=3,
                                edgecolor='white', 
                                linewidth=0.5
                            )
                            self.ax.add_patch(seed_circle)
                            
                            self.draw_swaying_fluff(
                                seed_x, seed_y,
                                typhoon_pos['size']/1200, 
                                color,
                                seed_display_alpha
                            )
        
        # 绘制信息框（在最上层）
        self.draw_info_box()
    
    def draw_swaying_fluff(self, x, y, radius, color, alpha=0.85):
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
                        color=color, linewidth=0.6, alpha=alpha*0.6, zorder=2)
    
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
        
        # 连接事件
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)  # 添加点击事件
        
        self.lifecycle_state = 'growing'
        self.lifecycle_time = 0
        self.growth_progress = 0
        
        def animate(frame):
            self.ax.clear()
            self.ax.set_xlim(-2, 12)
            self.ax.set_ylim(-2, 12)
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            self.ax.set_facecolor(self.colors['background'])
            
            dt = 0.04
            self.time += dt
            self.lifecycle_time += dt
            
            self.update_lifecycle()
            
            if self.wind_active:
                self.update_wind_blowing()
            
            self.draw_swaying_dandelion(positions)
            
            return []
        
        anim = animation.FuncAnimation(
            self.fig, animate, frames=np.arange(0, 10000),
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
    
    viz.set_text_style(
        fontsize_multiplier=8,
        padding=0.5,
        line_spacing=1.5,
        background_alpha=0.0,
        show_border=False,
        margin_left_px=0,
        margin_right_px=0,
        max_width_chars=None
    )

    viz.layout_config['text_rows'] = (3, 5)
    
    anim = viz.create_interactive_animation()
    plt.show()

if __name__ == "__main__":
    main()