import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import tempfile
import os

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

st.set_page_config(page_title="Dimensionador Metálico 3D", page_icon="🏗️", layout="wide")

# =========================================================================================
# BANCO DE DADOS DE PERFIS ATUALIZADO
# =========================================================================================

CATALOGO_LAMINADOS = {
    "W 150 x 13.0": {"familia": "Laminado W", "d": 148, "bf": 100, "tw": 4.3, "tf": 4.9, "A": 16.6, "Ix": 634, "Iy": 82, "Wx": 85.7, "Wy": 16.4},
    "W 150 x 18.0": {"familia": "Laminado W", "d": 153, "bf": 102, "tw": 5.8, "tf": 7.1, "A": 23.0, "Ix": 923, "Iy": 126, "Wx": 120.7, "Wy": 24.7},
    "W 200 x 15.0": {"familia": "Laminado W", "d": 200, "bf": 100, "tw": 4.3, "tf": 5.2, "A": 19.1, "Ix": 1305, "Iy": 87, "Wx": 130.5, "Wy": 17.4},
    "W 200 x 22.5": {"familia": "Laminado W", "d": 206, "bf": 102, "tw": 6.2, "tf": 8.0, "A": 28.6, "Ix": 2029, "Iy": 142, "Wx": 197.0, "Wy": 27.9},
    "W 250 x 25.3": {"familia": "Laminado W", "d": 257, "bf": 102, "tw": 6.1, "tf": 8.4, "A": 32.2, "Ix": 3415, "Iy": 149, "Wx": 265.8, "Wy": 29.3},
    "W 310 x 32.7": {"familia": "Laminado W", "d": 308, "bf": 102, "tw": 6.6, "tf": 10.8, "A": 41.7, "Ix": 6524, "Iy": 192, "Wx": 423.6, "Wy": 37.7},
    "W 360 x 22.0": {"familia": "Laminado W", "d": 356, "bf": 152, "tw": 5.1, "tf": 6.4, "A": 28.5, "Ix": 5800, "Iy": 320, "Wx": 325.0, "Wy": 42.0},
    "W 360 x 44.0": {"familia": "Laminado W", "d": 352, "bf": 171, "tw": 6.9, "tf": 9.8, "A": 56.1, "Ix": 12185, "Iy": 816, "Wx": 692.3, "Wy": 95.5},
    "W 360 x 122 (Original)": {"familia": "Laminado W Pesado", "d": 363, "bf": 257, "tw": 13.0, "tf": 22.0, "A": 154.6, "Ix": 36435, "Iy": 6231, "Wx": 2007.4, "Wy": 484.9},
    "W 360 x 122 (Remontado)": {"familia": "Viga Castelada", "d": 544, "bf": 257, "tw": 13.0, "tf": 22.0, "A": 178.1, "Ix": 90616, "Iy": 6234, "Wx": 3331.0, "Wy": 485.0},
    "Perfil I 10 x 4 5/8\"": {"familia": "Laminado I Padrão", "d": 254, "bf": 117.5, "tw": 7.9, "tf": 12.5, "A": 48.2, "Ix": 5120, "Iy": 265, "Wx": 403.0, "Wy": 45.0},
}

CATALOGO_CHAPA_DOBRADA = {
    "U 50 x 25 x 2.00": {"familia": "Chapa Dobrada U", "d": 50, "bf": 25, "tw": 2.00, "tf": 2.00, "A": 1.75, "Ix": 6.66, "Iy": 1.07, "Wx": 2.60, "Wy": 0.60},
    "U 50 x 25 x 2.65": {"familia": "Chapa Dobrada U", "d": 50, "bf": 25, "tw": 2.65, "tf": 2.65, "A": 2.27, "Ix": 8.55, "Iy": 1.38, "Wx": 3.42, "Wy": 0.76},
    "U 75 x 38 x 2.00": {"familia": "Chapa Dobrada U", "d": 75, "bf": 38, "tw": 2.00, "tf": 2.00, "A": 2.80, "Ix": 25.10, "Iy": 4.55, "Wx": 6.60, "Wy": 1.58},
    "U 100 x 40 x 2.25": {"familia": "Chapa Dobrada U", "d": 100, "bf": 40, "tw": 2.25, "tf": 2.25, "A": 3.89, "Ix": 57.67, "Iy": 5.89, "Wx": 11.50, "Wy": 1.96},
    "U 100 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 5.71, "Ix": 88.29, "Iy": 14.20, "Wx": 17.60, "Wy": 3.94},
    "U 127 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 127, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 6.53, "Ix": 154.8, "Iy": 15.32, "Wx": 24.30, "Wy": 4.08},
    "U 150 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 150, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 7.23, "Ix": 230.1, "Iy": 16.08, "Wx": 30.60, "Wy": 4.16},
    "U 150 x 50 x 3.35": {"familia": "Chapa Dobrada U (Chapa 10)", "d": 150, "bf": 50, "tw": 3.35, "tf": 3.35, "A": 7.97, "Ix": 257.0, "Iy": 17.10, "Wx": 34.30, "Wy": 4.60},
    "U 200 x 75 x 3.35": {"familia": "Chapa Dobrada U (Chapa 10)", "d": 200, "bf": 75, "tw": 3.35, "tf": 3.35, "A": 11.30, "Ix": 668.0, "Iy": 61.30, "Wx": 66.80, "Wy": 11.40},
    "UE 100 x 50 x 17 x 2.25": {"familia": "U Enrijecido", "d": 100, "bf": 50, "tw": 2.25, "tf": 2.25, "A": 4.88, "Ix": 78.4, "Iy": 15.1, "Wx": 15.68, "Wy": 4.25},
    "UE 150 x 60 x 20 x 3.00": {"familia": "U Enrijecido", "d": 150, "bf": 60, "tw": 3.00, "tf": 3.00, "A": 8.70, "Ix": 308.2, "Iy": 35.8, "Wx": 41.09, "Wy": 8.32},
}

CATALOGO_CANTONEIRAS = {
    "L 1.1/2\" x 1/8\"": {"familia": "Cantoneira L", "d": 38.1, "bf": 38.1, "tw": 3.17, "tf": 3.17, "A": 2.32, "Ix": 3.2, "Iy": 3.2, "Wx": 1.1, "Wy": 1.1},
    "2x L 2\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 50.8, "bf": 111.6, "tw": 4.76, "tf": 4.76, "A": 9.16, "Ix": 21.8, "Iy": 44.2, "Wx": 6.0, "Wy": 10.2},
    "2x L 2.1/2\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 63.5, "bf": 137.0, "tw": 6.35, "tf": 6.35, "A": 14.80, "Ix": 54.8, "Iy": 112.0, "Wx": 12.1, "Wy": 21.5},
    "2x L 4\" x 5/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 101.6, "bf": 213.2, "tw": 7.94, "tf": 7.94, "A": 31.00, "Ix": 306.0, "Iy": 612.0, "Wx": 42.2, "Wy": 71.7},
}

CATALOGO_COMPLETO = {**CATALOGO_LAMINADOS, **CATALOGO_CHAPA_DOBRADA, **CATALOGO_CANTONEIRAS}

PROPRIEDADES_ACO = {
    "ASTM A36": {"fy": 250, "fu": 400},
    "ASTM A572 Gr 50": {"fy": 345, "fu": 450},
    "USI CIVIL 300": {"fy": 300, "fu": 410}
}

# =========================================================================================
# MOTOR MATRICIAL 3D
# =========================================================================================

