from re import X
import torch
import torch.nn as nn
import torch.nn.functional as F

import math

from ..utils import Conv_BN_ReLU


class ChannelAttention(nn.Module):
    def __init__(self, in_planes, pool_size, ratio=16):
        super(ChannelAttention, self).__init__()

        self.avg_pool = nn.AdaptiveAvgPool2d(pool_size)
        self.max_pool = nn.AdaptiveMaxPool2d(pool_size)
           
        # self.fc = nn.Sequential(nn.Conv2d(in_planes, in_planes // 16, 1, bias=False),
        #                        nn.ReLU(),
        #                        nn.Conv2d(in_planes // 16, in_planes, 1, bias=False))
        # self.sigmoid = nn.Sigmoid()

    def forward(self, x):
  
        return self.avg_pool(x) + self.max_pool(x)

    # def forward(self, x):
    #     avg_out = self.fc(self.avg_pool(x))
    #     max_out = self.fc(self.max_pool(x))
    #     out = avg_out + max_out
    #     return out
    #     # return self.sigmoid(out)

# class SpatialAttention(nn.Module):
#     def __init__(self, kernel_size=7):
#         super(SpatialAttention, self).__init__()

#         self.conv1 = nn.Conv2d(2, 1, kernel_size, padding=kernel_size//2, bias=False)
#         # self.sigmoid = nn.Sigmoid()

#     def forward(self, x):
#         avg_out = torch.mean(x, dim=1, keepdim=True)
#         max_out, _ = torch.max(x, dim=1, keepdim=True)
#         x = torch.cat([avg_out, max_out], dim=1)
#         x = self.conv1(x)
#         return x
#         # return self.sigmoid(x)


class Channel_Attention(nn.Module):
    def __init__(self, inChannels, k):
        super(Channel_Attention, self).__init__()
        embedding_channels = inChannels // k  # C_bar

        pool_size = 1
        part_ratio = 0.5 # keep ratio

        self.key = ChannelAttention(embedding_channels, pool_size=pool_size)
        self.query = ChannelAttention(embedding_channels, pool_size=pool_size)


        self.softmax  = nn.Softmax(dim=1)
        self.sigmoid = nn.Sigmoid()

        self.part1_chnls = int(inChannels * part_ratio)

        # self.pos_encoder = PositionalEncoding(inChannels)


    def forward(self,q,k,v):
        """
            inputs:
                x: input feature map [Batch, Channel, Height, Width]
            returns:
                out: self attention value + input feature
                attention: [Batch, Channel, Height, Width]
        """

        ori = q + k + v

        batchsize, C, H, W = q.size()

        f_x = self.key(k).view(batchsize,   -1, C)      # Keys                  [B, C_bar, N]
        g_x = self.query(q).view(batchsize, -1, C)      # Queries               [B, C_bar, N]
        h_x = v.view(batchsize, -1, C)                      # Values                [B, C_bar, N]
        
        
        # f_x = self.pos_encoder(f_x) # postion embedding
        # g_x = self.pos_encoder(g_x) # postion embedding


        s =  torch.bmm(f_x.permute(0,2,1), g_x)         # Scores                [B, N, N]
        beta = self.softmax(s)                          # Attention Map         [B, N, N]

        v = torch.bmm(h_x, beta)                        # Value x Softmax       [B, C_bar, N]
        o = v.view(batchsize, C, H, W)                  # Recover input shape   [B, C_bar, H, W]

        
        o = self.sigmoid(o)

        y = o * ori                     
        
        return y

### original
class attn_v5(nn.Module):

    def __init__(self, planes):
        super(attn_v5, self).__init__()

        k = 4

        self.t = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0)
        self.b = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0)
        self.m = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0)

        self.q = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0) 
        self.k = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0) 
        self.v = Conv_BN_ReLU(planes,planes,1,stride=1,padding=0) 

        self.attn = Channel_Attention(planes,k=k)

    def forward(self, t, b, m):

        mix_fusion = self.t(t) + self.b(b) + self.m(m)

        q, k, v = self.q(mix_fusion), self.k(mix_fusion), self.v(mix_fusion)

        out = self.attn(q, k, v)

        return out

class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int,max_len: int = 5000):
        super().__init__()

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return x