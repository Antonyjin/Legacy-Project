# Test Database Information

## Database: `test.gwb`

### Location
`GeneWeb/bases/test.gwb/`

### Content
The `test.gwb` database contains genealogical data for the **British Royal Family**, specifically focused on Charles Windsor (King Charles III) and related individuals.

**Sample persons** (from GEDCOM export):
- **Charles Windsor** (Charles III Philip Arthur George)
  - Born: November 14, 1948
  - Description: "Prince Charles, born in 1948, Prince of Wales and heir apparent to the British crown..."
- Plus approximately 188 total individuals in the family tree

### Format
- **Binary format**: `.gwb` (GeneWeb's proprietary database format)
- **Configuration**: `test.gwf` (settings for access, privacy, display options)
- **Lock file**: `test.lck` (prevents concurrent modifications)

### Purpose
This database is used for:
1. **Golden tests**: Regression testing to ensure OCaml behavior doesn't change
2. **Integration tests**: Validating HTTP endpoints and HTML rendering
3. **Development**: Local testing and development with real genealogical data

### Configuration (`test.gwf`)
```
access_by_key=yes
disable_forum=yes
hide_private_names=no
use_restrict=no
show_consang=yes
display_sosa=yes
max_anc_level=8
max_desc_level=12
template=*
```

### Origin
The database appears to be:
- A sample genealogical dataset shipped with the GeneWeb distribution
- Based on publicly available information about the British Royal Family
- Used as a demonstration/test dataset (188 persons is appropriately sized for testing)

### Access URLs
When `gwd` is running:
- Home page: `http://localhost:2317/test`
- Person page (Charles): `http://localhost:2317/test?p=Charles&n=Windsor`
- Search: `http://localhost:2317/test?m=LR&v=<name>`

### Notes
- **NOT production data**: This is a test/demo database
- **Public figures**: Contains only publicly available information
- **Privacy**: No sensitive personal data; all individuals are public figures
- **Size**: Small enough for fast tests, large enough to be realistic

## Alternative Database: `base.gwb`

A second database `base.gwb` also exists with similar content and configuration. The golden tests automatically detect and use `test.gwb` if present, falling back to `base.gwb` if needed.

## For New Tests

When adding new test cases:
1. Use `test.gwb` as the primary test database
2. Reference well-known individuals like Charles Windsor for consistency
3. Export to GEDCOM to inspect available data: `./GeneWeb/gw/gwb2ged GeneWeb/bases/test.gwb -o output.ged`

