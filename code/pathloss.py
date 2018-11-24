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

def pathloss(algorithm="OkumuraHata", parameters={}, distance=0):

    if algorithm == "OkumuraHata":

        f = parameters['freq']
        hm = parameters['rxH']
        hb = parameters['txH']
        ak = parameters['area_kind']
        ck = parameters['city_kind']

        return okumura_hata(f, hm, hb, ak, ck, distance)

    return -1
