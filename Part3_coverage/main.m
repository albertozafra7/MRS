% Struct agent:
    % position
    % radius
    % power
    % velocity
    % max_power
    % max_vel

% matrix world where each position (element) goes from 0-10 (being this value the coverage level)

N_iterations = 100; % Global number of iterations of the system

    
for K = 1:N_iterations
    % alpha(K) = K*sigma_i;
    % Coverage(K+1) = F*coverage(K) + G*alpha(K)
    % action(K) = (increment_x, increment_y)
    % P(k+1) = P(K) + action(K)
end
