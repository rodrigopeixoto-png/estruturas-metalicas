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

from modules.solver import MotorCalculo3D

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
    "U 75 x 38 x 2.00": {"familia": "Chapa Dobrada U", "d": 75, "bf": 38, "tw": 2.00, "tf": 2.00, "A": 2.80, "Ix": 25.10, "Iy": 4.55, "Wx": 6.60, "Wy": 1.58},
    "U 100 x 40 x 2.25": {"familia": "Chapa Dobrada U", "d": 100, "bf": 40, "tw": 2.25, "tf": 2.25, "A": 3.89, "Ix": 57.67, "Iy": 5.89, "Wx": 11.50, "Wy": 1.96},
    "U 100 x 50 x 2.00": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 2.00, "tf": 2.00, "A": 3.65, "Ix": 58.15, "Iy": 9.24, "Wx": 11.60, "Wy": 2.52},
    "U 100 x 50 x 2.25": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 2.25, "tf": 2.25, "A": 4.35, "Ix": 68.55, "Iy": 10.94, "Wx": 13.70, "Wy": 3.00},
    "U 100 x 50 x 2.65": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 2.65, "tf": 2.65, "A": 5.04, "Ix": 78.60, "Iy": 12.59, "Wx": 15.70, "Wy": 3.48},
    "U 100 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 5.71, "Ix": 88.29, "Iy": 14.20, "Wx": 17.60, "Wy": 3.94},
    "U 127 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 127, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 6.53, "Ix": 154.80, "Iy": 15.32, "Wx": 24.30, "Wy": 4.08},
    "U 150 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 150, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 7.23, "Ix": 230.10, "Iy": 16.08, "Wx": 30.60, "Wy": 4.16},
    "U 200 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 200, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 8.75, "Ix": 462.40, "Iy": 17.31, "Wx": 46.20, "Wy": 4.29},
    "UE 100 x 50 x 17 x 2.25": {"familia": "U Enrijecido", "d": 100, "bf": 50, "tw": 2.25, "tf": 2.25, "A": 4.88, "Ix": 78.4, "Iy": 15.1, "Wx": 15.68, "Wy": 4.25},
    "UE 127 x 50 x 17 x 2.65": {"familia": "U Enrijecido", "d": 127, "bf": 50, "tw": 2.65, "tf": 2.65, "A": 6.46, "Ix": 161.0, "Iy": 18.2, "Wx": 25.35, "Wy": 4.98},
    "UE 150 x 60 x 20 x 3.00": {"familia": "U Enrijecido", "d": 150, "bf": 60, "tw": 3.00, "tf": 3.00, "A": 8.70, "Ix": 308.2, "Iy": 35.8, "Wx": 41.09, "Wy": 8.32},
}

