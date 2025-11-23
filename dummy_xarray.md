You: 

I want a xarray like object where I can set variables and their metadata. I should understand dimensions and their sizes. think of it as a dummy xarray object. it should show the yaml or json representation of what was added. I should in a way use this to create an actual xarray object by providing the data in the respective fields

ChatGPT: 

Below is a **lightweight, dummy “xarray-like” object** that lets you:

✔ Define **dimensions** and their sizes  
✔ Add **variables**, each with  
  • a list of dimensions  
  • metadata (attrs)  
  • optionally placeholder data  
✔ Export everything to **YAML** or **JSON**  
✔ Later create a **real `xarray.Dataset`** by injecting actual NumPy arrays

This is **not** a full xarray implementation—it’s a *spec builder* so you can construct clean metadata before generating actual datasets.

---

# ✅ Minimal Dummy Xarray-Like Object

```python
import json
import yaml

class DummyArray:
    def __init__(self, dims, attrs=None, data=None):
        self.dims = dims                      # list of dim names
        self.attrs = attrs or {}              # metadata dictionary
        self.data = data                      # optional placeholder

    def to_dict(self):
        return {
            "dims": self.dims,
            "attrs": self.attrs,
            "data": "provided" if self.data is not None else None
        }


class DummyDataset:
    def __init__(self):
        self.dims = {}        # dim_name → size
        self.coords = {}      # coord_name → DummyArray
        self.variables = {}   # var_name   → DummyArray
        self.attrs = {}       # global metadata

    # --------------------------------------
    def add_dim(self, name, size):
        self.dims[name] = size

    def add_coord(self, name, dims, attrs=None, data=None):
        self.coords[name] = DummyArray(dims, attrs, data)

    def add_variable(self, name, dims, attrs=None, data=None):
        self.variables[name] = DummyArray(dims, attrs, data)

    # --------------------------------------
    def to_dict(self):
        return {
            "dimensions": self.dims,
            "coordinates": {k: v.to_dict() for k, v in self.coords.items()},
            "variables":   {k: v.to_dict() for k, v in self.variables.items()},
            "attrs": self.attrs
        }

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), indent=2, **kwargs)

    def to_yaml(self):
        return yaml.dump(self.to_dict(), sort_keys=False)

    # --------------------------------------
    def to_xarray(self):
        import xarray as xr
        import numpy as np

        coords = {}
        for name, arr in self.coords.items():
            if arr.data is None:
                raise ValueError(f"Coordinate '{name}' has no data.")
            coords[name] = (arr.dims, arr.data, arr.attrs)

        variables = {}
        for name, arr in self.variables.items():
            if arr.data is None:
                raise ValueError(f"Variable '{name}' has no data.")
            variables[name] = (arr.dims, arr.data, arr.attrs)

        return xr.Dataset(
            data_vars=variables,
            coords=coords,
            attrs=self.attrs
        )
```

---

# ✅ Example Usage

```python
ds = DummyDataset()

# add dims
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

# coords
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

# variables (no data yet)
ds.add_variable("tas", ["time", "lat", "lon"],
                attrs={"long_name": "air_temperature", "units": "K"})
ds.add_variable("pr", ["time", "lat", "lon"],
                attrs={"units": "kg m-2 s-1"})
```

---

# 🔍 JSON/YAML Representation

```python
print(ds.to_yaml())
```

Example output:

```yaml
dimensions:
  time: 12
  lat: 180
  lon: 360
coordinates:
  lat:
    dims:
    - lat
    attrs:
      units: degrees_north
    data: null
  lon:
    dims:
    - lon
    attrs:
      units: degrees_east
    data: null
variables:
  tas:
    dims:
    - time
    - lat
    - lon
    attrs:
      long_name: air_temperature
      units: K
    data: null
  pr:
    dims:
    - time
    - lat
    - lon
    attrs:
      units: kg m-2 s-1
    data: null
attrs: {}
```

---

# 🚀 Converting to a Real xarray Dataset

Just supply real NumPy data matching dimensions:

```python
import numpy as np

ds.variables["tas"].data = np.random.rand(12, 180, 360)
ds.variables["pr"].data = np.random.rand(12, 180, 360)

real_ds = ds.to_xarray()
print(real_ds)
```

---

# Want Extensions?

I can easily add:

🔧 automatic dimension size inference from data  
📌 CF-compliance helpers  
📦 save/load spec YAML  
💡 validation (dim mismatch, metadata checks)  
🔑 attribute templates (e.g. CMIP6 tables)

Just tell me what you'd like next.

You: 

make sure setting global attributes on this dummy dataset is also possible. I like automatic dimension size inference from data. save/load spec YAML is also desirable

