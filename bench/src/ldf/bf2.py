import sys
from math import *
from java.lang import *
from java.util import *
from java.nio import *
from javax.swing import *

from edu.mines.jtk.awt import *
from edu.mines.jtk.dsp import *
from edu.mines.jtk.io import *
from edu.mines.jtk.mosaic import *
from edu.mines.jtk.util import *
from edu.mines.jtk.util.ArrayMath import *

from ldf import *

#############################################################################
# functions

def main(args):
  goFilter(True)
  #goEdges()

gauss = BilateralFilter.Type.GAUSS
huber = BilateralFilter.Type.HUBER
tukey = BilateralFilter.Type.TUKEY

def goFilter(guided):
  #n1,n2 = 251,357
  #clip = 4.5
  #fileName = "/data/seis/tp/csm/oldslices/tp73.dat"
  n1,n2 = 462,951
  clip = 5.0
  fileName = "/data/seis/f3d/f3d75.dat"
  x = readImage(fileName,n1,n2)
  print "x min =",min(x)," max =",max(x)
  t = makeImageTensors(x)
  plot(x,clip)
  #s = computeSigmaX(20.0,t,x)
  #print "s min =",min(s)," max =",max(s)
  #plot(s,clip)
  y = zerofloat(n1,n2)
  sigmaX = 1.0
  for sigmaS in [20.0]: #[2.5,5.0,10.0,20.0]:
    bf = BilateralFilter(sigmaS,sigmaX)
    if guided: 
      bf.apply(t,x,y)
      plot(y,clip)
      bf.apply(t,copy(y),y)
      plot(y,clip)
      bf.apply(t,copy(y),y)
    else: 
      bf.apply(x,y)
    plot(y,clip)
    plot(sub(x,y),0.5*clip)

def goEdges():
  n1,n2 = 251,357
  clip = 4.5
  fileName = "/data/seis/tp/csm/oldslices/tp73.dat"
  x = readImage(fileName,n1,n2)
  t = makeImageTensors(x)
  plot(x,clip)
  sigma1 = 4.0; c1 = 0.5*sigma1*sigma1
  sigma2 = 8.0; c2 = 0.5*sigma2*sigma2
  sigma3 = 2.0; c3 = 0.5*sigma3*sigma3
  lsf = LocalSmoothingFilter()
  rgf = RecursiveGaussianFilter(sigma3)
  y1 = copy(x)
  y2 = copy(x)
  lsf.apply(t,c1,x,y1)
  lsf.apply(t,c2,x,y2)
  #plot(y1)
  #plot(y2)
  y = sub(y2,y1)
  plot(y)
  z = mul(x,y)
  plot(z)
  rgf.apply00(z,z)
  plot(z)

def readImage(fileName,n1,n2):
  x = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readFloats(x)
  ais.close()
  return x

def powerGain(x,p):
  return mul(sgn(x),pow(abs(x),p))

def computeSigmaX(sigmaS,t,x):
  n1,n2 = len(x[0]),len(x)
  c = 0.5*sigmaS*sigmaS
  lsf = LocalSmoothingFilter()
  u = copy(x)
  lsf.applySmoothS(x,u)
  lsf.apply(t,c,copy(u),u) # u = <x>
  plot(u,5.0)
  sub(x,u,u) # u = x-<x>
  mul(u,u,u) # u = (x-<x>)^2
  v = copy(u)
  lsf.applySmoothS(u,u)
  lsf.apply(t,c,u,v)
  sqrt(v,v)
  return v

def makeImageTensors(s):
  n1,n2 = len(s[0]),len(s)
  lof = LocalOrientFilter(8.0)
  lof.setGradientSmoothing(2.0)
  t = lof.applyForTensors(s)
  t.setEigenvalues(0.001,1.000)
  #t.setEigenvalues(1.000,1.000)
  return t

def coherence(sigma,t,s):
  lsf = LocalSemblanceFilter(int(sigma),4*int(sigma))
  return lsf.semblance(LocalSemblanceFilter.Direction2.V,t,s)

#############################################################################
# plot

pngDir = "./png"
#pngDir = None

def plot(f,clip=0.0,png=None):
  n1,n2 = len(f[0]),len(f)
  s1 = Sampling(n1,1.0,0.0)
  s2 = Sampling(n2,1.0,0.0)
  sp = SimplePlot(SimplePlot.Origin.UPPER_LEFT)
  pv = sp.addPixels(s1,s2,f)
  if clip!=0.0:
    pv.setClips(-clip,clip)
  pv.setInterpolation(PixelsView.Interpolation.NEAREST)
  #sp.setFontSizeForSlide(1.0,1.0)
  sp.setSize(1192,863)
  sp.setVisible(True)
  if png and pngDir:
    sp.paintToPng(100,6,pngDir+"/"+png+".png")

#############################################################################
# Do everything on Swing thread.

class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())