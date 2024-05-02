%% 2D acc
clf
N = 20;
speed = 1;
alpha = 1*speed;
beta = 0.02*speed;

dims = 2;
n_bodies = 4;

P = (rand([n_bodies,dims])-0.5)*2*10;
dP = zeros([n_bodies,dims]);

% P = [10,0;0,-10;-10,0;0,10]+rand([n_bodies,dims])*5;
% dP = [0,-1;-1,0;0,1;1,0]/6;

% P = [0,10;0,-10;0,5;0,-5]+(rand([n_bodies,dims])-0.5)*0.1;
% dP = [3,0;-3,0;1,0;-1,0]/10;

ctr = mean(P);
while 1==1
    clf
    if dims == 2
        scatter(P(:,1),P(:,2),'red')
        xlim([-N N]);
        ylim([-N N]);
        hold on;
        quiver(P(:,1),P(:,2),dP(:,1),dP(:,2),'red')
    else
        scatter3(P(:,1),P(:,2),P(:,3),'red')
        xlim([-N N]);
        ylim([-N N]);
        zlim([-N N]);
        hold on;
        quiver3(P(:,1),P(:,2),P(:,3),dP(:,1),dP(:,2),dP(:,3),'red')
    end
    title(sprintf('Ec: %.2f, Mean: %.2f', sum(sqrt(sum(dP.^2,2))),sqrt(sum(mean(P,1).^2))));
    g = grad(P);
    dP = dP + g*beta;
    P = P + dP*alpha;
    pause(0.0001)
end

% Functions

% 2D
function dP = grad(P)
    dP = grad1(P);
end

function dP = grad1(P)
    dP = zeros(size(P));

    for i = 1:size(P,1)
        auxP = P-P(i,:);
        auxP(i,:) = [];
        mods2 = sum(auxP.^2,2);
        dP(i,:) = sum(auxP./(mods2),1);
    end
end