class MotorCalculo3D:
    def __init__(self):
        self.E = 200e6  
        self.G = 77e6   
        self.nos = []
        self.barras = []
        self.apoios = []
        self.cargas_nodais = []
        self.fef_local = {}

    def construir_malha(self, nos_x, nos_y, nos_z, barras_info, apoios_idx, tipo_apoio_base):
        self.nos = list(zip(nos_x, nos_y, nos_z))
        self.barras = barras_info
        self.apoios = []
        if not self.nos: return
        for i in apoios_idx:
            if "Engastado" in tipo_apoio_base:
                self.apoios.extend([i*6 + dof for dof in range(6)])
            else:
                self.apoios.extend([i*6 + dof for dof in range(3)])

    def _get_T(self, dx, dy, dz, L, ang_graus=0.0):
        cx, cy, cz = dx/L, dy/L, dz/L
        if abs(cx) < 1e-4 and abs(cy) < 1e-4: 
            r3x3 = np.array([[0, 0, cz], [0, 1, 0], [-cz, 0, 0]])
        else:
            D = np.sqrt(cx**2 + cy**2)
            r3x3 = np.array([[cx, cy, cz], [-cy/D, cx/D, 0], [-cx*cz/D, -cy*cz/D, D]])
            
        if ang_graus != 0.0:
            ang_rad = np.radians(ang_graus)
            R_loc = np.array([
                [1, 0, 0],
                [0, np.cos(ang_rad), np.sin(ang_rad)],
                [0, -np.sin(ang_rad), np.cos(ang_rad)]
            ])
            r3x3 = R_loc @ r3x3

        T = np.zeros((12, 12))
        for b in range(4): T[b*3:(b+1)*3, b*3:(b+1)*3] = r3x3
        return T, r3x3

    def _matriz_elemento_3d(self, barra):
        n1, n2 = barra['n1'], barra['n2']
        A, Iy, Iz, J = barra['A'], barra['Iy'], barra['Iz'], barra['J']
        ang = barra.get('ang', 0.0)
        
        x1, y1, z1 = self.nos[n1]
        x2, y2, z2 = self.nos[n2]
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        L = np.sqrt(dx**2 + dy**2 + dz**2)
        if L == 0: L = 1e-6
        
        k_loc = np.zeros((12, 12))
        EA_L = (self.E * A) / L
        k_loc[0, 0] = k_loc[6, 6] = EA_L
        k_loc[0, 6] = k_loc[6, 0] = -EA_L
        
        GJ_L = (self.G * J) / L
        k_loc[3, 3] = k_loc[9, 9] = GJ_L
        k_loc[3, 9] = k_loc[9, 3] = -GJ_L
        
        k12_Iz, k6_Iz, k4_Iz, k2_Iz = (12*self.E*Iz)/(L**3), (6*self.E*Iz)/(L**2), (4*self.E*Iz)/L, (2*self.E*Iz)/L
        k_loc[1, 1] = k_loc[7, 7] = k12_Iz
        k_loc[1, 7] = k_loc[7, 1] = -k12_Iz
        k_loc[1, 5] = k_loc[5, 1] = k_loc[1, 11] = k_loc[11, 1] = k6_Iz
        k_loc[5, 7] = k_loc[7, 5] = -k6_Iz
        k_loc[7, 11] = k_loc[11, 7] = -k6_Iz
        k_loc[5, 5] = k_loc[11, 11] = k4_Iz
        k_loc[5, 11] = k_loc[11, 5] = k2_Iz

        k12_Iy, k6_Iy, k4_Iy, k2_Iy = (12*self.E*Iy)/(L**3), (6*self.E*Iy)/(L**2), (4*self.E*Iy)/L, (2*self.E*Iy)/L
        k_loc[2, 2] = k_loc[8, 8] = k12_Iy
        k_loc[2, 8] = k_loc[8, 2] = -k12_Iy
        k_loc[2, 4] = k_loc[4, 2] = k_loc[2, 10] = k_loc[10, 2] = -k6_Iy
        k_loc[4, 8] = k_loc[8, 4] = k6_Iy
        k_loc[8, 10] = k_loc[10, 8] = k6_Iy
        k_loc[4, 4] = k_loc[10, 10] = k4_Iy
        k_loc[4, 10] = k_loc[10, 4] = k2_Iy

        T, R = self._get_T(dx, dy, dz, L, ang)
        k_glob = T.T @ k_loc @ T
        return k_glob, k_loc, T, R, L

    def aplicar_carga_distribuida(self, q_kNm2, vao_x, espacamento):
        q_linear = q_kNm2 * espacamento
        num_dofs = len(self.nos) * 6
        self.cargas_nodais = np.zeros(num_dofs)
        self.fef_local = {}

        for i, barra in enumerate(self.barras):
            n1, n2 = barra['n1'], barra['n2']
            z1, z2 = self.nos[n1][2], self.nos[n2][2]
            ang = barra.get('ang', 0.0)
            
            is_vertical = abs(z1 - z2) > 1e-2 and abs(self.nos[n1][0] - self.nos[n2][0]) < 1e-2 and abs(self.nos[n1][1] - self.nos[n2][1]) < 1e-2
            
            if not is_vertical and barra['grupo'] not in ["Pilares Metálicos", "Pilares Concreto", "Montantes", "Diagonais"]:
                x1, y1, _ = self.nos[n1]
                x2, y2, _ = self.nos[n2]
                L = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
                if L == 0: continue
                
                T, R = self._get_T(x2-x1, y2-y1, z2-z1, L, ang)
                q_glob = np.array([0, 0, -q_linear])
                q_loc = R @ q_glob
                qx, qy, qz = q_loc
                
                fef_loc = np.zeros(12)
                fef_loc[0], fef_loc[6] = -qx*L/2, -qx*L/2
                fef_loc[1], fef_loc[7] = -qy*L/2, -qy*L/2
                fef_loc[5], fef_loc[11] = -qy*(L**2)/12, qy*(L**2)/12
                fef_loc[2], fef_loc[8] = -qz*L/2, -qz*L/2
                fef_loc[4], fef_loc[10] = qz*(L**2)/12, -qz*(L**2)/12
                
                self.fef_local[i] = fef_loc
                fef_glob = T.T @ fef_loc
                
                self.cargas_nodais[n1*6:n1*6+6] -= fef_glob[0:6]
                self.cargas_nodais[n2*6:n2*6+6] -= fef_glob[6:12]

    def resolver(self):
        try:
            num_dofs = len(self.nos) * 6
            K_global = np.zeros((num_dofs, num_dofs))
            k_locs, Ts = {}, {}
            vetores_locais = []
            
            for i, barra in enumerate(self.barras):
                k_glob, k_loc, T, R, _ = self._matriz_elemento_3d(barra)
                k_locs[i], Ts[i] = k_loc, T
                vetores_locais.append(R.tolist())
                n1, n2 = barra['n1'], barra['n2']
                dofs = [n1*6 + d for d in range(6)] + [n2*6 + d for d in range(6)]
                for r in range(12):
                    for c in range(12):
                        K_global[dofs[r], dofs[c]] += k_glob[r, c]

            dofs_livres = [d for d in range(num_dofs) if d not in self.apoios]
            max_k = np.max(np.diag(K_global)) if len(K_global) > 0 else 1.0
            for d in dofs_livres:
                if K_global[d, d] < 1e-6 * max_k:
                    K_global[d, d] += 1e-4 * max_k

            K_livre = K_global[np.ix_(dofs_livres, dofs_livres)]
            F_livre = self.cargas_nodais[dofs_livres]

            try:
                U_livre = np.linalg.solve(K_livre, F_livre)
            except np.linalg.LinAlgError:
                U_livre = np.linalg.lstsq(K_livre, F_livre, rcond=None)[0]

            U_completo = np.zeros(num_dofs)
            U_completo[dofs_livres] = U_livre

            esforcos = []
            esforcos_grupos = {}
            for b in self.barras:
                if b['grupo'] not in esforcos_grupos:
                    esforcos_grupos[b['grupo']] = {
                        "n_max": 0.0, "v_max": 0.0, "my_max": 0.0, "mz_max": 0.0, "d_max": 0.0, "L_max": 0.0,
                        "n_pos": -1e9, "n_neg": 1e9, "v_pos": -1e9, "v_neg": 1e9, "my_pos": -1e9, "my_neg": 1e9, "mz_pos": -1e9, "mz_neg": 1e9
                    }

            for i, barra in enumerate(self.barras):
                n1, n2 = barra['n1'], barra['n2']
                grp = barra['grupo']
                
                dofs = [n1*6 + d for d in range(6)] + [n2*6 + d for d in range(6)]
                u_elem = U_completo[dofs]
                
                f_loc = k_locs[i] @ Ts[i] @ u_elem
                if i in self.fef_local:
                    f_loc += self.fef_local[i]
                    
                N1, N2 = -f_loc[0], f_loc[6]
                Vy1, Vy2 = f_loc[1], -f_loc[7]
                Vz1, Vz2 = f_loc[2], -f_loc[8]
                My1, My2 = -f_loc[4], f_loc[10]
                Mz1, Mz2 = -f_loc[5], f_loc[11]

                esforcos.append({
                    "n1": n1, "n2": n2,
                    "N": (N1, N2), "Vy": (Vy1, Vy2), "Vz": (Vz1, Vz2),
                    "My": (My1, My2), "Mz": (Mz1, Mz2)
                })

                n_abs_max = max(abs(N1), abs(N2))
                v_abs_max = max(abs(Vy1), abs(Vy2), abs(Vz1), abs(Vz2))
                my_abs_max = max(abs(My1), abs(My2))
                mz_abs_max = max(abs(Mz1), abs(Mz2))
                
                L = np.sqrt((self.nos[n2][0]-self.nos[n1][0])**2 + (self.nos[n2][1]-self.nos[n1][1])**2 + (self.nos[n2][2]-self.nos[n1][2])**2)
                
                d_bow = 0.0
                if i in self.fef_local and L > 0:
                    q_z_local = (self.fef_local[i][4] * 12.0) / (L**2)
                    d_bow = abs((5.0 * q_z_local * (L**4)) / (384.0 * self.E * barra['Iy'])) * 1000.0
                
                d_no1 = np.linalg.norm(U_completo[n1*6:n1*6+3]) * 1000.0
                d_no2 = np.linalg.norm(U_completo[n2*6:n2*6+3]) * 1000.0
                d_max = max(d_no1, d_no2) + d_bow

                esforcos_grupos[grp]["n_max"] = max(esforcos_grupos[grp]["n_max"], n_abs_max)
                esforcos_grupos[grp]["v_max"] = max(esforcos_grupos[grp]["v_max"], v_abs_max)
                esforcos_grupos[grp]["my_max"] = max(esforcos_grupos[grp]["my_max"], my_abs_max)
                esforcos_grupos[grp]["mz_max"] = max(esforcos_grupos[grp]["mz_max"], mz_abs_max)
                esforcos_grupos[grp]["d_max"] = max(esforcos_grupos[grp]["d_max"], d_max)
                esforcos_grupos[grp]["L_max"] = max(esforcos_grupos[grp]["L_max"], L)

                esforcos_grupos[grp]["n_pos"] = max(esforcos_grupos[grp]["n_pos"], N1, N2)
                esforcos_grupos[grp]["n_neg"] = min(esforcos_grupos[grp]["n_neg"], N1, N2)
                esforcos_grupos[grp]["v_pos"] = max(esforcos_grupos[grp]["v_pos"], Vz1, Vz2)
                esforcos_grupos[grp]["v_neg"] = min(esforcos_grupos[grp]["v_neg"], Vz1, Vz2)
                esforcos_grupos[grp]["my_pos"] = max(esforcos_grupos[grp]["my_pos"], My1, My2)
                esforcos_grupos[grp]["my_neg"] = min(esforcos_grupos[grp]["my_neg"], My1, My2)
                esforcos_grupos[grp]["mz_pos"] = max(esforcos_grupos[grp]["mz_pos"], Mz1, Mz2)
                esforcos_grupos[grp]["mz_neg"] = min(esforcos_grupos[grp]["mz_neg"], Mz1, Mz2)

            F_total = K_global @ U_completo
            reacoes = {}
            for dof in self.apoios:
                no = dof // 6
                eixo = dof % 6
                if no not in reacoes: reacoes[no] = [0.0]*6
                reacoes[no][eixo] = float(F_total[dof] - self.cargas_nodais[dof])

            global_n = max([v["n_max"] for k, v in esforcos_grupos.items()]) if esforcos_grupos else 0.0
            global_v = max([v["v_max"] for k, v in esforcos_grupos.items()]) if esforcos_grupos else 0.0
            global_m = max([v["my_max"] for k, v in esforcos_grupos.items()]) if esforcos_grupos else 0.0
            global_d = max([v["d_max"] for k, v in esforcos_grupos.items()]) if esforcos_grupos else 0.0

            return {
                "sucesso": True, "num_nos": len(self.nos), "num_barras": len(self.barras),
                "n_max_kn": global_n, "v_max_kn": global_v, "m_max_knm": global_m, "desloc_max_mm": global_d,
                "esforcos": esforcos, "reacoes": reacoes, "nos": self.nos, 
                "barras": self.barras,
                "esforcos_grupos": esforcos_grupos,
                "deslocamentos_nodais": U_completo.tolist(),
                "vetores_locais": vetores_locais
            }
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

# =========================================================================================
# VERIFICADOR NBR 8800 E FUNÇÕES VISUAIS
# =========================================================================================