ChatGPT: 

Here is an **upgraded version** of the dummy xarray-like system, now with:

✅ **Global attributes support**  
✅ **Automatic dimension-size inference from data**  
  • If a variable or coord has data and you don’t specify dims, dims are inferred  
  • If dims are specified but dim sizes unknown, sizes are inferred  
✔ Dim conflicts trigger clear errors  
🧩 **Save spec to YAML**  
🧩 **Load spec from YAML**

Everything still exports clean **JSON/YAML** and can build a real `xarray.Dataset`.

---

# ⭐ Enhanced Dummy Xarray-Like Object

```python
import json
import yaml
import numpy as np


class DummyArray:
    def __init__(self, dims=None, attrs=None, data=None):
        self.dims = dims            # list of dimension names
        self.attrs = attrs or {}    # metadata
        self.data = data            # optional numpy array or list

    def infer_dims_from_data(self):
        if self.data is not None:
            shape = np.asarray(self.data).shape
            if self.dims is None:
                # auto-generate dims: dim_0, dim_1, ...
                self.dims = [f"dim_{i}" for i in range(len(shape))]
            return dict(zip(self.dims, shape))
        return {}

    def to_dict(self):
        return {
            "dims": self.dims,
            "attrs": self.attrs,
            "has_data": self.data is not None
        }


class DummyDataset:
    def __init__(self):
        self.dims = {}         # dim_name → size
        self.coords = {}       # coord_name → DummyArray
        self.variables = {}    # var_name  → DummyArray
        self.attrs = {}        # global attributes

    # ------------------------------------------------------------
    # Core user API
    # ------------------------------------------------------------

    def set_global_attrs(self, **kwargs):
        """Set/Update global dataset metadata."""
        self.attrs.update(kwargs)

    def add_dim(self, name, size):
        self.dims[name] = size

    def add_coord(self, name, dims=None, attrs=None, data=None):
        arr = DummyArray(dims, attrs, data)
        self._infer_and_register_dims(arr)
        self.coords[name] = arr

    def add_variable(self, name, dims=None, attrs=None, data=None):
        arr = DummyArray(dims, attrs, data)
        self._infer_and_register_dims(arr)
        self.variables[name] = arr

    # ------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------

    def _infer_and_register_dims(self, arr):
        """Infer dimension sizes from data and update the dataset's dimension table."""
        inferred = arr.infer_dims_from_data()

        for dim, size in inferred.items():
            if dim in self.dims:
                if self.dims[dim] != size:
                    raise ValueError(
                        f"Dimension mismatch for '{dim}': existing size={self.dims[dim]}, new size={size}"
                    )
            else:
                self.dims[dim] = size

    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------

    def to_dict(self):
        return {
            "dimensions": self.dims,
            "coordinates": {k: v.to_dict() for k, v in self.coords.items()},
            "variables":   {k: v.to_dict() for k, v in self.variables.items()},
            "attrs": self.attrs,
        }

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), indent=2, **kwargs)

    def to_yaml(self):
        return yaml.dump(self.to_dict(), sort_keys=False)

    # ------------------------------------------------------------
    # Save / Load spec
    # ------------------------------------------------------------

    def save_yaml(self, path):
        with open(path, "w") as f:
            f.write(self.to_yaml())

    @classmethod
    def load_yaml(cls, path):
        with open(path) as f:
            spec = yaml.safe_load(f)

        ds = cls()

        # restore dims
        ds.dims.update(spec.get("dimensions", {}))

        # restore coords
        for name, info in spec.get("coordinates", {}).items():
            ds.coords[name] = DummyArray(
                dims=info["dims"],
                attrs=info["attrs"],
                data=None
            )

        # restore variables
        for name, info in spec.get("variables", {}).items():
            ds.variables[name] = DummyArray(
                dims=info["dims"],
                attrs=info["attrs"],
                data=None
            )

        # restore attrs
        ds.attrs.update(spec.get("attrs", {}))

        return ds

    # ------------------------------------------------------------
    # Convert to xarray
    # ------------------------------------------------------------

    def to_xarray(self):
        import xarray as xr

        coords = {}
        for name, arr in self.coords.items():
            if arr.data is None:
                raise ValueError(f"Coordinate '{name}' missing data.")
            coords[name] = (arr.dims, arr.data, arr.attrs)

        variables = {}
        for name, arr in self.variables.items():
            if arr.data is None:
                raise ValueError(f"Variable '{name}' missing data.")
            variables[name] = (arr.dims, arr.data, arr.attrs)

        return xr.Dataset(
            data_vars=variables,
            coords=coords,
            attrs=self.attrs
        )
```

