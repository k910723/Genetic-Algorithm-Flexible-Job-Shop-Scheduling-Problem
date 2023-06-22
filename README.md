# Genetic Algorithm Flexible Job Shop Scheduling Problem

## input data format ##

**a txt file :**

+ First line : 3 integers
  [the number of jobs (a), the number of machines (b), capacity for simultaneous operations on each machine]
 
+ Second line : b integers
  [the unit time to install and uninstall for each machinme]
 
+ Third line : 4 integers
  [time for cleaning up a machine, time to move between 1, 2 and 3 units of machine distance]
 
+ Fourth line : 2 parameters
  [failure rate (decimal), time for machine recovery (integer, in unit time)]
  If the failure rate is non-zero, the machine will randomly fail with the given probability before starting 
  and will remain idle until recovery time is over.
 
+ The Following a lines :
  [number of operations for the job (m),
  (the number of machine available for a operation (n), (the index of the machine, its processing time for the operation) * n) *m
  ]

## License ##
MIT license
