FROM registry.baidubce.com/paddlepaddle/paddle:2.5.1
RUN pip3 install --upgrade pip \
&& python3 -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple \
&& git clone https://gitee.com/paddlepaddle/PaddleOCR  \
&& cd PaddleOCR  \
&& pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip install fastapi 'uvicorn[standard]' python-multipart -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip install "paddleocr>=2.0.1" 
