import sys
from distutils.core import setup
import py2exe
import numpy  # WARNING: requried to avoid a dll error message

import os
from os.path import expanduser

# data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
# data_files = [("Microsoft.VC90.CRT",glob(r'C:\Windows\WinSxS\amd64_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.9158_none_08e47e47a83d53d6\*.*'))]

sys.argv.append('py2exe')  # so we don't have to append it each time
py2exe_options = dict(
    excludes=['_ssl', 'pyreadline', 'doctest', 'calendar', 'pbd'],
    bundle_files=3,
    compressed=False,
    dll_excludes=['api-ms-win-core-heap-l2-1-0.dll',  # never found this one
                  'api-ms-win-core-errorhandling-l1-1-1.dll',
                  'api-ms-win-core-file-l1-2-1.dll',
                  'api-ms-win-core-handle-l1-1-0.dll',
                  'api-ms-win-core-heap-l1-1-0.dll',
                  'api-ms-win-core-processthreads-l1-1-2.dll',
                  'api-ms-win-core-profile-l1-1-0.dll',
                  'api-ms-win-core-heap-l1-2-0.dll',
                  'api-ms-win-core-registry-l1-1-0.dll',
                  'API-MS-Win-core-string-l2-1-0.dll',
                  'api-ms-win-core-io-l1-1-1.dll',
                  'api-ms-win-core-sysinfo-l1-2-1.dll',
                  'api-ms-win-core-string-l1-1-0.dll',
                  'api-ms-win-core-libraryloader-l1-2-0.dll',
                  'api-ms-win-core-synch-l1-2-0.dll',
                  'api-ms-win-core-com-l1-1-1.dll',
                  'api-ms-win-core-memory-l1-1-2.dll',
                  'api-ms-win-core-libraryloader-l1-2-1.dll',
                  'api-ms-win-core-io-l1-1-1.dll',
                  'api-ms-win-core-heap-l1-2-0.dll',
                  'api-ms-win-core-version-l1-1-1.dll',
                  'api-ms-win-core-localization-l1-2-1.dll',
                  'api-ms-win-core-version-l1-1-0.dll',
                  'api-ms-win-security-base-l1-2-0.dll',
                  'api-ms-win-core-rtlsupport-l1-2-0.dll'],
    dist_dir=expanduser("~\AppData\Local\Lasagna\dist"),
)

build_options = dict(
    build_base=expanduser("~\AppData\Local\Lasagna\\build"),
)

print("BUILDING IN {}".format(py2exe_options['dist_dir']))
setup(
    console=['main.py'],
    options={'py2exe': py2exe_options, 'build': build_options},
    zipfile=None,
#	data_files=data_files
)

print("BUILT IN {}".format(py2exe_options['dist_dir']))
