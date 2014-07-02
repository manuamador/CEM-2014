from __future__ import division
from matplotlib import *
from numpy import *
from numpy.random import *
from pylab import *
from pylab import rcParams
from mpl_toolkits.mplot3d import Axes3D
import os
from Efield2 import Efarfield
rcParams['text.usetex']=True
rcParams['text.latex.unicode']=True
rcParams['legend.fontsize'] = 'medium'
rc('font',**{'family':'serif','serif':['Computer Modern Roman']})

Zissou_map =   {'red':  ((0., 60./255, 60./255),
                         (0.25, 120./255, 120./255),
                         (0.5, 235./255, 235./255),
                         (0.75, 225./255, 225./255),
                         (1,  242./255, 242./255)),
               'green':  ((0.,  154./255, 154./255),
                         (0.25, 183./255, 183./255),
                         (0.5,  204./255, 204./255),
                         (0.75,  175./255, 175./255),
                         (1, 35./255, 35./255)),
               'blue':  ((0., 178./255, 178./255),
                         (0.25, 197./255, 197./255),
                         (0.5, 42./255, 42./255),
                         (0.75, 0./255, 0./255),
                         (1, 0./255, 0./255))}

Zissou_cmap = matplotlib.colors.LinearSegmentedColormap('Zissou_colormap',Zissou_map,4096)

c = 299792458.0
a=1. #EUT radius in m

freq= linspace(4e6,1e9,250)#[10e6,100e6,1e9]#Frequency in Hz
ka=2*pi*freq/c*a #electric size, ka=2*pi/lambda*a

#Radiation pattern
np=360  #number of points along phi
nt=180  #number of points along theta

phi=linspace(0,2*pi,np)
theta=arccos(2*linspace(0,1,nt)-1)#linspace(0,pi,nt)
TH,PH=meshgrid(theta,phi)
t=reshape(TH,(np*nt))
p=reshape(PH,(np*nt))
R = 100 #Measurement sphere radius in m

n=100 #number of radiating dipoles on the EUT
#generate the dipoles
theta_eut=arccos(2*rand(n,1)-1) #uniformly random along theta
phi_eut=2*pi*rand(n,1) #uniformly random along phi
x=a*cos(phi_eut)*sin(theta_eut)  
y=a*sin(phi_eut)*sin(theta_eut) 
z=a*cos(theta_eut) 
tilt=arccos(2*rand(n,1)-1)
azimut=2*pi*rand(n,1)
ld=.1     
amplitude=ones((n,1))*ld #random amplitude of the currents
phas=2*pi*rand(n,1) #random phase

#Currents matrix
I=concatenate((x,y,z,tilt,azimut,amplitude,phas), axis=1)


for u in arange(0,len(freq)):
    #Efield computation
    Ethac=zeros((len(phi),len(theta)),complex) #initialisation de $E_\theta$
    Ephac=zeros((len(phi),len(theta)),complex) #initialisation de $E_\phi$
    Etheta,Ephi=Efarfield(R,t,p,I,freq[u])
    Ethac=reshape(Etheta,(np,nt))
    Ephac=reshape(Ephi,(np,nt))
    Pol=arctan(Ephac/Ethac)
    P=abs(Ethac)**2+abs(Ephac)**2
    D=P.max()/P.mean()
    fig = figure(num=1,figsize=(10, 10), dpi=50)
    ax = fig.add_subplot(111, projection='3d', frame_on=False)
    ax._axis3don = False
    ax.azim=u/len(freq)*360
    RR = P/P.max()
    xx = RR  * outer(cos(phi), sin(theta))
    yy = RR  * outer(sin(phi), sin(theta))
    zz = RR  * outer(ones_like(phi), cos(theta))
    ax.plot_surface(xx, yy, zz, rstride=1, cstride=1, facecolors=Zissou_cmap(RR),\
        linewidth=1,shade=True,antialiased=False)
    max_radius = 0.7
    title(r"$f=%2.1f$ MHz, $ka= %2.1f$, $D\approx %2.1f$"%(freq[u]/1e6,ka[u], D),fontsize=30)
    #title(r'$f= %2.3f$ GHz, $D = %2.1f$' %(f[u]/1e9,D),fontsize=20)
    for axis in 'xyz':
        getattr(ax, 'set_{}lim'.format(axis))((-max_radius, max_radius))
    fname = 'rp_%d' %(u)
    print 'Saving frame', fname
    fig.savefig(fname+'.png',bbox='tight')
    clf()