class VerificadorNBR8800:
    def __init__(self, tipo_aco="ASTM A572 Gr 50"):
        self.aco = PROPRIEDADES_ACO.get(tipo_aco, PROPRIEDADES_ACO["ASTM A572 Gr 50"])
        self.gamma_a1 = 1.10
        self.E_cm = 20000.0  

    def verificar_elemento(self, nome_perfil, N_trac_sd, N_comp_sd, V_sd, My_sd, Mz_sd, delta_sd_mm, vao_m, fator_esforso=1.0):
        perfil = CATALOGO_COMPLETO.get(nome_perfil, CATALOGO_LAMINADOS["W 200 x 22.5"])
        fy = self.aco["fy"] / 10.0  
        A = perfil["A"]
        Ix = perfil["Ix"]
        Iy = perfil["Iy"]
        Wx = perfil["Wx"]
        Wy = perfil.get("Wy", 0.1)
        d = perfil["d"] / 10.0
        tw = perfil["tw"] / 10.0

        N_trac_sd_e = N_trac_sd * fator_esforso
        N_comp_sd_e = N_comp_sd * fator_esforso
        V_sd_e = abs(V_sd) * fator_esforso
        My_sd_e = abs(My_sd) * fator_esforso  
        Mz_sd_e = abs(Mz_sd) * fator_esforso  

        L_cm = vao_m * 100.0
        Kx, Ky = 1.0, 1.0
        
        rx = np.sqrt(Ix / A) if A > 0 else 1e-5
        ry = np.sqrt(Iy / A) if A > 0 else 1e-5
        
        esbeltez_x = (Kx * L_cm) / rx
        esbeltez_y = (Ky * L_cm) / ry
        esbeltez_max = max(esbeltez_x, esbeltez_y)
        
        Q = 1.0 
        Ne = (np.pi**2 * self.E_cm * A) / (esbeltez_max**2) if esbeltez_max > 0 else 1e9
        lambda_0 = np.sqrt((Q * A * fy) / Ne) if Ne > 0 else 999.0
        
        if lambda_0 <= 1.5: chi = 0.658 ** (lambda_0**2)
        else: chi = 0.877 / (lambda_0**2)
            
        M_rd_x = (Wx * fy) / (100.0 * self.gamma_a1)  
        M_rd_y = (Wy * fy) / (100.0 * self.gamma_a1)
        
        Av = d * tw
        V_rd = (0.60 * Av * fy) / self.gamma_a1
        
        N_rd_trac = (A * fy) / self.gamma_a1
        N_rd_comp = (chi * Q * A * fy) / self.gamma_a1

        ratio_N_trac = N_trac_sd_e / N_rd_trac if N_rd_trac > 0 else 0
        ratio_N_comp = N_comp_sd_e / N_rd_comp if N_rd_comp > 0 else 0
        ratio_N_max = max(ratio_N_trac, ratio_N_comp)
        
        ratio_Mx = My_sd_e / M_rd_x if M_rd_x > 0 else 0
        ratio_My = Mz_sd_e / M_rd_y if M_rd_y > 0 else 0

        if ratio_N_max >= 0.2: taxa_interacao = ratio_N_max + (8.0/9.0) * (ratio_Mx + ratio_My)
        else: taxa_interacao = (ratio_N_max / 2.0) + (ratio_Mx + ratio_My)

        ratio_V = V_sd_e / V_rd if V_rd > 0 else 0

        delta_lim_mm = (vao_m * 1000.0) / 250.0
        ratio_delta = delta_sd_mm / delta_lim_mm if delta_lim_mm > 0 else 0

        taxa_maxima = max(taxa_interacao, ratio_V, ratio_delta)

        return {
            "perfil": nome_perfil, "familia": perfil["familia"], "aprovado": taxa_maxima <= 1.0,
            "taxa_maxima": taxa_maxima * 100.0, "taxa_interacao": taxa_interacao * 100.0,
            "ratio_N": ratio_N_max * 100.0, "ratio_N_trac": ratio_N_trac * 100.0, "ratio_N_comp": ratio_N_comp * 100.0,
            "ratio_Mx": ratio_Mx * 100.0, "ratio_My": ratio_My * 100.0, "ratio_V": ratio_V * 100.0, "ratio_delta": ratio_delta * 100.0,
            "M_rd_x": M_rd_x, "M_rd_y": M_rd_y, "V_rd": V_rd, "N_rd_trac": N_rd_trac, "N_rd_comp": N_rd_comp,
            "chi": chi, "esbeltez_max": esbeltez_max, "Ne": Ne, "lambda_0": lambda_0, "rx": rx, "ry": ry, "delta_lim_mm": delta_lim_mm
        }

def desenhar_secao_transversal(nome_perfil):
    p = CATALOGO_COMPLETO.get(nome_perfil)
    if not p: return None
    
    d, bf, tw, tf = p['d'], p['bf'], p['tw'], p['tf']
    fam = p['familia']
    fig = go.Figure()
    
    if "W" in fam or "I" in fam or "Castelada" in fam:
        x_poly = [-bf/2, bf/2, bf/2, tw/2, tw/2, bf/2, bf/2, -bf/2, -bf/2, -tw/2, -tw/2, -bf/2, -bf/2]
        y_poly = [d/2, d/2, d/2-tf, d/2-tf, -d/2+tf, -d/2+tf, -d/2, -d/2, -d/2+tf, -d/2+tf, d/2-tf, d/2-tf, d/2]
        fig.add_trace(go.Scatter(x=x_poly, y=y_poly, fill="toself", line_color="royalblue", name=nome_perfil))
    elif "U" in fam:
        if "Enrijecido" in fam:
            c = 15.0 if '15' in nome_perfil else 17.0
            x_poly = [-bf/2, bf/2, bf/2, bf/2-tw, bf/2-tw, -bf/2+tw, -bf/2+tw, bf/2-tw, bf/2-tw, bf/2, bf/2, -bf/2, -bf/2]
            y_poly = [d/2, d/2, d/2-c, d/2-c, d/2-tf, d/2-tf, -d/2+tf, -d/2+tf, -d/2+c, -d/2+c, -d/2, -d/2, d/2]
        else:
            x_poly = [-bf/2, bf/2, bf/2, -bf/2+tw, -bf/2+tw, bf/2, bf/2, -bf/2, -bf/2]
            y_poly = [d/2, d/2, d/2-tf, d/2-tf, -d/2+tf, -d/2+tf, -d/2, -d/2, d/2]
        fig.add_trace(go.Scatter(x=x_poly, y=y_poly, fill="toself", line_color="seagreen", name=nome_perfil))
    elif "Cantoneira" in fam:
        if "Dupla" in fam:
            x_poly = [-bf, bf, bf, tw, tw, -tw, -tw, -bf, -bf]
            y_poly = [-d/2+tf, -d/2+tf, -d/2, -d/2, d/2, d/2, -d/2, -d/2, -d/2+tf]
        else:
            x_poly = [0, bf, bf, tw, tw, 0, 0]
            y_poly = [0, 0, tf, tf, d, d, 0]
        fig.add_trace(go.Scatter(x=x_poly, y=y_poly, fill="toself", line_color="darkorange", name=nome_perfil))
        
    fig.update_layout(
        title=f"Secção Geométrica 2D: {nome_perfil}<br><sup>d={d:.1f}mm | bf={bf:.1f}mm | tw={tw:.1f}mm | tf={tf:.1f}mm</sup>",
        xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=True, visible=False),
        yaxis=dict(showgrid=False, zeroline=True, visible=False),
        showlegend=False, width=400, height=400, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='white', paper_bgcolor='white'
    )
    return fig

def get_section_data(perfil_nome):
    p = CATALOGO_COMPLETO.get(perfil_nome)
    if not p: return [], []
    d, bf, fam = p['d'] / 1000.0, p['bf'] / 1000.0, p['familia']
    lines = [] 
    if "W" in fam or "I" in fam or "Castelada" in fam:
        lines.extend([(0, d/2, 0, -d/2), (-bf/2, d/2, bf/2, d/2), (-bf/2, -d/2, bf/2, -d/2)]) 
        extremos = [(0, d/2), (0, -d/2), (-bf/2, d/2), (bf/2, d/2), (-bf/2, -d/2), (bf/2, -d/2)]
    elif "U" in fam:
        lines.extend([(-bf/2, d/2, -bf/2, -d/2), (-bf/2, d/2, bf/2, d/2), (-bf/2, -d/2, bf/2, -d/2)]) 
        extremos = [(-bf/2, d/2), (-bf/2, -d/2), (bf/2, d/2), (bf/2, -d/2)]
    elif "Cantoneira" in fam:
        if "Dupla" in fam:
            lines.extend([(0, d/2, 0, -d/2), (-bf/2, d/2, bf/2, d/2)]) 
            extremos = [(0, -d/2), (-bf/2, d/2), (bf/2, d/2)]
        else:
            lines.extend([(-bf/2, d/2, -bf/2, -d/2), (-bf/2, -d/2, bf/2, -d/2)]) 
            extremos = [(-bf/2, d/2), (-bf/2, -d/2), (bf/2, -d/2)]
    else:
        lines.extend([(0, d/2, 0, -d/2), (-bf/2, 0, bf/2, 0)])
        extremos = [(0, d/2), (0, -d/2), (-bf/2, 0), (bf/2, 0)]
    return lines, extremos