---

# 📝 Example Usage

```python
ds = DummyDataset()

ds.set_global_attrs(
    title="Test dataset",
    institution="DKRZ",
    experiment="demo"
)

# Variable with data → dims auto-inferred
import numpy as np
temp = np.random.rand(12, 64, 128)

ds.add_variable(
    "tas",
    data=temp,
    attrs={"units": "K", "long_name": "air_temperature"}
)

# dims now automatically contain:
#   dim_0: 12
#   dim_1: 64
#   dim_2: 128

print(ds.to_yaml())
```

Result:

```yaml
dimensions:
  dim_0: 12
  dim_1: 64
  dim_2: 128
coordinates: {}
variables:
  tas:
    dims:
    - dim_0
    - dim_1
    - dim_2
    attrs:
      units: K
      long_name: air_temperature
    has_data: true
attrs:
  title: Test dataset
  institution: DKRZ
  experiment: demo
```

---

# 📂 Saving / Loading the spec

```python
ds.save_yaml("spec.yml")

loaded = DummyDataset.load_yaml("spec.yml")
print(loaded.to_yaml())
```

This round-trips cleanly.

---

# Want more?

Possible extensions:

🔧 CF metadata helpers (standard\_name, axis, bounds detection)  
🧪 Validation: dim mismatch, missing coord for variable dims  
🧱 Support for encoding (dtype, compression)  
🚀 Automatic Zarr builder  
📦 CMIP6 Table-driven variable template generator

Tell me what direction you want to grow this into!

You: 

I like to have validation, support for encoding and zarr builder for now from you suggestion

ChatGPT: 

Great — here is a design plan + full implementation outline adding:

## ✅ New Features You Requested

### 1\. **Validation**

-   Variable dims must exist in global dims
    
-   Coord dims must exist
    
-   Variable dims must match provided data shapes
    
-   Reserved checks:
    
    -   Conflicting dim sizes
        
    -   Missing coordinates for variables (optional: enable strict mode)
        

### 2\. **Support for Encodings**

-   Each variable/coord can define:
    
    -   dtype
        
    -   chunks
        
    -   compressor
        
    -   fill\_value
        
    -   \_Unsigned
        
    -   scale\_factor / add\_offset  
        (compatible subset of xarray/zarr encoding)
        

### 3\. **Zarr Builder**

-   Convert the dummy dataset into an **on-disk Zarr store**
    
-   Automatically uses provided encoding
    
-   Uses `xr.Dataset.to_zarr()` internally
    
-   Ensures data are validated before writing
    

---

# ⭐ Enhanced Implementation (Full Version)

Below is the complete extended implementation with all three features.

