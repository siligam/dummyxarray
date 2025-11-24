# CF Standards Approach

## Design Decision: cf_xarray as Required Dependency

This document explains why we use `cf_xarray` as a **required dependency** for CF
standards compliance instead of creating our own implementation or using IOOS
compliance-checker.

## The Problem

We need to ensure datasets follow CF conventions, particularly for:
- Coordinate axis detection (X, Y, Z, T)
- Appropriate metadata attributes
- Standard names
- Community-agreed conventions

## Options Considered

### 1. Build Our Own (❌ Not Recommended)

**Pros:**
- No external dependencies
- Full control

**Cons:**
- Reinventing the wheel
- May diverge from community standards
- Maintenance burden
- Potential incompatibilities with ecosystem

### 2. IOOS Compliance Checker (⚠️ Limited Use)

**Pros:**
- Comprehensive validation
- Industry standard
- Well-tested

**Cons:**
- **Requires actual NetCDF files** - Can't validate metadata-only
- **Requires data** - Must populate arrays first
- Heavy dependency
- Slow for quick checks
- Overkill for metadata validation

### 3. cf_xarray (✅ **CHOSEN - Required Dependency**)

**Pros:**
- **Metadata-focused** - Works without data (we create temporary arrays)
- **Community standards** - Based on CF conventions + MetPy + Iris
- **Lightweight** - Minimal dependencies
- **Ecosystem integration** - Works with xarray
- **Actively maintained** - Regular updates
- **Flexible** - Can work with in-memory objects

**Decision:**
- **Required dependency** - Ensures all users get same CF validation
- **No fallback needed** - Simpler codebase, consistent behavior

## Our Approach: Hybrid Strategy

We implement a **three-tier approach**:

### Tier 1: Built-in Basic Validation (Always Available)
```python
# No dependencies, fast, essential checks
ds.infer_axis()
ds.validate_cf()
```

**Use for:**
- Quick prototyping
- Development iteration
- When no dependencies allowed
- Basic compliance checks

### Tier 2: cf_xarray Standards (Required, Recommended)
```python
# Required dependency, community standards, works without data!
ds.apply_cf_standards()
ds.validate_cf_metadata()
```

**Use for:**
- Production datasets
- Publishing data
- Ecosystem compatibility
- Following community standards
- **Metadata-only workflows** (no data needed!)

### Tier 3: IOOS Compliance Checker (Optional, Comprehensive)
```python
# For final validation of complete datasets
ds.populate_with_random_data()
result = validate_with_compliance_checker(ds)
```

**Use for:**
- Final validation before publication
- Comprehensive compliance reports
- When you have complete datasets with data

## Why cf_xarray for Metadata?

### 1. Community Agreement

cf_xarray's criteria are based on:
- Official CF Conventions
- MetPy's coordinate detection (widely used in meteorology)
- Iris coordinate system (used by UK Met Office)
- Community feedback and contributions

This means **we're not making up our own rules** - we're using what the community
has already agreed upon.

### 2. Metadata-First Design ✨

**NEW**: cf_xarray now works with metadata alone - no data required!

```python
# Works without data! (we create temporary arrays internally)
ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_variable("temperature", dims=["time"], attrs={"units": "K"})
ds.apply_cf_standards()  # Detects T axis, adds attributes
# Data is still None!
```

IOOS compliance-checker still requires:
```python
# Must have data
ds.populate_with_random_data()  # Required!
validate_with_compliance_checker(ds)  # Only then can validate
```

### 3. Lightweight and Fast

```python
# cf_xarray: ~0.01s
ds.apply_cf_standards()

# compliance-checker: ~1-5s (must write NetCDF file)
validate_with_compliance_checker(ds)
```

### 4. Ecosystem Integration

Using cf_xarray ensures compatibility with:
- xarray (native integration)
- MetPy (meteorological calculations)
- Iris (climate data analysis)
- Cartopy (map projections)
- Other CF-aware tools

## Implementation Details

### How cf_xarray Detects Axes

cf_xarray uses multiple criteria (in order of precedence):

1. **Explicit axis attribute**: `axis="T"`
2. **Standard name**: `standard_name="time"`
3. **Units**: `units="days since 2000-01-01"`
4. **Name patterns**: Variable named `time`, `lat`, `lon`, etc.
5. **Coordinate type**: 1D coordinate with matching dimension

### What We Add

We provide convenience methods:

```python
class CFStandardsMixin:
    def apply_cf_standards(self, verbose=False):
        """Apply community-agreed CF standards."""
        # Uses cf_xarray.guess_coord_axis()
        
    def validate_cf_metadata(self, strict=False):
        """Validate against CF standards."""
        # Uses cf_xarray criteria
        
    def check_cf_standards_available(self):
        """Check if cf_xarray is installed."""
```

## Usage Recommendations

### For Users

**Development (Metadata-Only):**
```python
# Fast iteration, no data needed!
ds.apply_cf_standards()
ds.validate_cf_metadata()
```

**Production:**
```python
# Apply community standards (always available)
ds.apply_cf_standards()
result = ds.validate_cf_metadata()
```

**Publication:**
```python
# Final comprehensive check (requires data)
ds.populate_with_random_data()
result = validate_with_compliance_checker(ds, cf_version="1.8")
```

### For Contributors

When adding CF-related features:

1. **Don't reinvent** - Check if cf_xarray already does it
2. **Stay compatible** - Ensure our built-in methods align with cf_xarray
3. **Document differences** - Explain when to use built-in vs cf_xarray
4. **Test both** - Ensure features work with and without cf_xarray

## Benefits of This Approach

1. **Community alignment** - Uses agreed standards (cf_xarray required)
2. **Metadata-only workflows** - Works without data (temporary arrays)
3. **Flexibility** - Users choose their level of validation
4. **Performance** - Fast for metadata-only, thorough for production
5. **Ecosystem compatibility** - Datasets work with other tools
6. **Simpler codebase** - No optional dependency handling

## Future Considerations

### Potential Enhancements

1. **Cache cf_xarray results** - Avoid repeated detection
2. **Expose cf_xarray criteria** - Let users see detection rules
3. **Custom criteria** - Allow users to add domain-specific rules
4. **Validation profiles** - Pre-defined validation levels

### Monitoring

We should track:
- cf_xarray API changes
- New CF convention versions
- Community feedback on our approach

## Conclusion

By using cf_xarray as a required dependency for CF standards, we:
- ✅ Follow community-agreed conventions
- ✅ Avoid reinventing the wheel
- ✅ Ensure ecosystem compatibility
- ✅ **Enable metadata-only workflows** (no data required!)
- ✅ Simplify codebase (no optional dependency handling)
- ✅ Guarantee consistent behavior for all users

This is the right approach for a metadata-focused library that wants to integrate
with the broader scientific Python ecosystem while maintaining true metadata-only
capabilities.

## References

- [cf_xarray Documentation](https://cf-xarray.readthedocs.io/)
- [CF Conventions](http://cfconventions.org/)
- [IOOS Compliance Checker](https://github.com/ioos/compliance-checker)
- [MetPy](https://unidata.github.io/MetPy/)
- [Iris](https://scitools-iris.readthedocs.io/)
