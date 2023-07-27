# BK Consulting Robot Server
Source code for BK Consulting Robot Server

## 1. Installation
- Create virtual environment
```
python -m venv venv

```
- Activate environment
```
source venv/bin/activate # For linux
.\venv\Scripts\activate
```
- Install requirements
```
pip install -r requirements.txt
```

## 2. Run
To change server configs, go to file `configs.yml`. Then run server with following command:
```
bash scripts/run.sh
```