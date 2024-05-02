%% 2D
clf
N = 5;
M = 5;
nX = 20;
nY = 20;
alpha = 0.1;

X = repmat(linspace(-N,N,nX),[nY 1]);
Y = repmat(linspace(-M,M,nY)',[1 nX]);

[U,V] = grad(X,Y);

quiver(X,Y,U,V)

[x, y] = ginput(3);

while 1==1
    clf
    quiver(X,Y,U,V)
    hold on;
    scatter(x,y,'red')
    [dx,dy] = grad(x,y);
    x = x+dx*alpha;
    y = y+dy*alpha;
    pause(0.001)
end

%% 2D acc
clf
N = 3;
M = 3;
nX = 20;
nY = 20;
alpha = 0.1;
beta = 0.01;

X = repmat(linspace(-N,N,nX),[nY 1]);
Y = repmat(linspace(-M,M,nY)',[1 nX]);

[U,V] = grad(X,Y);

quiver(X,Y,U,V)

n_bodies = 3;

% [x, y] = ginput(n_bodies);
x = zeros([n_bodies,1])-1;
y = zeros([n_bodies,1])+1;
x = x+(rand([n_bodies,1])-0.5)*0.0001;
y = y+(rand([n_bodies,1])-0.5)*0.0001;

dx = zeros([n_bodies,1]);
dy = zeros([n_bodies,1]);

while 1==1
    clf
    quiver(X,Y,U,V)
    hold on;
    scatter(x,y,'red')
    quiver(x,y,dx,dy,'red')
    [ddx,ddy] = grad(x,y);
    dx = dx+ddx*beta;
    dy = dy+ddy*beta;
    x = x+dx*alpha;
    y = y+dy*alpha;
    pause(0.0001)
end

%% 3D
close all; % figures

N = 1;
alpha = 0.01;

x = rand([N,1]);
y = rand([N,1]);
z = rand([N,1]);
i=0;
while 1==1
    i = mod((i+1),5);
    [dx,dy,dz] = grad3d(x,y,z);
    if i == 0
        scatter3(x,y,z)
        hold on;
    end
    x = x+dx*alpha;
    y = y+dy*alpha;
    z = z+dz*alpha;
    pause(0.001)
end


%% Functions

% 2D
function [x,y] = grad(X,Y)
    [x,y] = grad8(X,Y);
end

function [x,y] = grad1(X,Y)
    x = cos(Y);
    y = sin(X);
end

function [x,y] = grad2(X,Y)
    x = -cos(atan2(Y,X))./(X.*X+Y.*Y);
    y = -sin(atan2(Y,X))./(X.*X+Y.*Y);
end

function [x,y] = grad3(X,Y)
    x = X.*cos(Y);
    y = Y.*sin(X);
end

function [x,y] = grad4(X,Y)
    x = sin(atan2(Y,X));
    y = -cos(atan2(Y,X));
end

function [x,y] = grad5(X,Y)
    x = sin(atan2(Y,X))./sqrt(X.*X+Y.*Y);
    y = -cos(atan2(Y,X))./sqrt(X.*X+Y.*Y);
end

function [x,y] = grad6(X,Y)
    X1 = X+4;
    Y1 = Y;
    x = sin(atan2(Y1,X1))./sqrt(X1.*X1+Y1.*Y1);
    y = -cos(atan2(Y1,X1))./sqrt(X1.*X1+Y1.*Y1);
    X2 = X-4;
    Y2 = Y;
    x = x+sin(atan2(Y2,X2))./sqrt(X2.*X2+Y2.*Y2);
    y = y-cos(atan2(Y2,X2))./sqrt(X2.*X2+Y2.*Y2);
end

function [x,y] = grad7(X,Y)
    x = zeros(size(X));
    y = zeros(size(Y));
    Xlist = -[3,-3,0];
    Ylist = -[0,0,3];
    for i = 1:length(Xlist)
        Xaux = X+Xlist(i);
        Yaux = Y+Ylist(i);
        x = x+sin(atan2(Yaux,Xaux))./sqrt(Xaux.*Xaux+Yaux.*Yaux);
        y = y-cos(atan2(Yaux,Xaux))./sqrt(Xaux.*Xaux+Yaux.*Yaux);
    end
end

function [x,y] = grad8(X,Y)
    x = zeros(size(X));
    y = zeros(size(Y));
    Xlist = -[-1,1.5,0];
    Ylist = -[-1,0,1.5];
    for i = 1:length(Xlist)
        Xaux = X+Xlist(i);
        Yaux = Y+Ylist(i);
        x = x-cos(atan2(Yaux,Xaux))./sqrt(Xaux.*Xaux+Yaux.*Yaux);
        y = y-sin(atan2(Yaux,Xaux))./sqrt(Xaux.*Xaux+Yaux.*Yaux);
    end
end

% 3D

function [x,y,z] = grad3d(X,Y,Z)
    [x,y,z] = grad3d1(X,Y,Z);
end

function [x,y,z] = grad3d1(X,Y,Z)
    a = 10;
    b = 8/3;
    c = 28;
    x = a*(Y-X);
    y = X.*(c-Z)-Y;
    z = X.*Y-b.*Z;
end
