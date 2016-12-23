if  date >= 160812 % MSU system in Boulder modfied to use QC pulse generator timing
    profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
    MCS.bins = 280;  % setting for 7 kHz (21 km)
    MCS.bin_duration = 500;  % ns
    MCS.accum = 10000; 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = ((1.25+1/2)-0.5/2)*150;  % changed hardware timing to start after pulse through
    blank_range = 300; % new pulse generator shifts gate timing so less outgoing pulse contamination 
elseif (date >= 160711) && (date <= 160811) % MSU system in Boulder original setup 
    profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2);  % 9kHz, 10k accum data rate is ~1.1s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2); % 9kHz, 10k accum data rate is ~1.1s 
    MCS.bins = 220;  
    MCS.bin_duration = 500;  % ns 
    MCS.accum = 10000; 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = -((0.1+1/2)-0.5/2)*150; 
    blank_range = 375; % new pulse generator shifts gate timing so less outgoing pulse contamination 
end
