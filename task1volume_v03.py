import os
import re
import vtk
import vtk.util.numpy_support as VN
import numpy as np
import json


def RenderToPng(myRenWin, path):
  w2i = vtk.vtkWindowToImageFilter()
  w2i.SetInput(myRenWin)
  w2i.Update()
  pngfile = vtk.vtkPNGWriter()
  pngfile.SetInputConnection(w2i.GetOutputPort())
  pngfile.SetFileName(path)
  pngfile.Write()


##pre
name = os.listdir(os.path.join(os.getcwd(), "yC31"))
for name_i in range(len(name)):
  name[name_i] = name[name_i].rstrip(".vti")

for name_i in range(len(name)):
  # read .vti
  timestep = None
  filename = os.path.join(os.getcwd(), "yC31", name[name_i] + ".vti")
  match = re.match(r'.*_(\d+)$', name[name_i])
  if match:
    timestep = match.group(1)
  else:
    assert ("Exception: Regelar No Match")
  #print(name[name_i][0:6:-1])
  reader = vtk.vtkXMLImageDataReader()
  reader.SetFileName(filename)
  reader.Update()

  #the name of data array which is used in this example
  daryName = 'v03'

  # for accessing build-in color access
  colors = vtk.vtkNamedColors()

  # Create the renderer, the render window, and the interactor. The
  # renderer draws into the render window, the interactor enables
  # mouse- and keyboard-based interaction with the data within the
  # render window.
  aRenderer = vtk.vtkRenderer()
  renWin = vtk.vtkRenderWindow()

  iren = vtk.vtkRenderWindowInteractor()
  iren.SetRenderWindow(renWin)

  # Set a background color for the renderer and set the size of the
  # render window.
  aRenderer.SetBackground(51 / 255, 77 / 255, 102 / 255)
  renWin.SetSize(600, 600)

  # specify the data array in the file to process
  reader.GetOutput().GetPointData().SetActiveAttribute(daryName, 0)

  # convert the data array to numpy array and get the min and maximum valule
  dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars(daryName))
  cmap = vtk.vtkColorTransferFunction()

  #cmap.HSVWrapOff()
  omap = vtk.vtkPiecewiseFunction()

  # load color transfer function
  with open("naiveCool2Warm.json") as f:
    xx = json.load(f)
    nOpaPoints = int(len(xx[0]['Points']) / 4)
    for i in range(nOpaPoints):
      token0 = float(xx[0]['Points'][i * 4])
      token1 = float(xx[0]['Points'][i * 4 + 1])
      token2 = float(xx[0]['Points'][i * 4 + 2])
      token3 = float(xx[0]['Points'][i * 4 + 3])
      omap.AddPoint(token0, token1, token2, token3)

    nRGBPoints = int(len(xx[0]['RGBPoints']) /
                     4)  # number of opacity function control point
    for i in range(nRGBPoints):
      token0 = float(xx[0]['RGBPoints'][i * 4])
      token1 = float(xx[0]['RGBPoints'][i * 4 + 1])
      token2 = float(xx[0]['RGBPoints'][i * 4 + 2])
      token3 = float(xx[0]['RGBPoints'][i * 4 + 3])
      cmap.AddRGBPoint(token0, token1, token2, token3)
  #print(omap)
  cmap.SetColorSpaceToRGB()
  # The property describes how the data will look
  volumeProperty = vtk.vtkVolumeProperty()
  #volumeProperty.ShadeOff()
  volumeProperty.SetColor(cmap)
  volumeProperty.SetGradientOpacity(omap)
  volumeProperty.SetInterpolationTypeToLinear()

  #volumeMapper = vtk.vtkSmartVolumeMapper()
  volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
  #volumeMapper.SetRequestedRenderMode(0)
  volumeMapper.SetInputConnection(reader.GetOutputPort())

  # The volume holds the mapper and the property and
  # can be used to position/orient the volume
  volume = vtk.vtkVolume()
  volume.SetMapper(volumeMapper)
  volume.SetProperty(volumeProperty)

  # It is convenient to create an initial view of the data. The
  # FocalPoint and Position form a vector direction. Later on
  # (ResetCamera() method) this vector is used to position the camera
  # to look at the data in this direction.
  aCamera = vtk.vtkCamera()
  aCamera.SetViewUp(-1, 0, 0)
  aCamera.SetPosition(0, -3, 0)
  aCamera.SetFocalPoint(0, 0, 0)
  aCamera.ComputeViewPlaneNormal()
  aCamera.Azimuth(30.0)
  aCamera.Elevation(30.0)

  aRenderer.AddVolume(volume)

  # Calling Render() directly on a vtkRenderer is strictly forbidden.
  # Only calling Render() on the vtkRenderWindow is a valid call.
  aRenderer.SetActiveCamera(aCamera)
  aRenderer.ResetCamera()
  aCamera.Dolly(1.5)
  renWin.AddRenderer(aRenderer)
  renWin.Render()

  # create the scalar_bar
  scalar_bar = vtk.vtkScalarBarActor()
  scalar_bar.SetOrientationToHorizontal()
  scalar_bar.SetLookupTable(cmap)

  # create the scalar_bar_widget
  scalar_bar_widget = vtk.vtkScalarBarWidget()
  scalar_bar_widget.SetInteractor(iren)
  scalar_bar_widget.SetScalarBarActor(scalar_bar)
  scalar_bar_widget.On()

  # create timestep
  txt = vtk.vtkTextActor()
  txt.SetInput(str(timestep))
  txtprop = txt.GetTextProperty()
  txtprop.SetFontFamilyToArial()
  txtprop.SetFontSize(18)
  txtprop.SetColor(1, 1, 1)
  txt.SetDisplayPosition(20, 550)
  aRenderer.AddActor(txt)

  # Note that when camera movement occurs (as it does in the Dolly()
  # method), the clipping planes often need adjusting. Clipping planes
  # consist of two planes: near and far along the view direction. The
  # near plane clips out objects in front of the plane; the far plane
  # clips out objects behind the plane. This way only what is drawn
  # between the planes is actually rendered.
  aRenderer.ResetCameraClippingRange()

  # Interact with the data.
  renWin.Render()
  RenderToPng(renWin, os.path.join(os.getcwd(), "png", name[name_i] + ".png"))
  iren.Initialize()
  #iren.Start()
