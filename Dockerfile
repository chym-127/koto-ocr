FROM registry.baidubce.com/paddlepaddle/paddle:2.5.1
RUN pip3 install --upgrade pip \
&& python3 -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple \
&& git clone https://gitee.com/paddlepaddle/PaddleOCR  \
&& cd PaddleOCR  \
&& pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& cd .. \
&& git clone https://gitee.com/paddlepaddle/PaddleSeg.git \
&& cd PaddleSeg/Matting  \
&& mkdir pretrained_models && cd pretrained_models \
&& wget https://paddleseg.bj.bcebos.com/matting/models/ppmattingv2-stdc1-human_512.pdparams \
&& cd .. \
&& pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip install -v -e . \
&& pip install fastapi 'uvicorn[standard]' python-multipart -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip install "paddleocr>=2.0.1" \
&& apt update && apt install ffmpeg -y \
&& cd /home && mkdir PaddleSeg-OutPut
