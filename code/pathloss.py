#
# pathloss.py
#


import numpy as np


'''
'''

def okumura_hata(f, hm, hb, ak, ck, d):

    if (f <= 200 and ck == 'large'):

        a = 8.29*(np.log10(1.54*hm))**2-1.1

    elif (f >= 400 and ck == 'large'):

        a = 3.2*(np.log10(11.75*hm)**2)-4.97

    else:

        a = (1.1*np.log10(f-0.7))*hm -(1.56*np.log10(f-0.8))

    lossUrban = 69.55 +(26.16)*np.log10(f)-13.82*np.log10(hb) - a + (44.9-6.55*np.log10(hb))*np.log10(d)

    if (ak == 'rural'):

        lossOpen = lossUrban - 4.78*((np.log10(f))^2)+18.33*np.log10(f)-40.94

        return lossOpen

    elif (ak == 'suburban'):

        lossSubUrban= lossUrban - 2*(np.log10(f/28.0))^2 - 5.4

        return lossSubUrban

    else:

        return lossUrban


'''
'''

def cost_231(f, hm, hb, ws, bs, hr, ak, ck, d):

    deltaH = hm/hb #relaction between heighths
    Lbsh= 18*np.log10(1+deltaH) # Loss due to difference of heights
    Ka=54.0  #Coefficient of proximity Buildings
    Kd=18.0  #Coeficiente of proximidade Edifica??es
    Kf=4.0  #Coeficient of environment(urban or not)

    #Coeficient's calculate
    if (hr > hb):
        Lbsh=0.0

    if (hb<=hr and d>=0.5):
        Ka = Ka - 0.8*deltaH
    elif (hb<=hr and d<0.5):
        Ka = Ka - 0.8*deltaH*(d/0.5)

    if (hb < hr):
        Kd=Kd-15*(hb-hr)/(hr-hm)

    if (ck == 'small'):
        Kf = Kf +0.7*(f/925-1)
    else:
        Kf = Kf +1.5*(f/925-1)

    #path loss's calculate
    Lo = 32.4+20*np.log10(d)+20*np.log10(f)                     #free space path loss
    Lrts = 8.2+10*np.log(ws) + 10*np.log10(f) + 10*np.log(deltaH) # roofTop loss
    Lmsd =Lbsh+ Ka+ Kd*np.log10(d)+Kf*np.log10(f)-9*np.log10(bs)    #Multpath loss
    #final path loss
    PL = Lo + Lrts + Lmsd;

    return PL


'''
'''

def ecc_33(f, hm, hb, ak, ck, d):

    PLfs = 92.4+20*np.log10(d)+20*np.log10(f/1000)
    PLbm = 20.41+9.83*np.log10(d)+7.894*(np.log10(f/1000))+9.56*(np.log10(f/1000))**2
    Gb = np.log10(hb/200)*(13.98+5.8*(np.log10(d))**2)
    Gm =(42.57+13.7*np.log10(f/1000))*(np.log10(hm)-0.585)
    PL= PLfs+PLbm-Gb-Gm

    return PL


'''
'''

def pathloss(algorithm='OkumuraHata', parameters={}, distance=0):

    if algorithm == 'OkumuraHata':

        f = parameters['freq']
        hm = parameters['rxH']
        hb = parameters['txH']
        ak = parameters['area_kind']
        ck = parameters['city_kind']

        return okumura_hata(f, hm, hb, ak, ck, distance)

    elif algorithm == 'COST231':

        f = parameters['freq']
        hm = parameters['rxH']
        hb = parameters['txH']
        ws = parameters['ws']
        bs = parameters['bs']
        hr = parameters['hr']
        ak = parameters['area_kind']
        ck = parameters['city_kind']

        return cost_231(f, hm, hb, ws, bs, hr, ak, ck, distance)

    elif algorithm == 'ECC33':

        f = parameters['freq']
        hm = parameters['rxH']
        hb = parameters['txH']
        ak = parameters['area_kind']
        ck = parameters['city_kind']

        return ecc_33(f, hm, hb, ak, ck, distance)

    return -1
