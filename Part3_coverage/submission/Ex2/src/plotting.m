function plotting(agents,world,ratio,colMap)
    
    world(1,1) = 1;
    clf
    imagesc(world)
    xlim([1,size(world,2)]);
    ylim([1,size(world,1)]);
    hold on;
    colorbar;
    colormap (colMap);
%     colormap hsv;
    if ~isempty(agents)
        scatter(agents.position(:,2),agents.position(:,1),'red')
        scatter(agents.goal(:,2),agents.goal(:,1),'green','d')
    end
    axis image;
    
    title(sprintf('Correct Lambda: %.2f%%',ratio));
end