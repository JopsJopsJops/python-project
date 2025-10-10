from setuptools import setup, find_packages

setup(
    name="expense-tracker-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15",
        "pandas>=1.5",
        "openpyxl>=3.0",
        "fpdf>=1.7",
        "reportlab>=4.0",
        "matplotlib>=3.5",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-qt>=4.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.0",
            "pytest-xdist>=3.0",
        ],
    },
)
