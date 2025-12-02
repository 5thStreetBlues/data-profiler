"""Check installed distributions for missing or non-string versions.
Run this in the environment that showed the pip error to find the bad package.
"""
import importlib.metadata as md


def main():
    bad = []
    total = 0
    for dist in md.distributions():
        total += 1
        name = None
        try:
            name = dist.metadata.get('Name') if dist.metadata else None
        except Exception:
            pass
        try:
            ver = dist.version
        except Exception as e:
            bad.append((name, None, f"error: {e!r}"))
            continue
        if ver is None or not isinstance(ver, str):
            bad.append((name, ver, type(ver).__name__))

    if not bad:
        print(f"checked {total} distributions, found 0 problematic entries")
        return

    print(f"checked {total} distributions, found {len(bad)} problematic entries")
    print("Detailed info follows:\n")
    for name, ver, info in bad:
        print("--- Problematic distribution ---")
        print("Name:", repr(name))
        print("Version:", repr(ver))
        print("Info:", info)
        # attempt to find the actual Distribution object again to print its files/location
        for dist in md.distributions():
            try:
                dname = dist.metadata.get('Name') if dist.metadata else None
            except Exception:
                dname = None
            dver = None
            try:
                dver = dist.version
            except Exception:
                dver = None
            if dname == name and dver == ver:
                # print some attributes
                try:
                    print('repr(dist):', repr(dist))
                except Exception as e:
                    print('repr(dist): error', e)
                try:
                    print('_path:', getattr(dist, '_path', None))
                except Exception as e:
                    print('_path: error', e)
                try:
                    print('locate_file on first file:', None)
                except Exception:
                    pass
                try:
                    print('files:', list(dist.files)[:5] if dist.files else None)
                except Exception as e:
                    print('files: error', e)
                try:
                    print('metadata keys:', list(dist.metadata.keys()) if dist.metadata else None)
                except Exception as e:
                    print('metadata: error', e)
                break
    if bad:
        # non-zero exit to fail CI
        import sys

        sys.exit(1)



if __name__ == '__main__':
    main()
