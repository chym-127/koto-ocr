import subprocess
from pathlib import Path
import os

OUTPUT_PATH = '/home/PaddleSeg-OutPut'

def remove_image_bg(input_file_path: str):
    suffix = Path(input_file_path).suffix
    rgba_filename = os.path.basename(input_file_path).replace(suffix,'_rgba.png')
    alpha_filename = os.path.basename(input_file_path).replace(suffix,'_alpha.png')

    proc = subprocess.Popen(f'cd /home/PaddleSeg/Matting && python tools/predict.py \
                            --config configs/ppmattingv2/ppmattingv2-stdc1-human_512.yml \
                            --model_path pretrained_models/ppmattingv2-stdc1-human_512.pdparams \
                            --image_path {input_file_path} \
                            --save_dir {OUTPUT_PATH} \
                            --fg_estimate True', shell=True)
    try:
        proc.communicate(timeout=300)
        return {
            "rgba": f'{OUTPUT_PATH}/{rgba_filename}',
            "alpha": f'{OUTPUT_PATH}/{alpha_filename}'
        }
    except Exception:
        proc.kill()
        raise Exception("failed")