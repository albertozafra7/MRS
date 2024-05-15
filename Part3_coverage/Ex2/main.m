%% PARAMETERS
params.A = -0.01;  % Forgetting factor: how the enviroment forgets
params.B = 1;  % Gain: how does the agent affect
params.gridSize = 200;

params.time_steps = 300;   % number or -1 for infinite
params.num_agents = 6;     % number of agents
params.method = "quant";   % update method (min/rand/quant/terc)

<<<<<<< Updated upstream
params.rad = 40;           % radius of the robot
params.power = 50;         % power of the robot
params.max_vel = 4;        % max velocity of the robot

params.minPerc = 0.3;      % minimum admisible percentage
params.maxPerc = 0.8;      % maximum admisible percentage
=======
params.rad = 40;    % radius of actuation of the robot
params.power = 50;  % power of the robot
params.max_vel = 4; % max vel of the robot

params.minPerc = 0.3; % minimum acceptable percentage of coverage
params.maxPerc = 0.8; % maximum acceptable percentage of coverage
>>>>>>> Stashed changes

% SIMULATION
[Lambda,ratios] = simulate(params);

%% PLOTTING
figure;
plot(ratios(:,1),'black');
hold on;
plot(ratios(:,2),'red');
plot(ratios(:,3),'green');
legend(["Undercovered" "Overcovered" "Covered"])
ylim([1 100]);
ylabel("Area (%)")
xlabel("Time")
title("Percentage of area")

%% REPLAY
colMap = getColormap(params.minPerc,params.maxPerc);
figure;
for k = 1:length(Lambda)
    plotting([],squeeze(Lambda(k,:,:)),ratios(k,3),colMap)
    pause(0.01);
end