def desenhar_diagrama(res, tipo_diagrama, vista_camera="iso"):
    fig = go.Figure()
    nos, barras, esforcos = res["nos"], res["barras"], res["esforcos"]
    
    if tipo_diagrama == "Geometria (Apenas Linhas)":
        for b_info in barras:
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='black', width=4), showlegend=False))
            
    elif tipo_diagrama == "Deslocamentos (Deformada)":
        for b_info in barras:
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='lightgrey', width=1, dash='dash'), showlegend=False))
            
        U = res.get("deslocamentos_nodais", [])
        if U:
            U_arr = np.array(U)
            max_disp = np.max(np.abs(U_arr))
            coords_arr = np.array(nos)
            scale = 0.0
            if max_disp > 1e-6:
                dim_max = max(np.max(coords_arr[:, 0]), np.max(coords_arr[:, 1]), np.max(coords_arr[:, 2]))
                scale = (dim_max * 0.1) / max_disp 
            for b_info in barras:
                n1, n2 = b_info['n1'], b_info['n2']
                x1 = nos[n1][0] + U[n1*6] * scale
                y1 = nos[n1][1] + U[n1*6+1] * scale
                z1 = nos[n1][2] + U[n1*6+2] * scale
                x2 = nos[n2][0] + U[n2*6] * scale
                y2 = nos[n2][1] + U[n2*6+1] * scale
                z2 = nos[n2][2] + U[n2*6+2] * scale
                fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='red', width=5), showlegend=False))

    elif tipo_diagrama == "Reações de Apoio":
        for b_info in barras:
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='lightgrey', width=2), showlegend=False))
        rx, ry, rz, texts = [], [], [], []
        for no_idx, reac in res["reacoes"].items():
            x, y, z = nos[no_idx]
            Fx, Fy, Fz = reac[0], reac[1], reac[2]
            rx.append(x); ry.append(y); rz.append(z)
            texts.append(f"Fz: {Fz:.1f}kN<br>Fx: {Fx:.1f}kN<br>Fy: {Fy:.1f}kN")
        fig.add_trace(go.Scatter3d(x=rx, y=ry, z=rz, mode='markers+text', marker=dict(size=8, color='purple', symbol='diamond'), text=texts, textposition="top center", textfont=dict(size=11, color='purple'), showlegend=False))
    
    elif tipo_diagrama == "Vista Extrudada (Seções 3D)":
        for i, b_info in enumerate(barras):
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            perfil_nome = b_info.get('perfil_nome')
            if not perfil_nome: continue
            
            lines_loc, ext_loc = get_section_data(perfil_nome)
            R = res.get("vetores_locais", [])[i] if "vetores_locais" in res else None
            if not R: continue
            R_inv = np.array(R).T
            
            for (ly1, lz1, ly2, lz2) in lines_loc:
                p1_1 = np.array([x1, y1, z1]) + R_inv @ np.array([0, ly1, lz1])
                p2_1 = np.array([x1, y1, z1]) + R_inv @ np.array([0, ly2, lz2])
                fig.add_trace(go.Scatter3d(x=[p1_1[0], p2_1[0]], y=[p1_1[1], p2_1[1]], z=[p1_1[2], p2_1[2]], mode='lines', line=dict(color='black', width=3), showlegend=False))
                
                dx, dy, dz = x2-x1, y2-y1, z2-z1
                L = np.sqrt(dx**2 + dy**2 + dz**2)
                p1_2 = np.array([x1, y1, z1]) + R_inv @ np.array([L, ly1, lz1])
                p2_2 = np.array([x1, y1, z1]) + R_inv @ np.array([L, ly2, lz2])
                fig.add_trace(go.Scatter3d(x=[p1_2[0], p2_2[0]], y=[p1_2[1], p2_2[1]], z=[p1_2[2], p2_2[2]], mode='lines', line=dict(color='black', width=3), showlegend=False))
            
            for (ly, lz) in ext_loc:
                p1 = np.array([x1, y1, z1]) + R_inv @ np.array([0, ly, lz])
                p2 = np.array([x1, y1, z1]) + R_inv @ np.array([L, ly, lz])
                fig.add_trace(go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]], mode='lines', line=dict(color='gray', width=2), showlegend=False))
                
            cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
            scale_axis = max(L * 0.15, 0.5) 
            fig.add_trace(go.Scatter3d(x=[cx, cx + R[0][0]*scale_axis], y=[cy, cy + R[0][1]*scale_axis], z=[cz, cz + R[0][2]*scale_axis], mode='lines', line=dict(color='red', width=4), showlegend=False))
            fig.add_trace(go.Scatter3d(x=[cx, cx + R[1][0]*scale_axis], y=[cy, cy + R[1][1]*scale_axis], z=[cz, cz + R[1][2]*scale_axis], mode='lines', line=dict(color='green', width=4), showlegend=False))
            fig.add_trace(go.Scatter3d(x=[cx, cx + R[2][0]*scale_axis], y=[cy, cy + R[2][1]*scale_axis], z=[cz, cz + R[2][2]*scale_axis], mode='lines', line=dict(color='blue', width=4), showlegend=False))
            
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='red', width=4), name='Eixo X (Longitudinal)'))
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='green', width=4), name='Eixo Y (Forte)'))
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='blue', width=4), name='Eixo Z (Fraco)'))
        fig.update_layout(showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"))

    elif tipo_diagrama == "Eixos Locais dos Perfis":
        for i, b_info in enumerate(barras):
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='lightgrey', width=3), showlegend=False))
            
            cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
            dx, dy, dz = x2-x1, y2-y1, z2-z1
            L = np.sqrt(dx**2 + dy**2 + dz**2)
            scale = max(L * 0.15, 0.5) 
            
            R = res.get("vetores_locais", [])[i] if "vetores_locais" in res else None
            if R:
                fig.add_trace(go.Scatter3d(x=[cx, cx + R[0][0]*scale], y=[cy, cy + R[0][1]*scale], z=[cz, cz + R[0][2]*scale], mode='lines', line=dict(color='red', width=5), showlegend=False))
                fig.add_trace(go.Scatter3d(x=[cx, cx + R[1][0]*scale], y=[cy, cy + R[1][1]*scale], z=[cz, cz + R[1][2]*scale], mode='lines', line=dict(color='green', width=5), showlegend=False))
                fig.add_trace(go.Scatter3d(x=[cx, cx + R[2][0]*scale], y=[cy, cy + R[2][1]*scale], z=[cz, cz + R[2][2]*scale], mode='lines', line=dict(color='blue', width=5), showlegend=False))
        
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='red', width=4), name='Eixo X (Longitudinal)'))
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='green', width=4), name='Eixo Y (Forte)'))
        fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='blue', width=4), name='Eixo Z (Fraco)'))
        fig.update_layout(showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"))

    else:
        for b_info in barras:
            n1, n2 = b_info['n1'], b_info['n2']
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='lightgrey', width=2), showlegend=False))

        max_val = 1e-5
        for esf in esforcos:
            v1, v2 = (esf["N"] if "Normal" in tipo_diagrama else (esf["Vz"] if "Cortante" in tipo_diagrama else esf["My"]))
            max_val = max(max_val, abs(v1), abs(v2))
            
        escala = 1.2 / max_val
        for i, esf in enumerate(esforcos):
            n1, n2 = esf["n1"], esf["n2"]
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
            L = np.sqrt(dx**2 + dy**2 + dz**2)
            if L == 0: continue
            
            if "Normal" in tipo_diagrama: 
                v1, v2 = esf["N"]
                valor_medio = (v1 + v2) / 2.0
                cor = 'royalblue' if valor_medio >= -0.01 else 'crimson'
            elif "Cortante" in tipo_diagrama: 
                v1, v2 = esf["Vz"]
                cor = 'seagreen'
            else: 
                v1, v2 = esf["My"]
                cor = 'darkorange'
                
            nx, ny, nz = (1, 0, 0) if abs(dz)/L > 0.95 else (0, 0, 1)
            ox1, oy1, oz1 = x1 + nx*v1*escala, y1 + ny*v1*escala, z1 + nz*v1*escala
            ox2, oy2, oz2 = x2 + nx*v2*escala, y2 + ny*v2*escala, z2 + nz*v2*escala
            
            fig.add_trace(go.Scatter3d(x=[x1, ox1, ox2, x2], y=[y1, oy1, oy2, y2], z=[z1, oz1, oz2, z2], mode='lines', line=dict(color=cor, width=3), showlegend=False))
            
            t_x, t_y, t_z, t_val = [], [], [], []
            if abs(v1) > 0.1:
                t_x.append(ox1); t_y.append(oy1); t_z.append(oz1); t_val.append(f"{v1:.1f}")
            if abs(v2) > 0.1 and abs(v2 - v1) > 0.1: 
                t_x.append(ox2); t_y.append(oy2); t_z.append(oz2); t_val.append(f"{v2:.1f}")
            elif abs(v2) > 0.1 and abs(v1) <= 0.1:
                t_x.append(ox2); t_y.append(oy2); t_z.append(oz2); t_val.append(f"{v2:.1f}")

            if t_x:
                fig.add_trace(go.Scatter3d(x=t_x, y=t_y, z=t_z, mode='text', text=t_val, textposition="top center", textfont=dict(color=cor, size=11, family="Arial Black"), showlegend=False))

        if "Normal" in tipo_diagrama:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='royalblue', width=4), name='Tração (+)'))
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='crimson', width=4), name='Compressão (-)'))
        elif "Cortante" in tipo_diagrama:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='seagreen', width=4), name='Cortante'))
        else:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='darkorange', width=4), name='Momento Fletor'))
            
        fig.update_layout(showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"))

    # Controlo de Camaras Ortogonais (Geometria 2D vs 3D Isometrica)
    if vista_camera == "frontal":
        fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=0, y=-2.0, z=0), projection=dict(type="orthographic")))
    elif vista_camera == "superior":
        fig.update_layout(scene_camera=dict(up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0), eye=dict(x=0, y=0, z=2.0), projection=dict(type="orthographic")))
    elif vista_camera == "lateral":
        fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=2.0, y=0, z=0), projection=dict(type="orthographic")))

    fig.update_layout(scene=dict(xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)', aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0), height=600)
    return fig

# =========================================================================================
# GERADORES DE RELATÓRIO
# =========================================================================================

def gerar_relatorio_txt(dados, res_analise, resultados_comp, tudo_aprovado, tolerancia):
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    status_global = "APROVADA" if tudo_aprovado else "REPROVADA (Requer revisão de perfis)"
    aco = PROPRIEDADES_ACO[dados['tipo_aco']]
    fy_mpa, fy_kncm2, gamma_a1 = aco['fy'], aco['fy'] / 10.0, 1.10
    
    relatorio = f"""=========================================================
      MEMÓRIA DE CÁLCULO ESTRUTURAL DETALHADA
=========================================================
Data de Geração: {data_atual}
Projeto: {dados.get('nome_projeto', 'Não informado')}
Local: {dados.get('cidade', 'Não informada')}
Status Global da Estrutura: {status_global}
Tolerância de Aprovação Aplicada: +{tolerancia:.1f}%

1. DADOS GEOMÉTRICOS E DE CONTORNO
---------------------------------------------------------
- Sistema Principal: {dados['sistema_principal']}
"""
    if dados['sistema_principal'] != "Mão Francesa / Suporte (Plano 2D)":
        relatorio += f"- Tipo de Pilar: {dados['tipo_pilar']}\n"
    relatorio += f"""- Vão Transversal (X): {dados['vao_x']:.2f} m
- Altura (Z): {dados['altura_z']:.2f} m
- Largura de Influência / Espaçamento: {dados['espacamento']:.2f} m
"""
    if dados['sistema_principal'] not in ["Mão Francesa / Suporte (Plano 2D)"]:
        relatorio += f"- Comprimento Longitudinal (Y): {dados['comp_y']:.2f} m\n"
        if dados['sistema_principal'] == "Mezanino / Passarela Metálica":
            relatorio += f"- Espaçamento entre Vigotas Transversais: {dados['espacamento_vigota']:.2f} m\n- Tipo de Piso: {dados['tipo_piso']}\n"

    relatorio += f"""
2. CARGAS DE PROJETO (ELU - NBR 6120 / NBR 8800)
---------------------------------------------------------
- Carga Permanente Total (G): {dados['g_total']:.2f} kN/m²
- Sobrecarga Normativa de Uso (Q): {dados['q_sobre']:.2f} kN/m²
>> CARGA DE PROJETO COMBINADA (ELU): {dados['q_elu']:.2f} kN/m²

3. ESFORÇOS SOLICITANTES MÁXIMOS GLOBAIS
---------------------------------------------------------
- Esforço Normal Máximo (N_sd): {res_analise.get('n_max_kn', 0.0):.2f} kN
- Esforço Cortante Máximo (V_sd): {res_analise.get('v_max_kn', 0.0):.2f} kN
- Momento Fletor Máximo (M_sd): {res_analise.get('m_max_knm', 0.0):.2f} kNm
- Deslocamento Máximo (Flecha ELS): {res_analise.get('desloc_max_mm', 0.0):.2f} mm

4. TABELA DE ESFORÇOS EXTREMOS BIAXIAIS (LEGENDAS)
---------------------------------------------------------
"""
    for grp, esf in res_analise.get('esforcos_grupos', {}).items():
        if esf.get("n_pos", -1e9) == -1e9: continue
        relatorio += f"[{grp.upper()}]\n"
        relatorio += f"  Normal (N)   -> Máx (Tração): {esf.get('n_pos', 0.0):.2f} kN | Mín (Comp): {esf.get('n_neg', 0.0):.2f} kN\n"
        relatorio += f"  Cortante (V) -> Máx: {esf.get('v_pos', 0.0):.2f} kN | Mín: {esf.get('v_neg', 0.0):.2f} kN\n"
        relatorio += f"  Momento FORTE(Mx) -> Máx (+): {esf.get('my_pos', 0.0):.2f} kNm | Mín (-): {esf.get('my_neg', 0.0):.2f} kNm\n"
        relatorio += f"  Momento FRACO(My) -> Máx (+): {esf.get('mz_pos', 0.0):.2f} kNm | Mín (-): {esf.get('mz_neg', 0.0):.2f} kNm\n"
        relatorio += f"  Flecha Máx        -> {esf.get('d_max', 0.0):.2f} mm\n\n"

    relatorio += f"""
5. VERIFICAÇÃO DETALHADA BIAXIAL POR COMPONENTE (NBR 8800)
---------------------------------------------------------
Propriedades do Material: {dados['tipo_aco']} (fy = {fy_mpa} MPa = {fy_kncm2:.1f} kN/cm²)
Coeficiente de Minoração (γ_a1) = {gamma_a1}

"""
    for v in resultados_comp:
        perf = CATALOGO_COMPLETO[v['perfil']]
        A, Wx, Wy = perf['A'], perf['Wx'], perf.get('Wy', 0.1)
        d, tw = perf['d'] / 10.0, perf['tw'] / 10.0
        Av = d * tw
        status_comp = "APROVADO (COM TOLERÂNCIA)" if v['aprovado'] and v['taxa_maxima'] > 100.0 else ("APROVADO" if v['aprovado'] else "REPROVADO")

        relatorio += f"[{v['componente'].upper()}]\n  Perfil Selecionado: {v['perfil']} ({v['familia']})\n"
        relatorio += f"  A. ESFORÇOS ATUANTES MÁXIMOS EM MÓDULO ABSOLUTO (Sd)\n"
        relatorio += f"     N_Sd (Tração) = {v.get('N_trac_sd', 0.0):.2f} kN | N_Sd (Compressão) = {v.get('N_comp_sd', 0.0):.2f} kN\n"
        relatorio += f"     V_Sd = {v.get('V_sd', 0.0):.2f} kN\n"
        relatorio += f"     M_Sd,x (Eixo Forte) = {v.get('My_sd', 0.0):.2f} kNm | M_Sd,y (Eixo Fraco) = {v.get('Mz_sd', 0.0):.2f} kNm\n\n"
        relatorio += f"  B. PROPRIEDADES GEOMÉTRICAS DA SEÇÃO\n"
        relatorio += f"     Área Bruta (A) = {A:.2f} cm² | Área de Cisalhamento Efetiva (Av) = {Av:.2f} cm²\n"
        relatorio += f"     Mód. Resistente: Wx (Forte) = {Wx:.2f} cm³ | Wy (Fraco) = {Wy:.2f} cm³\n"
        relatorio += f"     Raios de Giração: rx = {v.get('rx', 0.0):.2f} cm | ry = {v.get('ry', 0.0):.2f} cm\n\n"
        relatorio += f"  C. ANÁLISE DE FLAMBAGEM GLOBAL E ESBELTEZ\n"
        relatorio += f"     Índice de Esbeltez (λ) = {v.get('esbeltez_max', 0.0):.1f} (Limite: 200)\n"
        relatorio += f"     Fator de Redução de Compressão (χ) = {v.get('chi', 1.0):.3f}\n\n"
        relatorio += f"  D. VERIFICAÇÕES DE RESISTÊNCIA E FLECHA\n"
        relatorio += f"     Resistência Tracionada (N_Rd,t = {v.get('N_rd_trac', 0.0):.2f} kN) -> Taxa: {v.get('ratio_N_trac', 0.0):.1f}%\n"
        relatorio += f"     Resistência Comprimida (N_Rd,c = {v.get('N_rd_comp', 0.0):.2f} kN) -> Taxa: {v.get('ratio_N_comp', 0.0):.1f}%\n"
        relatorio += f"     Cisalhamento (V_Rd = {v.get('V_rd', 0.0):.2f} kN): V_Sd/V_Rd = {v.get('ratio_V', 0.0):.1f}%\n"
        relatorio += f"     Flexão Forte (M_Rd,x = {v.get('M_rd_x', 0.0):.2f} kNm): M_Sd,x/M_Rd,x = {v.get('ratio_Mx', 0.0):.1f}%\n"
        relatorio += f"     Flexão Fraca (M_Rd,y = {v.get('M_rd_y', 0.0):.2f} kNm): M_Sd,y/M_Rd,y = {v.get('ratio_My', 0.0):.1f}%\n"
        relatorio += f"     Interação Flexo-Compressão Biaxial: Taxa Integrada = {v.get('taxa_interacao', 0.0):.1f}%\n"
        relatorio += f"     Flecha (L_vão = {v.get('L_teorico_m', 0.0):.2f} m | δ_lim = {v.get('delta_lim_mm', 0.0):.1f} mm): {v.get('D_sd', 0.0):.2f} / {v.get('delta_lim_mm', 1.0):.1f} = {v.get('ratio_delta', 0.0):.1f}%\n\n"
        relatorio += f"  >> STATUS DA PEÇA: {status_comp} (Taxa Máxima: {v.get('taxa_maxima', 0.0):.1f}%)\n.........................................................\n\n"
    return relatorio

def gerar_relatorio_pdf_avancado(dados, res_analise, resultados_comp, incluir_graficos=True):
    if FPDF is None: return None
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Capa e Texto Padrão
    texto = gerar_relatorio_txt(dados, res_analise, resultados_comp, True, 2.0)
    pdf.add_page()
    pdf.set_font("Courier", size=9) 
    for linha in texto.split('\n'):
        pdf.multi_cell(0, 5, txt=linha.encode('latin-1', 'replace').decode('latin-1'))
        
    if incluir_graficos and res_analise:
        # 2. Vistas Geométricas da Estrutura
        pdf.add_page()
        pdf.set_font("Courier", 'B', 12)
        pdf.cell(0, 10, "6. ANEXO A - VISTAS GEOMETRICAS DA ESTRUTURA", ln=True)
        pdf.set_font("Courier", size=9)
        
        vistas = [
            ("Vista Isometrica 3D", "iso"),
            ("Vista Frontal (Plano XZ)", "frontal"),
            ("Vista Superior (Plano XY)", "superior"),
            ("Vista Lateral (Plano YZ)", "lateral")
        ]
        
        for nome_vista, cam in vistas:
            fig = desenhar_diagrama(res_analise, "Geometria (Apenas Linhas)", cam)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                fig.write_image(tmp.name, width=800, height=450)
                pdf.cell(0, 10, f"-> {nome_vista}:", ln=True)
                pdf.image(tmp.name, x=10, w=190)
                tmp_path = tmp.name
            if os.path.exists(tmp_path): os.unlink(tmp_path)
            
        # 3. Diagramas de Esforços Globais
        pdf.add_page()
        pdf.set_font("Courier", 'B', 12)
        pdf.cell(0, 10, "7. ANEXO B - DIAGRAMAS DE ESFORCOS", ln=True)
        pdf.set_font("Courier", size=9)
        
        diagramas = ["Deslocamentos (Deformada)", "Esforço Normal (Tração/Compressão)", "Momento Fletor (My)", "Reações de Apoio"]
        for diag in diagramas:
            fig = desenhar_diagrama(res_analise, diag, "iso")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                fig.write_image(tmp.name, width=800, height=450)
                pdf.cell(0, 10, f"-> {diag}:", ln=True)
                pdf.image(tmp.name, x=10, w=190)
                tmp_path = tmp.name
            if os.path.exists(tmp_path): os.unlink(tmp_path)
            
        # 4. Desenho das Seções Transversais Individuais
        pdf.add_page()
        pdf.set_font("Courier", 'B', 12)
        pdf.cell(0, 10, "8. ANEXO C - GEOMETRIA DETALHADA DAS SECOES", ln=True)
        pdf.set_font("Courier", size=9)
        
        perfis_desenhados = set()
        for v in resultados_comp:
            nome_perfil = v['perfil']
            if nome_perfil in perfis_desenhados: continue
            perfis_desenhados.add(nome_perfil)
            
            fig_sec = desenhar_secao_transversal(nome_perfil)
            if fig_sec:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    fig_sec.write_image(tmp.name, width=400, height=400)
                    pdf.ln(5)
                    pdf.cell(0, 10, f"Geometria 2D do Perfil Aplicado: {nome_perfil} ({v['componente']})", ln=True)
                    pdf.image(tmp.name, x=50, w=100)
                    tmp_path = tmp.name
                if os.path.exists(tmp_path): os.unlink(tmp_path)

    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)

