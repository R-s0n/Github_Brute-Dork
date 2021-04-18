# Add search for user

import sys, getopt, time, json, requests, base64, time, math
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "ho:u:t:vdU:"
long_options = ["help", "org=", "user=", "token=", "verbose", "deep", "guser="]

help_notification = """
This tool is a quick and easy Python script designed to identify Github search terms that can yield
potentially valuable results for security researchers and bug bounty hunters.  Using the Github api,
this script will perform search repos associated with a target organization and return a list of the
searches sorted by the number of results.  This will allow researchers to identify potential code
stored in Github that may contain sensitive information.  -rs0n

******************************************************************************************************
*              I AM NOT RESPONSABLE FOR HOW YOU USE THIS TOOL.  DON'T BE A DICK!                     *
******************************************************************************************************

        python3 github_brutedork.py -u [USER] -t [TOKEN] -U [TARGET_USER] -o [TARGET_ORG] -v -d

------------------------------------------------------------------------------------------------------
|  Short  |    Long    |  Required  |                               Notes                             |
|---------|------------|------------|-----------------------------------------------------------------|
|   -h    |  --help    |     no     |                   Display this help message                     |
|   -o    |  --org     |     no     |                Name of the target organization                  |
|   -u    |  --user    |     yes    |                      Add Github Username                        |
|   -t    |  --token   |     yes    |                Add Github Personal Access Token                 |
|   -U    |  --guser   |     no     |                Search in specific user's repos                  |
|   -v    |  --verbose |     no     |                    Display verbose messages                     |
|   -d    |  --deep    |     no     |             Performs all searches from wordlist (1760)          |
-------------------------------------------------------------------------------------------------------"""

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    print (help_notification)
    sys.exit(2)

resultTotals = []
counter = 0
verbose = False
deep = False
hasOrg = False
hasUser = False
hasToken = False
hasGuser = False

for current_argument, current_value in arguments:
    if current_argument in ("-o", "--org"):
        organization = current_value
        hasOrg = True
    if current_argument in ("-u", "--user"):
        user = current_value
        hasUser = True
    if current_argument in ("-t", "--token"):
        token = current_value
        hasToken = True
    if current_argument in ("-U", "--guser"):
        guser = current_value
        hasGuser = True

if hasUser is False or hasToken is False:
    print(help_notification)
    sys.exit(0)

for current_argument, current_value in arguments:
    if current_argument in ("-h", "--help"):
        print(help_notification)
        sys.exit(0)
    if current_argument in ("-v", "--verbose"):
        print("Enabling verbose mode")
        verbose = True
    if current_argument in ("-d", "--deep"):
        print("Performing a deep dive")
        deep = True


plain_text_authtoken = f"{user}:{token}"
pta_bytes = plain_text_authtoken.encode("ascii")
base64_bytes = base64.b64encode(pta_bytes)
base64_string = base64_bytes.decode("ascii")

wordlist = open("wordlist.txt", "r").read().split()
headers = {"Authorization":f"Basic {base64_string}","User-Agent":f"{user}"}

search_params = ""

if hasGuser == True:
    search_params += f'user%3A{guser}+'
if hasOrg == True:
    search_params += f'"{organization}"+'

print("\n[-] Starting Search...")

start = time.time()

for payload in wordlist:
    r = requests.get(f'https://api.github.com/search/code?q={search_params}"{payload}"', headers=headers)
    if verbose is True:
        print(f'[-] Scanning URL: https://api.github.com/search/code?q={search_params}"{payload}"')

    content = json.loads(r.text)
    try:
        resultTotals.append({"payload":payload,"resultCount":content['total_count'],"searchUrl":f'https://github.com/search?q={search_params}"{payload}"&s=indexed&type=code'})
        if verbose is True:
            if content['total_count'] > 0:
                print(f"[+] Search for {payload} returned {content['total_count']} results!")
            else:
                print(f"[!] Search for {payload} did not return any results.")
    except Exception as e:
        if verbose is True:
            print("[!] Rate Limit exceded for Github API.  Pausing for 30 seconds...")
        time.sleep(30)
        wordlist.append(payload)
        if verbose is True:
            print(f'[*] Payload "{payload}" has been added to the end of the queue.  Continuing scan...')
    counter+=1
    if not counter % 10:
        print(f"[*] {counter} requests made...")
    time.sleep(0.5)
    if deep is False and counter > 170:
        break

sortedResultTotals = sorted(resultTotals, key=lambda k: k['resultCount'], reverse=True)

resultsString = ""

for result in sortedResultTotals:
    if result['resultCount'] > 0:
        resultsString += f"{result['payload']}|{result['resultCount']}|{result['searchUrl']}\n"

now = datetime.now().strftime("%d-%m-%y_%I%p")
output = open(f"brutedork_{now}.txt", "w")
output.write(resultsString)
output.close

print(resultsString)

end = time.time()
runtime_seconds = math.floor(end - start)
runtime_minutes = math.floor(runtime_seconds / 60)

print(f"[+] Github_bruteforce.py completed successfully in {runtime_minutes} minutes!")