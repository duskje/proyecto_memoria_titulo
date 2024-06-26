import subprocess

from loguru import logger

class Flatpak:
    def __init__(self):
        pass

    @property
    def installed_packages(self):
        result = subprocess.run(['flatpak', 'list'], capture_output=True, text=True)

        package_names = []

        for line in result.stdout.split('\n'):
            if line:
                package_title, package_name, version, branch, origin, installation = line.split('\t')
                package_names.append(package_name)

        return package_names

    def execute_update(self, package_name: str, commit: str):
        if package_name not in self.installed_packages:
            raise ModuleNotFoundError

        result = subprocess.run(['flatpak', 'update', '-y', '--commit', commit, package_name],
                                capture_output=True,
                                text=True)

        logger.debug("\n" + result.stdout)


if __name__ == "__main__":
    Flatpak().execute_update('org.flatpak.debian_package_python', '84f856addf54777f242d8f86b6176f8ba07c97c3ad6c07d19421403de65368d7')
