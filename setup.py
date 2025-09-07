from setuptools import setup, find_packages

setup(
    name="bill-converter",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个将支付宝、微信、银行信用卡等账单数据转换为MoneyPro格式的工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bill-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "PyPDF2>=1.26.0",
        "click>=8.0.0",
        "forex-python>=1.8",
    ],
    entry_points={
        "console_scripts": [
            "bill-converter=bill_converter.main:main",
        ],
    },
)