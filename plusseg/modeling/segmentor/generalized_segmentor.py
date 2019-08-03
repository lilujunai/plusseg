"""
Implement the Generalized Segmentation Model
"""

import torch
from torch import nn

# from plusseg.structures
from ..backbone import build_backbone
from ..decoder import build_decoder
from ..postprocess import build_post_processor

class GeneralizeSegmentor(nn.Module):
    """
    Main class for Generalized Segmentation Model. Current support semantic segmentation
    It consits of three main parts:
    - backbone
    - decoder
    - post_processor
    """

    def __init__(self, cfg):
        super(GeneralizeSegmentor, self).__init__()

        self.backbone = build_backbone(cfg)
        self.decoder = build_decoder(cfg, self.backbone.out_channels)
        self.postprocessor = build_post_processor(cfg)

    def forward(self, images, targets=None):
        """
        Arguments:
            images (list[Tensor] or ImageList): images to be processed
            targets (list[Tenosr]): ground-truth mask for this image(optional)
        
        Returns:
            results (list[Tensor]): the output from the model
        """
        if self.training and targets is None:
            raise ValueError("In the training time, targets should be passed")
        
        # images = to_image_list(images)
        features = self.backbone(images)

        decoder_out = self.decoder(features)

        if self.postprocessor:
            final_out = self.postprocessor(decoder_out)
        else:
            final_out = decoder_out
        
        
        if self.training:
            segmentation_loss = self.loss_calculator(final_out, targets)
            return final_out, segmentation_loss
        
        return final_out