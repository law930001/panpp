model = dict(
    # type='PAN_PP',
    type='PAN_PP_V2',
    # type='PAN_PP_V3',
    backbone=dict(
        type='resnet18',
        # type='resnet18_fusion',
        # type='resnet18_csp',
        # type='resnet50',
        # type='resnet101',
        # type='efficentnet_b0',
        # type='efficentnet_b3',
        # type='efficentnet_b7',
        pretrained=True
    ),
    neck=dict(
        # type='FPEM_v2',
        type='FPN_v3_3',
        # type='FPN_v3_3_2',
        # type='FPN_v3_4', # cb_multi_part
        in_channels=(64, 128, 256, 512), # resnet18 & resnet_csp
        # in_channels=(256, 512, 1024, 2048), # resnet50 & resnet101
        # in_channels=(16, 40, 112, 320), # efficientNet_b0
        # in_channels=(24, 48, 136, 384), # efficientNet_b3
        # in_channels=(48, 80, 224, 640), # efficientNet_b7
        out_channels=128
    ),
    detection_head=dict(
        # type='PAN_PP_DetHead',
        # type='PAN_PP_DetHead_v2',
        type='PAN_PP_DetHead_v2_1', # attention_head
        in_channels=512,
        hidden_dim=128,
        num_classes=6,
        loss_text=dict(
            type='DiceLoss',
            loss_weight=1.0
        ),
        loss_kernel=dict(
            type='DiceLoss',
            loss_weight=0.5
        ),
        loss_emb=dict(
            type='EmbLoss_v2',
            feature_dim=4,
            loss_weight=0.25
        ),
        use_coordconv=False,
    )
)
data = dict(
    batch_size=3, # 12
    num_workers=8, # 8
    train=dict(
        type='PAN_PP_TT',
        split='train',
        is_transform=True,
        # img_size=640, # 640
        # short_size=640, # 640
        img_size=1000, # 1000
        short_size=1000, # 1000
        kernel_scale=0.5, #0.5
        read_type='pil',
        with_rec=True
    ),
    test=dict(
        type='PAN_PP_TT',
        split='test',
        # short_size=640,
        short_size=1000,
        read_type='pil',
        with_rec=True
    )
)
train_cfg = dict(
    lr=1e-3,
    schedule='polylr',
    epoch=600, # 600
    optimizer='Adam',
    use_ex=False,
    # pretrain='checkpoints/pan_pp_synth/checkpoint.pth.tar'
)
test_cfg = dict(
    min_score=0.9, # 0.9
    min_area=260, #D 260
    min_kernel_area=2.6, # 2.6
    # scale=4, # 4
    scale=1,
    bbox_type='poly',
    result_path='outputs/submit_tt',
)
