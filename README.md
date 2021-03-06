# Github_Brute-Dork

This tool is a quick and easy Python script designed to identify Github search terms that can yield
potentially valuable results for security researchers and bug bounty hunters.  Using the Github api,
this script will perform a search for repos associated with a target organization and return a list 
of the searches sorted by the number of results.  This will allow researchers to identify potential 
code stored in Github that may contain sensitive information.  -rs0n

*******************************************************************
*I AM NOT RESPONSABLE FOR HOW YOU USE THIS TOOL.  DON'T BE A DICK!*
*******************************************************************

This tool requires Python Requests.  If you don't have the requests module installed, run this command:
`pip3 install requests`

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
-------------------------------------------------------------------------------------------------------
