import os
import re
import vtk
import vtk.util.numpy_support as VN
from vtk.numpy_interface import dataset_adapter as dsa
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
  daryName = 'tev'

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
  aRenderer.SetBackground(30 / 255, 30 / 255, 30 / 255)
  renWin.SetSize(1024, 768)

  # specify the data array in the file to process
  # data process
  temp_reader = vtk.vtkXMLImageDataReader()
  temp_reader.SetFileName(filename)
  temp_reader.Update()
  temp_reader.GetOutput().GetPointData().SetActiveAttribute(daryName, 0)
  dary = VN.vtk_to_numpy(
      temp_reader.GetOutput().GetPointData().GetScalars(daryName))

  diff = dary - 0.067592956
  diff_vtk = VN.numpy_to_vtk(diff)
  diff_vtk.SetName('Diff')
  reader.GetOutput().GetPointData().AddArray(diff_vtk)
  reader.GetOutput().GetPointData().SetActiveAttribute('Diff', 0)
  dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars('Diff'))
  daryName = 'Diff'

  # color setting
  cmap = vtk.vtkColorTransferFunction()
  #cmap.HSVWrapOff()
  omap = vtk.vtkPiecewiseFunction()

  # load color transfer function
  with open("naiveCool2Warm_diff.json") as f:
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

  volumeMapper = vtk.vtkSmartVolumeMapper()
  #volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
  #volumeMapper.SetRequestedRenderMode(0)
  volumeMapper.SetInputConnection(reader.GetOutputPort())

  # The volume holds the mapper and the property and
  # can be used to position/orient the volume
  volume = vtk.vtkVolume()
  volume.SetMapper(volumeMapper)
  volume.SetProperty(volumeProperty)
  aRenderer.AddVolume(volume)

  # It is convenient to create an initial view of the data. The
  # FocalPoint and Position form a vector direction. Later on
  # (ResetCamera() method) this vector is used to position the camera
  # to look at the data in this direction.
  aCamera = vtk.vtkCamera()
  aCamera.SetViewUp(-0.013383777971105865, 0.9081385615922546,
                    -0.41845576520866684)
  aCamera.SetPosition(535855.9101585128, 5667762.656331816, 10329926.610160775)
  aCamera.SetFocalPoint(5.7499855756759644e-05, 900000.0000024999,
                        -6.400048732757568e-06)
  aCamera.ComputeViewPlaneNormal()
  aCamera.Dolly(1.0)
  aRenderer.SetActiveCamera(aCamera)
  aRenderer.ResetCamera()
  aRenderer.ResetCameraClippingRange()

  # create timestep
  txt = vtk.vtkTextActor()
  txt.SetInput(str(timestep))
  txtprop = txt.GetTextProperty()
  txtprop.SetFontFamilyToArial()
  txtprop.SetFontSize(18)
  txtprop.SetColor(1, 1, 1)
  txt.SetDisplayPosition(20, 718)
  aRenderer.AddActor(txt)

  # Calling Render() directly on a vtkRenderer is strictly forbidden.
  # Only calling Render() on the vtk
  # RenderWindow is a valid call.

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

  # Interact with the data.
  RenderToPng(renWin, os.path.join(os.getcwd(), "png", name[name_i] + ".png"))
  iren.Initialize()
  #iren.Start()
