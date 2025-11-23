from dummyxarray import DummyDataset

ds = DummyDataset()
ds.add_dim(name="time", size=12)
ds.add_dim(name="lat", size=180)
ds.add_dim(name="lon", size=360)
ds.add_coord(name="time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord(name="lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord(name="lon", dims=["lon"], attrs={"units": "degrees_east"})
ds.add_variable(
    name="temperature",
    dims=["time", "lat", "lon"],
    attrs={"units": "K", "long_name": "Near-Surface Air Temperature"},
    encoding={"dtype": "float32", "chunks": [6, 32, 64]},
)
ds.assign_attrs(title="Climate Model Output", institution="DKRZ", experiment="historical")
