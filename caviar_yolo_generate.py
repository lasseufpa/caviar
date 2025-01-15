# Based on https://github.com/WongKinYiu/YOLO/blob/main/examples/notebook_inference.ipynb

import sys
from pathlib import Path

import torch
from hydra import compose, initialize
from PIL import Image

project_root = Path().resolve().parent
sys.path.append(str(project_root))

from yolo import (
    AugmentationComposer,
    Config,
    PostProcess,
    create_converter,
    create_model,
    draw_bboxes,
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
    model = create_model(cfg.model).to(device)

    torch.save("model", "caviar_yolo.pt")

    transform = AugmentationComposer([], cfg.image_size)

    converter = create_converter(
        cfg.model.name, model, cfg.model.anchor, cfg.image_size, device
    )
    post_proccess = PostProcess(converter, cfg.task.nms)


IMAGE_PATH = "/home/joaoborges/Downloads/airsimtest.png"
pil_image = Image.open(IMAGE_PATH)
image, bbox, rev_tensor = transform(pil_image)
image = image.to(device)[None]
rev_tensor = rev_tensor.to(device)[None]

with torch.no_grad():
    model.eval()
    predict = model(image)
    pred_bbox = post_proccess(predict, rev_tensor)
    pred_class = cfg.dataset.class_list[int(pred_bbox[0][0].cpu().numpy()[0])]
    pred_prob = pred_bbox[0][0].cpu().numpy()[5]

img = draw_bboxes(pil_image, pred_bbox, idx2label=cfg.dataset.class_list)

img.show()

print("END!")
