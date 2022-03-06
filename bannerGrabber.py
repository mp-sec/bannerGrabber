#!/usr/bin/python3

import socket
import subprocess
import re
import errno
import os
import datetime


def banner(user_ip, ports):
    for port in ports:
        sock = socket.socket()
        # connect_ex returns 0 upon success, or an appropriate ERRNO for anything else
        result = sock.connect_ex((user_ip, port))

        # Handles BrokenPipe error so execution can continue
        try:
            # Sends input to the socket if the port is an HTTP port so execution can continue
            sock.send(f"GET / HTTP/1.1\r\nHost: {user_ip}\r\n\r\n".encode('UTF-8'))
        except IOError as brokenPipe:
            if brokenPipe.errno == errno.EPIPE:
                print("Information sent to closed socked.")

        if result == 0:
            grabbed = sock.recv(4096)
            # If the socket waits for 4KB of data for more than 5 seconds then timeout the connection
            sock.settimeout(5)
            service(grabbed, user_ip, port)
            # print(grabbed)
            # print(grabbed.decode('UTF-8'), "\n")
        sock.close()


def service(grabbed, user_ip, port):
    # Converts the retrieved information from byte format and convert it into UTF-8
    decoded = grabbed.decode('UTF-8')
    # Regular expression to extract the service on the port
    # Looks for "Server: ", use . to match any character, + for 1 or more characters, ? for 0 or 1, and \\n for newline
    pattern = "Server: (.+?)\\n"
    # Because the output of the decoded byte string uses newlines, multimode must be used
    grabbed_parse = re.search(pattern, decoded, re.MULTILINE)
    # Need to use .group(1) to get only the matching string, .group(0) returns the entire matched string
    # print("Matched service: {}".format(grabbed_parse.group(1)))

    exploit_finder(grabbed_parse, user_ip, port)


def exploit_finder(grabbed_parse, user_ip, port):
    # This is required to get rid of the "tput: No value for $TERM and no -T specified" error
    os.environ["TERM"] = "dumb"

    searchsploit_process = subprocess.check_output(["searchsploit", grabbed_parse.group(1)]).decode('UTF-8')

    printer_and_file_writer(grabbed_parse, user_ip, port, searchsploit_process)


def printer_and_file_writer(grabbed_parse, user_ip, port, searchsploit_process):
    extension = ".txt"
    now = datetime.datetime.now()
    # Changes the format to be numerical day, month, year_24h hour, minute
    title_timestamp = now.strftime("%d%m%Y_%H%M")

    file_path = "/home/hackerman/PycharmProjects/module8/"

    # File path and filename can be altered as user sees fit
    with open(file_path + "bannergrab_" + title_timestamp + extension, "a") as file_writer:
        file_writer.write("{} - {} -{}".format(user_ip, port, grabbed_parse.group(1)))
        print("{} - {} -{}".format(user_ip, port, grabbed_parse.group(1)))
        file_writer.write("Available exploits and shellcodes for {}: \n{}\n".format(grabbed_parse.group(1), searchsploit_process))
        print("Available exploits and shellcodes for {}: \n{}".format(grabbed_parse.group(1), searchsploit_process))


def main():
    user_ip = input("Enter an IP address for the banner grabber: ")
    ports = []

    # Lets the user know that the scan is in progress
    print("-" * 60)
    print("Scanning host", user_ip)
    print("-" * 60)

    try:
        # Reads all possible ports to find which are open for the given IP address
        for port in range(1, 65535):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect_ex returns 0 upon success, or an appropriate ERRNO for anything else
            result = sock.connect_ex((user_ip, port))
            if result == 0:
                ports.append(port)
            sock.close()
    except KeyboardInterrupt:
        print("Ctrl+C input detected. Terminating program execution.")
        exit()

    except socket.error:
        print("ERROR: Unable to connect to address.")
        exit()

    print("List of all open ports for", user_ip, ":", ports)

    banner(user_ip, ports)


main()
