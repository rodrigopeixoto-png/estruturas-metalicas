import numpy as np

# Catálogo de Perfis Laminados (Linha W Gerdau e Perfis Especiais)
CATALOGO_LAMINADOS = {
    "W 150 x 13.0": {"familia": "Laminado W", "d": 148, "bf": 100, "tw": 4.3, "tf": 4.9, "A": 16.6, "Ix": 634, "Iy": 82, "Wx": 85.7, "Wy": 16.4},
    "W 150 x 18.0": {"familia": "Laminado W", "d": 153, "bf": 102, "tw": 5.8, "tf": 7.1, "A": 23.0, "Ix": 923, "Iy": 126, "Wx": 120.7, "Wy": 24.7},
    "W 200 x 15.0": {"familia": "Laminado W", "d": 200, "bf": 100, "tw": 4.3, "tf": 5.2, "A": 19.1, "Ix": 1305, "Iy": 87, "Wx": 130.5, "Wy": 17.4},
    "W 200 x 22.5": {"familia": "Laminado W", "d": 206, "bf": 102, "tw": 6.2, "tf": 8.0, "A": 28.6, "Ix": 2029, "Iy": 142, "Wx": 197.0, "Wy": 27.9},
    "W 250 x 25.3": {"familia": "Laminado W", "d": 257, "bf": 102, "tw": 6.1, "tf": 8.4, "A": 32.2, "Ix": 3415, "Iy": 149, "Wx": 265.8, "Wy": 29.3},
    "W 310 x 32.7": {"familia": "Laminado W", "d": 308, "bf": 102, "tw": 6.6, "tf": 10.8, "A": 41.7, "Ix": 6524, "Iy": 192, "Wx": 423.6, "Wy": 37.7},
    "W 360 x 22.0": {"familia": "Laminado W", "d": 356, "bf": 152, "tw": 5.1, "tf": 6.4, "A": 28.5, "Ix": 5800, "Iy": 320, "Wx": 325.0, "Wy": 42.0},
    "W 360 x 44.0": {"familia": "Laminado W", "d": 352, "bf": 171, "tw": 6.9, "tf": 9.8, "A": 56.1, "Ix": 12185, "Iy": 816, "Wx": 692.3, "Wy": 95.5},
    
    # Perfis Pesados e Remontados (Vigas Alveolares/Casteladas expandidas)
    "W 360 x 122 (Original)": {"familia": "Laminado W Pesado", "d": 363, "bf": 257, "tw": 13.0, "tf": 22.0, "A": 154.6, "Ix": 36435, "Iy": 6231, "Wx": 2007.4, "Wy": 484.9},
    "W 360 x 122 (Remontado)": {"familia": "Viga Castelada", "d": 544, "bf": 257, "tw": 13.0, "tf": 22.0, "A": 178.1, "Ix": 90616, "Iy": 6234, "Wx": 3331.0, "Wy": 485.0},
    
    "Perfil I 10 x 4 5/8\"": {"familia": "Laminado I Padrão", "d": 254, "bf": 117.5, "tw": 7.9, "tf": 12.5, "A": 48.2, "Ix": 5140, "Iy": 282, "Wx": 405.0, "Wy": 47.7},
}