CATALOGO_CANTONEIRAS = {
    # 1" (25.4 mm)
    "L 1\" x 1/8\"": {"familia": "Cantoneira L", "d": 25.4, "bf": 25.4, "tw": 3.17, "tf": 3.17, "A": 1.51, "Ix": 0.8, "Iy": 0.8, "Wx": 0.4, "Wy": 0.4},
    "2x L 1\" x 1/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 25.4, "bf": 60.8, "tw": 3.17, "tf": 3.17, "A": 3.02, "Ix": 1.6, "Iy": 3.2, "Wx": 0.8, "Wy": 1.4},
    "L 1.1/4\" x 1/8\"": {"familia": "Cantoneira L", "d": 31.7, "bf": 31.7, "tw": 3.17, "tf": 3.17, "A": 1.92, "Ix": 1.8, "Iy": 1.8, "Wx": 0.8, "Wy": 0.8},
    "2x L 1.1/4\" x 1/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 31.7, "bf": 73.4, "tw": 3.17, "tf": 3.17, "A": 3.84, "Ix": 3.6, "Iy": 7.2, "Wx": 1.6, "Wy": 2.7},
    "L 1.1/2\" x 1/8\"": {"familia": "Cantoneira L", "d": 38.1, "bf": 38.1, "tw": 3.17, "tf": 3.17, "A": 2.32, "Ix": 3.2, "Iy": 3.2, "Wx": 1.1, "Wy": 1.1},
    "2x L 1.1/2\" x 1/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 38.1, "bf": 86.2, "tw": 3.17, "tf": 3.17, "A": 4.64, "Ix": 6.4, "Iy": 12.8, "Wx": 2.2, "Wy": 3.7},
    "L 1.1/2\" x 3/16\"": {"familia": "Cantoneira L", "d": 38.1, "bf": 38.1, "tw": 4.76, "tf": 4.76, "A": 3.40, "Ix": 4.6, "Iy": 4.6, "Wx": 1.7, "Wy": 1.7},
    "2x L 1.1/2\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 38.1, "bf": 86.2, "tw": 4.76, "tf": 4.76, "A": 6.80, "Ix": 9.2, "Iy": 18.4, "Wx": 3.4, "Wy": 5.8},
    "L 2\" x 1/8\"": {"familia": "Cantoneira L", "d": 50.8, "bf": 50.8, "tw": 3.17, "tf": 3.17, "A": 3.12, "Ix": 7.7, "Iy": 7.7, "Wx": 2.1, "Wy": 2.1},
    "2x L 2\" x 1/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 50.8, "bf": 111.6, "tw": 3.17, "tf": 3.17, "A": 6.24, "Ix": 15.4, "Iy": 30.8, "Wx": 4.2, "Wy": 7.1},
    "L 2\" x 3/16\"": {"familia": "Cantoneira L", "d": 50.8, "bf": 50.8, "tw": 4.76, "tf": 4.76, "A": 4.58, "Ix": 10.9, "Iy": 10.9, "Wx": 3.0, "Wy": 3.0},
    "2x L 2\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 50.8, "bf": 111.6, "tw": 4.76, "tf": 4.76, "A": 9.16, "Ix": 21.8, "Iy": 44.2, "Wx": 6.0, "Wy": 10.2},
    "L 2\" x 1/4\"": {"familia": "Cantoneira L", "d": 50.8, "bf": 50.8, "tw": 6.35, "tf": 6.35, "A": 6.06, "Ix": 14.1, "Iy": 14.1, "Wx": 4.0, "Wy": 4.0},
    "2x L 2\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 50.8, "bf": 111.6, "tw": 6.35, "tf": 6.35, "A": 12.12, "Ix": 28.2, "Iy": 56.4, "Wx": 8.0, "Wy": 13.6},
    "L 2.1/2\" x 3/16\"": {"familia": "Cantoneira L", "d": 63.5, "bf": 63.5, "tw": 4.76, "tf": 4.76, "A": 5.80, "Ix": 22.4, "Iy": 22.4, "Wx": 4.8, "Wy": 4.8},
    "2x L 2.1/2\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 63.5, "bf": 137.0, "tw": 4.76, "tf": 4.76, "A": 11.60, "Ix": 44.8, "Iy": 89.6, "Wx": 9.6, "Wy": 16.3},
    "L 2.1/2\" x 1/4\"": {"familia": "Cantoneira L", "d": 63.5, "bf": 63.5, "tw": 6.35, "tf": 6.35, "A": 7.67, "Ix": 28.8, "Iy": 28.8, "Wx": 6.3, "Wy": 6.3},
    "2x L 2.1/2\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 63.5, "bf": 137.0, "tw": 6.35, "tf": 6.35, "A": 14.80, "Ix": 54.8, "Iy": 112.0, "Wx": 12.1, "Wy": 21.5},
    "L 3\" x 3/16\"": {"familia": "Cantoneira L", "d": 76.2, "bf": 76.2, "tw": 4.76, "tf": 4.76, "A": 7.03, "Ix": 39.5, "Iy": 39.5, "Wx": 7.1, "Wy": 7.1},
    "2x L 3\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 76.2, "bf": 162.4, "tw": 4.76, "tf": 4.76, "A": 14.06, "Ix": 79.0, "Iy": 158.0, "Wx": 14.2, "Wy": 24.1},
    "L 3\" x 1/4\"": {"familia": "Cantoneira L", "d": 76.2, "bf": 76.2, "tw": 6.35, "tf": 6.35, "A": 9.29, "Ix": 51.1, "Iy": 51.1, "Wx": 9.3, "Wy": 9.3},
    "2x L 3\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 76.2, "bf": 162.4, "tw": 6.35, "tf": 6.35, "A": 18.58, "Ix": 102.2, "Iy": 204.4, "Wx": 18.6, "Wy": 31.6},
    "L 3\" x 5/16\"": {"familia": "Cantoneira L", "d": 76.2, "bf": 76.2, "tw": 7.94, "tf": 7.94, "A": 11.50, "Ix": 62.4, "Iy": 62.4, "Wx": 11.5, "Wy": 11.5},
    "2x L 3\" x 5/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 76.2, "bf": 162.4, "tw": 7.94, "tf": 7.94, "A": 23.00, "Ix": 124.8, "Iy": 249.6, "Wx": 23.0, "Wy": 39.1},
    "L 3\" x 3/8\"": {"familia": "Cantoneira L", "d": 76.2, "bf": 76.2, "tw": 9.52, "tf": 9.52, "A": 13.60, "Ix": 72.8, "Iy": 72.8, "Wx": 13.6, "Wy": 13.6},
    "2x L 3\" x 3/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 76.2, "bf": 162.4, "tw": 9.52, "tf": 9.52, "A": 27.20, "Ix": 145.6, "Iy": 291.2, "Wx": 27.2, "Wy": 46.2},
    "L 4\" x 1/4\"": {"familia": "Cantoneira L", "d": 101.6, "bf": 101.6, "tw": 6.35, "tf": 6.35, "A": 12.50, "Ix": 124.0, "Iy": 124.0, "Wx": 17.0, "Wy": 17.0},
    "2x L 4\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 101.6, "bf": 213.2, "tw": 6.35, "tf": 6.35, "A": 25.00, "Ix": 248.0, "Iy": 496.0, "Wx": 34.0, "Wy": 57.8},
    "L 4\" x 5/16\"": {"familia": "Cantoneira L", "d": 101.6, "bf": 101.6, "tw": 7.94, "tf": 7.94, "A": 15.50, "Ix": 153.0, "Iy": 153.0, "Wx": 21.1, "Wy": 21.1},
    "2x L 4\" x 5/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 101.6, "bf": 213.2, "tw": 7.94, "tf": 7.94, "A": 31.00, "Ix": 306.0, "Iy": 612.0, "Wx": 42.2, "Wy": 71.7},
    "L 4\" x 3/8\"": {"familia": "Cantoneira L", "d": 101.6, "bf": 101.6, "tw": 9.52, "tf": 9.52, "A": 18.50, "Ix": 179.0, "Iy": 179.0, "Wx": 24.9, "Wy": 24.9},
    "2x L 4\" x 3/8\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 101.6, "bf": 213.2, "tw": 9.52, "tf": 9.52, "A": 37.00, "Ix": 358.0, "Iy": 716.0, "Wx": 49.8, "Wy": 84.6},
    "L 4\" x 1/2\"": {"familia": "Cantoneira L", "d": 101.6, "bf": 101.6, "tw": 12.70, "tf": 12.70, "A": 24.20, "Ix": 230.0, "Iy": 230.0, "Wx": 32.4, "Wy": 32.4},
    "2x L 4\" x 1/2\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 101.6, "bf": 213.2, "tw": 12.70, "tf": 12.70, "A": 48.40, "Ix": 460.0, "Iy": 920.0, "Wx": 64.8, "Wy": 110.1},
}

CATALOGO_COMPLETO = {**CATALOGO_LAMINADOS, **CATALOGO_CHAPA_DOBRADA, **CATALOGO_CANTONEIRAS}

PROPRIEDADES_ACO = {
    "ASTM A36": {"fy": 250, "fu": 400},
    "ASTM A572 Gr 50": {"fy": 345, "fu": 450},
    "USI CIVIL 300": {"fy": 300, "fu": 410}
}

