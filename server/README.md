# BK Consulting Robot Server
Source code for BK Consulting Robot Server

## 1. Installation
- Create virtual environment
```
python -m venv venv
source venv/bin/activate
```
- Clone VietASR repo to `stt` directory
```
mkdir stt
git clone git@github.com:dangvansam98/viet-asr.git stt
```
- Install `torch`
```
pip install torch===1.11.0+cu115 torchvision===0.12.0 torchaudio===0.11.0 -f https://download.pytorch.org/whl/torch_stable.html
```
- Install `kenlm`
```
pip install https://github.com/kpu/kenlm/archive/master.zip
```
- Install requirements
```
pip install -r requirements.txt
```

## 2. Run
To config server params, go to file `configs.yml`. Then run server with following command:
```
python app.py --config=configs.yml
```