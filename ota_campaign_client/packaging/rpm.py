import subprocess

class RPM:
    def __init__(self):
        pass

    def get_current_package_version(self, package_name: str) -> str:
        result = subprocess.run(['rpm', '-qa',  '--queryformat', "'%{VERSION}'", package_name], capture_output=True)
        return result.stdout.decode('utf-8')

    def use_package(self, package: str):
        pass
