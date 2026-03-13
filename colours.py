def wavelength_to_rgb(wavelength_nm):
    '''Returns an (r, g, b) tuple for a light wavelength in nanometers, nm. Only an approximation, and only relatively accurate from 380-780nm (visible range)'''
    l = wavelength_nm
    
    if(l<420):
        intensity = 0.3 + 0.7*(l-380)/(420-380)
    elif(l>700):
        intensity = 0.3 + 0.7 * (780 - l) / (780-700)
    else:
        intensity = 1.

    if(l<=440):
        rgb = ((440-l)/(440-380),0,1)
    elif(440<l<=490):
        rgb = (0.0, (l-440)/(490-440), 1)
    elif(490<l<=510):
        rgb = (0.0, 1.0, (510-l)/(510-490))
    elif(510<l<=580):
        rgb = ((l-510)/(580-510), 1.0, 0.)
    elif(580<l<=645):
        rgb = (1., (645-l)/(645-580), 0.)
    elif(645<l):
        rgb = (1., 0., 0.)

    return (rgb[0]*intensity, rgb[1]*intensity, rgb[2]*intensity)
 
