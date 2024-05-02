function plotting(agents,world,coverage)
    % Struct agent:
        % position
        % radius
        % power
        % velocity
        % max_power
        % max_vel

    % matrix world where each position (element) goes from 0-10 (being this value the coverage level)
    
    
    clf
    scatter(agents(:).position(1),agents(:).position(2),'red')
    xlim([-size(world,2)/2 size(world,2)/2]);
    ylim([-size(world,1)/2 size(world,1)/2]);
    hold on;
    % quiver(P(:,1),P(:,2),dP(:,1),dP(:,2),'red')
    
    title(sprintf('\Lambda: %.2f', coverage));
    
end