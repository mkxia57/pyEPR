"""
self defined module for EPR data processing
@author: Mingkang Xia
"""

import numpy as np
import pandas as pd
import os

class dataProcessing():
    def __init__(self, epra, eprd):
        self.epra = epra
        self.eprd = eprd
        self.variations = eprd.variations
    
    def cal_g3(self, mode: int, c3: float, variation: str=None):
        """
        

        Parameters
        ----------
        mode : int
            the mode for analysis
        c3 : float
            the 3rd-order term coeffcient from Taylor expansion of Hamiltonian.
        variation : str, optional
            the variation of simulation. default value is the latest simulation

        Returns
        -------
        None.

        """
        epra_ = self.epra
        if variation is None:
            variation = self.variations[-1]
        coef_list = epra_.get_epr_base_matrices(variation = variation) #coef_list = {p_mj, s_mj, omega_mm, E_jj, phi_zpf, pj_cap, n_zpf}
        p_mj = coef_list[0] #the first row of coef_list is p_mj
        p_snail = p_mj[mode] #the first row of p_mj is p_snail_j
        Ejs = epra_.get_Ejs(variation=variation)
        freqs = epra_.results[variation]['f_1']
        phi_ss = np.sqrt(p_snail[mode] * freqs.iloc[mode] / (2 * 1000 * Ejs[mode]))
        gsss = 3 * 1000 * c3 * phi_ss**3
        print("gsss is %.3f MHz"%gsss)
        return gsss, phi_ss
    
    def saveHFSSData(self, saveDir=""):
        eprd_ = self.eprd
        if saveDir == "":
            print("No saveDir!")
        with open(saveDir + "info_v9.csv", "w") as output: # export analyzed design properties
            info = eprd_._get_lv()
            for i in range(int(len(info)/2)):
                output.write(info[2*i]+','+info[2*i+1]+'\n')
                print("\ndesign properties saved!")
        with open(saveDir + "freq_v9.csv", "w") as output: # export frequency
            mode_info = eprd_.get_freqs_bare_pd(variation = str(eprd_.variations[-1]))
            output.write(mode_info.to_csv(line_terminator='\n'))
            print("\nfreq saved!")
    
    def saveQuantumData(self, saveDir):
        epra_ = self.epra
        with open(saveDir + "chiO1_v9.csv", "w") as output:
            chi_matrix = epra_.get_chis(numeric = False) #export chi_ij
            output.write(chi_matrix.to_csv(line_terminator='\n'))
            print("\nchi matrix saved!")
        with open(saveDir + "f_1_v9.csv", "w") as output:
            f1 = epra_.get_f1(numeric = False) #export chi_ij
            output.write(f1.to_csv(line_terminator='\n'))

    def saveResult(self, variation: str, saveDir=""):
        result_ = self.epra.results[variation]
        if saveDir == "":
            print("No saveDir!")
        for key in result_.keys():
            temp = 'y'
            if os.path.isfile(saveDir + f"{key}.csv"):
                print("\nfile exists!")
                temp = input("file already exist continue?[y/n]")
    
            if temp == 'y':
                with open(saveDir + f"{key}.csv", "w") as output:
                    try:
                        idata = result_[key] #export chi_ij
                        output.write(pd.DataFrame(idata).to_csv(line_terminator='\n'))
                        # print(f"\n{key} saved!")
                    except:
                        idata = result_[key]
                        output.write(str(idata))
                        # print(f"ERROR: can't write {key} data")
            else:
                print("aborted!")
                break

    def saveResult_All(self, saveDir):
        epra_ = self.epra
        results_ = epra_.results
        for i in results_:
            print(f"variation{i}:")
            isaveDir = saveDir + f"variation{i}/"
            try:
                self.saveResult(variation=i, saveDir=isaveDir)
            except:
                os.makedirs(isaveDir, exist_ok=False)
                self.saveResult(variation=i, saveDir=isaveDir)
            print('\tfinished!')