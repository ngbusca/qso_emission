import numpy as np
import matplotlib.pyplot as plt
import const
import iminuit
import read_file
import line_models
import likelihood
from configparser import ConfigParser
import lib

loc = "./util.ini"

def window(z, flux, wave, ivar, line_id):
    range_window = float(lib.set_system_values(loc, 'chi2 scan', 'window'))
    line = const.emission_lines[line_id]
    mask = ( wave >= lib.go_to_lf(line - range_window /2, z) ) & ( wave <= lib.go_to_lf(line + range_window /2, z) )
    mi, val_fit = minimization(wave[mask], flux[mask], ivar[mask], lib.go_to_lf(line, z))
    plt.plot(wave[mask], mi)
    return mi, 10** val_fit[1] / line - 1
    
def minimization(x, flux, ivar, line_lam):
    coef = ['a','b','c','d','e']
    def model(coef):
        return getattr(line_models, lib.set_system_values(loc,'line model','model'))(x,coef)
    def inter(coef):
        return getattr(likelihood, lib.set_system_values(loc, 'likelihood method', 'method'))(flux, ivar, model, coef)
    m = iminuit.Minuit(inter, use_array_call=True, forced_parameters = coef, pedantic = False, b = line_lam, c = float(lib.set_system_values(loc, 'minimization', 'sigma')))
    fmin  = m.migrad()
    inte = list(m.values.values()) 
    return model(inte), inte

class qso:

    def __init__(self, file_id, qso_id):
        pix_file_list = lib.set_system_values(loc, 'input','filename')
        self.flux, self.ivar, self.wave, self.id = read_file.read_pix(pix_file_list, file_id, qso_id)
        return

file_id = 0
qso_id = 480
qso1= qso(file_id, qso_id)

z_dict = read_file.read_drq(lib.set_system_values(loc, 'input','z_file'))
z = z_dict[qso1.id]

if qso1.id in z_dict and z > 2.1:
    plt.plot(qso1.wave, qso1.flux)
    fit, new_z = window( z, qso1.flux, qso1.wave, qso1.ivar,'Lya')
    plt.show()