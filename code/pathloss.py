#
# pathloss.py
#


'''
'''

def okumura_hata(parameters={}, distance=0):

    if (self.checkFreq):
        if (self.freq<=500 or self.freq>=1500):
            raise ValueError('The frequency range for Okumura-Hata Model is 500MHz-1500Mhz')
    hm,hb,f = self.rxH,self.txH,self.freq
    # a Calc
    if (f<=200 and self.cityKind==CityKind.Large):
        a = 8.29*(np.log10(1.54*hm))**2-1.1
    elif (f>=400 and self.cityKind==CityKind.Large):
        a = 3.2*(np.log10(11.75*hm)**2)-4.97
    else:
        a = (1.1*np.log10(f-0.7))*hm -(1.56*np.log10(f-0.8))
    # Pathloss Calc
    lossUrban = 69.55 +(26.16)*np.log10(f)-13.82*np.log10(hb) - a + (44.9-6.55*np.log10(hb))*np.log10(dist)
    if (self.areaKind==AreaKind.Rural):
        lossOpen = lossUrban - 4.78*((np.log10(f))^2)+18.33*np.log10(f)-40.94
        return lossOpen
    elif (self.areaKind==AreaKind.Suburban):
        lossSubUrban= lossUrban  - 2*(np.log10(f/28.0))^2 - 5.4
        return lossSubUrban
    else:
        return lossUrban


'''
'''

def pathloss(algorithm="OkumuraHata", parameters={}, distance=0):

    if algorithm == "OkumuraHata":

        return okumura_hata(parameters, distance)

    return -1
