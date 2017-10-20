1. How would your design change if the data was not static (i.e updated frequently
during the day)?
From a design perspective and if the data was not static I would look to use an RDD package such as Apache Spark to set up the map and reduce dataset functions that Pandas is currently performing on the csv format static data.

2. Do you think your design can handle 1000 concurrent requests per second? If not, what
would you change?
The process to compile the product data from the intial get request takes on average 0.2 seconds to return product data. With 1000 concurrent request this would cause considerable delays on the server. As above in 1 RDD would enable faster processing of the map reduce or parrallel instances running the server with a load balancer could be introduced.