class VerificadorNBR8800:
    def __init__(self, tipo_aco="ASTM A572 Gr 50"):
        self.aco = PROPRIEDADES_ACO.get(tipo_aco, PROPRIEDADES_ACO["ASTM A572 Gr 50"])
        self.gamma_a1 = 1.10
        self.E_cm = 20000.0  # Módulo de Elasticidade (200 GPa -> 20.000 kN/cm²)

    def verificar_elemento(self, nome_perfil, N_trac_sd, N_comp_sd, V_sd, My_sd, Mz_sd, delta_sd_mm, vao_m, fator_esforso=1.0):
        perfil = CATALOGO_COMPLETO.get(nome_perfil, CATALOGO_LAMINADOS["W 200 x 22.5"])
        fy = self.aco["fy"] / 10.0  # MPa para kN/cm²
        A = perfil["A"]
        Ix = perfil["Ix"]
        Iy = perfil["Iy"]
        Wx = perfil["Wx"]
        Wy = perfil.get("Wy", 0.1)
        d = perfil["d"] / 10.0
        tw = perfil["tw"] / 10.0

        # Esforços Majorados (já deveriam vir majorados pelo fator_esforso no solver, mantendo segurança extra)
        N_trac_sd_e = N_trac_sd * fator_esforso
        N_comp_sd_e = N_comp_sd * fator_esforso
        V_sd_e = abs(V_sd) * fator_esforso
        My_sd_e = abs(My_sd) * fator_esforso  
        Mz_sd_e = abs(Mz_sd) * fator_esforso  

        # -------------------------------------------------------------
        # 1. CÁLCULO DE FLAMBAGEM GLOBAL E ESBELTEZ (NBR 8800)
        # -------------------------------------------------------------
        L_cm = vao_m * 100.0
        Kx = 1.0  # Coeficiente de flambagem (articulado-articulado padrão)
        Ky = 1.0
        
        # Raios de giração dinâmicos
        rx = np.sqrt(Ix / A) if A > 0 else 1e-5
        ry = np.sqrt(Iy / A) if A > 0 else 1e-5
        
        # Índice de Esbeltez global (λ)
        esbeltez_x = (Kx * L_cm) / rx
        esbeltez_y = (Ky * L_cm) / ry
        esbeltez_max = max(esbeltez_x, esbeltez_y)
        
        # Fator de Flambagem Local (Q) - Assumido 1.0 (Perfil Compacto)
        Q = 1.0 
        
        # Força Normal de Flambagem Elástica (Ne)
        Ne = (np.pi**2 * self.E_cm * A) / (esbeltez_max**2) if esbeltez_max > 0 else 1e9
        
        # Parâmetro de Esbeltez Reduzida (λ0)
        lambda_0 = np.sqrt((Q * A * fy) / Ne) if Ne > 0 else 999.0
        
        # Fator de Redução (χ - Qui) para Compressão
        if lambda_0 <= 1.5:
            chi = 0.658 ** (lambda_0**2)
        else:
            chi = 0.877 / (lambda_0**2)
            
        # -------------------------------------------------------------
        # 2. VERIFICAÇÕES DE RESISTÊNCIA BÁSICAS
        # -------------------------------------------------------------
        M_rd_x = (Wx * fy) / (100.0 * self.gamma_a1)  # Dividido por 100 para kNm
        M_rd_y = (Wy * fy) / (100.0 * self.gamma_a1)
        
        Av = d * tw
        V_rd = (0.60 * Av * fy) / self.gamma_a1
        
        # Resistências Normais Distintas
        N_rd_trac = (A * fy) / self.gamma_a1
        N_rd_comp = (chi * Q * A * fy) / self.gamma_a1

        ratio_N_trac = N_trac_sd_e / N_rd_trac if N_rd_trac > 0 else 0
        ratio_N_comp = N_comp_sd_e / N_rd_comp if N_rd_comp > 0 else 0
        
        # O ratio de tração ou compressão pior define o dimensionamento
        ratio_N_max = max(ratio_N_trac, ratio_N_comp)
        
        ratio_Mx = My_sd_e / M_rd_x if M_rd_x > 0 else 0
        ratio_My = Mz_sd_e / M_rd_y if M_rd_y > 0 else 0

        # Interação Biaxial Flexo-Compressão/Tração
        if ratio_N_max >= 0.2:
            taxa_interacao = ratio_N_max + (8.0/9.0) * (ratio_Mx + ratio_My)
        else:
            taxa_interacao = (ratio_N_max / 2.0) + (ratio_Mx + ratio_My)

        ratio_V = V_sd_e / V_rd if V_rd > 0 else 0

        delta_lim_mm = (vao_m * 1000.0) / 250.0
        ratio_delta = delta_sd_mm / delta_lim_mm if delta_lim_mm > 0 else 0

        taxa_maxima = max(taxa_interacao, ratio_V, ratio_delta)

        return {
            "perfil": nome_perfil,
            "familia": perfil["familia"],
            "aprovado": taxa_maxima <= 1.0,
            "taxa_maxima": taxa_maxima * 100.0,
            "taxa_interacao": taxa_interacao * 100.0,
            "ratio_N": ratio_N_max * 100.0,
            "ratio_N_trac": ratio_N_trac * 100.0,
            "ratio_N_comp": ratio_N_comp * 100.0,
            "ratio_Mx": ratio_Mx * 100.0,
            "ratio_My": ratio_My * 100.0,
            "ratio_V": ratio_V * 100.0,
            "ratio_delta": ratio_delta * 100.0,
            "M_rd_x": M_rd_x,
            "M_rd_y": M_rd_y,
            "V_rd": V_rd,
            "N_rd_trac": N_rd_trac,
            "N_rd_comp": N_rd_comp,
            "chi": chi,
            "esbeltez_max": esbeltez_max,
            "Ne": Ne,
            "lambda_0": lambda_0,
            "rx": rx,
            "ry": ry,
            "delta_lim_mm": delta_lim_mm
        }

