#!/usr/bin/env python
import argparse
import collections
import os
import signal
import subprocess
import sys
import time
import yaml

IGNORABLE_WARNING = "InsecureRequestWarning"


def execute_load_test(command, load_time):
    """
    Executes a single load test with the given command

    The load test will first wait until all users are spawn. Then the swarm will
    load for the load_time. The output is then parsed to combine the data and
    average out the responses. The result is then put into a dict.

    Args:
        command (list): A list of strings that subprocess.Popen can exceute
        load_time (int): Number of seconds to run the test when all users spawn
    Returns:
        return data (dict): A dict of Users, RPS, and the percentiles

    """
    return_data = collections.OrderedDict(dict(users=command[4][3:]))
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines_iterator = iter(popen.stdout.readline, b"")
    warming_up = True
    while warming_up:
        for line in lines_iterator:
            if "All locusts hatched:" in line:
                warming_up = False
                break
    print "All users spawned"
    time.sleep(float(load_time))
    os.kill(popen.pid, signal.SIGTERM)

    #Seperate leftover lines after end of process
    for line in lines_iterator:
        if "Shutting down (exit code 0), bye" in line:
            break

    #Get to the first line of table 1's data and return RPS
    for line in lines_iterator:
        if "Total" in line:
            return_data['RPS'] = line.split()[3]
            break

    #Skip to the first line of table 2
    for line in lines_iterator:
        print line
        if "50%    66%    75%    80%    90%    95%    98%    99%   100%" in line:
            break

    for line in lines_iterator:
        print line
        if "--------" in line:
            break

    # collect percentile data
    total_requests = 0
    percent_values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for line in lines_iterator:
        print line
        if "--------" in line:
            break
        split_line = line.split()
        requests = int(split_line[2])
        for index in range(3, 12):
            percent_values[index-3] = int(percent_values[index-3])+int(split_line[index])*requests
        total_requests += requests

    if total_requests == 0:
        print "No data output"
        return return_data

    percentiles = ['50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%']
    for percentile, percentile_value in zip(percentiles, percent_values):
        try:
            value = percentile_value/total_requests
        except ZeroDivisionError:
            value = "-"
        return_data[percentile] = value
    for percentile, value in return_data.iteritems():
        print "{}: {},".format(percentile, value),
    print ""
    return return_data


def find_max_users(command):
    """
    Find the maximum number of users before the load server starts failing

    Args:
        command (list): A list of strings that subprocess.Popen can exceute
    Returns:
        (int): Max number of users
    """
    print command
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines_iterator = iter(popen.stdout.readline, b"")
    now = int(time.time()) #since # of users cannot be found, we use hatch rate in seconds
    print "Status is returned every 2 seconds"
    for line in lines_iterator:
        if IGNORABLE_WARNING not in line:
            if "%" in line and "Total" in line:
                # Prints current users
                print (int(time.time()) - now)*int(command[5][3:]),
                # If failure is less than 2 percent
                #TODO make failure threshold configurable
                if float(line.split()[2].split("(")[1].strip(")").strip("%")) >= 2:
                    popen.kill()
                    return (int(time.time()) - now)*int(command[5][3:])
            if "All locusts hatched:" in line:
                popen.kill()
                return int(command[4][3:])


def create_command(
        host=None,
        clients=None,
        hatch_rate=1,
        locustfile=None):
    """
    Creates the command to run the locustfile with parameters

    Args:
        host (str): url
        clients (int): Number of users
        hatch_rate (int): Users per second to spawn until clients is reached.
        locustfile (str): Directory of the locustfile
    """
    host = "--host={}".format(host)
    clients = "-c {}".format(clients)
    hatch_rate = "-r {}".format(hatch_rate)
    locustfile = "--locustfile={}".format(locustfile)

    result = ["locust", "--no-web", "--print-stats", locustfile, clients, hatch_rate, host]
    return result


def load_environment_variables(locust_folder):
    """
    Takes a directory and imports the config file and loads the env variables

    Args:
        locust_folder (str): location of the config file
    Returns:
        config_dict (dict): The env variables, which will later be logged
    """
    yaml_location = '{}/config.yaml'.format(locust_folder)
    f = open(yaml_location)
    yaml_data = yaml.safe_load(f)
    f.close()
    my_env = os.environ
    for key, value in yaml_data.iteritems():
        my_env[key] = value
    return yaml_data


