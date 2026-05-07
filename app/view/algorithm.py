import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.cm import ScalarMappable
from scipy import integrate

# 设置绘图风格
plt.rcParams['font.family'] = 'SimHei'  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class WorkingFace:
    """
    工作面数据结构
    """
    def __init__(self, face_id, x_range, y_range, H, m, alpha, q, tan_beta,otherParameters):
        self.id = face_id # 工作面编号
        self.x_start, self.x_end = sorted(x_range)  # 确保 start < end
        self.y_start, self.y_end = sorted(y_range)
        self.H = H # 采深
        self.m = m  # 采厚
        self.alpha_degree = alpha
        self.alpha = np.radians(alpha) # 煤层倾角 (转换为弧度)
        self.q = q # 下沉系数
        self.tan_beta = tan_beta # 影响范围
        
        self.songSan = otherParameters[0] # 松散层厚度
        self.baseThickness = otherParameters[1] # 基岩厚度
        self.baseYieldStrength = otherParameters[2] # 基岩抗压强度
        self.frictionAngle = otherParameters[3] # 关键层内摩擦角
        self.keyLayerPosition = otherParameters[4] # 关键层位置
        self.horizontalMovement = otherParameters[5] # 水平移动系数
        
        # 计算主要影响半径
        self.r0 = H / tan_beta
        # 计算最大下沉系数部分
        self.W_max = m * q * np.cos(self.alpha)

    def get_geometry(self):
        """返回用于绘图的矩形参数: (x, y, width, height)"""
        return (self.x_start, self.y_start, 
                self.x_end - self.x_start, 
                self.y_end - self.y_start)