# =========================================================================================
# FUNÇÕES DE INTERFACE E RELATÓRIO
# =========================================================================================

def desenhar_diagrama(res, tipo_diagrama):
    fig = go.Figure()
    nos, barras, esforcos = res["nos"], res["barras"], res["esforcos"]
    
    if tipo_diagrama == "Deslocamentos (Deformada)":
        for n1, n2 in barras:
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

            for n1, n2 in barras:
                x1 = nos[n1][0] + U[n1*6] * scale
                y1 = nos[n1][1] + U[n1*6+1] * scale
                z1 = nos[n1][2] + U[n1*6+2] * scale
                
                x2 = nos[n2][0] + U[n2*6] * scale
                y2 = nos[n2][1] + U[n2*6+1] * scale
                z2 = nos[n2][2] + U[n2*6+2] * scale
                
                fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='red', width=5), showlegend=False))

    elif tipo_diagrama == "Reações de Apoio":
        for n1, n2 in barras:
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
    
    else:
        # Base da estrutura
        for n1, n2 in barras:
            x1, y1, z1 = nos[n1]
            x2, y2, z2 = nos[n2]
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode='lines', line=dict(color='lightgrey', width=2), showlegend=False))

        max_val = 1e-5
        for esf in esforcos:
            v1, v2 = (esf["N"] if "Normal" in tipo_diagrama else (esf["Vz"] if "Cortante" in tipo_diagrama else esf["My"]))
            max_val = max(max_val, abs(v1), abs(v2))
            
        escala = 1.2 / max_val
        
        # Desenha os diagramas de esforço (Ftool-style)
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
                # Convenção: Tração > 0 (Azul), Compressão < 0 (Vermelho)
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
            
            # Polígono do diagrama
            fig.add_trace(go.Scatter3d(
                x=[x1, ox1, ox2, x2], y=[y1, oy1, oy2, y2], z=[z1, oz1, oz2, z2],
                mode='lines', line=dict(color=cor, width=3), showlegend=False
            ))
            
            # Adiciona os textos com os valores nas pontas da barra
            t_x, t_y, t_z, t_val = [], [], [], []
            
            if abs(v1) > 0.1:
                t_x.append(ox1); t_y.append(oy1); t_z.append(oz1); t_val.append(f"{v1:.1f}")
            if abs(v2) > 0.1 and abs(v2 - v1) > 0.1: 
                t_x.append(ox2); t_y.append(oy2); t_z.append(oz2); t_val.append(f"{v2:.1f}")
            elif abs(v2) > 0.1 and abs(v1) <= 0.1:
                t_x.append(ox2); t_y.append(oy2); t_z.append(oz2); t_val.append(f"{v2:.1f}")

            if t_x:
                fig.add_trace(go.Scatter3d(
                    x=t_x, y=t_y, z=t_z,
                    mode='text', text=t_val,
                    textposition="top center",
                    textfont=dict(color=cor, size=11, family="Arial Black"),
                    showlegend=False
                ))

        if "Normal" in tipo_diagrama:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='royalblue', width=4), name='Tração (+)'))
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='crimson', width=4), name='Compressão (-)'))
        elif "Cortante" in tipo_diagrama:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='seagreen', width=4), name='Cortante'))
        else:
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='lines', line=dict(color='darkorange', width=4), name='Momento Fletor'))
            
        fig.update_layout(showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"))

    fig.update_layout(scene=dict(xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)', aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0), height=600)
    return fig

def gerar_relatorio_txt(dados, res_analise, resultados_comp, tudo_aprovado, tolerancia):
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    status_global = "APROVADA" if tudo_aprovado else "REPROVADA (Requer revisão de perfis)"
    
    aco = PROPRIEDADES_ACO[dados['tipo_aco']]
    fy_mpa = aco['fy']
    fy_kncm2 = fy_mpa / 10.0
    gamma_a1 = 1.10
    
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
        relatorio += f"- Pilares Rotação 90°: {'Sim' if dados.get('rotacionar_pilares') else 'Não'}\n"

    relatorio += f"""- Vão Transversal (X): {dados['vao_x']:.2f} m
- Altura (Z): {dados['altura_z']:.2f} m
- Largura de Influência / Espaçamento: {dados['espacamento']:.2f} m
"""
    if dados['sistema_principal'] not in ["Mão Francesa / Suporte (Plano 2D)"]:
        relatorio += f"- Comprimento Longitudinal (Y): {dados['comp_y']:.2f} m\n"
        if dados['sistema_principal'] == "Mezanino / Passarela Metálica":
            relatorio += f"- Espaçamento entre Vigotas Transversais: {dados['espacamento_vigota']:.2f} m\n"
            relatorio += f"- Tipo de Piso: {dados['tipo_piso']}\n"

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
        A = perf['A']
        Wx = perf['Wx']
        Wy = perf.get('Wy', 0.1)
        d = perf['d'] / 10.0
        tw = perf['tw'] / 10.0
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

def gerar_relatorio_pdf(texto_memoria, res_analise=None, incluir_graficos=False):
    if FPDF is None: return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=9) 
    for linha in texto_memoria.split('\n'):
        pdf.multi_cell(0, 5, txt=linha.encode('latin-1', 'replace').decode('latin-1'))
        
    if res_analise and incluir_graficos:
        try:
            pdf.add_page()
            pdf.set_font("Courier", 'B', 12)
            pdf.cell(0, 10, "6. ANEXO - DIAGRAMAS 3D/2D", ln=True)
            pdf.set_font("Courier", size=9)
            
            diagramas = ["Deslocamentos (Deformada)", "Momento Fletor (My)", "Reações de Apoio"]
            
            for diag in diagramas:
                fig = desenhar_diagrama(res_analise, diag)
                fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    fig.write_image(tmp.name, width=800, height=600)
                    pdf.cell(0, 10, f"-> {diag}:", ln=True)
                    pdf.image(tmp.name, x=10, w=190)
                    pdf.ln(5)
                    tmp_path = tmp.name
                
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            pdf.multi_cell(0, 5, txt=f"\n[Aviso: Não foi possível gerar os diagramas no PDF. Servidor sem suporte ao 'kaleido' ou timeout. Detalhe: {e}]")

    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)

