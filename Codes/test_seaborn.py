'''
Lucas Jameson
Calculate Plasma Temperature
Dec 14, 2018
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import optimize

#sns.set(style="darkgrid")

PATH = '/Users/lucas/Documents/SLab/Data/Lab_3_data/data_2/'
file = '2 Data at 3_7A.csv'
e = 1.6*10**(-19) #C
k = 1.381*10**(-23)
# m = 9.1*10**(-31)
# A = np.pi * (0.015)**2
# dA = 0.001

def my_func(x,a,b,c):
	return a*np.exp(x*b) + c

def chi_sq (data_1, data_true):
	s = 0.0
	bins = len(data_1)
	for i in range(bins):
	    s += (data_1[i] - data_true[i])**2/data_true[i]
	s = s/(bins-1.0)
	return np.abs(s)

data = pd.read_csv(PATH + file, skiprows = 10)

#print(data.columns)
ERPA = data[data.columns[1]]
WAVE = data[data.columns[2]]
time = data[data.columns[0]]

# wave_err = [0.001 for i in range(len(WAVE))] #1mV resolution from the AD2
# erpa_err = [0.001 for i in range(len(WAVE))]

#subtract off the offset... AC coupling 
WAVE = 3.0*WAVE #scale factor
ERPA = 2.0*ERPA #scale factor
ERPA_offset = np.mean(ERPA)
WAVE_offset = np.mean(WAVE)
ERPA = ERPA - ERPA_offset
WAVE = WAVE - WAVE_offset
WAVE = WAVE + 1.0 #offset
ERPA = ERPA + 0.5 #offset

#curve fit and find the temp.
p0 = (1,1,1)
coef, pcovt = optimize.curve_fit(my_func,WAVE,ERPA,p0)
err = np.sqrt(np.diag(pcovt))

T = e/(coef[1]*k)
dT = T * err[1]/coef[1]
r2 = np.corrcoef(ERPA, my_func(WAVE, *coef))[0, 1]**2

#n = np.sqrt(m*coef[1]/e)*coef[0]/(e*A)*10**(-10)
#np.sqrt(2.0*np.pi*m/(k*T))*coef[0]/(e*A)
# dnda = np.sqrt(2.0*np.pi*m/(k*T))
# dndT = -0.5*np.sqrt(2.0*np.pi*m/k)*coef[0]/(e*A*T**(-3/2))
# dn = n*np.sqrt((dnda*err[0])**2 + (-dnda*coef[0]/(e*A**2)* dA)**2 + (-0.5*dndT*dT)**2)
# 3dn = 1.0

print("T +/- dT = %.2f +/- %.2f" % (T,dT))
print('chi2 = %.4f' % chi_sq(my_func(WAVE, *coef), ERPA))
print('r2 = %.4f' % r2)
print('a +/- da = %.4f +/- %.4f' % (coef[0],err[0]))
print('b +/- db = %.4f +/- %.4f' % (coef[1],err[1]))
print('c +/- dc = %.4f +/- %.4f' % (coef[2],err[2]))
#print('n +/- dn = %.4f +/- %.4f' % (n,dn))
coef_upper = coef + err
coef_lower = coef - err
cl_data = pd.DataFrame({"Wave": WAVE, "ERPA": ERPA, "fit": my_func(WAVE, *coef),
	 "fit_upper": my_func(WAVE, *coef_upper), "fit_lower": my_func(WAVE, *coef_lower), 'time': time})

plt.figure()
sns.regplot(x = 'Wave', y = 'ERPA', marker = '+', data = cl_data, fit_reg = False, label = 'ERPA Signal')
plt.plot(cl_data['Wave'],cl_data['fit'],c ='r',label ='fit')
# plt.plot(cl_data['Wave'],cl_data['fit_upper'],c ='k',label ='fit_upper')
# plt.plot(cl_data['Wave'],cl_data['fit_lower'],c ='k',label ='fit_lower')
plt.xlabel('Generated Signal (V)')
plt.ylabel('ERPA Signal (V)')
plt.legend()
# plt.savefig(PATH + file[:-4] + '_IV' + '.png')
plt.show()

# for just one peak [290:1350]
#for two peaks [290:2200]
# plt.figure()
# # plt.scatter(time[290:2200], ERPA[290:2200], c='b', label = 'ERPA Signal', marker = '.')
# # plt.scatter(time[290:2200], WAVE[290:2200], c='r', label = 'WAVE Signal', marker = '.')
# sns.regplot(x = 'time', y = 'ERPA', marker = '.', data = cl_data.iloc[290:2200], fit_reg = False, label = 'ERPA Signal', color = 'b')
# sns.regplot(x = 'time', y = 'Wave', marker = '.', data = cl_data.iloc[290:2200], fit_reg = False, label = 'Generated Signal', color = 'g')
# # sns.relplot(x = 'time', y = 'ERPA', data=cl_data, marker = '.', kind = "line")
# # sns.relplot(x = 'time', y = 'Wave', data=cl_data, marker = '.', kind = "line")
# plt.xlabel("Time (s)")
# plt.ylabel("Signal (V)")
# plt.legend(loc=2)
# plt.savefig(PATH + file[:-4] + '_signals' + '.png')
# plt.show()









