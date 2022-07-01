# How to execute

Create a control bot in your host 

$ sudo python3 slave.py admin

Create the desired amount of bots:

\> add x

where x is the number of bots desired. (Or omit it to add one.)

Available instructions:                                 
"stop" - stop the bots                                  
"status" - view botnet status                           
"target" - change target                                
"pause" - pause attack                                  
"resume" - resume attack                                
 "add" - add a bot                                       
"add x" - add x bots (pausing is recommended ;) ) 


If you close the control bot, the entire swarm will be shut down - this is effectively a bug but kept due to being really handy as an emergency shutdown.
If you create too many bots, your system *will* crash, be warned. 