# =========================================================================================
# FUNÇÃO PRINCIPAL UI STREAMLIT
# =========================================================================================

def main():
    st.title("🏗️ Dimensionamento de Estruturas Metálicas")
    st.caption("Conformidade: NBR 8800 | NBR 6120 | NBR 6123")

    if "res_analise" not in st.session_state:
        st.session_state.res_analise = None

    st.sidebar.title("Identificação da Obra")
    nome_projeto = st.sidebar.text_input("Nome do Projeto", value="Projeto Estrutural")
    cidade = st.sidebar.text_input("Cidade/Local", value="")
    st.sidebar.markdown("---")

    st.sidebar.title("Configurações Gerais")
    sistema_principal = st.sidebar.selectbox("Sistema Principal", ["Pórtico Alma Cheia", "Tesoura Plana (Treliçada)", "Arco", "Mezanino / Passarela Metálica", "Mão Francesa / Suporte (Plano 2D)"])
    
    if sistema_principal != "Mão Francesa / Suporte (Plano 2D)":
        tipo_pilar = st.sidebar.selectbox("Tipo de Pilar/Suporte", ["Pilar Metálico", "Pilar de Concreto Armado", "Sem Pilar"])
        distribuicao_pilares = "Em todos os pórticos"
        if tipo_pilar != "Sem Pilar":
            distribuicao_pilares = st.sidebar.selectbox("Distribuição de Pilares", ["Em todos os pórticos", "Apenas nos 4 cantos extremos"])
    else:
        tipo_pilar = "Pilar Metálico"
        distribuicao_pilares = "N/A"

    n_paineis = 6
    espacamento_vigota = 1.0
    forma_cobertura = "2 Águas"
    inclinacao = 10.0
    flecha_arco = 3.0

    if sistema_principal == "Mezanino / Passarela Metálica":
        espacamento_vigota = st.sidebar.number_input("Espaçamento Vigotas Transversais [m]", min_value=0.40, max_value=3.00, value=1.00, step=0.10)
    elif sistema_principal not in ["Arco", "Mão Francesa / Suporte (Plano 2D)"]:
        forma_cobertura = st.sidebar.selectbox("Forma da Cobertura", ["2 Águas", "1 Água"])
        inclinacao = st.sidebar.number_input("Inclinação do Telhado [%]", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        if sistema_principal == "Tesoura Plana (Treliçada)":
            n_paineis = st.sidebar.slider("Número de Painéis da Treliça", min_value=2, max_value=60, value=6, step=2)
    elif sistema_principal == "Arco":
        flecha_arco = st.sidebar.number_input("Flecha do Arco (m)", min_value=1.0, max_value=20.0, value=3.0, step=0.5)

    vao_x = st.sidebar.number_input("Vão Transversal (X) [m]", value=15.0 if sistema_principal not in ["Mezanino / Passarela Metálica", "Mão Francesa / Suporte (Plano 2D)"] else 6.0)
    comp_y = st.sidebar.number_input("Comprimento Longitudinal (Y) [m]", value=30.0 if sistema_principal != "Mezanino / Passarela Metálica" else 12.0) if sistema_principal != "Mão Francesa / Suporte (Plano 2D)" else 0.0
    altura_z = st.sidebar.number_input("Pé-direito / Altura (Z) [m]", value=6.0 if sistema_principal not in ["Mezanino / Passarela Metálica", "Mão Francesa / Suporte (Plano 2D)"] else 3.0)
    espacamento_label = "Largura de Influência [m] (Carga)" if sistema_principal == "Mão Francesa / Suporte (Plano 2D)" else "Espaçamento entre Pórticos [m]"
    espacamento = st.sidebar.number_input(espacamento_label, value=5.0 if sistema_principal != "Mezanino / Passarela Metálica" else 3.0)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Perfis Estruturais")
    tipo_aco = st.sidebar.selectbox("Aço Estrutural", list(PROPRIEDADES_ACO.keys()))
    lista_perfis = list(CATALOGO_COMPLETO.keys())
    
    if sistema_principal == "Mezanino / Passarela Metálica":
        perf_pil = st.sidebar.selectbox("Pilares", lista_perfis, index=lista_perfis.index("W 200 x 22.5") if "W 200 x 22.5" in lista_perfis else 0) if tipo_pilar == "Pilar Metálico" else None
        perf_v_prin = st.sidebar.selectbox("Vigas Principais (Longitudinais)", lista_perfis, index=lista_perfis.index("W 360 x 122 (Remontado)") if "W 360 x 122 (Remontado)" in lista_perfis else 0)
        perf_v_sec = st.sidebar.selectbox("Vigas Secundárias (Transversais)", lista_perfis, index=lista_perfis.index("W 150 x 18.0") if "W 150 x 18.0" in lista_perfis else 0)
        mapa_perfis = {"Pilares Metálicos": perf_pil, "Vigas Principais (Longitudinais)": perf_v_prin, "Vigas Secundárias (Transversais)": perf_v_sec}
    elif sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
        perf_pil = st.sidebar.selectbox("Fixação / Perfil Vertical", lista_perfis, index=lista_perfis.index("U 150 x 50 x 3.00") if "U 150 x 50 x 3.00" in lista_perfis else 0)
        perf_v_prin = st.sidebar.selectbox("Viga Horizontal", lista_perfis, index=lista_perfis.index("U 150 x 50 x 3.00") if "U 150 x 50 x 3.00" in lista_perfis else 0)
        perf_diag = st.sidebar.selectbox("Diagonal (Escora/Tirante)", lista_perfis, index=lista_perfis.index('2x L 2" x 3/16" (Dupla)') if '2x L 2" x 3/16" (Dupla)' in lista_perfis else 0)
        mapa_perfis = {"Pilares Metálicos": perf_pil, "Vigas Principais (Longitudinais)": perf_v_prin, "Diagonais": perf_diag}
    else:
        perf_pil = st.sidebar.selectbox("Pilares", lista_perfis, index=lista_perfis.index("W 250 x 25.3") if "W 250 x 25.3" in lista_perfis else 0) if tipo_pilar == "Pilar Metálico" else None
        perf_terca = st.sidebar.selectbox("Terças de Cobertura", lista_perfis, index=lista_perfis.index("U 100 x 50 x 2.25") if "U 100 x 50 x 2.25" in lista_perfis else 0)
        perf_bz_sup = st.sidebar.selectbox("Banzo Superior", lista_perfis, index=lista_perfis.index("U 100 x 50 x 3.00") if "U 100 x 50 x 3.00" in lista_perfis else 0)
        perf_bz_inf = st.sidebar.selectbox("Banzo Inferior", lista_perfis, index=lista_perfis.index("U 100 x 50 x 3.00") if "U 100 x 50 x 3.00" in lista_perfis else 0)
        perf_diag = st.sidebar.selectbox("Diagonais", lista_perfis, index=lista_perfis.index('2x L 2" x 3/16" (Dupla)') if '2x L 2" x 3/16" (Dupla)' in lista_perfis else 0)
        perf_mont = st.sidebar.selectbox("Montantes", lista_perfis, index=lista_perfis.index("2x L 2.1/2\" x 1/4\" (Dupla)") if "2x L 2.1/2\" x 1/4\" (Dupla)" in lista_perfis else 0)
        mapa_perfis = {"Pilares Metálicos": perf_pil, "Terças de Cobertura": perf_terca, "Banzo Superior": perf_bz_sup, "Banzo Inferior": perf_bz_inf, "Diagonais": perf_diag, "Montantes": perf_mont}

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Giro dos Eixos Locais (Beta)")
    angulos_grupos = {}
    for grupo in mapa_perfis.keys():
        angulos_grupos[grupo] = st.sidebar.number_input(f"Giro: {grupo} [°]", min_value=-360.0, max_value=360.0, value=0.0, step=45.0)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Condições e Aceitação")
    apoios_base = st.sidebar.selectbox("Vínculos na Base / Apoios", ["Engastado (Trava Translações e Rotações)", "Articulado (Trava apenas Translações)"])
    tolerancia_aceitacao = st.sidebar.number_input("Tolerância de Aceitação Máxima [%]", min_value=0.0, max_value=20.0, value=2.0, step=0.5)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌪️ Cargas / Vento")
    if sistema_principal == "Mezanino / Passarela Metálica":
        tipo_piso = st.sidebar.selectbox("Tipo de Piso", ["Painel Wall / Masterboard (0.30 kN/m²)", "Steel Deck + Concreto (2.00 kN/m²)", "Chapa Xadrez Metálica (0.40 kN/m²)", "Painel OSB / Madeira (0.25 kN/m²)"])
        sobrecarga_opcao = st.sidebar.selectbox("Uso / Sobrecarga", ["Escritórios / Leve (2.50 kN/m²)", "Residencial (1.50 kN/m²)", "Comercial / Lojas (3.00 kN/m²)", "Depósito Leve (4.00 kN/m²)", "Depósito Pesado (5.00 kN/m²)", "Passarela - Manutenção/Sem Público (2.50 kN/m²)", "Passarela - Acesso Público (3.00 kN/m²)", "Academias / Ginástica (5.00 kN/m²)"])
        peso_piso = float(tipo_piso.split("(")[1].split(" ")[0])
        carga_inst = 0.15
        g_total = peso_piso + carga_inst
        q_sobre = float(sobrecarga_opcao.split("(")[1].split(" ")[0])
        q_vento_liquido = 0.0
        q_elu = (1.25 * g_total) + (1.50 * q_sobre)
    elif sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
        carga_permanente = st.sidebar.number_input("Carga Permanente Distribuída (G) [kN/m²]", min_value=0.0, value=0.50, step=0.10)
        q_sobre = st.sidebar.number_input("Sobrecarga de Utilização (Q) [kN/m²]", min_value=0.0, value=1.50, step=0.10)
        g_total = carga_permanente
        q_vento_liquido = 0.0
        q_elu = (1.25 * g_total) + (1.50 * q_sobre)
    else:
        tipo_telha = st.sidebar.selectbox("Tipo de Cobertura", ["Trapezoidal (0.05 kN/m²)", "Termoacústica (0.15 kN/m²)", "Fibrocimento (0.18 kN/m²)"])
        carga_inst = st.sidebar.number_input("Carga Instalações [kN/m²]", min_value=0.0, value=0.10, step=0.02)
        q_sobre = st.sidebar.number_input("Sobrecarga [kN/m²]", min_value=0.0, value=0.25, step=0.05)
        v0 = st.sidebar.number_input("Velocidade V0 [m/s]", min_value=30.0, max_value=60.0, value=40.0, step=1.0)
        cpe = st.sidebar.number_input("Coef. Pressão Externa (Cpe)", min_value=-2.0, max_value=2.0, value=-0.80, step=0.10)
        cpi = st.sidebar.number_input("Coef. Pressão Interna (Cpi)", min_value=-1.0, max_value=1.0, value=0.20, step=0.10)
        peso_telha = float(tipo_telha.split("(")[1].split(" ")[0])
        g_total = peso_telha + carga_inst 
        q_vento_liquido = (0.613 * (v0 ** 2) / 1000) * (cpe - cpi) * 1.20
        q_elu = (1.25 * g_total) + (1.50 * q_sobre) + (1.40 * abs(q_vento_liquido))

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📐 Geometria", "🌪️ Cargas", "⚙️ Análise", "✅ Verificação", "📊 Diagramas", "📦 BIM"])

    if sistema_principal == "Mão Francesa / Suporte (Plano 2D)": y_coords = [0.0]
    else: y_coords = np.arange(0, comp_y + espacamento, espacamento); y_coords[-1] = comp_y if y_coords[-1] != comp_y else y_coords[-1]
        
    all_x, all_y, all_z, edges_raw = [], [], [], []
    has_pillar = (tipo_pilar != "Sem Pilar")
    
    dict_nos = {}
    def add_no(x, y, z):
        pt = (round(x, 3), round(y, 3), round(z, 3))
        if pt not in dict_nos:
            dict_nos[pt] = len(dict_nos)
            all_x.append(pt[0]); all_y.append(pt[1]); all_z.append(pt[2])
        return dict_nos[pt]

    apoios_idx = set()

    if sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
        n_tE = add_no(0, 0, altura_z)
        n_tD = add_no(vao_x, 0, altura_z)
        n_bE = add_no(0, 0, 0)
        edges_raw.append({"n1": n_bE, "n2": n_tE, "grupo": "Pilares Metálicos"})
        edges_raw.append({"n1": n_tE, "n2": n_tD, "grupo": "Vigas Principais (Longitudinais)"})
        edges_raw.append({"n1": n_bE, "n2": n_tD, "grupo": "Diagonais"})
        apoios_idx.update([n_tE, n_bE])
    elif sistema_principal == "Mezanino / Passarela Metálica":
        y_vigotas = np.arange(0, comp_y + espacamento_vigota, espacamento_vigota)
        y_vigotas[-1] = comp_y if y_vigotas[-1] != comp_y else y_vigotas[-1]
        for y_v in y_vigotas: edges_raw.append({"n1": add_no(0, y_v, altura_z), "n2": add_no(vao_x, y_v, altura_z), "grupo": "Vigas Secundárias (Transversais)"})
        for i in range(len(y_vigotas) - 1):
            edges_raw.append({"n1": add_no(0, y_vigotas[i], altura_z), "n2": add_no(0, y_vigotas[i+1], altura_z), "grupo": "Vigas Principais (Longitudinais)"})
            edges_raw.append({"n1": add_no(vao_x, y_vigotas[i], altura_z), "n2": add_no(vao_x, y_vigotas[i+1], altura_z), "grupo": "Vigas Principais (Longitudinais)"})
        for i_y, y_p in enumerate(y_coords):
            if distribuicao_pilares == "Em todos os pórticos" or i_y == 0 or i_y == (len(y_coords) - 1):
                n_tE, n_tD = add_no(0, y_p, altura_z), add_no(vao_x, y_p, altura_z)
                if has_pillar:
                    n_bE, n_bD = add_no(0, y_p, 0), add_no(vao_x, y_p, 0)
                    grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                    edges_raw.extend([{"n1": n_bE, "n2": n_tE, "grupo": grp_pilar}, {"n1": n_bD, "n2": n_tD, "grupo": grp_pilar}])
                    apoios_idx.update([n_bE, n_bD])
                else: apoios_idx.update([n_tE, n_tD])
    else:
        cobertura_por_frame = []
        for i_y, y in enumerate(y_coords):
            is_supported = (distribuicao_pilares == "Em todos os pórticos" or i_y == 0 or i_y == (len(y_coords) - 1))
            if sistema_principal == "Arco":
                x_arco = list(np.linspace(0, vao_x, 9))
                n_arco_ids = [add_no(x, y, altura_z + flecha_arco * (1 - (2*(x-vao_x/2)/vao_x)**2)) for x in x_arco]
                for i in range(8): edges_raw.append({"n1": n_arco_ids[i], "n2": n_arco_ids[i+1], "grupo": "Banzo Superior"})
                if is_supported:
                    n_tE, n_tD = n_arco_ids[0], n_arco_ids[-1]
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.extend([{"n1": n_bE, "n2": n_tE, "grupo": grp_pilar}, {"n1": n_bD, "n2": n_tD, "grupo": grp_pilar}])
                        apoios_idx.update([n_bE, n_bD])
                    else: apoios_idx.update([n_tE, n_tD])
                cobertura_por_frame.append(n_arco_ids)
            elif sistema_principal == "Tesoura Plana (Treliçada)":
                if forma_cobertura == "1 Água":
                    x_sub = np.linspace(0, vao_x, n_paineis + 1)
                    x_pts, z_pts = list(x_sub) + list(x_sub), [altura_z] * (n_paineis + 1) + list(altura_z + (vao_x - x_sub) * (inclinacao / 100.0))
                else:
                    n_lado = n_paineis // 2
                    x_all = np.concatenate([np.linspace(0, vao_x/2, n_lado + 1), np.linspace(vao_x/2, vao_x, n_lado + 1)[1:]])
                    z_sup_local = np.where(x_all <= vao_x/2, altura_z + x_all*(inclinacao/100.0), altura_z + (vao_x-x_all)*(inclinacao/100.0))
                    x_pts, z_pts = list(x_all) + list(x_all), [altura_z] * len(x_all) + list(z_sup_local)
                n_trel_ids = [add_no(x, y, z) for x, z in zip(x_pts, z_pts)]
                idx_inf, idx_sup = n_trel_ids[:len(n_trel_ids)//2], n_trel_ids[len(n_trel_ids)//2:]
                for i in range(len(idx_inf)-1):
                    edges_raw.extend([{"n1": idx_inf[i], "n2": idx_inf[i+1], "grupo": "Banzo Inferior"}, {"n1": idx_sup[i], "n2": idx_sup[i+1], "grupo": "Banzo Superior"}, {"n1": idx_inf[i], "n2": idx_sup[i], "grupo": "Montantes"}])
                    if forma_cobertura == "1 Água" or i < (len(idx_inf)-1)//2: edges_raw.append({"n1": idx_inf[i], "n2": idx_sup[i+1], "grupo": "Diagonais"})
                    else: edges_raw.append({"n1": idx_inf[i+1], "n2": idx_sup[i], "grupo": "Diagonais"})
                edges_raw.append({"n1": idx_inf[-1], "n2": idx_sup[-1], "grupo": "Montantes"})
                if is_supported:
                    n_tE, n_tD = idx_inf[0], idx_inf[-1]
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.extend([{"n1": n_bE, "n2": n_tE, "grupo": grp_pilar}, {"n1": n_bD, "n2": n_tD, "grupo": grp_pilar}])
                        apoios_idx.update([n_bE, n_bD])
                    else: apoios_idx.update([n_tE, n_tD])
                cobertura_por_frame.append(idx_sup)
            else: 
                n_tE, n_tD = add_no(0, y, altura_z), add_no(vao_x, y, altura_z)
                if forma_cobertura == "2 Águas":
                    n_cum = add_no(vao_x/2, y, altura_z + (vao_x / 2.0) * (inclinacao / 100.0))
                    edges_raw.extend([{"n1": n_tE, "n2": n_cum, "grupo": "Banzo Superior"}, {"n1": n_cum, "n2": n_tD, "grupo": "Banzo Superior"}])
                    cobertura_por_frame.append([n_tE, n_cum, n_tD])
                else:
                    n_cum = add_no(vao_x, y, altura_z + vao_x * (inclinacao / 100.0))
                    edges_raw.append({"n1": n_tE, "n2": n_cum, "grupo": "Banzo Superior"})
                    cobertura_por_frame.append([n_tE, n_cum])
                edges_raw.append({"n1": n_tE, "n2": n_tD, "grupo": "Banzo Inferior"})
                if is_supported:
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.extend([{"n1": n_bE, "n2": n_tE, "grupo": grp_pilar}, {"n1": n_bD, "n2": n_tD, "grupo": grp_pilar}])
                        apoios_idx.update([n_bE, n_bD])
                    else: apoios_idx.update([n_tE, n_tD])
        for i in range(len(cobertura_por_frame) - 1):
            for p in range(len(cobertura_por_frame[i])):
                if p < len(cobertura_por_frame[i+1]): edges_raw.append({"n1": cobertura_por_frame[i][p], "n2": cobertura_por_frame[i+1][p], "grupo": "Terças de Cobertura"})

    barras_prontas = []
    barras_visualizacao = []
    
    for edge in edges_raw:
        grp = edge["grupo"]
        barras_visualizacao.append({"n1": edge["n1"], "n2": edge["n2"], "grupo": grp})
        if grp == "Pilares Concreto":
            barras_prontas.append({"n1": edge["n1"], "n2": edge["n2"], "grupo": grp, "A": 0.16, "Iy": 0.002, "Iz": 0.002, "J": 0.002, "ang": 0.0, "perfil_nome": "Concreto"})
            continue
        nome_perf = mapa_perfis.get(grp)
        if nome_perf is None: continue 
        props = obter_propriedades(nome_perf)
        ang = angulos_grupos.get(grp, 0.0)
        barras_prontas.append({
            "n1": edge["n1"], "n2": edge["n2"], "grupo": grp, 
            "A": props["A"], "Iy": props["Iy"], "Iz": props["Iz"], "J": props["J"], 
            "ang": ang, "perfil_nome": nome_perf
        })

    with tab1:
        fig = go.Figure()
        for b in barras_visualizacao:
            x1, y1, z1 = all_x[b["n1"]], all_y[b["n1"]], all_z[b["n1"]]
            x2, y2, z2 = all_x[b["n2"]], all_y[b["n2"]], all_z[b["n2"]]
            line_color = 'gray' if b["grupo"] == "Pilares Concreto" else 'blue'
            line_width = 8 if b["grupo"] == "Pilares Concreto" else 4
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color=line_color, width=line_width), showlegend=False))
        fig.update_layout(scene=dict(xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)', aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0), height=550)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("🌪️ Detalhamento de Cargas (ELU)")
        st.info(f"**Carga de Projeto Total (q_ELU):** {q_elu:.2f} kN/m²")
        if sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
            st.success(f"Carga Linear aplicada na viga principal: **{q_elu * espacamento:.2f} kN/m**")

    with tab3:
        st.subheader("⚙️ Análise Estrutural Matricial")
        if st.button("🚀 Executar Análise com Matriz Específica", type="primary"):
            with st.spinner("Montando matriz global de rigidez ponderada..."):
                motor = MotorCalculo3D()
                motor.construir_malha(all_x, all_y, all_z, barras_prontas, list(apoios_idx), apoios_base)
                espacamento_calc = espacamento_vigota if sistema_principal == "Mezanino / Passarela Metálica" else espacamento
                motor.aplicar_carga_distribuida(q_elu, vao_x, espacamento_calc)
                st.session_state.res_analise = motor.resolver()
        if st.session_state.res_analise:
            if st.session_state.res_analise.get("sucesso"): st.success("✅ Análise Concluída com sucesso!")
            else: st.error(f"❌ Erro na análise: {st.session_state.res_analise.get('erro')}")

    with tab4:
        st.subheader("✅ Verificação Biaxial Integrada e Flambagem (NBR 8800)")
        if not st.session_state.res_analise: st.warning("Execute a Análise na Aba 3 para habilitar as verificações.")
        elif not st.session_state.res_analise.get("sucesso"): st.error("A análise falhou.")
        else:
            res = st.session_state.res_analise
            verificador = VerificadorNBR8800(tipo_aco)
            resultados_comp = []
            tudo_aprovado = True

            for grupo, esf_grp in res.get("esforcos_grupos", {}).items():
                nome_perfil = mapa_perfis.get(grupo)
                if nome_perfil is None: continue 
                
                if sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
                    L_teorico = vao_x if grupo == "Vigas Principais (Longitudinais)" else (altura_z if "Pilares" in grupo else esf_grp.get("L_max", vao_x))
                else:
                    if grupo == "Vigas Secundárias (Transversais)": L_teorico = vao_x
                    elif grupo == "Vigas Principais (Longitudinais)": L_teorico = comp_y if distribuicao_pilares == "Apenas nos 4 cantos extremos" else espacamento
                    elif "Pilares" in grupo: L_teorico = altura_z
                    elif grupo == "Terças de Cobertura": L_teorico = espacamento
                    elif grupo in ["Banzo Superior", "Banzo Inferior"]: L_teorico = vao_x
                    else: L_teorico = esf_grp.get("L_max", vao_x)
                        
                N_trac = max(0.0, esf_grp.get("n_pos", 0.0))
                N_comp = abs(min(0.0, esf_grp.get("n_neg", 0.0)))

                v = verificador.verificar_elemento(
                    nome_perfil, N_trac, N_comp, esf_grp.get("v_max", 0.0), esf_grp.get("my_max", esf_grp.get("m_max", 0.0)), 
                    esf_grp.get("mz_max", 0.0), esf_grp.get("d_max", 0.0), L_teorico, 1.0 
                )
                
                v["componente"] = grupo
                v["N_sd"] = max(N_trac, N_comp)
                v["N_trac_sd"], v["N_comp_sd"] = N_trac, N_comp
                v["V_sd"] = esf_grp.get("v_max", 0.0)
                v["My_sd"], v["Mz_sd"] = esf_grp.get("my_max", esf_grp.get("m_max", 0.0)), esf_grp.get("mz_max", 0.0)
                v["D_sd"] = esf_grp.get("d_max", 0.0)
                v["L_teorico_m"] = L_teorico
                
                if v["taxa_maxima"] <= (100.0 + tolerancia_aceitacao) and v["esbeltez_max"] <= 200.0: v["aprovado"] = True
                else: v["aprovado"] = False; tudo_aprovado = False

                resultados_comp.append(v)

            if tudo_aprovado: st.success("### 🎉 TODOS OS PERFIS FORAM APROVADOS!")
            elif len(resultados_comp) > 0: st.error("### ❌ HÁ PERFIS REPROVADOS!")
            
            if len(resultados_comp) > 0:
                st.markdown("---")
                dados_r = {
                    "nome_projeto": nome_projeto,
                    "cidade": cidade,
                    "sistema_principal": sistema_principal, "tipo_pilar": tipo_pilar, 
                    "distribuicao_pilares": distribuicao_pilares, "vao_x": vao_x, "comp_y": comp_y, 
                    "altura_z": altura_z, "espacamento": espacamento, "espacamento_vigota": espacamento_vigota,
                    "g_total": g_total, "q_sobre": q_sobre, "q_elu": q_elu, "tipo_aco": tipo_aco, 
                    "q_vento_liquido": q_vento_liquido, "tipo_piso": tipo_piso if sistema_principal == "Mezanino / Passarela Metálica" else "N/A"
                }
                
                # NOVO MENU DE GERAÇÃO DO PDF EXTREMO
                st.subheader("📑 Gerador do Memorial de Cálculo Definitivo (PDF)")
                st.info("Este gerador irá desenhar todas as vistas 2D (Frontal, Lateral, Superior), os diagramas globais e a geometria de secção transversal para cada peça individual. Pode demorar cerca de 15 a 30 segundos.")
                
                if FPDF is not None:
                    if st.button("⚙️ Processar Relatório Gráfico PDF", type="primary"):
                        with st.spinner("A renderizar as plantas, diagramas e vistas 2D... Aguarde."):
                            pdf_bytes = gerar_relatorio_pdf_avancado(dados_r, res, resultados_comp, True)
                            st.session_state['pdf_pronto'] = pdf_bytes
                            st.success("✅ Relatório renderizado com sucesso!")
                    
                    if st.session_state.get('pdf_pronto'):
                        st.download_button(
                            label="📥 Descarregar Memorial Completo (PDF)",
                            data=st.session_state['pdf_pronto'],
                            file_name=f"Memorial_{nome_projeto.replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                
                st.markdown("---")
                for v in resultados_comp:
                    st.write(f"#### 🔹 {v['componente']} — `{v['perfil']}`")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    status_text = "✅ Ok" if v['taxa_maxima'] <= 100 and v['esbeltez_max'] <= 200 else ("⚠️ Ok (Tolerado)" if v['aprovado'] else "❌ Reprovado")
                    c1.metric("Status", status_text)
                    c2.metric("Taxa Integ.", f"{v['taxa_maxima']:.1f}%")
                    c3.metric("Normal", f"{v['ratio_N']:.1f}%")
                    c4.metric("Momento X", f"{v['ratio_Mx']:.1f}%")
                    c5.metric("Esbeltez (λ)", f"{v['esbeltez_max']:.1f}")
                    if v['taxa_maxima'] > 100: st.progress(min(max(int(v['taxa_maxima']), 0), 100))
                    
                    perf = CATALOGO_COMPLETO[v['perfil']]
                    A, Wx, Wy = perf['A'], perf['Wx'], perf.get('Wy', 0.1)
                    d, tw = perf['d'] / 10.0, perf['tw'] / 10.0
                    
                    with st.expander("🧮 Ver Memória de Cálculo Detalhada e Flambagem"):
                        st.markdown(f"""
                        **A. ESFORÇOS ATUANTES MÁXIMOS (Sd)**
                        * **N_Sd (Tração)** = {v['N_trac_sd']:.2f} kN | **N_Sd (Compressão)** = {v['N_comp_sd']:.2f} kN
                        * **V_Sd** = {v['V_sd']:.2f} kN
                        * **M_Sd,x (Forte)** = {v['My_sd']:.2f} kNm | **M_Sd,y (Fraco)** = {v['Mz_sd']:.2f} kNm
                        
                        **B. PROPRIEDADES GEOMÉTRICAS DA SEÇÃO**
                        * **Área Bruta (A)** = {A:.2f} cm² | **Área de Cisalhamento Efetiva (Av)** = {d*tw:.2f} cm²
                        * **Módulos Resistentes:** Wx = {Wx:.2f} cm³ | Wy = {Wy:.2f} cm³
                        * **Raios de Giração:** rx = {v['rx']:.2f} cm | ry = {v['ry']:.2f} cm
                        
                        **C. ANÁLISE DE FLAMBAGEM GLOBAL E ESBELTEZ**
                        * **Índice de Esbeltez (λ):** {v['esbeltez_max']:.1f} (Limite NBR = 200)
                        * **Força Crítica Elástica (Ne):** {v['Ne']:.2f} kN | **Esbeltez Reduzida (λ0):** {v['lambda_0']:.3f}
                        * **Fator de Redução (χ):** **{v['chi']:.3f}**
                        
                        **D. VERIFICAÇÕES DE RESISTÊNCIA E FLECHA**
                        * **Tração (N_Rd,t = {v['N_rd_trac']:.2f} kN):** {v['ratio_N_trac']:.1f}% | **Compressão (N_Rd,c = {v['N_rd_comp']:.2f} kN):** {v['ratio_N_comp']:.1f}%
                        * **Cisalhamento (V_Rd = {v['V_rd']:.2f} kN):** {v['ratio_V']:.1f}%
                        * **Flexão X (M_Rd,x = {v.get('M_rd_x', 0):.2f} kNm):** {v['ratio_Mx']:.1f}% | **Flexão Y (M_Rd,y = {v.get('M_rd_y', 0):.2f} kNm):** {v['ratio_My']:.1f}%
                        * **Interação Flexo-Compressão Biaxial:** **{v.get('taxa_interacao', 0):.1f}%**
                        * **Flecha (δ_lim = {v['delta_lim_mm']:.1f} mm):** {v['D_sd']:.2f} mm ➔ **{v['ratio_delta']:.1f}%**
                        """)
                    st.markdown("---")

    with tab5:
        if st.session_state.res_analise and st.session_state.res_analise.get("sucesso"):
            tipo_diagrama = st.selectbox("Visualizar:", ["Deslocamentos (Deformada)", "Esforço Normal (Tração/Compressão)", "Esforço Cortante (Vz)", "Momento Fletor (My)", "Eixos Locais dos Perfis", "Vista Extrudada (Seções 3D)", "Reações de Apoio"])
            st.plotly_chart(desenhar_diagrama(st.session_state.res_analise, tipo_diagrama))

if __name__ == "__main__":
    main()
