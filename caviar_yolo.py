# Based on https://github.com/WongKinYiu/YOLO/blob/main/examples/notebook_inference.ipynb

import sys
from pathlib import Path

import torch
from hydra import compose, initialize

project_root = Path().resolve().parent
sys.path.append(str(project_root))

from yolo import (
    FastModelLoader,
    AugmentationComposer,
    Config,
    PostProcess,
    create_converter,
)

CONFIG_PATH = "./yolo_config"
CONFIG_NAME = "config"
MODEL = "v9-c"

DEVICE = "cuda:0"

device = torch.device(DEVICE)

with initialize(config_path=CONFIG_PATH, version_base=None, job_name="caviar"):
    cfg: Config = compose(
        config_name=CONFIG_NAME,
        overrides=[
            "task=inference",
            f"model={MODEL}",
        ],
    )

    model = FastModelLoader(cfg).load_model(device)

    transform = AugmentationComposer([], cfg.image_size)

    converter = create_converter(
        cfg.model.name, model, cfg.model.anchor, cfg.image_size, device
    )

    post_proccess = PostProcess(converter, cfg.task.nms)
