import imageio,os

images = []
path = './yA31_v02/iso/'
gif_name = 'tsunami_iso.gif'

filenames=sorted((fn for fn in os.listdir(path) if fn.endswith('.png')))
for filename in filenames:
    images.append(imageio.imread(path + filename))
    
imageio.mimsave(gif_name, images,duration=0.3)