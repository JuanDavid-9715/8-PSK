"""
============================================
8-PSK Calculator Module
============================================
"""

import numpy as np
from math import sqrt, atan2, degrees, radians
from typing import Dict, List, Tuple, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100


class PSK8Calculator:
    
    CONVERTER_I = {
        (0, 0): -0.541, (0, 1): -1.307,
        (1, 0): +0.541, (1, 1): +1.307,
    }
    
    CONVERTER_Q = {
        (0, 1): -1.307, (0, 0): -0.541,
        (1, 1): +1.307, (1, 0): +0.541,
    }
    
    TRIBIT_DATA = {
        '000': {'i_out': -0.541, 'q_out': -1.307, 'phase': -112.5},
        '001': {'i_out': -1.307, 'q_out': -0.541, 'phase': -157.5},
        '010': {'i_out': +0.541, 'q_out': -1.307, 'phase': -67.5},
        '011': {'i_out': +1.307, 'q_out': -0.541, 'phase': -22.5},
        '100': {'i_out': -0.541, 'q_out': +1.307, 'phase': +112.5},
        '101': {'i_out': -1.307, 'q_out': +0.541, 'phase': +157.5},
        '110': {'i_out': +0.541, 'q_out': +1.307, 'phase': +67.5},
        '111': {'i_out': +1.307, 'q_out': +0.541, 'phase': +22.5},
    }
    
    COLORS = {
        '000': '#ff6b6b', '001': '#4ecdc4', '010': '#45b7d1', '011': '#f9ca24',
        '100': '#a55eea', '101': '#26de81', '110': '#fd79a8', '111': '#00cec9'
    }
    
    def get_converter_output(self, q: int, i: int, c: int) -> Tuple[float, float]:
        i_out = self.CONVERTER_I[(i, c)]
        q_out = self.CONVERTER_Q[(q, 1 - c)]
        return i_out, q_out
    
    def calculate_development(self, q: int, i: int, c: int) -> Dict[str, Any]:
        i_out, q_out = self.get_converter_output(q, i, c)
        magnitude = sqrt(i_out**2 + q_out**2)
        phase_deg = degrees(atan2(q_out, i_out))
        
        # Formatear números con signo para ecuaciones
        def fmt(n):
            return f"+{n}" if n >= 0 else str(n)
        
        # Formatear sin signo para coordenadas
        def fmt_coord(n):
            return f"+{n}" if n > 0 else str(n)
        
        tribit = f"{q}{i}{c}"
        
        return {
            'tribit': tribit,
            'q': q, 'i': i, 'c': c,
            'i_out': i_out,
            'q_out': q_out,
            'magnitude': round(magnitude, 2),
            'phase': round(phase_deg, 1),
            'color': self.COLORS[tribit],
            # PASO 1: Ecuación original
            'equation': f"S(t) = {fmt(i_out)}·sen(ωt) {fmt(q_out)}·cos(ωt)",
            # PASO 2: Coordenadas cartesianas (I, Q) con V
            'cartesian': f"({i_out}, {q_out})V",
            # PASO 3: Componentes polares (sen→0°, cos→90°)
            'polar_components': f"{i_out}∠0° {fmt_coord(q_out)}∠90°",
            # PASO 4: Forma rectangular/compleja
            'rectangular': f"{i_out} {fmt_coord(q_out)}j",
            # PASO 5: Resultado final polar
            'result': f"{round(magnitude, 2)}∠{round(phase_deg, 1)}°",
        }
    
    def get_all_developments(self) -> List[Dict[str, Any]]:
        developments = []
        for tribit in ['000', '001', '010', '011', '100', '101', '110', '111']:
            q, i, c = int(tribit[0]), int(tribit[1]), int(tribit[2])
            developments.append(self.calculate_development(q, i, c))
        return developments
    
    def get_converter_tables(self) -> Dict[str, List]:
        table_i = [{'i': i, 'c': c, 'output': out} for (i, c), out in sorted(self.CONVERTER_I.items())]
        table_q = [{'q': q, 'c_inv': c_inv, 'c': 1 - c_inv, 'output': out} for (q, c_inv), out in sorted(self.CONVERTER_Q.items())]
        return {'channel_i': table_i, 'channel_q': table_q}
    
    def get_table_data(self) -> List[Dict[str, Any]]:
        table = []
        for tribit in ['000', '001', '010', '011', '100', '101', '110', '111']:
            data = self.TRIBIT_DATA[tribit]
            table.append({
                'q': int(tribit[0]), 'i': int(tribit[1]), 'c': int(tribit[2]),
                'phase': data['phase'],
                'color': self.COLORS[tribit],
            })
        return table
    
    def generate_constellation_diagram(self) -> str:
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0a0a1a')
        ax.set_facecolor('#0a0a1a')
        
        ax.grid(True, alpha=0.2, color='#00ffff', linewidth=0.5)
        ax.axhline(y=0, color='#00ffff', linewidth=1, alpha=0.8)
        ax.axvline(x=0, color='#00ffff', linewidth=1, alpha=0.8)
        
        theta = np.linspace(0, 2*np.pi, 50)
        ax.plot(1.41 * np.cos(theta), 1.41 * np.sin(theta), '--', color='#00ffff', alpha=0.3, linewidth=1)
        
        for tribut, data in self.TRIBIT_DATA.items():
            i_val, q_val = data['i_out'], data['q_out']
            color = self.COLORS[tribut]
            
            ax.scatter(i_val, q_val, s=200, c=color, zorder=5, edgecolors='white', linewidths=1.5)
            ax.plot([0, i_val], [0, q_val], color=color, linewidth=1.5, alpha=0.5)
            
            angle = atan2(q_val, i_val)
            box_x, box_y = 2.0 * np.cos(angle), 2.0 * np.sin(angle)
            
            ax.annotate(f"{tribut}\n({i_val}, {q_val})", xy=(i_val, q_val), xytext=(box_x, box_y),
                       fontsize=9, color='white', ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor=color, linewidth=1.5),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1))
        
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_xlabel('I (sen ωt)', fontsize=12, color='white', fontweight='bold')
        ax.set_ylabel('Q (cos ωt)', fontsize=12, color='white', fontweight='bold')
        ax.set_title('Diagrama de Constelación 8-PSK', fontsize=14, color='white', fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        ax.set_aspect('equal')
        for spine in ax.spines.values():
            spine.set_color('#00ffff')
            spine.set_alpha(0.5)
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='#0a0a1a', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img
    
    def generate_phasor_diagram(self) -> str:
        fig, ax = plt.subplots(figsize=(12, 10), facecolor='#0a0a1a')
        ax.set_facecolor('#0a0a1a')
        
        ax.grid(True, alpha=0.2, color='#ff00ff', linewidth=0.5)
        ax.axhline(y=0, color='#ff00ff', linewidth=1, alpha=0.8)
        ax.axvline(x=0, color='#ff00ff', linewidth=1, alpha=0.8)
        
        theta = np.linspace(0, 2*np.pi, 50)
        ax.plot(1.41 * np.cos(theta), 1.41 * np.sin(theta), '--', color='#ff00ff', alpha=0.3, linewidth=1)
        
        for tribut, data in self.TRIBIT_DATA.items():
            i_val, q_val = data['i_out'], data['q_out']
            phase = data['phase']
            color = self.COLORS[tribut]
            magnitude = round(sqrt(i_val**2 + q_val**2), 2)
            
            ax.annotate('', xy=(i_val, q_val), xytext=(0, 0),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2.5, mutation_scale=12))
            ax.scatter(i_val, q_val, s=100, c=color, zorder=5, edgecolors='white', linewidths=1.5)
            
            angle = atan2(q_val, i_val)
            box_x, box_y = 2.5 * np.cos(angle), 2.5 * np.sin(angle)
            
            # Mostrar: Opción, ecuación sen/cos, cartesiano (magnitud∠fase)
            info = f"{tribut}\nS(t) = {i_val}·sen + {q_val}·cos\n{magnitude}∠{phase}°"
            ax.annotate(info, xy=(i_val, q_val), xytext=(box_x, box_y),
                       fontsize=8, color='white', ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor=color, linewidth=1.5),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1))
        
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3.5, 3.5)
        ax.set_xlabel('I (En Fase)', fontsize=12, color='white', fontweight='bold')
        ax.set_ylabel('Q (Cuadratura)', fontsize=12, color='white', fontweight='bold')
        ax.set_title('Diagrama Fasorial 8-PSK', fontsize=14, color='white', fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        ax.set_aspect('equal')
        for spine in ax.spines.values():
            spine.set_color('#ff00ff')
            spine.set_alpha(0.5)
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='#0a0a1a', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img
    
    def generate_modulated_output(self) -> str:
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='#0a0a1a')
        ax.set_facecolor('#0a0a1a')
        
        t = np.linspace(0, 1, 100)
        omega = 2 * np.pi  # Un solo período por símbolo
        tribits = ['000', '001', '010', '011', '100', '101', '110', '111']
        
        for idx, tribut in enumerate(tribits):
            data = self.TRIBIT_DATA[tribut]
            phase = data['phase']
            color = self.COLORS[tribut]
            
            # Extraer q, i, c del tribit
            q, i, c = tribut[0], tribut[1], tribut[2]
            
            ti = t + idx
            signal = np.sin(omega * ti + radians(phase))
            
            mask = (ti >= idx) & (ti <= idx + 1)
            ax.plot(ti[mask], signal[mask], color=color, linewidth=2, label=f'{tribut}: {phase}°')
            
            if idx > 0:
                ax.axvline(x=idx, color='#333', linewidth=0.5, linestyle='--')
            ax.axvspan(idx, idx + 1, alpha=0.05, color=color)
            
            # qic (etiqueta fija arriba)
            ax.text(idx + 0.5, 1.55, 'qic', ha='center', fontsize=9, color='white', alpha=0.9, fontweight='bold')
            
            # Opción y ángulo debajo
            ax.text(idx + 0.5, -1.5, tribut, ha='center', fontsize=11, color=color, fontweight='bold')
            ax.text(idx + 0.5, -1.85, f'{phase}°', ha='center', fontsize=9, color='white', alpha=0.8)
        
        ax.set_xlim(0, 8)
        ax.set_ylim(-2.2, 1.8)
        ax.set_xlabel('Tiempo (símbolos)', fontsize=12, color='white', fontweight='bold')
        ax.set_ylabel('Amplitud', fontsize=12, color='white', fontweight='bold')
        ax.set_title('Salida Modulada 8-PSK', fontsize=14, color='white', fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        ax.grid(True, alpha=0.1, color='white', linewidth=0.5)
        ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.5)
        ax.legend(loc='upper right', fontsize=8, facecolor='#1a1a2e', edgecolor='#333', labelcolor='white', ncol=4)
        for spine in ax.spines.values():
            spine.set_color('#333')
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='#0a0a1a', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img
    
    # Métodos para estilo serio (fondos blancos)
    def generate_constellation_diagram_serious(self) -> str:
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
        ax.set_facecolor('white')
        
        ax.grid(True, alpha=0.5, color='#333', linewidth=0.5)
        ax.axhline(y=0, color='#333', linewidth=1)
        ax.axvline(x=0, color='#333', linewidth=1)
        
        theta = np.linspace(0, 2*np.pi, 50)
        ax.plot(1.41 * np.cos(theta), 1.41 * np.sin(theta), '--', color='#666', alpha=0.5, linewidth=1)
        
        for tribut, data in self.TRIBIT_DATA.items():
            i_val, q_val = data['i_out'], data['q_out']
            color = self.COLORS[tribut]
            
            ax.scatter(i_val, q_val, s=200, c=color, zorder=5, edgecolors='black', linewidths=1.5)
            ax.plot([0, i_val], [0, q_val], color=color, linewidth=1.5, alpha=0.7)
            
            angle = atan2(q_val, i_val)
            box_x, box_y = 2.0 * np.cos(angle), 2.0 * np.sin(angle)
            
            ax.annotate(f"{tribut}\n({i_val}, {q_val})", xy=(i_val, q_val), xytext=(box_x, box_y),
                       fontsize=9, color='black', ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f5f5', edgecolor=color, linewidth=1.5),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1))
        
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_xlabel('I (sen ωt)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Q (cos ωt)', fontsize=12, fontweight='bold')
        ax.set_title('Diagrama de Constelación 8-PSK', fontsize=14, fontweight='bold')
        ax.tick_params(labelsize=9)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='white', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img
    
    def generate_phasor_diagram_serious(self) -> str:
        fig, ax = plt.subplots(figsize=(12, 10), facecolor='white')
        ax.set_facecolor('white')
        
        ax.grid(True, alpha=0.5, color='#333', linewidth=0.5)
        ax.axhline(y=0, color='#333', linewidth=1)
        ax.axvline(x=0, color='#333', linewidth=1)
        
        theta = np.linspace(0, 2*np.pi, 50)
        ax.plot(1.41 * np.cos(theta), 1.41 * np.sin(theta), '--', color='#666', alpha=0.5, linewidth=1)
        
        for tribut, data in self.TRIBIT_DATA.items():
            i_val, q_val = data['i_out'], data['q_out']
            phase = data['phase']
            color = self.COLORS[tribut]
            magnitude = round(sqrt(i_val**2 + q_val**2), 2)
            
            ax.annotate('', xy=(i_val, q_val), xytext=(0, 0),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2.5, mutation_scale=12))
            ax.scatter(i_val, q_val, s=100, c=color, zorder=5, edgecolors='black', linewidths=1.5)
            
            angle = atan2(q_val, i_val)
            box_x, box_y = 2.5 * np.cos(angle), 2.5 * np.sin(angle)
            
            # Mostrar: Opción, ecuación sen/cos, cartesiano (magnitud∠fase)
            info = f"{tribut}\nS(t) = {i_val}·sen + {q_val}·cos\n{magnitude}∠{phase}°"
            ax.annotate(info, xy=(i_val, q_val), xytext=(box_x, box_y),
                       fontsize=8, color='black', ha='center', va='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5', edgecolor=color, linewidth=1.5),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1))
        
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3.5, 3.5)
        ax.set_xlabel('I (En Fase)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Q (Cuadratura)', fontsize=12, fontweight='bold')
        ax.set_title('Diagrama Fasorial 8-PSK', fontsize=14, fontweight='bold')
        ax.tick_params(labelsize=9)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='white', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img
    
    def generate_modulated_output_serious(self) -> str:
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='white')
        ax.set_facecolor('white')
        
        t = np.linspace(0, 1, 100)
        omega = 2 * np.pi  # Un solo período por símbolo
        tribits = ['000', '001', '010', '011', '100', '101', '110', '111']
        
        for idx, tribut in enumerate(tribits):
            data = self.TRIBIT_DATA[tribut]
            phase = data['phase']
            color = self.COLORS[tribut]
            
            # Extraer q, i, c del tribit
            q, i, c = tribut[0], tribut[1], tribut[2]
            
            ti = t + idx
            signal = np.sin(omega * ti + radians(phase))
            
            mask = (ti >= idx) & (ti <= idx + 1)
            ax.plot(ti[mask], signal[mask], color=color, linewidth=2, label=f'{tribut}: {phase}°')
            
            if idx > 0:
                ax.axvline(x=idx, color='#ccc', linewidth=0.5, linestyle='--')
            ax.axvspan(idx, idx + 1, alpha=0.1, color=color)
            
            # qic (etiqueta fija arriba)
            ax.text(idx + 0.5, 1.55, 'qic', ha='center', fontsize=9, color='#333', fontweight='bold')
            
            # Opción y ángulo debajo
            ax.text(idx + 0.5, -1.5, tribut, ha='center', fontsize=11, color=color, fontweight='bold')
            ax.text(idx + 0.5, -1.85, f'{phase}°', ha='center', fontsize=9, color='#333')
        
        ax.set_xlim(0, 8)
        ax.set_ylim(-2.2, 1.8)
        ax.set_xlabel('Tiempo (símbolos)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amplitud', fontsize=12, fontweight='bold')
        ax.set_title('Salida Modulada 8-PSK', fontsize=14, fontweight='bold')
        ax.tick_params(labelsize=9)
        ax.grid(True, alpha=0.3, color='#333', linewidth=0.5)
        ax.axhline(y=0, color='#333', linewidth=0.5)
        ax.legend(loc='upper right', fontsize=8, facecolor='#f5f5f5', edgecolor='#ccc', ncol=4)
        
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', facecolor='white', bbox_inches='tight')
        buffer.seek(0)
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img


calculator = PSK8Calculator()
