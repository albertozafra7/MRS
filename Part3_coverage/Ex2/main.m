% Struct agent:
    % position
    % radius
    % power
    % velocity
    % max_power
    % max_vel

% matrix world where each position (element) goes from 0-10 (being this value the coverage level)

F = 0;  % Forgetting factor: how the enviroment forgets
G = 1;  % Gain: how does the agent affect
gridSize = 100;

k = 1;
time_steps = -1;
map = ones(gridSize)*100;

Lambda = 0;

while k<=time_steps || time_steps==-1
    F = exp(F*k);
    G = (G/F) * (exp(F) - 1);
    Lambda(k+1) = F * Lambda(k) + G * alpha;

    k = k+1;
end