```python
import json
import yaml
import numpy as np


class DummyArray:
    def __init__(self, dims=None, attrs=None, data=None, encoding=None):
        self.dims = dims
        self.attrs = attrs or {}
        self.data = data
        self.encoding = encoding or {}

    def infer_dims_from_data(self):
        """Infer dims and their sizes from data, if available."""
        if self.data is not None:
            shape = np.asarray(self.data).shape
            if self.dims is None:
                self.dims = [f"dim_{i}" for i in range(len(shape))]
            return dict(zip(self.dims, shape))
        return {}

    def to_dict(self):
        """Export structure (without data) for YAML."""
        return {
            "dims": self.dims,
            "attrs": self.attrs,
            "encoding": self.encoding,
            "has_data": self.data is not None,
        }


class DummyDataset:
    def __init__(self):
        self.dims = {}        # dim_name → size
        self.coords = {}      # coord_name → DummyArray
        self.variables = {}   # var_name  → DummyArray
        self.attrs = {}       # global attributes

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------
    def set_global_attrs(self, **kwargs):
        self.attrs.update(kwargs)

    def add_dim(self, name, size):
        self.dims[name] = size

    def add_coord(self, name, dims=None, attrs=None, data=None, encoding=None):
        arr = DummyArray(dims, attrs, data, encoding)
        self._infer_and_register_dims(arr)
        self.coords[name] = arr

    def add_variable(self, name, dims=None, attrs=None, data=None, encoding=None):
        arr = DummyArray(dims, attrs, data, encoding)
        self._infer_and_register_dims(arr)
        self.variables[name] = arr

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------
    def validate(self, strict_coords=False):
        """Validate entire dataset structure."""
        errors = []

        # 1. Dimensions must be known
        all_dims = set(self.dims.keys())

        for name, arr in {**self.coords, **self.variables}.items():
            if arr.dims is None:
                continue
            for d in arr.dims:
                if d not in all_dims:
                    errors.append(f"{name}: Unknown dimension '{d}'.")

        # 2. Data shapes must match dims
        for name, arr in {**self.coords, **self.variables}.items():
            if arr.data is not None and arr.dims is not None:
                shape = np.asarray(arr.data).shape
                dim_sizes = [self.dims[d] for d in arr.dims]
                if tuple(dim_sizes) != shape:
                    errors.append(
                        f"{name}: Data shape {shape} does not match dims {dim_sizes}."
                    )

        # 3. Variables reference coords?
        if strict_coords:
            coord_names = set(self.coords.keys())
            for name, arr in self.variables.items():
                for d in arr.dims:
                    if d not in coord_names:
                        errors.append(f"{name}: Missing coordinate for dimension '{d}'.")

        if errors:
            raise ValueError("Dataset validation failed:\n" + "\n".join(errors))

    # ------------------------------------------------------------
    # Internal dimension inference
    # ------------------------------------------------------------
    def _infer_and_register_dims(self, arr):
        inferred = arr.infer_dims_from_data()

        for dim, size in inferred.items():
            if dim in self.dims:
                if self.dims[dim] != size:
                    raise ValueError(
                        f"Dimension mismatch for '{dim}': existing={self.dims[dim]} new={size}"
                    )
            else:
                self.dims[dim] = size

    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------
    def to_dict(self):
        return {
            "dimensions": self.dims,
            "coordinates": {k: v.to_dict() for k, v in self.coords.items()},
            "variables":   {k: v.to_dict() for k, v in self.variables.items()},
            "attrs": self.attrs,
        }

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), indent=2, **kwargs)

    def to_yaml(self):
        return yaml.dump(self.to_dict(), sort_keys=False)

    def save_yaml(self, path):
        with open(path, "w") as f:
            f.write(self.to_yaml())

    @classmethod
    def load_yaml(cls, path):
        with open(path) as f:
            spec = yaml.safe_load(f)

        ds = cls()

        ds.dims.update(spec.get("dimensions", {}))

        for name, info in spec.get("coordinates", {}).items():
            ds.coords[name] = DummyArray(
                dims=info["dims"],
                attrs=info["attrs"],
                data=None,
                encoding=info.get("encoding", {})
            )

        for name, info in spec.get("variables", {}).items():
            ds.variables[name] = DummyArray(
                dims=info["dims"],
                attrs=info["attrs"],
                data=None,
                encoding=info.get("encoding", {})
            )

        ds.attrs.update(spec.get("attrs", {}))

        return ds

    # ------------------------------------------------------------
    # Build xarray.Dataset
    # ------------------------------------------------------------
    def to_xarray(self, validate=True):
        import xarray as xr

        if validate:
            self.validate(strict_coords=False)

        coords = {}
        for name, arr in self.coords.items():
            if arr.data is None:
                raise ValueError(f"Coordinate '{name}' missing data.")
            coords[name] = (arr.dims, arr.data, arr.attrs)

        variables = {}
        for name, arr in self.variables.items():
            if arr.data is None:
                raise ValueError(f"Variable '{name}' missing data.")
            variables[name] = (arr.dims, arr.data, arr.attrs)
        
        ds = xr.Dataset(
            data_vars=variables,
            coords=coords,
            attrs=self.attrs
        )

        # apply encodings
        for name, arr in self.variables.items():
            if arr.encoding:
                ds[name].encoding = arr.encoding

        return ds

    # ------------------------------------------------------------
    # Zarr Builder
    # ------------------------------------------------------------
    def to_zarr(self, store_path, mode="w", validate=True):
        ds = self.to_xarray(validate=validate)
        return ds.to_zarr(store_path, mode=mode)
```

---

# 🧪 Example Usage

## Add variable with encoding + auto dim inference

```python
ds = DummyDataset()

data = np.random.rand(12, 64, 128)

ds.add_variable(
    "tas",
    data=data,
    attrs={"units": "K"},
    encoding={
        "dtype": "float32",
        "chunks": (6, 32, 64),
        "compressor": None,      # e.g. zarr.Blosc()
    }
)
```

Dimensions `dim_0`, `dim_1`, `dim_2` auto-added.

---

## Validation

```python
ds.validate()
```

---

## Write to Zarr

```python
ds.to_zarr("out.zarr")
```

This respects chunking, dtype, compressors defined in encoding.

---

# Want More Enhancements?

I can add:

-   **Strict CF checker**
    
-   **Dimension registry with axis (X/Y/Z/T)**
    
-   **Template system for CMIP6 / CF / CORDEX**
    
-   **Auto bounds generation (lat\_bnds, time\_bnds)**
    
-   **Plugin hooks for custom validators**
    

Tell me what direction you’d like to develop next!