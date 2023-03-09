from __future__ import annotations
import pandas as pd
from periodictable import *
from tabulate import tabulate

def df_oxygen_calc(df_an: pd.DataFrame)-> pd.DataFrame:
    df_calc_oxy = df_an[["Analysis moisture [wt%]", "Ash_an [wt%]", "C_an [wt%]", "H_an [wt%]", "N_an [wt%]", "S_an [wt%]"]]
   # Oxygen by difference
    df_an["O_an [wt%]"] = 100 - df_calc_oxy.sum(axis=1)
    return df_an

def df_wf_calc(df_an: pd.DataFrame)-> pd.DataFrame:
    # Analysis Data to wf basis
    df_an_calc = df_an[["Ash_an [wt%]", "Volatiles_an [wt%]", "C_an [wt%]", "H_an [wt%]", "N_an [wt%]", "S_an [wt%]", "O_an [wt%]"]]
    df_an["wf_base"] = (100 - df_an["Analysis moisture [wt%]"]) / 100
    df_an[["Ash_wf [wt%]", "Volatiles_wf [wt%]", "C_wf [wt%]", "H_wf [wt%]", "N_wf [wt%]", "S_wf [wt%]", "O_wf [wt%]"]] = df_an_calc.div(df_an["wf_base"], axis=0)
    df_an_wf = df_an
    return df_an_wf

def df_waf_calc(df_an_wf: pd.DataFrame) -> pd.DataFrame:
    # Analysis Data to waf basis
    df_an_wf_calc = df_an_wf[["Volatiles_wf [wt%]", "C_wf [wt%]", "H_wf [wt%]", "N_wf [wt%]", "S_wf [wt%]", "O_wf [wt%]"]]
    df_an_wf["waf_base"] = (100 - df_an_wf["Ash_wf [wt%]"]) / 100
    df_an_wf[["Volatiles_waf [wt%]", "C_waf [wt%]", "H_waf [wt%]", "N_waf [wt%]", "S_waf [wt%]", "O_waf [wt%]"]] = df_an_wf_calc.div(df_an_wf["waf_base"], axis=0)
    df_an_wf_waf = df_an_wf
    return df_an_wf_waf





def remain_content_chn(carbon:float, hydrogen: float, nitrogen: float) -> float:
    """ hello """
    remain = 100 - (carbon + hydrogen + nitrogen)
    return remain

def fix_carbon(moisture: float, volatiles: float, ash: float) -> float:
    fix_c = 100 - (moisture + volatiles + ash)
    return fix_c

def oxygen_calc(moisture: float,  ash: float, carbon:float, hydrogen: float, nitrogen: float, sulfur: float) -> float:
    oxygen = 100 - (moisture + ash + carbon + hydrogen + nitrogen + sulfur)
    return oxygen

def oxygen_calc(moisture: float,  ash: float, carbon:float, hydrogen: float, nitrogen: float, sulfur: float) -> float:
    oxygen = 100 - (moisture + ash + carbon + hydrogen + nitrogen + sulfur)
    return oxygen

def results_wf(ash: float, volatiles: float, moisture: float, carbon_an: float, hydrogen_an: float, nitrogen_an: float, sulfur_an: float, oxygen_an: float ) -> float:
    wf_base = (100 - moisture) / 100
    c_wf = carbon_an / wf_base
    h_wf = hydrogen_an / wf_base
    o_wf = oxygen_an / wf_base
    n_wf = nitrogen_an / wf_base
    s_wf = sulfur_an / wf_base
    ash_wf = ash / wf_base
    moist_wf = 0.0

    lhv_wf, hhv_wf = boie_heating_value(c_wf, h_wf, s_wf, n_wf, o_wf, moist_wf)

    return c_wf, h_wf, o_wf, n_wf, s_wf, ash_wf, volatiles, moist_wf, lhv_wf, hhv_wf

def results_waf(carbon: float, hydrogen: float, nitrogen: float, sulfur: float, oxygen: float,
                   ash: float, volatiles: float, moisture: float) -> float:
    waf_base = (100 - moisture - ash) / 100
    c_waf = carbon / waf_base
    h_waf = hydrogen / waf_base
    o_waf = oxygen / waf_base
    n_waf = nitrogen / waf_base
    s_waf = sulfur / waf_base
    moist_waf = 0.0
    ash_waf = 0.0
    vol_waf = volatiles / waf_base
    lhv_waf, hhv_waf = boie_heating_value(c_waf, h_waf, s_waf, n_waf, o_waf, moist_waf)

    return c_waf, h_waf, o_waf, n_waf, s_waf, ash_waf, vol_waf, moist_waf, lhv_waf, hhv_waf

def boie_heating_value(carbon: float, hydrogen: float, nitrogen: float, sulfur: float, oxygen:float, moisture: float) -> float:
    """
    Computes the lower and upper heating value using the boie equation.
    Values for carbon, hydrogen, sulfur, nitrogen, oxygen and moisture have to be given in weight percent
    """
    lhv = 34800 * carbon + 93800 * hydrogen + 10460 * sulfur + 6280 * nitrogen - 10800 * oxygen - 2450 * moisture
    hhv = 34800 * carbon + 93800 * hydrogen + 10460 * sulfur + 6280 * nitrogen - 10800 * oxygen
    return lhv / 100, hhv / 100

# def print_chnso(oxygen(1)):
#    pd

# def print_chn(self):
#    return HTML(self.df.to_html(index=False))

def print_results(self):
    name = self.sample
    lhv, hhv = self.h_boie(self.c, self.h, self.s, self.n, self.o, self.moist)

    results_wf = self.results_wf()
    results_waf = self.results_waf()
    pd.options.display.float_format = '{:.2f}'.format
    df = pd.DataFrame({
        name: ['carbon [wt%]', 'hydrogen [wt%]', 'oxygen [wt%]', 'nitrogen [wt%]', 'sulfur [wt%]', 'ash [wt%]',
               'volatiles [wt%]', 'moisture [wt%]', 'lower heating value [kJ/kg]', 'higher heating value [kJ/kg]'],
        'row': [self.c, self.h, self.o, self.n, self.s, self.ash, self.vol, self.moist, lhv, hhv],
        'wf': results_wf,
        'waf': results_waf
    })
    return tabulate(df, headers='keys')


def mass_to_mol(element: str, mass: float) -> float:
    '''
    Parameters: element as element symbol
                mass in g
    Returns:    amount of substance in mol
    '''
    el = elements.symbol(element)
    atomic_w = el.mass
    n_mol = mass / atomic_w
    return n_mol


def oc_hc_ratio(wtp_c, wtp_h, wtp_o) -> float:
    c_nmol = mass_to_mol('C', wtp_c)
    print(c_nmol)
    h_nmol = mass_to_mol('H', wtp_h)
    print(h_nmol)
    o_nmol = mass_to_mol('O', wtp_o)
    oc_ratio = o_nmol / c_nmol
    hc_ratio = h_nmol / c_nmol
    return oc_ratio, hc_ratio

#help(mass_to_mol)