def process_results(result_list, auto_test_command, config_dict):
    """
    Save commands, config and results to a file

    Args:
        result_list (list): List of the results to parse
        auto_test_command (list): List of the arguments passed to this script
        config_dict (dict): Dict of the config file used
    """
    result_keys = ""
    result_values = ""

    file_name = "stats_{}".format(int(time.time()))

    with open(file_name, 'w') as f: # pylint: disable=invalid-name
        # add commandline and env variables
        f.write(' '.join(auto_test_command) + "\n")
        f.write(str(config_dict) + "\n")

        for key, value in result_list[0].iteritems():
            result_keys = "{}{}, ".format(result_keys, key)
        # cut trailing comma and space
        print result_keys[:-2]
        f.write("{}\n".format(result_keys[:-2]))

        for item in result_list:
            for key, value in item.iteritems():
                result_values = result_values + "{}, ".format(value)
            print result_values[:-2]
            f.write("{}\n".format(result_values[:-2]))
            result_values = ""


def kill_existing_locust():
    """
    In case another locustfile was running, this will kill it.
    """
    try:
        pid = subprocess.check_output(['pidof -s -x locust'], shell=True)
    except subprocess.CalledProcessError:
        pid = None
    if pid is not None:
        os.kill(int(pid), signal.SIGTERM)


def main():
    """Main function that runs the script"""
    parser = argparse.ArgumentParser()
    parser.usage = '''
    Example:
        python auto_test.py --load_time 100 --ramp_up_time 60 --max_users 1000 --max_user_hatch_rate 10 --steps 20 -d mobile_api

        Find the max number of users up to 1000 at 10 users/second. When that
        max is found, divide it into 20 steps which will take 60 seconds to ramp
        up and will run for 100 seconds. This test will run the locustfile and
        config located in the folder mobile_api.


    Default command:
        python auto_test.py --load_time 300 --ramp_up_time 180 --max_users 1000 --max_user_hatch_rate 1 --steps 10 -d mobile_api

        This test, given that 1000  is the max users will take
        (1000*1) + (180*10) + (300*10) = 5800 seconds or about 1.5 hours.

    Repeatable tests:
        python auto_test.py --load_time 300 --ramp_up_time 180 --max_users 300 --max_user_hatch_rate 300 --steps 12 -d mobile_api

        Will test an endpoint up to 300 users, in increments of 25 users
        (300 users/12 steps).


    '''
    parser.add_argument('-c', '--max_users', help='Upper limit for finding out max users default is 1000', default=1000, type=int)
    parser.add_argument('-r', '--max_user_hatch_rate', help='Hatch rate used when finding max users default is 1/s', default=1, type=int)
    parser.add_argument('-t', '--load_time', help='Time to wait per test default is 5 minutes', default=300, type=int)
    parser.add_argument('-a', '--ramp_up_time', help='Number of seconds to ramp up a test default is 3 minutes', default=180, type=int)
    parser.add_argument('-s', '--steps', help='Number of steps to test before max load default is 10', default=10, type=int)
    parser.add_argument('-d', '--directory', help='Location of the locustfile and config', default=None)
    parser.add_argument('-u', '--host', help='Host url. Default is http://localhost:8000', default="http://localhost:8000")


    args = parser.parse_args()
    auto_test_command = sys.argv
    if not args.directory:
        print "Missing `--directory <directory>`. Requires directory of locustfile and config."
        return

    result_list = []
    kill_existing_locust()
    config_dict = load_environment_variables(args.directory)
    locustfile = "{}/locustfile.py".format(args.directory)

    start_time = time.time()
    print "Estimated runtime in minutes: ", ((args.load_time + args.ramp_up_time) * args.steps + (args.max_users/args.max_user_hatch_rate))/60
    print "Current time: {}".format(time.strftime('%X %x %Z'))

    if args.max_users == args.max_user_hatch_rate:
        max_users = args.max_users
    else:
        print "Find out the max # of users up to {} users at a rate of {} per second".format(args.max_users, args.max_user_hatch_rate)
        max_users = find_max_users(
            create_command(
                host=args.host,
                clients=args.max_users,
                hatch_rate=args.max_user_hatch_rate,
                locustfile=locustfile
            )
        )

    print "\n================================================================"

    if max_users == args.max_users:
        print "No failures at max users: {}".\
            format(max_users)
    else:
        print "Max users before failure: {}".\
            format(max_users)
    user_steps = max_users/args.steps

    try:
        print "****************************************************************"
        print "Loadtesting in {} steps of {} for {} seconds each".\
            format(args.steps, user_steps, args.load_time)
        users = user_steps
        for _ in range(args.steps):
            print "Loadtesting with {} users...".format(users),
            hatch_rate = users/args.ramp_up_time
            if hatch_rate < 1:
                hatch_rate = 1
            data = execute_load_test(
                create_command(
                    host=args.host,
                    clients=users,
                    hatch_rate=hatch_rate,
                    locustfile=locustfile
                ),
                load_time=args.load_time
            )
            users += user_steps
            result_list.append(data)
    # If script prematurely ends, print out the data
    finally:
        print "****************************RESULTS****************************"
        end_time = time.time()
        print "Actual runtime in minutes: {}".format(int((end_time - start_time)/60))
        process_results(result_list, auto_test_command, config_dict)

if __name__ == "__main__":
    main()