class PIMSolver:
    """
    概率积分法核心计算引擎 (数值积分版)
    """

    def __init__(self, time_factor_c=0.2):
        self.faces = []
        # 时间参数c
        self.c = time_factor_c 

    def add_face(self, face: WorkingFace):
        self.faces.append(face)

    def _integrand(self, y_prime, x_prime, x, y, r0):
        """高斯分布密度函数核心"""
        r_squared = (x - x_prime)**2 + (y - y_prime)**2
        term = (1 / (2 * np.pi * (r0**2))) * np.exp(-r_squared / (2 * (r0**2)))
        return term

    def calculate_point_subsidence(self, x, y):
        """计算单点 (x,y) 的最终下沉值 W_final"""
        total_subsidence = 0.0
        for face in self.faces:
            # 使用二重数值积分
            integral_val, error = integrate.dblquad(
                func=self._integrand,
                a=face.x_start, b=face.x_end,
                gfun=lambda x: face.y_start,
                hfun=lambda x: face.y_end,
                args=(x, y, face.r0)
            )
            total_subsidence += face.W_max * integral_val
        return total_subsidence

    def calculate_stable_time(self, W_final, V_critical=0.001):
        """计算稳定时间 Ts"""
        if abs(W_final) < 1e-4: return 0.0
        try:
            val = V_critical / (W_final * self.c)
            if val >= 1: return 0.0
            return -np.log(val) / self.c
        except:
            return 0.0

    # 计算测线上的下沉分布
    def calculate_line_subsidence(self, start_pos, end_pos, num_points=100):
        """
        专门用于线程调用的纯计算方法：计算测线上的下沉分布
        返回: (distances, w_finals)
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        xs = np.linspace(x1, x2, num_points)
        ys = np.linspace(y1, y2, num_points)
        distances = np.sqrt((xs - x1)**2 + (ys - y1)**2)
        
        w_finals = np.zeros(num_points)
        # 这里是耗时循环，放在线程里跑
        for i in range(num_points):
            w_finals[i] = self.calculate_point_subsidence(xs[i], ys[i])
            
        return distances, w_finals
    
class SubsidenceVisualizer:
    """
    输出与可视化模块
    """
    def __init__(self, solver: PIMSolver):
        self.solver = solver
    
    def plot_profile_time_evolution(self, start_pos, end_pos, times_list, num_points=100,pre_calculated_data=None):
        """
        绘制观测线上的时空演化曲线 (下沉 + 速度)，并标注极值和稳定时间
        :param pre_calculated_data: (distances, w_finals) 元组，如果提供则跳过计算
        """
        # 1. 获取数据 (如果线程算好了就直接用)
        if pre_calculated_data:
            distances, w_finals = pre_calculated_data
        else:
            # 如果没传数据，才自己算 (兼容旧代码，但会卡界面)
            print("警告：正在主线程进行耗时计算...")
            distances, w_finals = self.solver.calculate_line_subsidence(start_pos, end_pos, num_points)

        # --- 新增步骤：计算关键指标 ---
        # 找到整条测线上绝对值最大的下沉点
        max_idx = np.argmax(np.abs(w_finals))
        max_w_val = w_finals[max_idx]   # 最大下沉值
        max_w_dist = distances[max_idx] # 最大下沉点的位置
        
        # 计算该点的理论稳定时间
        t_stable = self.solver.calculate_stable_time(max_w_val)
        # ---------------------------

        # 3. 创建画布
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        markers = ['s', 'o', '^', 'v', 'D', '<', '>', 'p', '*'] 
        colors = plt.cm.jet(np.linspace(0, 0.9, len(times_list)))
        c = self.solver.c 

        # 4. 循环绘制时间曲线
        for idx, t in enumerate(times_list):
            if t <= 0:
                w_t = np.zeros_like(w_finals)
                v_t = np.zeros_like(w_finals)
            else:
                w_t = w_finals * (1 - np.exp(-c * t))
                v_t = w_finals * c * np.exp(-c * t)
            
            marker = markers[idx % len(markers)]
            color = colors[idx]
            label_str = f'{t}个月'
            
            ax1.plot(distances, w_t, color=color, marker=marker, markevery=int(num_points/15),
                     label=label_str, linewidth=1.5, markersize=5)
            
            ax2.plot(distances, v_t, color=color, marker=marker, markevery=int(num_points/15),
                     linewidth=1.5, markersize=5)

        # --- 新增绘图：标注信息 ---
        # (1) 绘制最终下沉虚线作为参考
        ax1.plot(distances, w_finals, 'k--', alpha=0.6, label='最终下沉(t→∞)')
        
        # (2) 标注最大下沉值 (红色箭头)
        # 自动调整文本位置，防止遮挡
        text_y_offset = max_w_val * 0.15 if max_w_val != 0 else 0.1
        ax1.annotate(f'最终最大下沉: {max_w_val:.3f}m', 
                     xy=(max_w_dist, max_w_val), 
                     xytext=(max_w_dist, max_w_val - text_y_offset),
                     arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8),
                     ha='center', fontsize=10, fontweight='bold', color='red',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

        # (3) 标注稳定时间 (左下角文本框)
        info_text = (f"【关键参数统计】\n"
                     f"最大下沉点位置: X={max_w_dist:.1f}m\n"
                     f"理论稳定时间 ($T_s$): {t_stable:.1f} 个月\n"
                     f"(判定标准: V < 0.001 m/月)")
        # transform=ax1.transAxes 表示使用相对坐标(0-1)
        ax1.text(0.02, 0.05, info_text, transform=ax1.transAxes, 
                 fontsize=10, verticalalignment='bottom',
                 bbox=dict(boxstyle='round', facecolor='#ffffcc', alpha=0.8, edgecolor='orange'))
        # ------------------------

        # 5. 设置图表细节
        # ax1.set_title(f'主断面沉陷时空演化曲线 (c={c})')
        ax1.set_title(f'主断面沉陷时空演化曲线')
        ax1.set_ylabel('下沉量 (m)')
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend(loc='upper right', ncol=2, fontsize=9)
        ax1.invert_yaxis() 
        
        ax2.set_ylabel('下沉速度 (m/月)')
        ax2.set_xlabel('工作面走向长度 (m)')
        ax2.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        return fig
    
    def plot_2d_contour_and_gob(self, x_range, y_range, grid_density=50, independent_scale=False, pre_calculated_data=None):
        """
        :param x_range: (min, max) 绘图X范围
        :param y_range: (min, max) 绘图Y范围
        :param grid_density: 局部网格密度
        :param independent_scale: True(红心模式)/False(统一色标)
        :param pre_calculated_data: 
               如果使用线程计算，这里接收的应是列表: [(X, Y, Z_local, face, local_max), ...]
               如果为None，则在主线程实时计算(可能会卡顿)。
        """
        import itertools
        
        # --- 1. 初始化绘图环境 (PyQt 适配) ---
        fig = Figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f5f5f5') # 浅灰背景

        face_results = []
        global_max_w = 0.0

        # 用于煤柱计算的工作面列表
        faces_for_pillar_calc = []
        # --- 2. 数据获取 ---
        
        if pre_calculated_data is not None:
            # 模式A：使用线程算好的数据 
            # 要求 Worker 返回的数据结构必须是 list of tuples
            face_results = pre_calculated_data
            faces_for_pillar_calc = [item[3] for item in pre_calculated_data]
            
            # 计算全局最大值用于统一色标
            if not independent_scale:
                all_maxs = [item[4] for item in pre_calculated_data]
                if all_maxs:
                    global_max_w = max(all_maxs)
                
        else:
            # 模式B：实时计算 (原始逻辑，计算量大时会卡)
            # 遍历每个工作面，独立计算局部网格
            
            faces_for_pillar_calc = self.solver.faces
            
            for idx, face in enumerate(self.solver.faces):
                # 生成局部网格 (仅覆盖当前工作面范围)
                xs = np.linspace(face.x_start, face.x_end, grid_density)
                ys = np.linspace(face.y_start, face.y_end, grid_density)
                X, Y = np.meshgrid(xs, ys)
                Z_local = np.zeros_like(X)
                
                # 局部二重积分
                for i in range(len(ys)):
                    for j in range(len(xs)):
                        val, _ = integrate.dblquad(
                            func=self.solver._integrand,
                            a=face.x_start, b=face.x_end,
                            gfun=lambda x: face.y_start,
                            hfun=lambda x: face.y_end,
                            args=(xs[j], ys[i], face.r0)
                        )
                        Z_local[i, j] = face.W_max * val
                
                # 统计
                local_max = np.max(Z_local)
                if local_max > global_max_w: global_max_w = local_max
                
                face_results.append((X, Y, Z_local, face, local_max))

        # --- 3. 绘图循环 (独立绘制) ---
        cmap = plt.cm.jet 
        
        # 遍历结果列表，一个个画上去
        for X, Y, Z_local, face, local_max in face_results:
            
            # 判定色标策略
            if independent_scale:
                # 独立模式：以当前工作面最大值为上限 (红心模式)
                # 使用 levels 让 contourf 自动处理归一化
                cs = ax.contourf(X, Y, Z_local, levels=50, cmap=cmap, alpha=1.0)
            else:
                # 统一模式：使用全局最大值生成 levels (真实对比)
                if global_max_w < 1e-5: global_max_w = 1.0
                levels = np.linspace(0, global_max_w * 1.05, 50)
                cs = ax.contourf(X, Y, Z_local, levels=levels, cmap=cmap, alpha=1.0)
            
            # 绘制边框
            rect = patches.Rectangle((face.x_start, face.y_start), 
                                   face.x_end - face.x_start, 
                                   face.y_end - face.y_start, 
                                   linewidth=2, edgecolor='black', facecolor='none')
            ax.add_patch(rect)
            
            # 标签
            label_text = f"{face.id}"
            ax.text((face.x_start + face.x_end)/2, (face.y_start + face.y_end)/2, 
                    label_text, color='white', 
                    ha='center', va='center', fontweight='bold', fontsize=9, 
                    bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))

        # 4. Colorbar 设置
        if independent_scale:
            sm = ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('相对沉陷强度 (归一化)')
            fig.suptitle('采空区分布与地表沉陷等值线图')
        else:
            sm = ScalarMappable(cmap=cmap, norm=plt.Normalize(0, global_max_w))
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('地表沉陷值 W [m]')
            fig.suptitle('采空区分布与地表沉陷等值线图')

        # --- 5. 煤柱标注 (逻辑保持不变) ---
        pillar_threshold = 2000.0 
        for face_a, face_b in itertools.combinations(faces_for_pillar_calc, 2):
            # 计算几何中心
            ax_c, ay_c = (face_a.x_start + face_a.x_end)/2, (face_a.y_start + face_a.y_end)/2
            bx_c, by_c = (face_b.x_start + face_b.x_end)/2, (face_b.y_start + face_b.y_end)/2
            
            # 期望间距 vs 实际间距
            exp_dx = ((face_a.x_end - face_a.x_start) + (face_b.x_end - face_b.x_start)) / 2
            exp_dy = ((face_a.y_end - face_a.y_start) + (face_b.y_end - face_b.y_start)) / 2
            dx, dy = abs(ax_c - bx_c), abs(ay_c - by_c)
            
            px, py = None, None
            
            # 判定相邻关系
            if dy < exp_dy and 0 < (dx - exp_dx) < pillar_threshold:
                left = face_a if face_a.x_start < face_b.x_start else face_b
                right = face_b if face_a.x_start < face_b.x_start else face_a
                px, py = (left.x_end + right.x_start) / 2, (ay_c + by_c) / 2
            elif dx < exp_dx and 0 < (dy - exp_dy) < pillar_threshold:
                bottom = face_a if face_a.y_start < face_b.y_start else face_b
                top = face_b if face_a.y_start < face_b.y_start else face_a
                px, py = (ax_c + bx_c) / 2, (bottom.y_end + top.y_start) / 2
            
            # 如果检测到煤柱坐标，进行标注
            if px is not None:
                ax.annotate("煤柱", xy=(px, py), ha='center', va='center', fontsize=9, 
                            color='black', fontweight='bold', 
                            bbox=dict(boxstyle="round,pad=0.3", fc="#FFD700", alpha=0.9, ec="black"))

        # --- 收尾 ---
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.set_xlabel('X 坐标 (m)')
        ax.set_ylabel('Y 坐标 (m)')
        
        # 自动调整布局，防止标签被切
        fig.tight_layout()
        return fig