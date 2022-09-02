Some custom scripts for seiscomp

**update_key_bindings.py**
Uses slinktool to get a list of stations from an acquisition server, and then adds key binding files for any that are missing.

```
Usage: update_key_bindings.py [OPTIONS]

Options:
  --ip-address TEXT         IP Address of acquisition server.
  --slarchive-process TEXT  Name of slarchive process
  --help                    Show this message and exit.
```