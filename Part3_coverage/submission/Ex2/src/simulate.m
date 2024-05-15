function [Lambda,ratios] = simulate(p)
    time_size = p.time_steps;
    if time_size==-1
        time_size = 1;
    end
    
    colMap = getColormap(p.minPerc,p.maxPerc);

    Lambda = zeros([time_size,p.gridSize,p.gridSize]);
    world = zeros(p.gridSize);
    Lambda(1,:,:) = world;
    ratios = zeros([time_size 3]);
    
    agents = agent_initializer(p.num_agents,p.gridSize,p.rad,p.power,p.max_vel);
    
    k = 1;
    while k<p.time_steps || p.time_steps==-1
    
        plotting(agents,world,ratios(k,3),colMap)
        F = exp(p.A);
        G = (p.B/p.A) * (F - 1);
        alpha = compute_alphas(agents,p.gridSize);
        agents = update_positions(agents,world,p.minPerc,p.method);
        world = min(ones(p.gridSize),F * world + G * alpha);
        Lambda(k+1,:,:) = world;

        underRatio = world < p.minPerc;
        overRatio = world > p.maxPerc;
        ratios(k+1,1) = (sum(underRatio(:)) * 100) / length(world).^2;
        ratios(k+1,2) = (sum(overRatio(:)) * 100) / length(world).^2;
        ratios(k+1,3) = 100-ratios(k+1,2)-ratios(k+1,1);

        k = k+1;
    
        pause(0.01);
    end
end

%% Other functions

% Struct agent:
    % position
    % radius
    % power
    % velocity
    % max_power
    % max_vel
    % goal

function agents = agent_initializer(num,gridSize,rad,power,max_vel)
    agents = [];
    vel = [0,0];
    for i = 1:num
        agents.position(i,:) = rand([1,2])*gridSize;
        agents.radius(i) = rad;
        agents.power(i) = power;
        agents.velocity(i,:) = vel;
        agents.max_vel(i) = max_vel;
        agents.goal(i,:) = agents.position(i,:);
    end
    agents.n = num;
end

function alphas = compute_alphas(agents,gridSize)
    alphas = zeros(gridSize);
    for i = 1:agents.n
        rad = agents.radius(i);
        h = agents.power(i)*fspecial('gaussian', floor(2*rad), rad/2);
        h(h<h(rad,1)) = 0;
        pMin = floor(agents.position(i,:)-rad);
        pMax = floor(pMin+2*rad-1);
        aMin = max(1,pMin);
        aMax = min(gridSize,pMax);
        fMin = 1+max([0,0],aMin-pMin);
        fMax = floor(2*rad)-max([0,0],pMax-aMax);

        alphas(aMin(1):aMax(1),aMin(2):aMax(2)) = alphas(aMin(1):aMax(1),aMin(2):aMax(2))+h(fMin(1):fMax(1),fMin(2):fMax(2));
    end
end

function agents = update_positions(agents,world,minVal,method)
    stepSize = 2;
    gridSize = size(world,1);
%     mins = islocalmin(world);
    mins = world<minVal;
    mins(1,:)=0;mins(:,1)=0;mins(end,:)=0;mins(:,end)=0;

    idx = find(mins'==1);
    if isempty(idx)
        return
    end
    idy = floor(idx/gridSize)+1;
    idx = mod(idx,gridSize);
    
    for i = 1:agents.n
        pos = agents.position(i,:);
        dist2goal = sqrt(sum((pos-agents.goal(i,:)).^2));
        if dist2goal<5
            diff = [idx-pos(2),idy-pos(1)];
    
            squared_distances = sum(diff.^2, 2);  % Sum squares along columns
    
            if method == "min"
                [sqDist, index] = min(squared_distances);
            else if method == "rand"
                index = randi([1 length(squared_distances)]);
                sqDist = squared_distances(index);
            else if method == "quant"
                [sqDists, indexes] = sort(squared_distances);
                index = indexes(1+floor(abs(normrnd(0,length(indexes)/4))));
                sqDist = squared_distances(index);
            else if method == "terc"
                [sqDists, indexes] = sort(squared_distances);
                index = indexes(ceil(length(indexes)/3));
                sqDist = squared_distances(index);
            end
            end
            end
            end

            agents.goal(i,:) = [idy(index),idx(index)];
            dist2goal = sqrt(sqDist);
        end
        agents.velocity(i,:) = (agents.goal(i,:)-pos)/dist2goal;
        posIdx = floor(pos);
        agents.position(i,:) = max([1,1],min([gridSize,gridSize],pos + stepSize*agents.max_vel(i)*((world(posIdx(1),posIdx(2))+1).^2)*agents.velocity(i,:)/4));

    end
end
