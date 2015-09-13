--[[
Copyright (c) 2014 Google Inc.

See LICENSE file for full terms of limited license.
]]

if not dqn then
    require "initenv"
end

local cmd = torch.CmdLine()
cmd:text()
cmd:text('Train Agent in Environment:')
cmd:text()
cmd:text('Options:')

cmd:option('-framework', '', 'name of training framework')
cmd:option('-env', '', 'name of environment to use')
cmd:option('-game_path', '', 'path to environment file (ROM)')
cmd:option('-env_params', '', 'string of environment parameters')
cmd:option('-pool_frms', '',
           'string of frame pooling parameters (e.g.: size=2,type="max")')
cmd:option('-actrep', 1, 'how many times to repeat action')
cmd:option('-random_starts', 0, 'play action 0 between 1 and random_starts ' ..
           'number of times at the start of each training episode')

cmd:option('-name', '', 'filename used for saving network and training history')
cmd:option('-network', '', 'reload pretrained network')
cmd:option('-agent', '', 'name of agent file to use')
cmd:option('-agent_params', '', 'string of agent parameters')
cmd:option('-seed', 1, 'fixed input seed for repeatable experiments')
cmd:option('-games', 10, 'number of games to perform')

cmd:option('-verbose', 2,
           'the higher the level, the more information is printed to screen')
cmd:option('-threads', 1, 'number of BLAS threads')
cmd:option('-gpu', -1, 'gpu flag')

cmd:text()

local opt = cmd:parse(arg)

--- General setup.
local game_env, game_actions, agent, opt = setup(opt)

-- override print to always flush the output
local old_print = print
local print = function(...)
    old_print(...)
    io.flush()
end

local learn_start = agent.learn_start
local start_time = sys.clock()
local reward_counts = {}
local episode_counts = {}
local time_history = {}
local v_history = {}
local qmax_history = {}
local td_history = {}
local reward_history = {}
local step = 0
time_history[1] = 0

local total_reward
local nrewards
local nepisodes
local episode_reward
local game_count = 0
local game_step = 0

local screen, reward, terminal = game_env:newGame()

local output_path = '../frames/'

print("Iteration ..", step)
local best_game = {}
local curr_game = {}
local best_score = -1
local curr_score = 0
while game_count < opt.games do
    -- Save state
    curr_score = curr_score + reward
    -- frame = screen:reshape(3, 210, 160)  -- TODO: make this not hardcoded
    -- table.insert(curr_game, frame)
    
    step = step + 1
    game_step = game_step + 1
    local action_index = agent:perceive(reward, screen, terminal, true, 0.05)

    -- game over? get next game!
    if not terminal then
        screen, reward, terminal = game_env:step(game_actions[action_index])
    else
        print('Game ' .. game_count .. ' (' .. game_step .. ' steps): ' .. curr_score)
        if curr_score > best_score then
            best_game = curr_game
            best_score = curr_score
        end
        curr_score = 0
        curr_game = {}
        game_step = 0
        game_count = game_count + 1
        screen, reward, terminal = game_env:newGame()
    end

    if step%1000 == 0 then collectgarbage() end
end

print('played ' .. step .. ' steps and ' .. game_count .. ' games. Saving best game ...')
-- for idx, frame in pairs(best_game) do
--     image.save(output_path .. 'step-' .. idx .. '.png', frame)
-- end
