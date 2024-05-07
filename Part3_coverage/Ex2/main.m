

% matrix world where each position (element) goes from 0-10 (being this value the coverage level)

% START PARAMETERS
A = -0.1;  % Forgetting factor: how the enviroment forgets
B = 1;  % Gain: how does the agent affect
gridSize = 200;

k = 1;
time_steps = -1;
map = ones(gridSize)*100;
num_agents = 1;
% END PARAMETERS

time_size = time_steps;
if time_size==-1
    time_size = 1;
end

Lambda = zeros([time_size,gridSize,gridSize]);
Lambda(1,:,:) = rand(gridSize);

agents = agent_initializer(num_agents,gridSize);

while k<=time_steps || time_steps==-1
    plotting(agents,squeeze(Lambda(k,:,:)))
    F = exp(A*k);
    G = (B/A) * (F - 1);
    alpha = compute_alphas(agents,gridSize);
    Lambda(k+1,:,:) = F * squeeze(Lambda(k,:,:)) + G * alpha;
    k = k+1;
end

%%

% Struct agent:
    % position
    % radius
    % power
    % velocity
    % max_power
    % max_vel

function agents = agent_initializer(num,gridSize)
    agents = [];
    rad = 10;
    power = 10;
    vel = 1;
    max_vel = 1;
    for i = 1:num
        agents.position(i,:) = rand([1,2])*gridSize;
        agents.radius(i) = rad;
        agents.power(i) = power;
        agents.velocity(i) = vel;
        agents.max_vel(i) = max_vel;
    end
    agents.n = num;
end

function alphas = compute_alphas(agents,gridSize)
    alphas = zeros(gridSize);
    for i = 1:agents.n
        rad = agents(i).radius;
        h = agents(i).power*fspecial('gaussian', floor(2*rad), rad/2);
        h(h<h(rad,1)) = 0;
        pMin = floor(agents(i).position(:)-rad);
        pMax = floor(pMin+2*rad-1);
        aMin = max(1,pMin);
        aMax = min(gridSize,pMax);
        fMin = max(1,aMin-pMin);
        fMax = floor(2*rad)-min(0,aMax-pMax);

        alphas(aMin(2):aMax(2),aMin(1):aMax(1)) = alphas(aMin(2):aMax(2),aMin(1):aMax(1))+h(fMin(2):fMax(2),fMin(1):fMax(1));
    end
end



