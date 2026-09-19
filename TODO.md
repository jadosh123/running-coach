# Detailing Journey

## Where im at now DATE: 19th September 2026 5:52PM
Currently separated the garmin login/auth into its own module so the user can run it once in terminal and authenticate, which is what other mcp bundles seem to be doing with garminconnect.
Then the point is to reuse the tokens given by garmin or refresh them which the lib does already and not need to authenticate again (It would be needed occaisonally).

My next goals are:
1) Testing the first flow, authenticating in terminal, then fetching and populating db to make sure a re-authentication isn't needed. This way I can expose the syncing method as a tool so the llm can decide if to fetch in case of no data being returned.

2) Expose that sync tool in the mcp and test in claude code after authenticating to see if it decides to populate with a specific response telling it what tool to use after no data was returned (DB not populated yet in first run).

3) Start adding more tools for the basic usages like fetching stored activities and splits.