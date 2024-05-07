function plotting(agents,world)
    % Struct agent:
        % position
        % radius
        % power
        % velocity
        % max_power
        % max_vel

    % matrix world where each position (element) goes from 0-10 (being this value the coverage level)
    
    scale = 10;
    
    world(1,1) = 1;
    clf
    imagesc(world)
    xlim([1,size(world,2)]);
    ylim([1,size(world,1)]);
    hold on;
    colorbar;
    colormap hot;
    scatter(agents(:).position(1),agents(:).position(2),'red')
    axis image;
    
    title(sprintf('Lambda'));
    pause(0.5);
end