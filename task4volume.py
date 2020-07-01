import vtk
import vtk.util.numpy_support as VN
import numpy as np
import sys,os



# setup the dataset filepath
path = "./yA31/"
files = os.listdir(path);
time_index = [];
daryName = "v02";

for i in range(234, len(files) ,3):
        time_index.append(i);



for i in range(0, len(time_index)):
    filename = path+files[time_index[i]];
    print(i)
    print(filename);

    
    
    
    colors = vtk.vtkNamedColors();

    aRenderer = vtk.vtkRenderer();
    renWin = vtk.vtkRenderWindow();
    renWin.AddRenderer(aRenderer);
    iren = vtk.vtkRenderWindowInteractor();
    iren.SetRenderWindow(renWin);

    # Set a background color for the renderer
    # and set the size of the render window.
    aRenderer.SetBackground(colors.GetColor3d("Silver"));
    renWin.SetSize(600, 600);

    # data reader
    reader = vtk.vtkXMLImageDataReader();
    reader.SetFileName(filename);
    reader.Update();


    # specify the data array in the file to process
    reader.GetOutput().GetPointData().SetActiveAttribute(daryName, 0);


    # convert the data array to numpy array and get the min and maximum value
    dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars(daryName));
    dary = dary[dary!= 0]
    dMax = np.amax(dary);
    #dary = dary[dary>dMax/2]
    dMin = np.amin(dary);
    dRange = dMax - dMin;
    dMean = np.mean(dary);
    dMedian = np.median(dary);
    #dary = dary[dary>dMax/2]

    print("Data array max: ", dMax);
    print("Data array min: ", dMin);
    print("Data array range: ", dRange);
    print("Data array mean: ", dMean);
    print("Data array median: ", dMedian);

    ############ setup color map #########


    hueLut = vtk.vtkLookupTable();
    # This creates a red ,white, blue lut.
    hueLut.SetHueRange(0.67, 0.0)
    hueLut.Build();



    # An outline provides context around the data.
    outlineData = vtk.vtkOutlineFilter();
    outlineData.SetInputConnection(reader.GetOutputPort());
    outlineData.Update()

    mapOutline = vtk.vtkPolyDataMapper();
    mapOutline.SetInputConnection(outlineData.GetOutputPort());

    outline = vtk.vtkActor();
    outline.SetMapper(mapOutline);
    outline.GetProperty().SetColor(colors.GetColor3d("Black"));

    ################## create volume rendering ################################

    # Create transfer mapping scalar value to opacity
    opacityTransferFunction = vtk.vtkPiecewiseFunction();
    opacityTransferFunction.AddPoint(0.0, 0.0001);
    opacityTransferFunction.AddPoint(0.5, 0.0001);
    opacityTransferFunction.AddPoint(1.0, 0.005);

    # int AddRGBPoint (double x, double r, double g, double b)
    # int AddHSVPoint (double x, double h, double s, double v)
    # Create transfer mapping scalar value to color.
    colorTransferFunction = vtk.vtkColorTransferFunction()

    colorTransferFunction.AddRGBPoint(dMin, 0.0, 0.0, 1.0);
    colorTransferFunction.AddRGBPoint(0.5, 0.0, 1.0, 0.0);
    colorTransferFunction.AddRGBPoint(dMax, 1.0, 0.0, 0.0);

    # The property describes how the data will look.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    volumeProperty.SetScalarOpacityUnitDistance(100);
    volumeProperty.SetInterpolationTypeToLinear()

    # The mapper / ray cast function know how to render the data.
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper();
    volumeMapper.SetInputConnection(reader.GetOutputPort())

    # The volume holds the mapper and the property and
    # can be used to position/orient the volume.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    ######################## create a text #####################
    # create a text actor
    txt = vtk.vtkTextActor()
    txt.SetInput("Color map")
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(24)
    txtprop.SetColor(0.0, 0.0, 0.0)
    txt.SetDisplayPosition(450,550)

    ############################################################
    txt2 = vtk.vtkTextActor()
    txt_str2 = "timestep = "+filename[29:34]+", Scalar Value (v02)"
    txt2.SetInput(txt_str2)
    txtprop2=txt2.GetTextProperty()
    txtprop2.SetFontFamilyToArial()
    txtprop2.SetFontSize(24)
    txtprop2.SetColor(0,0,0)
    txt2.SetDisplayPosition(20,550)
    ############################ create a color bar ###########################


    # create the scalar_bar
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetOrientationToHorizontal()
    scalar_bar.SetLookupTable(hueLut)


    # create the scalar_bar_widget
    scalar_bar_widget = vtk.vtkScalarBarWidget()
    scalar_bar_widget.SetInteractor(iren)
    scalar_bar_widget.SetScalarBarActor(scalar_bar)
    scalar_bar_widget.On()


    aCamera = vtk.vtkCamera();
    aCamera.SetViewUp(0, 1, 0);
    aCamera.SetPosition(-0.2, 0.2, 0.5);
    aCamera.SetFocalPoint(0, 0, 0);
    aCamera.ComputeViewPlaneNormal();
    #aCamera.Azimuth(45.0);
    #aCamera.Elevation(45.0);
    #aCamera.Zoom(0.01);
    #aCamera.Dolly(10.0);

    # Actors are added to the renderer.
    aRenderer.AddActor(outline);
    aRenderer.AddVolume(volume);
    aRenderer.AddActor(txt);
    aRenderer.AddActor(txt2);
    # An initial camera view is created. The Dolly() method moves
    # the camera towards the FocalPoint, thereby enlarging the image.
    aRenderer.SetActiveCamera(aCamera);

    # Calling Render() directly on a vtkRenderer is strictly forbidden.
    # Only calling Render() on the vtkRenderWindow is a valid call.
    renWin.Render();
    aRenderer.ResetCamera();
    #aCamera.Dolly(-2.0);
    ####################################################################
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    saveName = "yA31_v02/vol/"+daryName+"_t_"+filename[29:34]+".png";
    writer.SetFileName(saveName)
    writer.SetInputData(w2if.GetOutput())
    writer.Write()

    #####################################################################
    # Note that when camera movement occurs (as it does in the Dolly() method),
    # the clipping planes often need adjusting.
    # Clipping planes consist of two planes:
    # near and far along the view direction.
    # The near plane clips out objects in front of the plane;
    # the far plane clips out objects behind the plane.
    # This way only what is drawn between the planes is actually rendered.

    aRenderer.ResetCameraClippingRange();

    # Interact with the data.
    renWin.Render();
    #iren.Initialize();
    #iren.Start();
