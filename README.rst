locust auto
===========
What is it?
------------
Locust.io is a load testing framework written in python. Usually to run locust you run a locustfile with your tests, and then go to a web gui to enter your parameters. Your results are then displayed on the page and you have the option to save the test results. Locust does not give you load over time. By using the commandline interface of locust we want to 

``1.`` Find out the maximum number of users before reaching max load

``2.`` Run a load test for each increment of users. I.E. If the max number of users
is 500 and we want to use 5 steps, a test for 100, 200, 300, 400 ,500
locust users would be run.

with a single command.

Setup
------------
A config.yaml file is required for setting up auto_test script. In case your locustfile requires some environment variables, include them like below.

Example config.yaml::

    BASIC_AUTH_USER:
        user
    BASIC_AUTH_PASSWORD:
        pass
    SINGLE_TEST:
        VideoSummaryList
    LARGE_COURSE_TEST:
        mongo
    VERBOSE:
        "TRUE"

Example tree::

    Repo
    |----auto_test.py
    |----mobile_api
    |    |----locustfile
    |    |----config.yaml

Example stdout
--------------
In this example below, the commandline we use is::

    python auto_test.py --load_time 360 --ramp_up_time 300 --max_users 300 --max_user_hatch_rate 300 
    --steps 12 --directory mobile_api --host="http://url-of-the-load-test-env"

This test will be using the file in the `directory` called mobile_api against the endpoint set in `host`
  
`max_users`, along with `max_user_hatch_rate` will determine the point at which the load test will start seeing failures. For example, if the `max_users` is 1000 and `max_user_hatch_rate` is 2, locust will start creating 2 users per second until it either reaches 1000 users or when failures start to occur. In this particular case, by setting them    equal to each other, we want the `max_users` to be set at 300.  
&nbsp;&nbsp;&nbsp;&nbsp;After our `max_users` are determined, the series of tests will be divided into `steps`, 12 in this case. Starting with 25 users (300 `max_users` / 12 `steps`), the `ramp_up_time` determines how long the server should take to spawn the users in seconds. Since the user spawn rate is capped to no less than 1 per second, it the `ramp_up_time` is greater than the number of users, the number of users will be the determining factor. In the case of 25 users and a `ramp_up_time` of    300 seconds, the actual time taken will be 25 seconds. 
 
After our users have been spawned, `load_time` determines how long this test should run in seconds. After this test has been completed, the test will now start over with the next set of users which is 50 and so on until the `max_users` has been met. ::

    Estimated runtime in minutes:  132
    Current time: 01:10:57 03/16/15 UTC
    Find out the max # of users up to 300 users at a rate of 300 per second
    Status is returned every 2 seconds
    300 900
    ================================================================
    No failures at max users: 300
    ****************************************************************
    Loadtesting in 12 steps of 25 for 360 seconds each
    Loadtesting with 25 users... All users spawned
    users: 25, RPS: 2.20, 50%: 2100, 66%: 2300, 75%: 2800, 80%: 2800, 90%: 2900, 95%: 2900, 98%: 3000, 99%: 3100, 100%: 3481,
    Loadtesting with 50 users... All users spawned
    users: 50, RPS: 3.90, 50%: 2200, 66%: 2300, 75%: 2900, 80%: 2900, 90%: 2900, 95%: 3000, 98%: 3100, 99%: 3100, 100%: 3271,
    Loadtesting with 75 users... All users spawned
    users: 75, RPS: 5.90, 50%: 2200, 66%: 2400, 75%: 2900, 80%: 2900, 90%: 3000, 95%: 3000, 98%: 3100, 99%: 3200, 100%: 3287,
    Loadtesting with 100 users... All users spawned
    users: 100, RPS: 7.80, 50%: 2400, 66%: 2500, 75%: 3000, 80%: 3000, 90%: 3100, 95%: 3200, 98%: 3300, 99%: 3400, 100%: 3612,
    Loadtesting with 125 users... All users spawned
    users: 125, RPS: 10.50, 50%: 2800, 66%: 3000, 75%: 3200, 80%: 3200, 90%: 3600, 95%: 3900, 98%: 4000, 99%: 4100, 100%: 4389,
    Loadtesting with 150 users... All users spawned
    users: 150, RPS: 12.60, 50%: 3000, 66%: 3200, 75%: 3300, 80%: 3400, 90%: 3700, 95%: 4000, 98%: 4300, 99%: 4400, 100%: 4712,
    Loadtesting with 175 users... All users spawned
    users: 175, RPS: 13.30, 50%: 3300, 66%: 3500, 75%: 3700, 80%: 3800, 90%: 4100, 95%: 4300, 98%: 4500, 99%: 4600, 100%: 5412,
    Loadtesting with 200 users... All users spawned
    users: 200, RPS: 13.90, 50%: 3700, 66%: 4000, 75%: 4200, 80%: 4400, 90%: 4600, 95%: 4800, 98%: 5000, 99%: 5200, 100%: 5850,
    Loadtesting with 225 users... All users spawned
    users: 225, RPS: 0.00, 50%: 4400, 66%: 4700, 75%: 4800, 80%: 4900, 90%: 5200, 95%: 5500, 98%: 5800, 99%: 6000, 100%: 203352,
    Loadtesting with 250 users... All users spawned
    users: 250, RPS: 11.70, 50%: 4650, 66%: 6050, 75%: 7050, 80%: 7550, 90%: 9050, 95%: 10050, 98%: 10550, 99%: 10550, 100%: 11532,
    Loadtesting with 275 users... All users spawned
    users: 275, RPS: 15.80, 50%: 6700, 66%: 8200, 75%: 9750, 80%: 10250, 90%: 11250, 95%: 12250, 98%: 13250, 99%: 13750, 100%: 14433,
    Loadtesting with 300 users... All users spawned
    users: 300, RPS: 11.60, 50%: 16000, 66%: 18500, 75%: 20000, 80%: 21000, 90%: 25500, 95%: 29500, 98%: 32500, 99%: 37000, 100%: 38646,
    ****************************RESULTS****************************
    Actual runtime in minutes: 104
    users, RPS, 50%, 66%, 75%, 80%, 90%, 95%, 98%, 99%, 100%
    25, 2.20, 2100, 2300, 2800, 2800, 2900, 2900, 3000, 3100, 3481
    50, 3.90, 2200, 2300, 2900, 2900, 2900, 3000, 3100, 3100, 3271
    75, 5.90, 2200, 2400, 2900, 2900, 3000, 3000, 3100, 3200, 3287
    100, 7.80, 2400, 2500, 3000, 3000, 3100, 3200, 3300, 3400, 3612
    125, 10.50, 2800, 3000, 3200, 3200, 3600, 3900, 4000, 4100, 4389
    150, 12.60, 3000, 3200, 3300, 3400, 3700, 4000, 4300, 4400, 4712
    175, 13.30, 3300, 3500, 3700, 3800, 4100, 4300, 4500, 4600, 5412
    200, 13.90, 3700, 4000, 4200, 4400, 4600, 4800, 5000, 5200, 5850
    225, 0.00, 4400, 4700, 4800, 4900, 5200, 5500, 5800, 6000, 203352
    250, 11.70, 4650, 6050, 7050, 7550, 9050, 10050, 10550, 10550, 11532
    275, 15.80, 6700, 8200, 9750, 10250, 11250, 12250, 13250, 13750, 14433
    300, 11.60, 16000, 18500, 20000, 21000, 25500, 29500, 32500, 37000, 38646

