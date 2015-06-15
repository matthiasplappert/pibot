--[[
Copyright (c) 2014 Google Inc.

See LICENSE file for full terms of limited license.
]]

require "nn"

local scale = torch.class('nn.Identity', 'nn.Module')


function scale:__init(height, width)
    self.height = height
    self.width = width
end

function scale:forward(x)
    return x
end

function scale:updateOutput(input)
    return self:forward(input)
end

function scale:float()
end