def obter_propriedades(nome_perfil):
    p = CATALOGO_COMPLETO[nome_perfil]
    return {"A": p["A"] * 1e-4, "Iy": p["Ix"] * 1e-8, "Iz": p["Iy"] * 1e-8, "J": (p["Iy"] * 1e-8) / 2.0}

def main():
    st.title("🏗️ Dimensionamento de Estruturas Metálicas")
    st.caption("Conformidade: NBR 8800 | NBR 6120 | NBR 6123")

    if "res_analise" not in st.session_state:
        st.session_state.res_analise = None

    # MENU LATERAL
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
        st.sidebar.markdown("**📐 Parâmetros do Piso/Passarela**")
        espacamento_vigota = st.sidebar.number_input("Espaçamento Vigotas Transversais [m]", min_value=0.40, max_value=3.00, value=1.00, step=0.10)
    elif sistema_principal not in ["Arco", "Mão Francesa / Suporte (Plano 2D)"]:
        forma_cobertura = st.sidebar.selectbox("Forma da Cobertura", ["2 Águas", "1 Água"])
        inclinacao = st.sidebar.number_input("Inclinação do Telhado [%]", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        if sistema_principal == "Tesoura Plana (Treliçada)":
            n_paineis = st.sidebar.slider("Número de Painéis da Treliça", min_value=2, max_value=60, value=6, step=2)
    elif sistema_principal == "Arco":
        flecha_arco = st.sidebar.number_input("Flecha do Arco (m)", min_value=1.0, max_value=20.0, value=3.0, step=0.5)

    vao_x = st.sidebar.number_input("Vão Transversal (X) [m]", value=15.0 if sistema_principal not in ["Mezanino / Passarela Metálica", "Mão Francesa / Suporte (Plano 2D)"] else 6.0)
    
    if sistema_principal != "Mão Francesa / Suporte (Plano 2D)":
        comp_y = st.sidebar.number_input("Comprimento Longitudinal (Y) [m]", value=30.0 if sistema_principal != "Mezanino / Passarela Metálica" else 12.0)
    else:
        comp_y = 0.0

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
        perf_terca = st.sidebar.selectbox("Terças de Cobertura", lista_perfis, index=lista_perfis.index("U 100 x 40 x 2.25") if "U 100 x 40 x 2.25" in lista_perfis else 0)
        perf_bz_sup = st.sidebar.selectbox("Banzo Superior", lista_perfis, index=lista_perfis.index("U 150 x 50 x 3.00") if "U 150 x 50 x 3.00" in lista_perfis else 0)
        perf_bz_inf = st.sidebar.selectbox("Banzo Inferior", lista_perfis, index=lista_perfis.index("U 150 x 50 x 3.00") if "U 150 x 50 x 3.00" in lista_perfis else 0)
        perf_diag = st.sidebar.selectbox("Diagonais", lista_perfis, index=lista_perfis.index('2x L 2" x 3/16" (Dupla)') if '2x L 2" x 3/16" (Dupla)' in lista_perfis else 0)
        perf_mont = st.sidebar.selectbox("Montantes", lista_perfis, index=lista_perfis.index("2x L 2.1/2\" x 1/4\" (Dupla)") if "2x L 2.1/2\" x 1/4\" (Dupla)" in lista_perfis else 0)
        mapa_perfis = {"Pilares Metálicos": perf_pil, "Terças de Cobertura": perf_terca, "Banzo Superior": perf_bz_sup, "Banzo Inferior": perf_bz_inf, "Diagonais": perf_diag, "Montantes": perf_mont}

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Condições e Aceitação")
    apoios_base = st.sidebar.selectbox("Vínculos na Base / Apoios", ["Engastado (Trava Translações e Rotações)", "Articulado (Trava apenas Translações)"])
    
    rotacionar_pilares = False
    if tipo_pilar == "Pilar Metálico" and sistema_principal != "Mão Francesa / Suporte (Plano 2D)":
        rotacionar_pilares = st.sidebar.checkbox("Rotacionar Pilares em 90° (Eixo Forte na direção Y)", value=False)
        
    tolerancia_aceitacao = st.sidebar.number_input("Tolerância de Aceitação Máxima [%]", min_value=0.0, max_value=20.0, value=2.0, step=0.5)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌪️ Cargas / Vento")
    if sistema_principal == "Mezanino / Passarela Metálica":
        tipo_piso = st.sidebar.selectbox("Tipo de Piso", ["Painel Wall / Masterboard (0.30 kN/m²)", "Steel Deck + Concreto (2.00 kN/m²)", "Chapa Xadrez Metálica (0.40 kN/m²)", "Painel OSB / Madeira (0.25 kN/m²)"])
        sobrecarga_opcao = st.sidebar.selectbox(
            "Uso / Sobrecarga", 
            [
                "Escritórios / Leve (2.50 kN/m²)", "Residencial (1.50 kN/m²)", "Comercial / Lojas (3.00 kN/m²)", 
                "Depósito Leve (4.00 kN/m²)", "Depósito Pesado (5.00 kN/m²)", "Passarela - Manutenção/Sem Público (2.50 kN/m²)", 
                "Passarela - Acesso Público (3.00 kN/m²)", "Academias / Ginástica (5.00 kN/m²)" 
            ]
        )
        peso_piso = float(tipo_piso.split("(")[1].split(" ")[0])
        carga_inst = 0.15
        g_total = peso_piso + carga_inst
        q_sobre = float(sobrecarga_opcao.split("(")[1].split(" ")[0])
        q_vento_liquido = 0.0
        q_elu = (1.25 * g_total) + (1.50 * q_sobre)
    elif sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
        st.info("Para inserir uma Carga Linear [kN/m] direta, defina a Largura de Influência como 1.0 m acima.")
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

    # =========================================================================================
    # GERADOR DE MALHA MATRICIAL
    # =========================================================================================
    
    if sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
        y_coords = [0.0]
    else:
        y_coords = np.arange(0, comp_y + espacamento, espacamento)
        if y_coords[-1] != comp_y: y_coords[-1] = comp_y
        
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
        if y_vigotas[-1] != comp_y: y_vigotas[-1] = comp_y
        
        for y_v in y_vigotas:
            edges_raw.append({"n1": add_no(0, y_v, altura_z), "n2": add_no(vao_x, y_v, altura_z), "grupo": "Vigas Secundárias (Transversais)"})
        for i in range(len(y_vigotas) - 1):
            edges_raw.append({"n1": add_no(0, y_vigotas[i], altura_z), "n2": add_no(0, y_vigotas[i+1], altura_z), "grupo": "Vigas Principais (Longitudinais)"})
            edges_raw.append({"n1": add_no(vao_x, y_vigotas[i], altura_z), "n2": add_no(vao_x, y_vigotas[i+1], altura_z), "grupo": "Vigas Principais (Longitudinais)"})
        
        for i_y, y_p in enumerate(y_coords):
            is_supported_frame = (distribuicao_pilares == "Em todos os pórticos" or i_y == 0 or i_y == (len(y_coords) - 1))
            if is_supported_frame:
                n_tE = add_no(0, y_p, altura_z)
                n_tD = add_no(vao_x, y_p, altura_z)
                if has_pillar:
                    n_bE = add_no(0, y_p, 0)
                    n_bD = add_no(vao_x, y_p, 0)
                    grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                    edges_raw.append({"n1": n_bE, "n2": n_tE, "grupo": grp_pilar})
                    edges_raw.append({"n1": n_bD, "n2": n_tD, "grupo": grp_pilar})
                    apoios_idx.update([n_bE, n_bD])
                else:
                    apoios_idx.update([n_tE, n_tD])

    else:
        cobertura_por_frame = []
        for i_y, y in enumerate(y_coords):
            is_supported_frame = (distribuicao_pilares == "Em todos os pórticos" or i_y == 0 or i_y == (len(y_coords) - 1))
            
            if sistema_principal == "Arco":
                x_arco = list(np.linspace(0, vao_x, 9))
                z_arco = [altura_z + flecha_arco * (1 - (2*(x-vao_x/2)/vao_x)**2) for x in x_arco]
                n_arco_ids = [add_no(x, y, z) for x, z in zip(x_arco, z_arco)]
                
                for i in range(8):
                    edges_raw.append({"n1": n_arco_ids[i], "n2": n_arco_ids[i+1], "grupo": "Banzo Superior"})
                
                if is_supported_frame:
                    n_tE, n_tD = n_arco_ids[0], n_arco_ids[-1]
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.append({"n1": n_bE, "n2": n_tE, "grupo": grp_pilar})
                        edges_raw.append({"n1": n_bD, "n2": n_tD, "grupo": grp_pilar})
                        apoios_idx.update([n_bE, n_bD])
                    else:
                        apoios_idx.update([n_tE, n_tD])
                cobertura_por_frame.append(n_arco_ids)

            elif sistema_principal == "Tesoura Plana (Treliçada)":
                if forma_cobertura == "1 Água":
                    x_sub = np.linspace(0, vao_x, n_paineis + 1)
                    x_pts = list(x_sub) + list(x_sub)
                    z_pts = [altura_z] * (n_paineis + 1) + list(altura_z + (vao_x - x_sub) * (inclinacao / 100.0))
                else:
                    n_lado = n_paineis // 2
                    x_all = np.concatenate([np.linspace(0, vao_x/2, n_lado + 1), np.linspace(vao_x/2, vao_x, n_lado + 1)[1:]])
                    z_sup_local = np.where(x_all <= vao_x/2, altura_z + x_all*(inclinacao/100.0), altura_z + (vao_x-x_all)*(inclinacao/100.0))
                    x_pts = list(x_all) + list(x_all)
                    z_pts = [altura_z] * len(x_all) + list(z_sup_local)
                
                n_trel_ids = [add_no(x, y, z) for x, z in zip(x_pts, z_pts)]
                meio = len(n_trel_ids) // 2
                idx_inf = n_trel_ids[:meio]
                idx_sup = n_trel_ids[meio:]
                
                for i in range(len(idx_inf)-1):
                    edges_raw.append({"n1": idx_inf[i], "n2": idx_inf[i+1], "grupo": "Banzo Inferior"})
                    edges_raw.append({"n1": idx_sup[i], "n2": idx_sup[i+1], "grupo": "Banzo Superior"})
                    edges_raw.append({"n1": idx_inf[i], "n2": idx_sup[i], "grupo": "Montantes"})
                    if forma_cobertura == "1 Água" or i < (len(idx_inf)-1)//2:
                        edges_raw.append({"n1": idx_inf[i], "n2": idx_sup[i+1], "grupo": "Diagonais"})
                    else:
                        edges_raw.append({"n1": idx_inf[i+1], "n2": idx_sup[i], "grupo": "Diagonais"})
                edges_raw.append({"n1": idx_inf[-1], "n2": idx_sup[-1], "grupo": "Montantes"})
                
                if is_supported_frame:
                    n_tE, n_tD = idx_inf[0], idx_inf[-1]
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.append({"n1": n_bE, "n2": n_tE, "grupo": grp_pilar})
                        edges_raw.append({"n1": n_bD, "n2": n_tD, "grupo": grp_pilar})
                        apoios_idx.update([n_bE, n_bD])
                    else:
                        apoios_idx.update([n_tE, n_tD])
                cobertura_por_frame.append(idx_sup)

            else: 
                n_tE = add_no(0, y, altura_z)
                n_tD = add_no(vao_x, y, altura_z)
                
                if forma_cobertura == "2 Águas":
                    h_cum = altura_z + (vao_x / 2.0) * (inclinacao / 100.0)
                    n_cum = add_no(vao_x/2, y, h_cum)
                    edges_raw.append({"n1": n_tE, "n2": n_cum, "grupo": "Banzo Superior"})
                    edges_raw.append({"n1": n_cum, "n2": n_tD, "grupo": "Banzo Superior"})
                    cobertura_por_frame.append([n_tE, n_cum, n_tD])
                else:
                    h_cum = altura_z + vao_x * (inclinacao / 100.0)
                    n_cum = add_no(vao_x, y, h_cum)
                    edges_raw.append({"n1": n_tE, "n2": n_cum, "grupo": "Banzo Superior"})
                    cobertura_por_frame.append([n_tE, n_cum])

                edges_raw.append({"n1": n_tE, "n2": n_tD, "grupo": "Banzo Inferior"})
                
                if is_supported_frame:
                    if has_pillar:
                        n_bE, n_bD = add_no(0, y, 0), add_no(vao_x, y, 0)
                        grp_pilar = "Pilares Metálicos" if tipo_pilar == "Pilar Metálico" else "Pilares Concreto"
                        edges_raw.append({"n1": n_bE, "n2": n_tE, "grupo": grp_pilar})
                        edges_raw.append({"n1": n_bD, "n2": n_tD, "grupo": grp_pilar})
                        apoios_idx.update([n_bE, n_bD])
                    else:
                        apoios_idx.update([n_tE, n_tD])
            
        for i in range(len(cobertura_por_frame) - 1):
            for p in range(len(cobertura_por_frame[i])):
                if p < len(cobertura_por_frame[i+1]):
                    edges_raw.append({"n1": cobertura_por_frame[i][p], "n2": cobertura_por_frame[i+1][p], "grupo": "Terças de Cobertura"})

    barras_prontas = []
    barras_visualizacao = []
    
    for edge in edges_raw:
        grp = edge["grupo"]
        barras_visualizacao.append({"n1": edge["n1"], "n2": edge["n2"], "grupo": grp})
        
        if grp == "Pilares Concreto":
            barras_prontas.append({"n1": edge["n1"], "n2": edge["n2"], "grupo": grp, "A": 0.16, "Iy": 0.002, "Iz": 0.002, "J": 0.002, "ang": 0.0})
            continue

        nome_perf = mapa_perfis.get(grp)
        if nome_perf is None: continue 
        
        props = obter_propriedades(nome_perf)
        
        ang = 90.0 if (grp == "Pilares Metálicos" and rotacionar_pilares) else 0.0
        barras_prontas.append({"n1": edge["n1"], "n2": edge["n2"], "grupo": grp, "A": props["A"], "Iy": props["Iy"], "Iz": props["Iz"], "J": props["J"], "ang": ang})

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
            q_linear_exibida = q_elu * espacamento
            st.success(f"Carga Linear aplicada na viga principal: **{q_linear_exibida:.2f} kN/m**")

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
            if st.session_state.res_analise.get("sucesso"):
                st.success("✅ Análise Concluída com sucesso!")
            else:
                st.error(f"❌ Erro na análise: {st.session_state.res_analise.get('erro')}")

    with tab4:
        st.subheader("✅ Verificação Biaxial Integrada e Flambagem (NBR 8800)")
        if not st.session_state.res_analise: 
            st.warning("Execute a Análise na Aba 3.")
        elif not st.session_state.res_analise.get("sucesso"):
             st.error("A análise falhou. Não é possível realizar a verificação.")
        else:
            res = st.session_state.res_analise
            verificador = VerificadorNBR8800(tipo_aco)
            
            resultados_comp = []
            tudo_aprovado = True
            
            for grupo, esf_grp in res.get("esforcos_grupos", {}).items():
                nome_perfil = mapa_perfis.get(grupo)
                if nome_perfil is None: continue 
                
                # Tratamento de Vão Teórico adaptado para incluir 2D
                if sistema_principal == "Mão Francesa / Suporte (Plano 2D)":
                    if grupo == "Vigas Principais (Longitudinais)":
                        L_teorico = vao_x
                    elif "Pilares" in grupo:
                        L_teorico = altura_z
                    else:
                        L_teorico = esf_grp.get("L_max", vao_x)
                else:
                    if grupo == "Vigas Secundárias (Transversais)":
                        L_teorico = vao_x
                    elif grupo == "Vigas Principais (Longitudinais)":
                        L_teorico = comp_y if distribuicao_pilares == "Apenas nos 4 cantos extremos" else espacamento
                    elif "Pilares" in grupo:
                        L_teorico = altura_z
                    elif grupo == "Terças de Cobertura":
                        L_teorico = espacamento
                    elif grupo in ["Banzo Superior", "Banzo Inferior"]:
                        L_teorico = vao_x
                    else:
                        L_teorico = esf_grp.get("L_max", vao_x)
                        
                # Define precisamente a Tração (+) e Compressão (-)
                N_trac = max(0.0, esf_grp.get("n_pos", 0.0))
                N_comp = abs(min(0.0, esf_grp.get("n_neg", 0.0)))

                v = verificador.verificar_elemento(
                    nome_perfil, 
                    N_trac, 
                    N_comp, 
                    esf_grp.get("v_max", 0.0), 
                    esf_grp.get("my_max", esf_grp.get("m_max", 0.0)), 
                    esf_grp.get("mz_max", 0.0), 
                    esf_grp.get("d_max", 0.0), 
                    L_teorico, 1.0 
                )
                
                v["componente"] = grupo
                v["N_sd"] = max(N_trac, N_comp)
                v["N_trac_sd"] = N_trac
                v["N_comp_sd"] = N_comp
                v["V_sd"] = esf_grp.get("v_max", 0.0)
                v["My_sd"] = esf_grp.get("my_max", esf_grp.get("m_max", 0.0))
                v["Mz_sd"] = esf_grp.get("mz_max", 0.0)
                v["D_sd"] = esf_grp.get("d_max", 0.0)
                v["L_teorico_m"] = L_teorico
                v["fator"] = 1.0
                
                if v["taxa_maxima"] <= (100.0 + tolerancia_aceitacao) and v["esbeltez_max"] <= 200.0:
                    v["aprovado"] = True
                else:
                    v["aprovado"] = False
                    tudo_aprovado = False

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
                    "q_vento_liquido": q_vento_liquido, "tipo_piso": tipo_piso if sistema_principal == "Mezanino / Passarela Metálica" else "N/A",
                    "rotacionar_pilares": rotacionar_pilares
                }
                texto_memoria = gerar_relatorio_txt(dados_r, res, resultados_comp, tudo_aprovado, tolerancia_aceitacao)
                
                col_d1, col_d2, col_d3 = st.columns([1.5, 1.5, 2])
                with col_d1: st.download_button("📄 Baixar TXT", data=texto_memoria, file_name="Calculo.txt")
                with col_d2:
                    if FPDF is not None:
                        incluir_img = col_d3.checkbox("Anexar Imagens 3D no PDF (Pode causar erro/lentidão na nuvem)")
                        st.download_button("📥 Baixar PDF", data=gerar_relatorio_pdf(texto_memoria, res, incluir_img), file_name="Calculo_Detalhado.pdf", mime="application/pdf", type="primary")

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
                    
                    if v['taxa_maxima'] > 100:
                        st.progress(min(max(int(v['taxa_maxima']), 0), 100))
                    
                    perf = CATALOGO_COMPLETO[v['perfil']]
                    A = perf['A']
                    Wx = perf['Wx']
                    Wy = perf.get('Wy', 0.1)
                    d = perf['d'] / 10.0
                    tw = perf['tw'] / 10.0
                    Av = d * tw
                    
                    with st.expander("🧮 Ver Memória de Cálculo Detalhada e Flambagem"):
                        st.markdown(f"""
                        **A. ESFORÇOS ATUANTES MÁXIMOS (Sd)**
                        * **N_Sd (Tração)** = {v['N_trac_sd']:.2f} kN | **N_Sd (Compressão)** = {v['N_comp_sd']:.2f} kN
                        * **V_Sd** = {v['V_sd']:.2f} kN
                        * **M_Sd,x (Forte)** = {v['My_sd']:.2f} kNm | **M_Sd,y (Fraco)** = {v['Mz_sd']:.2f} kNm
                        
                        **B. PROPRIEDADES GEOMÉTRICAS DA SEÇÃO**
                        * **Área Bruta (A)** = {A:.2f} cm² | **Área de Cisalhamento Efetiva (Av)** = {Av:.2f} cm²
                        * **Módulos Resistentes Elásticos:** Wx (Forte) = {Wx:.2f} cm³ | Wy (Fraco) = {Wy:.2f} cm³
                        * **Raios de Giração:** rx = {v['rx']:.2f} cm | ry = {v['ry']:.2f} cm
                        
                        **C. ANÁLISE DE FLAMBAGEM GLOBAL E ESBELTEZ**
                        * **Índice de Esbeltez Máximo (λ):** {v['esbeltez_max']:.1f} (Limite NBR 8800 = 200)
                        * **Força de Flambagem Elástica (Ne):** {v['Ne']:.2f} kN
                        * **Esbeltez Reduzida (λ0):** {v['lambda_0']:.3f}
                        * **Fator de Redução de Flambagem (χ):** **{v['chi']:.3f}** (Reduz a resistência à compressão)
                        
                        **D. VERIFICAÇÕES DE RESISTÊNCIA E FLECHA**
                        * **Resistência à Tração (Fórmula: A · fy / γ_a1):** 
                          $N_{{Rd,t}}$ = {v['N_rd_trac']:.2f} kN ➔ $N_{{Sd,trac}}$ / $N_{{Rd,t}}$ = **{v['ratio_N_trac']:.1f}%**
                        * **Resistência à Compressão (Fórmula: χ · Q · A · fy / γ_a1):** 
                          $N_{{Rd,c}}$ = {v['N_rd_comp']:.2f} kN ➔ $N_{{Sd,comp}}$ / $N_{{Rd,c}}$ = **{v['ratio_N_comp']:.1f}%**
                        * **Cisalhamento (Fórmula: 0.60 · Av · fy / γ_a1):** 
                          $V_{{Rd}}$ = {v['V_rd']:.2f} kN ➔ $V_{{Sd}}$ / $V_{{Rd}}$ = **{v['ratio_V']:.1f}%**
                        * **Flexão Eixo Forte (Fórmula: Wx · fy / γ_a1):** 
                          $M_{{Rd,x}}$ = {v.get('M_rd_x', 0):.2f} kNm ➔ $M_{{Sd,x}}$ / $M_{{Rd,x}}$ = **{v['ratio_Mx']:.1f}%**
                        * **Flexão Eixo Fraco (Fórmula: Wy · fy / γ_a1):** 
                          $M_{{Rd,y}}$ = {v.get('M_rd_y', 0):.2f} kNm ➔ $M_{{Sd,y}}$ / $M_{{Rd,y}}$ = **{v['ratio_My']:.1f}%**
                        * **Interação Flexo-Compressão Biaxial (NBR 8800 Eq. 4.14):** 
                          Taxa Integrada = **{v.get('taxa_interacao', 0):.1f}%**
                        * **Flecha (L_vão = {v['L_teorico_m']:.2f} m):** 
                          $\\delta_{{real}}$ = {v['D_sd']:.2f} mm | $\\delta_{{lim}}$ = {v['delta_lim_mm']:.1f} mm ➔ $\\delta_{{real}}$ / $\\delta_{{lim}}$ = **{v['ratio_delta']:.1f}%**
                        """)
                    
                    st.markdown("---")

    with tab5:
        if st.session_state.res_analise and st.session_state.res_analise.get("sucesso"):
            tipo_diagrama = st.selectbox("Visualizar:", ["Deslocamentos (Deformada)", "Esforço Normal (Tração/Compressão)", "Esforço Cortante (Vz)", "Momento Fletor (My)", "Reações de Apoio"])
            st.plotly_chart(desenhar_diagrama(st.session_state.res_analise, tipo_diagrama))

if __name__ == "__main__":
    main()
