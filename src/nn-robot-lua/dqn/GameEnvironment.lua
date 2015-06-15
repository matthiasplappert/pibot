-- The GameEnvironment class.
local gameEnv = torch.class('dqn.GameEnvironment')
local py = require('fb.python')


function gameEnv:__init(_opt)
    -- TODO: make this configurable
    py.exec([=[
import pickle
import Pyro4
import cv2
class GameEnvironment(object):
    def __init__(self, name, host=None, port=None, grayscale=True, crop=True, resize=(84, 84)):
        uri = 'PYRONAME:' + name
        if host is not None:
            uri += '@' + str(host)
            if port is not None:
                uri += ':' + str(port)
        self.agent = Pyro4.Proxy(uri)
        self.grayscale = grayscale
        self.crop = crop
        self.resize = resize
        self.prev_score = 0
    def step(self, action):
        self.agent.perform_action(action)
        frame = pickle.loads(self.agent.perceive(grayscale=self.grayscale, crop=self.crop, resize=self.resize))
        # Calculate histogram over 16 bins. We then select the top bin. Our agent likes light, so the more
        # pixels we have in the top bin, the bigger a bright spot in the image is. Our agent is very happy if the
        # entire image is just a bright spot.
        n_bins = 16
        histogram = cv2.calcHist([frame], [0], None, [n_bins], [0, 255])[:, 0]
        curr_score = histogram[-1]
        if curr_score == 0:
            curr_score = 1
        delta = curr_score - self.prev_score
        print abs(delta) / curr_score
        reward = 0
        if abs(delta) / curr_score > 0.1:
            if delta > 0:
                reward = 1
            else:
                reward = -1
        self.prev_score = curr_score
        # TODO: maybe use those?
        terminal = False
        lives = 1
        return frame.astype(float) / 255.0, reward, terminal, lives
game = game.GameEnvironment('nn-robot', host='192.168.1.57', port=9090')
]=])
    
    local _opt = _opt or {}
    -- defaults to emulator speed
    self.game_path      = _opt.game_path or '.'
    self.verbose        = _opt.verbose or 0
    self._actrep        = _opt.actrep or 1
    self._random_starts = _opt.random_starts or 1
    self:reset(_opt.env, _opt.env_params, _opt.gpu)
    return self
end


function gameEnv:_updateState(frame, reward, terminal, lives)
    self._state.frame        = frame
    self._state.reward       = reward
    self._state.terminal     = terminal
    self._state.prev_lives   = self._state.lives or lives
    self._state.lives        = lives
    return self
end


function gameEnv:getState()
    return self._state.frame, self._state.reward, self._state.terminal
end


function gameEnv:reset(_env, _params, _gpu)
    self._actions = self:getActions()

    -- start the game
    if self.verbose > 0 then
        print('\nPlaying game')
    end

    self:_resetState()
    self:_updateState(self:_step(0))
    self:getState()
    return self
end


function gameEnv:_resetState()
    self._state = self._state or {}
    return self
end


-- Function plays `action` in the game and return game state.
function gameEnv:_step(action)
    local result = py.eval('game.step(' .. action .. ')')
    -- return x.data, x.reward, x.terminal, x.lives
    return result[1], result[2], result[3], result[4]
end


-- Function plays one random action in the game and return game state.
function gameEnv:_randomStep()
    return self:_step(self._actions[torch.random(#self._actions)])
end


function gameEnv:step(action, training)
    -- accumulate rewards over actrep action repeats
    local cumulated_reward = 0
    local frame, reward, terminal, lives
    for i=1,self._actrep do
        -- Take selected action; ATARI games' actions start with action "0".
        frame, reward, terminal, lives = self:_step(action)

        -- accumulate instantaneous reward
        cumulated_reward = cumulated_reward + reward

        -- Loosing a life will trigger a terminal signal in training mode.
        -- We assume that a "life" IS an episode during training, but not during testing
        if training and lives and lives < self._state.lives then
            terminal = true
        end

        -- game over, no point to repeat current action
        if terminal then break end
    end
    self:_updateState(frame, cumulated_reward, terminal, lives)
    return self:getState()
end


--[[ Function advances the emulator state until a new game starts and returns
this state. The new game may be a different one, in the sense that playing back
the exact same sequence of actions will result in different outcomes.
]]
function gameEnv:newGame()
    local obs, reward, terminal
    terminal = self._state.terminal
    while not terminal do
        obs, reward, terminal, lives = self:_randomStep()
    end
    -- take one null action in the new game
    return self:_updateState(self:_step(0)):getState()
end


--[[ Function advances the emulator state until a new (random) game starts and
returns this state.
]]
function gameEnv:nextRandomGame(k)
    local obs, reward, terminal = self:newGame()
    k = k or torch.random(self._random_starts)
    for i=1,k-1 do
        obs, reward, terminal, lives = self:_step(0)
        if terminal then
            print(string.format('WARNING: Terminal signal received after %d 0-steps', i))
        end
    end
    return self:_updateState(self:_step(0)):getState()
end


--[[ Function returns the number total number of pixels in one frame/observation
from the current game.
]]
function gameEnv:nObsFeature()
    return 84 * 84 * 1 -- 84 x 84 pixels and one channel
end


-- Function returns a table with valid actions in the current game.
function gameEnv:getActions()
    -- simply return a list of indexes that represent actions
    return {0, 1, 2, 3}
end
