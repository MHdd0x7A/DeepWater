import vtk
import vtk.util.numpy_support as VN
import numpy as np
import sys, os


# setup the dataset filepath
path = "./yA31/"
files = os.listdir(path);
time_index = [];
daryName = "v02"; 


for i in range(234, len(files) ,3):
        time_index.append(i)

        
for i in range(0, len(time_index)):
    filename = path+ files[time_index[i]];
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
    dMin = np.amin(dary);
    dRange = dMax - dMin;
    dMean = np.mean(dary);
    dMedian = np.median(dary);
    dstd = np.std(dary);

    print("Data array max: ", dMax);
    print("Data array min: ", dMin);
    print("Data array range: ", dRange);
    print("Data array mean: ", dMean);
    print("Data array median: ", dMedian);
    print("Data array std: ", dstd);

    ############ setup color map #########
    # Now create a loopup table that consists of the full hue circle
    # (from HSV).
    hueLut = vtk.vtkLookupTable();
    hueLut.SetTableRange(dMin, dMax);
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




    #################### create isosurface v02 = mean ######################################
    # isosurface 
    iso = vtk.vtkContourFilter();
    iso.SetInputConnection(reader.GetOutputPort());
    iso.Update();
    iso.SetValue(0, dMean);

    normals = vtk.vtkPolyDataNormals();
    normals.SetInputConnection(iso.GetOutputPort());
    normals.SetFeatureAngle(45);

    isoMapper = vtk.vtkPolyDataMapper();
    isoMapper.SetInputConnection(normals.GetOutputPort());
    isoMapper.ScalarVisibilityOff();

    isoActor = vtk.vtkActor();
    isoActor.SetMapper(isoMapper);
    isoActor.GetProperty().SetColor(colors.GetColor3d("bisque"));
    isoActor.GetProperty().SetOpacity(0.5);
    ############################### create isosurface v02 = median######################################

    aCamera = vtk.vtkCamera();
    aCamera.SetViewUp(0, 0, 1);
    aCamera.SetPosition(1, 1, 2);
    aCamera.SetFocalPoint(0, 0, 0);
    aCamera.ComputeViewPlaneNormal();
    aCamera.Azimuth(45.0);
    aCamera.Elevation(-140.0);

    ######################## create a text #####################
    # create a text actor

    txt = vtk.vtkTextActor()
    txt_str = "isosurface value(bisque) (mean) = "+str(dMean)[:5]
    txt.SetInput(txt_str)
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(24)
    txtprop.SetColor(colors.GetColor3d("bisque"))
    txt.SetDisplayPosition(50,550)
    ############################################################
    txt2 = vtk.vtkTextActor()
    txt_str2 = "isosurface value (median)(blue) = "+ str(dMedian)[:5]
    txt2.SetInput(txt_str2)
    txtprop2=txt2.GetTextProperty()
    txtprop2.SetFontFamilyToArial()
    txtprop2.SetFontSize(24)
    txtprop2.SetColor(0,0.9,0.9)
    txt2.SetDisplayPosition(50,525)
    ##########################################################

    txt3 = vtk.vtkTextActor()
    txt_str3 = "timestep = "+filename[29:34]
    txt3.SetInput(txt_str3)
    txtprop3=txt3.GetTextProperty()
    txtprop3.SetFontFamilyToArial()
    txtprop3.SetFontSize(24)
    txtprop3.SetColor(0,0,0)
    txt3.SetDisplayPosition(50,500)



    # Actors are added to the renderer.
    aRenderer.AddActor(outline);
    aRenderer.AddActor(isoActor);
    #aRenderer.AddActor(isoActor2);
    aRenderer.AddActor(txt);
    #aRenderer.AddActor(txt2);
    aRenderer.AddActor(txt3);
    # An initial camera view is created. The Dolly() method moves
    # the camera towards the FocalPoint, thereby enlarging the image.
    #aRenderer.SetActiveCamera(aCamera);

    # Calling Render() directly on a vtkRenderer is strictly forbidden.
    # Only calling Render() on the vtkRenderWindow is a valid call.
    renWin.Render();
    aRenderer.ResetCamera();
    aCamera.Dolly(-2.0);

    ####################################################################
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    saveName = "yA31_v02/iso/"+daryName+"_t_"+filename[29:34]+".png";
    writer.SetFileName(saveName)
    writer.SetInputData(w2if.GetOutput())
    writer.Write()

    #####################################################################

    # Note that when camera movement occurs (as it does in the Dolly() method),
    # the clipping planes often
    #need adjusting.
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
