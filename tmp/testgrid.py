from scipy.interpolate import griddata

def func(x, y):
	return (x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2)

grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]
points = np.random.rand(1000, 2)
npoints = vstack((points.transpose(),zeros(1000))).transpose()
values = func(points[:,0], points[:,1])


nvalues = mgrid[0:1000,0:5][1]*values.reshape(1000,1)

grid_z1 = griddata(points, nvalues, (0.5, 0.51), method='linear')
