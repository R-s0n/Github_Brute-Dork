import sys, getopt, time, json, requests, base64

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "ho:u:t:vd"
long_options = ["help", "org=", "user=", "token=", "verbose", "deep"]

help_notification = """
This tool is a quick and easy Python script designed to identify Github search terms that can yield
potentially valuable results for security researchers and bug bounty hunters.  Using the Github api,
this script will perform search repos associated with a target organization and return a list of the
searches sorted by the number of results.  This will allow researchers to identify potential code
stored in Github that may contain sensitive information.  -rs0n

******************************************************************************************************
*              I AM NOT RESPONSABLE FOR HOW YOU USE THIS TOOL.  DON'T BE A DICK!                     *
******************************************************************************************************

python3 github_brutedork.py [-h --help] [-o --org] [-u --user] [-t --token] [-v --verbose] [-d --deep]

------------------------------------------------------------------------------------------------------
|  Short  |    Long    |  Required  |                               Notes                             |
|---------|------------|------------|-----------------------------------------------------------------|
|   -h    |  --help    |     no     |                   Display this help message                     |
|   -o    |  --org     |     yes    |                Name of the target organization                  |
|   -u    |  --user    |     yes    |                      Add Github Username                        |
|   -t    |  --token   |     yes    |                Add Github Personal Access Token                 |
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

if hasOrg is False or hasUser is False or hasToken is False:
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
headers = {"Authorization":f"Basic {base64_string}","User-Agent":"R-son"}

print("\nStarting Search...")


for payload in wordlist:
    r = requests.get(f'https://api.github.com/search/code?q="{organization}"+{payload}', headers=headers)
    content = json.loads(r.text)
    try:
        resultTotals.append({"payload":payload,"resultCount":content['total_count'],"searchUrl":f"https://github.com/search?q=%22{organization}%22+{payload}&type=code"})
        if verbose is True:
            print(f"Search for {payload} returned {content['total_count']} results")
    except:
        print("Rate Limit exceded for Github API.  Pausing for 30 seconds...")
        time.sleep(30)
    counter+=1
    if not counter % 10:
        print(f"{counter} requests made...")
    time.sleep(0.5)
    if deep is False and counter > 170:
        break

sortedResultTotals = sorted(resultTotals, key=lambda k: k['resultCount'], reverse=True)

resultsString = ""

for result in sortedResultTotals:
    resultsString += f"{result['payload']}:{result['resultCount']}:{result['searchUrl']}\n"

output = open(f"brutedork.{organization}.txt", "w")
output.write(resultsString)
output.close

print(resultsString)