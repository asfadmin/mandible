# Mandible
[![Test](https://github.com/asfadmin/mandible/actions/workflows/test.yml/badge.svg)](https://github.com/asfadmin/mandible/actions/workflows/test.yml)

A generic framework for writing satellite data ingest systems

## Installing
Mandible can be installed from GitHub using `pip`.
```
$ pip install git+https://github.com/asfadmin/mandible@v0.8.0
```

To install with all extra dependencies:
```
$ pip install git+https://github.com/asfadmin/mandible@v0.8.0#egg=mandible[all]
```

To install the latest development version:
```
$ pip install git+https://github.com/asfadmin/mandible
```

## Features
- [Templated metadata extraction](#templated-metadata-extraction)

### Templated metadata extraction
The metadata mapper is used to extract metadata from one or more source files
and insert it into a JSON style template.

Example:
```python
from mandible.metadata_mapper import (
    ConfigSourceProvider,
    Context,
    MetadataMapper,
)

mapper = MetadataMapper(
    template={
        "polarization": {
            "@mapped": {
                "source": "met.json",
                "key": "Polarization"
            }
        }
    },
    source_provider=ConfigSourceProvider({
        "met.json": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": r".*\.met\.json"
                }
            },
            "format": {
                "class": "Json"
            }
        }
    })
)
context = Context(
    files=[{
        "name": "my-granule.met.json",
        "path": "/tmp/ingest/my-granule.met.json"
    }]
)

mapper.get_metadata(context)
# Returns an object that looks like the template with values replaced
# {"polarization": "VV"}
```
