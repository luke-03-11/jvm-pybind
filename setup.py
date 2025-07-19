import os

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        self.install_pth_file()

    def install_pth_file(self):
        """Install .pth file in site-packages directory"""
        try:
            site_packages = self.install_lib
            if site_packages is None:
                print("Failed to get site-packages directory")
                return
            pth_file = os.path.join(site_packages, "jvm.pth")

            with open(pth_file, "w") as f:
                f.write("import jvm\n")

            print(f"Installed .pth file: {pth_file}")
        except Exception as e:
            print(f"Failed to install .pth file: {e}")


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)
        self.install_pth_file()

    def install_pth_file(self):
        """Install .pth file in site-packages directory for editable install"""
        try:
            import site

            site_packages = site.getsitepackages()[0]
            pth_file = os.path.join(site_packages, "jvm.pth")

            with open(pth_file, "w") as f:
                f.write("import jvm\n")

            print(f"Installed .pth file for editable install: {pth_file}")
        except Exception as e:
            print(f"Failed to install .pth file for editable install: {e}")


if __name__ == "__main__":
    setup(
        cmdclass={
            "install": PostInstallCommand,
            "develop": PostDevelopCommand,
        },
    )