# Catálogo de Perfis de Chapa Dobrada (U Simples, U Enrijecidos e Cantoneiras)
CATALOGO_CHAPA_DOBRADA = {
    "U 50 x 25 x 2.00": {"familia": "Chapa Dobrada U", "d": 50, "bf": 25, "tw": 2.00, "tf": 2.00, "A": 1.75, "Ix": 6.66, "Iy": 1.07, "Wx": 2.60, "Wy": 0.60},
    "U 75 x 38 x 2.00": {"familia": "Chapa Dobrada U", "d": 75, "bf": 38, "tw": 2.00, "tf": 2.00, "A": 2.80, "Ix": 25.10, "Iy": 4.55, "Wx": 6.60, "Wy": 1.58},
    "U 100 x 40 x 2.25": {"familia": "Chapa Dobrada U", "d": 100, "bf": 40, "tw": 2.25, "tf": 2.25, "A": 3.89, "Ix": 57.67, "Iy": 5.89, "Wx": 11.50, "Wy": 1.96},
    "U 100 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 100, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 5.71, "Ix": 88.29, "Iy": 14.20, "Wx": 17.60, "Wy": 3.94},
    "U 127 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 127, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 6.53, "Ix": 154.80, "Iy": 15.32, "Wx": 24.30, "Wy": 4.08},
    "U 150 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 150, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 7.23, "Ix": 230.10, "Iy": 16.08, "Wx": 30.60, "Wy": 4.16},
    "U 200 x 50 x 3.00": {"familia": "Chapa Dobrada U", "d": 200, "bf": 50, "tw": 3.00, "tf": 3.00, "A": 8.75, "Ix": 462.40, "Iy": 17.31, "Wx": 46.20, "Wy": 4.29},
    "UE 100 x 50 x 17 x 2.25": {"familia": "U Enrijecido", "d": 100, "bf": 50, "tw": 2.25, "tf": 2.25, "A": 4.88, "Ix": 78.4, "Iy": 15.1, "Wx": 15.68, "Wy": 4.25},
    "UE 127 x 50 x 17 x 2.65": {"familia": "U Enrijecido", "d": 127, "bf": 50, "tw": 2.65, "tf": 2.65, "A": 6.46, "Ix": 161.0, "Iy": 18.2, "Wx": 25.35, "Wy": 4.98},
    "UE 150 x 60 x 20 x 3.00": {"familia": "U Enrijecido", "d": 150, "bf": 60, "tw": 3.00, "tf": 3.00, "A": 8.70, "Ix": 308.2, "Iy": 35.8, "Wx": 41.09, "Wy": 8.32},
    "2x L 2\" x 3/16\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 50.8, "bf": 50.8, "tw": 4.76, "tf": 4.76, "A": 9.16, "Ix": 21.8, "Iy": 44.2, "Wx": 6.0, "Wy": 10.2},
    "2x L 2.1/2\" x 1/4\" (Dupla)": {"familia": "Cantoneira Dupla", "d": 63.5, "bf": 63.5, "tw": 6.35, "tf": 6.35, "A": 14.8, "Ix": 54.8, "Iy": 112.0, "Wx": 12.1, "Wy": 21.5},
}

CATALOGO_COMPLETO = {**CATALOGO_LAMINADOS, **CATALOGO_CHAPA_DOBRADA}

PROPRIEDADES_ACO = {
    "ASTM A36": {"fy": 250, "fu": 400},
    "ASTM A572 Gr 50": {"fy": 345, "fu": 450},
    "USI CIVIL 300": {"fy": 300, "fu": 410}
}

class VerificadorNBR8800:
    def __init__(self, tipo_aco="ASTM A572 Gr 50"):
        self.aco = PROPRIEDADES_ACO.get(tipo_aco, PROPRIEDADES_ACO["ASTM A572 Gr 50"])
        self.gamma_a1 = 1.10

    def verificar_elemento(self, nome_perfil, N_sd, V_sd, My_sd, Mz_sd, delta_sd_mm, vao_m, fator_esforso=1.0):
        perfil = CATALOGO_COMPLETO.get(nome_perfil, CATALOGO_LAMINADOS["W 200 x 22.5"])
        fy = self.aco["fy"] / 10.0  # MPa -> kN/cm²
        A = perfil["A"]
        Wx = perfil["Wx"]
        Wy = perfil["Wy"]
        d = perfil["d"] / 10.0
        tw = perfil["tw"] / 10.0

        N_sd_e = abs(N_sd) * fator_esforso
        V_sd_e = abs(V_sd) * fator_esforso
        My_sd_e = abs(My_sd) * fator_esforso  # Momento eixo Forte (Catálogo Wx)
        Mz_sd_e = abs(Mz_sd) * fator_esforso  # Momento eixo Fraco (Catálogo Wy)

        M_rd_x = (Wx * fy) / (100.0 * self.gamma_a1)
        M_rd_y = (Wy * fy) / (100.0 * self.gamma_a1)
        
        Av = d * tw
        V_rd = (0.60 * Av * fy) / self.gamma_a1
        N_rd = (A * fy) / self.gamma_a1

        ratio_N = N_sd_e / N_rd if N_rd > 0 else 0
        ratio_Mx = My_sd_e / M_rd_x if M_rd_x > 0 else 0
        ratio_My = Mz_sd_e / M_rd_y if M_rd_y > 0 else 0

        # Interação Flexo-Compressão Biaxial (NBR 8800 - Equações 4.14 e 4.15)
        if ratio_N >= 0.2:
            taxa_interacao = ratio_N + (8.0/9.0) * (ratio_Mx + ratio_My)
        else:
            taxa_interacao = (ratio_N / 2.0) + (ratio_Mx + ratio_My)

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
            "ratio_N": ratio_N * 100.0,
            "ratio_Mx": ratio_Mx * 100.0,
            "ratio_My": ratio_My * 100.0,
            "ratio_V": ratio_V * 100.0,
            "ratio_delta": ratio_delta * 100.0,
            "M_rd_x": M_rd_x,
            "M_rd_y": M_rd_y,
            "V_rd": V_rd,
            "N_rd": N_rd,
            "delta_lim_mm": delta_lim_mm
        }
