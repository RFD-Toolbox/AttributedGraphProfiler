# **RFD Query Rewriter**
## Authors
- [Casciano Maurizio](https://linkedin.com/in/mauriziocasciano)
- [Tropeano Domenico Antonio](https://www.linkedin.com/in/domenico-antonio-tropeano/)
### System Requirements
- Python 3.6
- GCC

### Environment Setup
##### Install Python 3.6
```console
# Install Python 3.6
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.6
sudo apt install python3.6-dev

# Check all the installed Python versions and paths
whereis python

# Check Python 3.6 version
python3.6 -V
```

##### Virtual Environment
```console
# Create virtual environment using Python 3.6
virtualenv -p python3.6 venv
# Activate it
source venv/bin/activate
```